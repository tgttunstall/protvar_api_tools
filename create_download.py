#!/usr/bin/env python3

"""Create a ProtVar download job from an uploaded result ID.

Examples:
  python create_download.py --result-id <upload-result-id> --assembly GRCh37 --annotations full
  python create_download.py --result-id resultid.txt --jobid-file download_job.txt --annotations structure
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


API_URL = "https://www.ebi.ac.uk/ProtVar/api/download"


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    if parent and not parent.exists():
        print(f"Creating directory: {parent}")
        parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a ProtVar download job from an upload result ID and save the returned download job ID."
    )
    parser.add_argument(
        "--result-id",
        required=True,
        help="ProtVar upload result ID (from submit.py), or a path to a text file containing it.",
    )
    parser.add_argument(
        "--assembly",
        default="GRCh37",
        choices=["AUTO", "GRCh37", "GRCh38"],
        help="Genome assembly to use for the download request. Default: GRCh37.",
    )
    parser.add_argument(
        "--jobid-file",
        default="download_jobid.txt",
        help="Output text file for the returned download job ID. Default: download_jobid.txt.",
    )
    parser.add_argument(
        "--annotations",
        required=True,
        choices=["structure", "function", "population", "full"],
        help="Annotation mode to request. Use full for all three.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds. Default: 120.",
    )
    return parser.parse_args()


def load_result_id(result_id_or_path: str) -> str:
    candidate = Path(result_id_or_path)
    if candidate.is_file():
        result_id = candidate.read_text(encoding="utf-8").strip()
    else:
        result_id = result_id_or_path.strip()
    if not result_id:
        raise SystemExit("Result ID is empty.")
    return result_id


def extract_download_id(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()

    if isinstance(payload, dict):
        for key in ("resultId", "jobId", "id", "filename", "url", "fname"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for value in payload.values():
            if isinstance(value, str) and value.strip():
                return value.strip()

    raise ValueError(f"Could not extract download job ID from response: {payload!r}")


def main() -> int:
    args = parse_args()
    result_id = load_result_id(args.result_id)

    annotations = {
        "structure": False,
        "function": False,
        "population": False,
    }
    if args.annotations == "full":
        annotations = {key: True for key in annotations}
    else:
        annotations[args.annotations] = True

    payload = {
        "resultId": result_id,
        "assembly": args.assembly,
        "structure": annotations["structure"],
        "function": annotations["function"],
        "population": annotations["population"],
        "full": True,
    }

    response = requests.post(
        API_URL,
        headers={"accept": "application/json"},
        json=payload,
        timeout=args.timeout,
    )
    response.raise_for_status()

    try:
        body = response.json()
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ProtVar returned non-JSON response: {response.text}") from exc

    download_id = extract_download_id(body)
    jobid_path = Path(args.jobid_file)
    ensure_parent_dir(jobid_path)
    jobid_path.write_text(f"{download_id}\n", encoding="utf-8")
    print(download_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
