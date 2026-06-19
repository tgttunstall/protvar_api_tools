# ProtVar API Tools

Small CLI tools for working with the ProtVar API.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Overview

- `submit.py` uploads a variant file and writes the ProtVar upload `resultId`.
- `create_download.py` creates a download job from that `resultId`.
- `poll.py` checks the download job status.
- `retrieve.py` downloads the finished result file.

## Input data

Sample input is in `data/test.txt`.

## Output locations

- `submit.py` writes the upload `resultId` to `--jobid-file`.
- `create_download.py` writes the download job ID to `--jobid-file`.
- `retrieve.py` writes the downloaded file to `--output`.
- Parent directories for output paths are created automatically.

## ID flow

1. `submit.py` returns the upload `resultId`.
2. Pass that same `resultId` to `create_download.py`.
3. `create_download.py` returns a separate download job ID.
4. Pass that download job ID to `poll.py`.
5. When ready, use `retrieve.py` to fetch the file.

## `submit.py`

Upload a plain-text variant file, one variant per line.

Options:
- `--input` required, path to the variant file.
- `--assembly` optional, one of `AUTO`, `GRCh37`, `GRCh38`. Default: `GRCh37`.
- `--jobid-file` optional, output file for the returned upload `resultId`.
- `--timeout` optional, request timeout in seconds.

Example:

```bash
python submit.py --input data/test.txt --assembly GRCh37 --jobid-file results/jobid.txt
```

This writes the upload `resultId` to `results/jobid.txt`.

## `create_download.py`

Create a ProtVar download job from the upload `resultId`.

Options:
- `--result-id` required, the upload `resultId` from `submit.py`, or a file containing it.
- `--assembly` optional, one of `AUTO`, `GRCh37`, `GRCh38`. Default: `GRCh37`.
- `--annotations` required, one of `structure`, `function`, `population`, or `full`.
- `--jobid-file` optional, output file for the returned download job ID.
- `--timeout` optional, request timeout in seconds.

Example:

```bash
python create_download.py --result-id results/jobid.txt --assembly GRCh37 --annotations full --jobid-file results/download_jobid.txt
```

This writes the download job ID to `results/download_jobid.txt`.

## `poll.py`

Check the status of a ProtVar download job.

Options:
- `--job-id` required, either the download job ID itself or a file containing it.
- `--timeout` optional, request timeout in seconds.

Example:

```bash
python poll.py --job-id results/download_jobid.txt
```

Status meanings:
- `queued`
- `processing`
- `ready`
- `failed`
- `expired`

## `retrieve.py`

Download a ready result file.

Options:
- `--filename` required, the download filename/id or a file containing it.
- `--output` optional, local output file path.
- `--timeout` optional, request timeout in seconds.

Example:

```bash
python retrieve.py --filename <download-filename> --output results/results.json
```

## Example workflow

```bash
python submit.py --input data/test.txt --assembly GRCh37 --jobid-file results/jobid.txt
python create_download.py --result-id results/jobid.txt --assembly GRCh37 --annotations full --jobid-file results/download_jobid.txt
python poll.py --job-id results/download_jobid.txt
python retrieve.py --filename <download-filename> --output results/results.json
```

## Notes

- `results/` is a suggested output folder in the examples.
- The scripts can write wherever you point `--jobid-file` and `--output`.
- `submit.py` and `create_download.py` write IDs to text files so later scripts can reuse them.
