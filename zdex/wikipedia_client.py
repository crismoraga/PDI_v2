"""Wikipedia lookup helpers for enriching species information."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Optional
from urllib.parse import quote

import requests
import wikipediaapi

from . import config

logger = logging.getLogger(__name__)


@dataclass
class WikipediaEntry:
    title: str
    summary: str
    page_url: str
    image_url: Optional[str]
    language: str
    conservation_status: Optional[str] = None
    distribution: Optional[str] = None
    habitat: Optional[str] = None
    diet: Optional[str] = None


class WikipediaFetcher:
    """Lazy Wikipedia client with multi-language fallback and caching."""

    def __init__(self, languages: Iterable[str] = config.WIKIPEDIA_LANG_PRIORITY) -> None:
        self._languages = tuple(languages)
        self._apis = {
            lang: wikipediaapi.Wikipedia(
                language=lang,
                extract_format=wikipediaapi.ExtractFormat.WIKI,
                user_agent=f"{config.APP_NAME}/1.0 (https://github.com/google/cameratrapai)"
            )
            for lang in self._languages
        }
        self._session = requests.Session()

    def fetch_for_terms(self, *terms: str) -> Optional[WikipediaEntry]:
        seen = set()
        candidates = [term for term in terms if term and term.strip()]
        for candidate in candidates:
            key = candidate.lower()
            if key in seen:
                continue
            seen.add(key)
            entry = self._fetch_candidate(candidate)
            if entry:
                return entry
        return None

    def _fetch_candidate(self, candidate: str) -> Optional[WikipediaEntry]:
        for lang in self._languages:
            api = self._apis[lang]
            page = api.page(candidate)
            if not page.exists():
                continue
            summary = page.summary.strip()
            if len(summary) > config.WIKIPEDIA_SUMMARY_CHAR_LIMIT:
                summary = summary[: config.WIKIPEDIA_SUMMARY_CHAR_LIMIT].rsplit(". ", 1)[0] + "."
            image_url = self._resolve_main_image(lang, page.title)
            # Try structured extraction: Wikidata via SPARQL -> fall back to infobox parsing
            habitat, diet = None, None
            conservation, distribution = None, None
            try:
                props = self._extract_wikidata_properties(lang, page.title)
                wikidata_habitat = props.get("habitat")
                wikidata_diet = props.get("diet")
                conservation = props.get("conservation")
                distribution = props.get("distribution")
                if wikidata_habitat:
                    habitat = wikidata_habitat
                if wikidata_diet:
                    diet = wikidata_diet
            except Exception:
                pass
            try:
                habitat, diet = self._extract_habitat_diet(lang, page.title)
            except Exception:
                # best-effort only
                habitat, diet = None, None
            return WikipediaEntry(
                title=page.title,
                summary=summary,
                page_url=page.fullurl,
                image_url=image_url,
                language=lang,
                conservation_status=conservation,
                distribution=distribution,
                habitat=habitat,
                diet=diet,
            )
        return None

    @lru_cache(maxsize=128)
    def _resolve_main_image(self, lang: str, title: str) -> Optional[str]:
        """Use the Wikimedia REST API to obtain a lead image."""
        try:
            response = self._session.get(
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}",
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Failed to fetch wikipedia image for %s:%s (%s)", lang, title, exc)
            return None
        thumbnail = data.get("thumbnail") or {}
        return thumbnail.get("source")

    def _extract_habitat_diet(self, lang: str, title: str) -> tuple[Optional[str], Optional[str]]:
        """Best-effort extraction of 'habitat' & 'diet' from MediaWiki raw content.

        Uses the action=query&prop=revisions API to get the page wikitext and searches
        the infobox lines for common fields. This is best-effort — it will not parse
        complex templates but works for many species pages.
        """
        habitat = None
        diet = None
        try:
            # Get raw page wikitext from MediaWiki
            api = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "titles": title,
                "format": "json",
                "formatversion": 2,
            }
            r = self._session.get(api, params=params, timeout=6)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                return habitat, diet
            content = pages[0].get("revisions", [])
            if not content:
                return habitat, diet
            wikitext = content[0].get("slots", {}).get("main", {}).get("content", "")

            # Look for common infobox keys
            # Habitat candidates often: 'habitat', 'distribution', 'range'
            # Diet candidates often: 'diet', 'feeding', 'food'
            def _extract_field(keys: list[str]) -> Optional[str]:
                for key in keys:
                    # simple patterns: | key = value
                    # match with optional spaces around '='
                    import re

                    pattern = re.compile(r"\|\s*" + re.escape(key) + r"\s*=\s*(.+)")
                    m = pattern.search(wikitext)
                    if m:
                        value = m.group(1)
                        # stop at next pipe that starts a new field
                        # remove templates and markup crudely
                        value = value.split("\n|", 1)[0].split("\n", 1)[0]
                        # Strip wiki markup
                        value = re.sub(r"\{\{.*?\}\}", "", value)
                        value = re.sub(r"\[\[([^|\]]*\|)?", "", value)
                        # avoid Python "invalid escape" warnings - simply remove the closing brackets
                        value = value.replace("]]", "").strip()
                        if len(value) > 0:
                            return value
                return None

            habitat = _extract_field(["habitat", "distribution", "range", "environment"])
            diet = _extract_field(["diet", "feeding", "food", "feeds on"]) or _extract_field([
                "carnivore", "herbivore", "omnivore"
            ])

            # Shorten long strings
            if habitat and len(habitat) > 300:
                habitat = habitat[:300] + "..."
            if diet and len(diet) > 300:
                diet = diet[:300] + "..."
            return habitat, diet
        except Exception:
            return None, None

    def _extract_habitat_diet_wikidata(self, lang: str, title: str) -> tuple[Optional[str], Optional[str]]:
        """Attempt to fetch habitat and diet from Wikidata using the entity ID of the page.

        Steps:
        1. Query Wikipedia pageprops for `wikibase_item` (the Q-ID on Wikidata).
        2. Run a SPARQL query searching for properties labelled 'habitat' and 'diet' and return label(s).

        This is best-effort: property labels may vary, but many species pages have standard properties.
        """
        try:
            # Get the wikibase item id (Q##) for the page
            api = f"https://{lang}.wikipedia.org/w/api.php"
            r = self._session.get(api, params={
                "action": "query",
                "titles": title,
                "prop": "pageprops",
                "format": "json",
            }, timeout=6)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                return None, None
            wikibase_item = pages[0].get("pageprops", {}).get("wikibase_item")
            if not wikibase_item:
                return None, None

            # SPARQL endpoint
            sparql = "https://query.wikidata.org/sparql"

            def query_property(prop_label: str) -> Optional[str]:
                q = (
                    'SELECT ?valueLabel WHERE {'
                    f' wd:{wikibase_item} ?prop ?value .'
                    f' ?prop rdfs:label "{prop_label}"@en .'
                    ' SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }'
                    ' } LIMIT 1'
                )
                headers = {"Accept": "application/sparql-results+json"}
                rr = self._session.get(sparql, params={"query": q}, headers=headers, timeout=8)
                rr.raise_for_status()
                out = rr.json()
                bindings = out.get("results", {}).get("bindings", [])
                if bindings and "valueLabel" in bindings[0]:
                    return bindings[0]["valueLabel"]["value"]
                return None

            habitat = query_property("habitat") or query_property("hábitat")
            diet = query_property("diet") or query_property("feeding")
            return habitat, diet
        except Exception:
            return None, None

    def _extract_wikidata_properties(self, lang: str, title: str) -> dict:
        """Find various structured attributes using Wikidata SPARQL.

        We search for property URIs whose label contains keywords such as
        'habitat', 'diet', 'conservation', 'distribution', etc., then
        query the item for those properties. This allows extracting a
        variety of typed data without hardcoding every property ID.
        """
        try:
            # Find the Wikidata Q-ID first
            api = f"https://{lang}.wikipedia.org/w/api.php"
            r = self._session.get(api, params={
                "action": "query",
                "titles": title,
                "prop": "pageprops",
                "format": "json",
            }, timeout=6)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                return {}
            wikibase_item = pages[0].get("pageprops", {}).get("wikibase_item")
            if not wikibase_item:
                return {}

            sparql = "https://query.wikidata.org/sparql"

            def find_props_for_term(term: str) -> list[str]:
                q = (
                    'SELECT ?prop ?propLabel WHERE {'
                    '?prop a wikibase:Property .'
                    '?prop rdfs:label ?propLabel .'
                    'FILTER(LANGMATCHES(LANG(?propLabel), "en")) .'
                    'FILTER(CONTAINS(LCASE(?propLabel), "' + term.lower() + '"))'
                    'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }'
                    '} LIMIT 30'
                )
                headers = {"Accept": "application/sparql-results+json"}
                rr = self._session.get(sparql, params={"query": q}, headers=headers, timeout=8)
                rr.raise_for_status()
                out = rr.json()
                return [b.get("prop", {}).get("value") for b in out.get("results", {}).get("bindings", []) if b.get("prop")]

            def values_for_property_uri(prop_uri: str) -> list[str]:
                import re

                # Try to extract P###
                m = re.search(r"P\d+", prop_uri)
                if not m:
                    return []
                pid = m.group(0)
                q = (
                    f'SELECT ?valueLabel WHERE {{ wd:{wikibase_item} wdt:{pid} ?value . '
                    'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5'
                )
                headers = {"Accept": "application/sparql-results+json"}
                rr = self._session.get(sparql, params={"query": q}, headers=headers, timeout=8)
                rr.raise_for_status()
                out = rr.json()
                return [b["valueLabel"]["value"] for b in out.get("results", {}).get("bindings", []) if "valueLabel" in b]

            props = {}
            for term in ("habitat", "diet", "conservation", "distribution", "endemic"):
                prop_uris = find_props_for_term(term)
                found = []
                for uri in prop_uris:
                    vals = values_for_property_uri(uri)
                    found.extend(vals)
                if found:
                    # join into single shorthand string
                    props[term if term != "conservation" else "conservation"] = ", ".join(found)

            return props
        except Exception:
            return {}


FETCHER = WikipediaFetcher()
