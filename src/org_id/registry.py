from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable
from urllib.request import urlopen

from org_id.model import ListEntry

DEFAULT_DOWNLOAD_URL = "https://org-id.guide/download.json"


@dataclass(frozen=True, slots=True)
class RegistrySource:
    kind: str
    location: str


class Registry:
    def __init__(
        self, entries: Iterable[ListEntry], source: RegistrySource | None = None
    ):
        normalized_entries = tuple(entries)
        self._entries = normalized_entries
        self._by_code = {entry.code: entry for entry in normalized_entries}
        self.source = source

    @classmethod
    def default(cls) -> "Registry":
        resource = files("org_id").joinpath("data/download.json")
        with resource.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data, source=RegistrySource("bundled", str(resource)))

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        source: RegistrySource | None = None,
    ) -> "Registry":
        entries = [ListEntry.from_dict(item) for item in data.get("lists", [])]
        entries.sort(key=lambda entry: (-entry.quality, entry.code))
        return cls(entries, source=source)

    @classmethod
    def from_file(cls, path: str | Path) -> "Registry":
        path = Path(path)
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data, source=RegistrySource("file", str(path)))

    @classmethod
    def from_url(
        cls,
        url: str = DEFAULT_DOWNLOAD_URL,
        *,
        timeout: float = 30.0,
    ) -> "Registry":
        with urlopen(url, timeout=timeout) as response:
            data = json.load(response)
        return cls.from_dict(data, source=RegistrySource("url", url))

    def __iter__(self):
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def get(self, code: str) -> ListEntry | None:
        return self._by_code.get(code.strip().upper())

    def search(
        self,
        *,
        country: str | None = None,
        structure: str | None = None,
        quality: int | None = None,
        min_quality: int | None = None,
        deprecated: bool | None = False,
    ) -> list[ListEntry]:
        results: list[ListEntry] = []
        for entry in self._entries:
            if deprecated is not None and entry.deprecated != deprecated:
                continue
            if country is not None and not entry.covers_country(country):
                continue
            if structure is not None and not entry.has_structure(structure):
                continue
            if quality is not None and entry.quality != quality:
                continue
            if min_quality is not None and entry.quality < min_quality:
                continue
            results.append(entry)
        return results

    def best(
        self,
        *,
        country: str | None = None,
        structure: str | None = None,
        min_quality: int | None = None,
        deprecated: bool | None = False,
    ) -> ListEntry | None:
        matches = self.search(
            country=country,
            structure=structure,
            min_quality=min_quality,
            deprecated=deprecated,
        )
        if not matches:
            return None
        return matches[0]


def refresh_snapshot(
    destination: str | Path,
    *,
    url: str = DEFAULT_DOWNLOAD_URL,
    timeout: float = 30.0,
) -> Path:
    destination = Path(destination)
    with urlopen(url, timeout=timeout) as response:
        data = json.load(response)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return destination
