from org_id import Registry


def make_registry() -> Registry:
    return Registry.from_dict(
        {
            "lists": [
                {
                    "code": "GB-COH",
                    "name": {"en": "Companies House"},
                    "description": {"en": "UK company register"},
                    "coverage": ["GB"],
                    "structure": ["company"],
                    "deprecated": False,
                    "quality": 75,
                },
                {
                    "code": "GB-OLD",
                    "name": {"en": "Old register"},
                    "description": {"en": "Deprecated register"},
                    "coverage": ["GB"],
                    "structure": ["company"],
                    "deprecated": True,
                    "quality": 20,
                },
                {
                    "code": "US-EIN",
                    "name": {"en": "IRS EIN"},
                    "description": {"en": "US tax register"},
                    "coverage": ["US"],
                    "structure": ["charity"],
                    "deprecated": False,
                    "quality": 80,
                },
            ]
        }
    )


def test_registry_get():
    registry = make_registry()
    entry = registry.get("gb-coh")
    assert entry is not None
    assert entry.code == "GB-COH"
    assert entry.name.best == "Companies House"


def test_registry_search_filters_and_sorts_by_quality():
    registry = make_registry()
    matches = registry.search(country="GB", structure="company", deprecated=None)
    assert [entry.code for entry in matches] == ["GB-COH", "GB-OLD"]


def test_registry_best_returns_highest_quality_entry():
    registry = make_registry()
    best = registry.best(country="GB", structure="company", deprecated=None)
    assert best is not None
    assert best.code == "GB-COH"


def test_default_registry_loads_bundled_snapshot():
    registry = Registry.default()
    entry = registry.get("GB-COH")
    assert entry is not None
    assert entry.code == "GB-COH"
