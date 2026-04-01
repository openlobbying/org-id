from dataclasses import dataclass, field
from typing import Any


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        value = [value]
    items = []
    for item in value:
        text = _clean_text(item)
        if text is not None:
            items.append(text)
    return tuple(items)


@dataclass(frozen=True, slots=True)
class LocalizedText:
    en: str | None = None
    local: str | None = None

    @classmethod
    def from_value(cls, value: Any) -> "LocalizedText":
        if isinstance(value, dict):
            return cls(
                en=_clean_text(value.get("en")),
                local=_clean_text(value.get("local")),
            )
        text = _clean_text(value)
        return cls(en=text)

    @property
    def best(self) -> str | None:
        return self.en or self.local


@dataclass(frozen=True, slots=True)
class ListEntry:
    code: str
    name: LocalizedText
    description: LocalizedText
    url: str | None = None
    coverage: tuple[str, ...] = ()
    subnational_coverage: tuple[str, ...] = ()
    structure: tuple[str, ...] = ()
    sector: tuple[str, ...] = ()
    confirmed: bool = False
    deprecated: bool = False
    list_type: str | None = None
    quality: int = 0
    former_prefixes: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ListEntry":
        return cls(
            code=str(data["code"]).upper(),
            name=LocalizedText.from_value(data.get("name")),
            description=LocalizedText.from_value(data.get("description")),
            url=_clean_text(data.get("url")),
            coverage=tuple(
                country.upper() for country in _clean_list(data.get("coverage"))
            ),
            subnational_coverage=tuple(
                country.upper()
                for country in _clean_list(data.get("subnationalCoverage"))
            ),
            structure=_clean_list(data.get("structure")),
            sector=_clean_list(data.get("sector")),
            confirmed=bool(data.get("confirmed", False)),
            deprecated=bool(data.get("deprecated", False)),
            list_type=_clean_text(data.get("listType")),
            quality=int(data.get("quality") or 0),
            former_prefixes=tuple(
                prefix.upper() for prefix in _clean_list(data.get("formerPrefixes"))
            ),
            raw=dict(data),
        )

    def covers_country(self, country: str) -> bool:
        country = country.strip().upper()
        return country in self.coverage or any(
            subnational == country or subnational.startswith(f"{country}-")
            for subnational in self.subnational_coverage
        )

    def has_structure(self, structure: str) -> bool:
        wanted = structure.strip().lower()
        return any(item.lower() == wanted for item in self.structure)


@dataclass(frozen=True, slots=True)
class ParsedOrgId:
    scheme: str
    identifier: str

    def __str__(self) -> str:
        return f"{self.scheme}-{self.identifier}"


@dataclass(frozen=True, slots=True)
class IdResult:
    identifier: str
    scheme: str | None
    registration_number: str | None
    entry: ListEntry | None
    listed: bool
    deprecated: bool
    fallback: bool
    normalized: bool
