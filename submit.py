#!/usr/bin/env python3

"""Submit a ProtVar variant file and write the returned job ID to disk.

Example:
  python submit.py --input test.txt --assembly GRCh37
  python submit.py --input test.txt --assembly GRCh37 --jobid-file myjob.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


API_URL = "https://www.ebi.ac.uk/ProtVar/api/input/file"


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    if parent and not parent.exists():
        print(f"Creating directory {parent}")
        parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Upload a plain-text variant file to ProtVar and save the returned job ID."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a text file with one variant per line.",
    )
    parser.add_argument(
        "--assembly",
        default="GRCh37",
        choices=["AUTO", "GRCh37", "GRCh38"],
        help="Genome assembly to submit with the upload. Default: GRCh37.",
    )
    parser.add_argument(
        "--jobid-file",
        default="jobid.txt",
        help="Output text file for the returned job ID. Default: jobid.txt.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds. Default: 120.",
    )
    return parser.parse_args()


def extract_job_id(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()

    if isinstance(payload, dict):
        for key in ("resultId", "jobId", "id", "filename"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for value in payload.values():
            if isinstance(value, str) and value.strip() and len(value.strip()) >= 8:
                return value.strip()

    raise ValueError(f"Could not extract job ID from response: {payload!r}")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    with input_path.open("rb") as fh:
        response = requests.post(
            API_URL,
            params={"assembly": args.assembly},
            headers={"accept": "application/json"},
            files={"file": (input_path.name, fh, "text/plain")},
            timeout=args.timeout,
        )

    response.raise_for_status()

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ProtVar returned non-JSON response: {response.text}") from exc

    job_id = extract_job_id(payload)
    jobid_path = Path(args.jobid_file)
    ensure_parent_dir(jobid_path)
    jobid_path.write_text(f"{job_id}\n", encoding="utf-8")
    print(job_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
