# AGENTS.md

Guidance for coding agents working in this repository.

## Project Summary

`ttg-quant-tools` contains Python scripts for market analysis using Massive API data:

- Top ITM options by volume: `options/top-itm-contracts.py`
- Top OTM options by volume: `options/top-otm-contracts.py`
- Support/resistance from OHLC bars: `stocks/support-resistance.py`
- Unified entry point: `ttg-cli.py`

## Runtime Requirements

- Python 3.10+
- Dependencies from `requirements.txt`:
  - `requests`
  - `pandas`
  - `scipy`

## Environment Variables

Required:

- `MASSIVE_API_KEY`
- `MASSIVE_API_BASE_URL`

Optional:

- `MASSIVE_HTTP_TIMEOUT_SECONDS` (default `20`)

Use `/.env.example` as the template and keep real secrets in `/.env`.

## Local Run Commands

Windows (Cursor PowerShell):

- `.\run-windows.ps1`
- `.\run-windows.ps1 itm --ticker AAPL --top-n 3 --pretty`

macOS/Linux:

- `bash "./run-mac.sh"`
- `bash "./run-mac.sh" itm --ticker AAPL --top-n 3 --pretty`

Git Bash on Windows:

- `bash "./run-windows.sh"`

## Agent Guardrails

- Do not hardcode API credentials or secrets in code.
- Do not commit real `.env` values.
- Preserve existing CLI flags and JSON response shapes unless explicitly requested.
- Keep error behavior consistent: JSON error to stderr and non-zero exit.
- If dependencies change, update `requirements.txt` and relevant README sections.
- If behavior or usage changes, update `README.md` examples.

## Quick Validation

Before finishing changes, run lightweight checks that do not require network access:

- `python ".\ttg-cli.py" itm --help`
- `python ".\ttg-cli.py" otm --help`
- `python ".\ttg-cli.py" support-resistance --help`

Use functional/API calls only when environment variables are configured.
