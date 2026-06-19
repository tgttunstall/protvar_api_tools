#!/usr/bin/env python3

"""Check the status of a ProtVar download job.

Examples:
  python poll.py --job-id 84bf84a7f17a44ea5b52077091a06dc6
  python poll.py --job-id jobid.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


STATUS_URL = "https://www.ebi.ac.uk/ProtVar/api/download/status"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poll ProtVar for the status of a download job."
    )
    parser.add_argument(
        "--job-id",
        required=True,
        help="ProtVar job/result ID, or a path to a text file containing it.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds. Default: 120.",
    )
    return parser.parse_args()


def load_job_id(job_id_or_path: str) -> str:
    candidate = Path(job_id_or_path)
    if candidate.is_file():
        job_id = candidate.read_text(encoding="utf-8").strip()
    else:
        job_id = job_id_or_path.strip()
    if not job_id:
        raise SystemExit("Job ID is empty.")
    return job_id


def main() -> int:
    args = parse_args()
    job_id = load_job_id(args.job_id)

    response = requests.post(
        STATUS_URL,
        headers={"accept": "application/json"},
        json=[job_id],
        timeout=args.timeout,
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ProtVar returned non-JSON response: {response.text}") from exc

    status = payload.get(job_id)
    if status is None:
        raise SystemExit(f"ProtVar did not return status for job ID {job_id}: {payload!r}")

    state = status.get("state", "unknown")
    message = status.get("message")

    print(f"job_id: {job_id}")
    print(f"state: {state}")
    if message:
        print(f"message: {message}")
    if "size" in status and status["size"] is not None:
        print(f"size: {status['size']}")

    if state in {"failed", "expired"}:
        return 2
    if state != "ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
