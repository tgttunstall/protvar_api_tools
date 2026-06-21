#!/usr/bin/env python3

"""Retrieve one or more ready ProtVar download files.

Examples:
  python retrieve.py --download-id 38e6aedd-bb36-4a5d-a944-ae827ccb4f3b.csv.zip
  python retrieve.py --download-id id1 id2 id3 --outdir results/
  python retrieve.py --download-id download_id.txt --outdir results/

The --download-id argument accepts either one or more literal download IDs on the
command line, or one file containing one download ID per non-empty line.
"""

from __future__ import annotations

import argparse
from email.message import Message
from pathlib import Path
import sys

import requests


API_URL = "https://www.ebi.ac.uk/ProtVar/api/download"


def ensure_parent_dir(path: Path) -> None:
    parent = path.parent
    if parent and not parent.exists():
        print(f"Creating directory: {parent}")
        parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download one or more ready ProtVar result files. Streams files to "
            "disk in chunks."
        ),
        epilog=(
            "Examples:\n"
            "  python retrieve.py --download-id id1 --outdir results/\n"
            "  python retrieve.py --download-id id1 id2 id3 --outdir results/\n"
            "  python retrieve.py --download-id results/download_jobids.txt --outdir results/"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--download-id",
        required=True,
        nargs="+",
        help=(
            "One or more download IDs, or one file containing one or more "
            "download IDs, one per line."
        ),
    )
    parser.add_argument(
        "--outdir",
        help="Local output directory. The ProtVar filename is preserved.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds. Default: 120.",
    )
    return parser.parse_args()


def load_download_ids(download_ids_or_path: list[str]) -> list[str]:
    if len(download_ids_or_path) == 1:
        candidate = Path(download_ids_or_path[0])
        if candidate.is_file():
            values = [
                line.strip()
                for line in candidate.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        else:
            values = [download_ids_or_path[0].strip()]
    else:
        file_args = [value for value in download_ids_or_path if Path(value).is_file()]
        if file_args:
            raise SystemExit(
                "Use either literal download IDs or one ID file, not both. "
                f"File-like argument(s): {', '.join(file_args)}"
            )
        values = [value.strip() for value in download_ids_or_path if value.strip()]

    if not values:
        raise SystemExit("Download ID is empty.")
    return values


def filename_from_response(response: requests.Response, fallback: str) -> str:
    remote_name = fallback
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        message = Message()
        message["content-disposition"] = content_disposition
        remote_name = message.get_filename() or fallback
    return Path(remote_name).name


def retrieve_download(download_id: str, output_dir: Path, timeout: int) -> Path:
    """Download one ProtVar result file to disk using response streaming.

    ProtVar result archives can become large for big variant lists or full
    annotations. Using stream=True and writing iter_content() chunks avoids
    loading the complete zip into memory before writing it to disk.
    """
    with requests.get(f"{API_URL}/{download_id}", stream=True, timeout=timeout) as response:
        response.raise_for_status()
        output_path = output_dir / filename_from_response(response, download_id)
        ensure_parent_dir(output_path)
        with output_path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
    return output_path


def main() -> int:
    args = parse_args()
    download_ids = load_download_ids(args.download_id)
    output_dir = Path(args.outdir) if args.outdir else Path(".")

    failed = False
    for download_id in download_ids:
        try:
            output_path = retrieve_download(download_id, output_dir, args.timeout)
        except requests.RequestException as exc:
            failed = True
            print(f"Failed {download_id}: {exc}", file=sys.stderr)
            continue
        print(f"Saved to: {output_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
