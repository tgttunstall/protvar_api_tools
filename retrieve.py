#!/usr/bin/env python3

"""Retrieve a ready ProtVar download file.

Examples:
  python retrieve.py --filename 550e8400-e29b-41d4-a716-446655440000
  python retrieve.py --filename ready_id.txt --output results.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

import requests


API_URL = "https://www.ebi.ac.uk/ProtVar/api/download"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a ProtVar result file by filename or from a file containing it."
    )
    parser.add_argument(
        "--filename",
        required=True,
        help="Download filename, or a path to a text file containing it.",
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


def load_filename(filename_or_path: str) -> str:
    candidate = Path(filename_or_path)
    if candidate.is_file():
        value = candidate.read_text(encoding="utf-8").strip()
    else:
        value = filename_or_path.strip()
    if not value:
        raise SystemExit("Filename is empty.")
    return value


def main() -> int:
    args = parse_args()
    filename = load_filename(args.filename)

    response = requests.get(f"{API_URL}/{filename}", timeout=args.timeout)
    response.raise_for_status()

    output = args.output
    if not output:
        output = filename
        cd = response.headers.get("content-disposition", "")
        if "filename=" in cd:
            output = cd.split("filename=", 1)[1].strip('"\' ')

    Path(output).write_bytes(response.content)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
