import re
from typing import Any


GB_COH_RE = re.compile(
    r"^(((AC|CE|CS|FC|FE|GE|GS|IC|LP|NC|NF|NI|NL|NO|NP|OC|OE|PC|R0|RC|SA|SC|SE|SF|SG|SI|SL|SO|SR|SZ|ZC|\d{2})\d{6})|((IP|SP|RS)[A-Z\d]{6})|(SL\d{5}[\dA])|(RS007853Z))$"
)

EMPTY_VALUES = {"", "NAN", "NONE", "N/A"}


def coerce_registration_number(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, set, tuple)):
        values = list(value)
        if not values:
            return None
        value = values[0]
    text = str(value).strip().upper()
    if text in EMPTY_VALUES:
        return None
    return text


def is_gb_coh(company_number: str) -> bool:
    return bool(company_number and GB_COH_RE.match(company_number))


def normalize_gb_coh(company_number: Any) -> str | None:
    normalized = coerce_registration_number(company_number)
    if normalized is None:
        return None
    if normalized.isdigit() and len(normalized) < 8:
        normalized = normalized.zfill(8)
    if is_gb_coh(normalized):
        return normalized
    return None


MD_IDNO_RE = re.compile(r"^\d{13}$")
# The 13th digit of a Moldovan IDNO is a check digit: the sum of the first 12
# digits weighted 7, 3, 1, 7, 3, 1, ... modulo 10.
MD_IDNO_WEIGHTS = (7, 3, 1) * 4


def is_md_idno(idno: str) -> bool:
    if not MD_IDNO_RE.match(idno):
        return False
    total = sum(int(digit) * weight for digit, weight in zip(idno, MD_IDNO_WEIGHTS))
    return total % 10 == int(idno[12])


def normalize_md_idno(idno: Any) -> str | None:
    normalized = coerce_registration_number(idno)
    if normalized is None or not is_md_idno(normalized):
        return None
    return normalized


VALIDATORS = {
    "GB-COH": normalize_gb_coh,
    "MD-IDNO": normalize_md_idno,
}


def normalize_registration_number(register: str, value: Any) -> str | None:
    register = register.strip().upper()
    normalized = coerce_registration_number(value)
    if normalized is None:
        return None
    validator = VALIDATORS.get(register)
    if validator is None:
        return normalized
    return validator(normalized)
