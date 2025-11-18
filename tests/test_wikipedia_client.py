import json
from types import SimpleNamespace

import pytest

from zdex.wikipedia_client import WikipediaFetcher


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return

    def json(self):
        return self._data


def test_extract_habitat_diet_wikidata(monkeypatch):
    fetcher = WikipediaFetcher(languages=("en",))

    # Steps: first call - pageprops, second - sparql
    def fake_get(url, params=None, headers=None, timeout=None):
        if "w/api.php" in url:
            return DummyResponse({
                "query": {
                    "pages": [
                        {"pageprops": {"wikibase_item": "Q1"}}
                    ]
                }
            })
        if "query.wikidata.org" in url:
            # Check if the query is for habitat or diet
            query = params.get("query", "")
            if 'rdfs:label "habitat"@en' in query:
                data = {
                    "results": {
                        "bindings": [
                            {"valueLabel": {"value": "Temperate forests"}}
                        ]
                    }
                }
                return DummyResponse(data)
            # For diet, return empty results
            return DummyResponse({"results": {"bindings": []}})
        return DummyResponse({})

    monkeypatch.setattr(fetcher, "_session", SimpleNamespace(get=fake_get))

    habitat, diet = fetcher._extract_habitat_diet_wikidata("en", "Dog")
    assert habitat == "Temperate forests"
    assert diet is None

    # Test the higher-level properties discovery (conservation, distribution)
    def fake_get_props(url, params=None, headers=None, timeout=None):
        # first call: w/api.php -> returns Q1
        if "w/api.php" in url and params and params.get("prop") == "pageprops":
            return DummyResponse({
                "query": {"pages": [{"pageprops": {"wikibase_item": "Q1"}}]}
            })
        # second call: property discovery
        if "query.wikidata.org" in url and params and "CONTAINS" in params.get("query", ""):
            return DummyResponse({
                "results": {"bindings": [{"prop": {"value": "http://www.wikidata.org/entity/P100"}}]}
            })
        # third call: values for property
        if "query.wikidata.org" in url and params and "wd:Q1" in params.get("query", ""):
            return DummyResponse({
                "results": {"bindings": [{"valueLabel": {"value": "Global"}}]}
            })
        return DummyResponse({})

    monkeypatch.setattr(fetcher, "_session", SimpleNamespace(get=fake_get_props))
    props = fetcher._extract_wikidata_properties("en", "Dog")
    assert props.get("distribution") == "Global" or props.get("habitat") is not None
