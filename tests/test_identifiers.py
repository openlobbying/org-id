import hashlib
import logging

import pytest

from org_id import (
    Registry,
    build_org_id,
    is_org_id,
    make_hashed_id,
    make_id,
    make_org_id,
    parse_org_id,
)


@pytest.fixture
def registry() -> Registry:
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
            ]
        }
    )


def test_parse_org_id():
    parsed = parse_org_id("GB-COH-09506232")
    assert parsed is not None
    assert parsed.scheme == "GB-COH"
    assert parsed.identifier == "09506232"
    assert is_org_id("GB-COH-09506232")
    assert not is_org_id("not-an-id")


def test_make_org_id_normalizes_gb_coh_and_logs(
    caplog: pytest.LogCaptureFixture, registry: Registry
):
    caplog.set_level(logging.WARNING)
    identifier = make_org_id("12345", register="GB-COH", registry=registry)
    assert identifier == "GB-COH-00012345"
    assert "Normalized GB-COH registration number" in caplog.text


def test_make_org_id_returns_none_for_invalid_gb_coh(registry: Registry):
    assert make_org_id("abc", register="GB-COH", registry=registry) is None


def test_build_org_id_warns_for_deprecated_register(registry: Registry):
    with pytest.warns(UserWarning, match="deprecated"):
        result = build_org_id("12345678", register="GB-OLD", registry=registry)
    assert result is not None
    assert result.identifier == "GB-OLD-12345678"
    assert result.deprecated is True


def test_build_org_id_warns_for_unknown_register(registry: Registry):
    with pytest.warns(UserWarning, match="not present"):
        result = build_org_id("ABC-42", register="GB-PARL", registry=registry)
    assert result is not None
    assert result.identifier == "GB-PARL-ABC-42"
    assert result.fallback is True


def test_make_id_keeps_hashed_fallback_behavior():
    identifier = make_id("openlobbying", "Samizdata Ltd")
    digest = hashlib.sha1("openlobbying".encode("utf-8"))
    digest.update("Samizdata Ltd".encode("utf-8"))
    assert identifier == f"openlobbying-{digest.hexdigest()}"


def test_make_id_prefers_structured_identifier(registry: Registry):
    identifier = make_id(
        "openlobbying",
        "Samizdata Ltd",
        reg_nr="16957965",
        register="GB-COH",
        registry=registry,
    )
    assert identifier == "GB-COH-16957965"


def test_make_id_requires_register_when_reg_nr_is_given():
    with pytest.raises(ValueError, match="requires a 'register'"):
        make_id("openlobbying", "Samizdata Ltd", reg_nr="16957965")
