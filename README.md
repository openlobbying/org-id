# org-id

`org-id` is a small Python package for working with `org-id.guide` organization identifiers.

It supports:

- loading a bundled snapshot of the `org-id.guide` registry
- looking up and searching list metadata
- parsing and validating identifier strings
- creating normalized identifiers for known registers
- falling back to hashed IDs when no structured identifier is available

## Install

```bash
uv sync
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

### GitHub and PyPI setup

1. Create the package on PyPI by doing one manual upload first, or reserve the project name if needed.
2. In PyPI, open the `org-id` project settings.
3. Add a trusted publisher for this GitHub repository.
4. Set the owner to your GitHub account or organization.
5. Set the repository name to the repo that will host `org-id`.
6. Set the workflow name to `publish.yml`.
7. Set the environment name blank unless you later decide to gate publishing with a GitHub environment.
8. Push this package to its own GitHub repository.
9. Create a version tag that matches `pyproject.toml`, for example `v0.1.0`.
10. Push the tag with `git push origin v0.1.0`.

### Recommended release flow

1. Update `version` in `pyproject.toml`.
2. Commit the change.
3. Create and push a matching git tag, such as `v0.1.1`.
4. Watch the `Publish` workflow in GitHub Actions.
5. Confirm the new release on PyPI.

### Notes

- The workflow uses PyPI trusted publishing via GitHub OIDC, so no `PYPI_API_TOKEN` secret is required.
- If the package name is not yet available on PyPI, verify that `org-id` can be claimed before wiring up automated publishing.
- The publish step only runs after tests pass.
