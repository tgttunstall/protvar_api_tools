# ProtVar Submit/Retrieve Variants

Small CLI helpers for the ProtVar API.

## Files

- `submit.py` uploads a variant file and writes the upload `resultId`.
- `create_download.py` creates a download job from that `resultId`.
- `poll.py` checks the download job status.
- `retrieve.py` downloads the ready file.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Example Input

`data/test.txt` contains a small sample variant list.

## Usage

Submit:

```bash
python submit.py --input data/test.txt --assembly GRCh37
```

Create download job:

```bash
python create_download.py --result-id jobid.txt --assembly GRCh37 --annotations full
```

Poll:

```bash
python poll.py --job-id download_jobid.txt
```

Retrieve:

```bash
python retrieve.py --filename <download-filename> --output results.json
```

## ID Flow

- `submit.py` returns an upload `resultId`.
- `create_download.py` uses that `resultId` and returns a download job ID.
- `poll.py` checks the download job ID.
- `retrieve.py` downloads the finished file.

## Notes

- Default assembly is `GRCh37`.
- `--annotations` accepts `structure`, `function`, `population`, or `full`.
- `full` requests all three annotation groups.
