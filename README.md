# ProtVar API Tools

Small CLI tools for working with the ProtVar API.

## Setup

```bash
python3 -m venv ~/my_envs/pv_api_env/
source ~/my_envs/pv_api_env/bin/activate
pip install -r requirements.txt
```

## Overview

- `submit.py` uploads a variant file and writes the ProtVar upload `resultId`.
- `create_download.py` creates a download job from that `resultId`.
- `poll.py` checks the download job status.
- `retrieve.py` downloads one or more finished result files and keeps the ProtVar filenames.

## Input data

Sample input is in `data/test.txt`.

## Output locations

- `submit.py` writes the upload `resultId` to `--jobid-file`.
- `create_download.py` writes the download job ID to `--jobid-file`.
- `retrieve.py` writes downloaded files to `--outdir` while preserving the ProtVar filenames.
- Parent directories for output paths are created automatically.

## ID flow

1. `submit.py` returns the upload `resultId`.
2. Pass that same `resultId` to `create_download.py`.
3. `create_download.py` returns a separate download job ID.
4. Pass that download job ID to `poll.py`.
5. When ready, use `retrieve.py` with the remote download ID/filename returned by ProtVar.

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

Example*:

```bash
python create_download.py --result-id results/jobid.txt --assembly AUTO --annotations full --jobid-file results/download_jobid.txt
```

This writes the download job ID to `results/download_jobid.txt`.
That file is local state only, not the remote download filename.

**Note: `--assembly AUTO` works correctly with `data/test.txt`, but not reliably with `csvs_all_variants_grch37_NOINDELS_100000`; for that larger GRCh37 list, the ProtVar download step currently needs a workaround.**

## `poll.py`

Check the status of a ProtVar download job.

Options:
- `--job-id` required, either the download job ID itself or a file containing it.
- `--timeout` optional, request timeout in seconds.

Example:

```bash
python poll.py --job-id results/download_jobid.txt
```

`poll.py` accepts either the job ID itself or a file containing it.

Status meanings:
- `queued`
- `processing`
- `ready`
- `failed`
- `expired`

## `retrieve.py`

Download one or more ready result files.

Downloads are streamed to disk in chunks rather than loaded fully into memory.
This is safer for large ProtVar zip files, such as full-annotation downloads or
downloads created from large variant lists.

Options:
- `--download-id` required, one or more download IDs, or one file containing one or more download IDs, one per line.
- `--outdir` optional, local output directory. The ProtVar filename is preserved.
- `--timeout` optional, request timeout in seconds.

Single-ID example:

```bash
python retrieve.py --download-id results/download_jobid.txt --outdir results/
```

Multiple IDs on the command line:

```bash
python retrieve.py --download-id id1 id2 id3 --outdir results/
```

Multiple IDs from a file:

```text
id1
id2
id3
```

```bash
python retrieve.py --download-id results/download_jobids.txt --outdir results/
```

Use either literal IDs on the command line or one ID file. Do not mix literal IDs and an ID file in the same command.

`results/download_jobid.txt` contains the same download job ID you check with `poll.py`.
Downloaded files are saved as `results/<ProtVar filename>`.

## Example workflow

```bash
python submit.py --input data/test.txt --assembly GRCh37 --jobid-file results/jobid.txt
python create_download.py --result-id results/jobid.txt --assembly AUTO --annotations full --jobid-file results/download_jobid.txt
python poll.py --job-id results/download_jobid.txt
python retrieve.py --download-id results/download_jobid.txt --outdir results/
```

* `create_download.py ... --assembly AUTO` See Note above.

## Notes

- `results/` is a suggested output folder in the examples.
- The scripts can write wherever you point `--jobid-file` and `--outdir`.
- `submit.py` and `create_download.py` write IDs to text files so later scripts can reuse them.
