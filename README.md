# org-id

`org-id` is a small Python package for working with [`org-id.guide`](https://org-id.guide) organisation identifiers.

It supports:

- loading a bundled snapshot of the `org-id.guide` registry
- looking up and searching list metadata
- parsing and validating identifier strings
- creating normalized identifiers for known registers
- falling back to hashed IDs when no structured identifier is available

## Install

```bash
uv pip install org-id
```

## Usage

```python
from org_id import Registry, make_id, make_org_id, parse_org_id

registry = Registry.default()

entry = registry.get("GB-COH")
assert entry is not None
assert entry.code == "GB-COH"

identifier = make_org_id("16957965", register="GB-COH", registry=registry)
assert identifier == "GB-COH-16957965"

fallback = make_id("openlobbying", "Samizdata Ltd", reg_nr=None)

parsed = parse_org_id("GB-COH-16957965")
assert parsed.scheme == "GB-COH"
assert parsed.identifier == "16957965"
```

If a register is missing from the bundled `org-id.guide` list, creation still proceeds and emits a warning. Deprecated registers also continue with a warning.

## Search

```python
registry = Registry.default()

gb_company_lists = registry.search(country="GB", structure="company")
best_gb_company_list = registry.best(country="GB", structure="company")
```

`search()` sorts higher-quality entries first.

## Refreshing the bundled snapshot

Fetch a fresh copy of `download.json` and write it to a file:

```bash
uv run org-id-refresh ./download.json
```

To update the bundled package snapshot in this repo:

```bash
uv run org-id-refresh ./src/org_id/data/download.json
```

## Development

```bash
uv run pytest
```

## Publishing

This repo includes a GitHub Actions workflow at `.github/workflows/publish.yml`.

It will:

- run the test suite
- build the package with `uv build`
- publish to PyPI when you push a tag like `v0.1.0`