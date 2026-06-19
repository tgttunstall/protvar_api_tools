#!/usr/bin/env python3

"""Retrieve a ready ProtVar download file.

Examples:
  python retrieve.py --download-id 38e6aedd-bb36-4a5d-a944-ae827ccb4f3b.csv.zip
  python retrieve.py --download-id download_id.txt --output results.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

import requests


API_URL = "https://www.ebi.ac.uk/ProtVar/api/download"


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    if parent and not parent.exists():
        print(f"Creating directory {parent}")
        parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a ProtVar result file by download ID or from a file containing it."
    )
    parser.add_argument(
        "--download-id",
        required=True,
        help="ProtVar download ID/filename, or a path to a text file containing it.",
    )
    parser.add_argument(
        "--output",
        help="Local output filename. Defaults to the remote filename or response name.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds. Default: 120.",
    )
    return parser.parse_args()


def load_download_id(download_id_or_path: str) -> str:
    candidate = Path(download_id_or_path)
    if candidate.is_file():
        value = candidate.read_text(encoding="utf-8").strip()
    else:
        value = download_id_or_path.strip()
    if not value:
        raise SystemExit("Download ID is empty.")
    return value


def main() -> int:
    args = parse_args()
    download_id = load_download_id(args.download_id)

    response = requests.get(f"{API_URL}/{download_id}", timeout=args.timeout)
    response.raise_for_status()

    output = args.output
    if not output:
        output = download_id
        cd = response.headers.get("content-disposition", "")
        if "filename=" in cd:
            output = cd.split("filename=", 1)[1].strip('"\' ')

    output_path = Path(output)
    ensure_parent_dir(output_path)
    output_path.write_bytes(response.content)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
