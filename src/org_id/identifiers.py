from __future__ import annotations

import hashlib
import logging
import re
import warnings
from typing import Any

from org_id.model import IdResult, ParsedOrgId
from org_id.registry import Registry
from org_id.validators import coerce_registration_number, normalize_registration_number

log = logging.getLogger(__name__)

ORG_ID_PATTERN = re.compile(r"^(?P<scheme>[A-Z]{2}-[A-Z0-9_]+)-(?P<identifier>\S+)$")


def make_hashed_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha1(prefix.encode("utf-8"))
    for part in (part for part in parts if part is not None):
        if isinstance(part, (list, set, tuple)):
            for item in part:
                digest.update(str(item).encode("utf-8"))
        else:
            digest.update(str(part).encode("utf-8"))
    return f"{prefix}-{digest.hexdigest()}"


def parse_org_id(identifier: str) -> ParsedOrgId | None:
    text = identifier.strip()
    match = ORG_ID_PATTERN.match(text)
    if match is None:
        return None
    return ParsedOrgId(
        scheme=match.group("scheme"),
        identifier=match.group("identifier"),
    )


def is_org_id(identifier: str) -> bool:
    return parse_org_id(identifier) is not None


def build_org_id(
    reg_nr: Any,
    register: str = "GB-COH",
    *,
    registry: Registry | None = None,
    warn: bool = True,
) -> IdResult | None:
    register = register.strip().upper()
    if registry is None:
        registry = Registry.default()
    original = coerce_registration_number(reg_nr)
    if original is None:
        return None

    entry = registry.get(register)
    listed = entry is not None
    deprecated = bool(entry.deprecated) if entry is not None else False

    if not listed and warn:
        warnings.warn(
            f"Register {register} is not present in the org-id registry; creating a fallback identifier.",
            stacklevel=2,
        )
    if deprecated and warn:
        warnings.warn(
            f"Register {register} is deprecated in the org-id registry.",
            stacklevel=2,
        )

    normalized = normalize_registration_number(register, original)
    if normalized is None:
        return None
    if normalized != original:
        log.warning(
            "Normalized %s registration number from %r to %r",
            register,
            original,
            normalized,
        )

    identifier = f"{register}-{normalized}"
    return IdResult(
        identifier=identifier,
        scheme=register,
        registration_number=normalized,
        entry=entry,
        listed=listed,
        deprecated=deprecated,
        fallback=not listed,
        normalized=normalized != original,
    )


def make_org_id(
    reg_nr: Any,
    register: str = "GB-COH",
    *,
    registry: Registry | None = None,
    warn: bool = True,
) -> str | None:
    result = build_org_id(reg_nr, register=register, registry=registry, warn=warn)
    if result is None:
        return None
    return result.identifier


def make_id(
    prefix: str,
    *parts: Any,
    reg_nr: Any = None,
    register: str | None = None,
    registry: Registry | None = None,
    warn: bool = True,
) -> str:
    if reg_nr:
        if not register:
            raise ValueError("Mapping an org-id requires a 'register' (e.g. 'GB-COH')")
        org_id = make_org_id(reg_nr, register=register, registry=registry, warn=warn)
        if org_id is not None:
            return org_id
    return make_hashed_id(prefix, *parts)
