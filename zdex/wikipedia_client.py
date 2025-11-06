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
            return WikipediaEntry(
                title=page.title,
                summary=summary,
                page_url=page.fullurl,
                image_url=image_url,
                language=lang,
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


FETCHER = WikipediaFetcher()
