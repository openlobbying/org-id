from __future__ import annotations

import argparse

from org_id.registry import DEFAULT_DOWNLOAD_URL, refresh_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download an org-id.guide registry snapshot."
    )
    parser.add_argument("output", help="Path to write download.json to")
    parser.add_argument("--url", default=DEFAULT_DOWNLOAD_URL, help="Snapshot URL")
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Request timeout in seconds"
    )
    args = parser.parse_args()
    refresh_snapshot(args.output, url=args.url, timeout=args.timeout)


if __name__ == "__main__":
    main()
