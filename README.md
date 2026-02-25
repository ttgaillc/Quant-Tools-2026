<div align="center">

# Quant Tools 2026
### By True Trading Group

<p>
  <img src="https://truetradinggroup.com/wp-content/uploads/2025/11/ai_icon-2.png" alt="TTG AI logo" width="180" />
</p>

Battle-tested quantitative trading scripts for real-world market analysis and technical signal development, with native support for Massive.com (formerly Polygon.io).

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-6366f1)
![Data](https://img.shields.io/badge/Data-Massive.com-f97316)

Built by **TTG AI LLC** • Used in workflows at **True Trading Group**  
<a href="https://truetradinggroup.com" target="_blank" rel="noopener noreferrer"><strong>Visit TrueTradingGroup.com</strong></a>

</div>

---

## Quick Navigation

- [Tool Map by Trader Type](#tool-map-by-trader-type)
- [Trader-Focused Docs](#trader-focused-docs)
- [Environment Variables](#environment-variables)
- [Setup + Launch Scripts](#setup--launch-scripts)
- [Unified Launcher (One Script for Everything)](#unified-launcher-one-script-for-everything)
- [Detailed Script Breakdown](#detailed-script-breakdown)

## Tool Map by Trader Type

| Script | What it does | Scalper | Day Trader | Swing Trader | Investor |
| --- | --- | --- | --- | --- | --- |
| `options/top-itm-contracts.py` | Finds highest-volume ITM options, optionally filtered by expiration | Fast shortlist of active ITM contracts | Confirm near-term directional concentration | Select multi-week ITM candidates | Find liquid ITM contracts for stock-replacement ideas |
| `options/top-otm-contracts.py` | Finds highest-volume OTM options, optionally filtered by expiration | Track short-dated speculative flow | Monitor call/put concentration shifts | Confirm breakout/event setups | Read market sentiment and risk appetite |
| `stocks/support-resistance.py` | Calculates support/resistance from OHLC structure | Map immediate reaction zones | Plan session breakout/retest/fade levels | Mark medium-term pullback/target zones | Identify higher-timeframe accumulation/distribution zones |
| `ttg-cli.py` | Unified interactive launcher with guided prompts and navigation | Run scans quickly | Compare ITM/OTM flow faster | Reuse settings across tickers | Keep analysis workflow consistent |

## Trader-Focused Docs

- [Support/Resistance Trader Guide](docs/support-resistance-trader-guide.md)
- [Top ITM Options Trader Guide](docs/top-itm-options-trader-guide.md)
- [Top OTM Options Trader Guide](docs/top-otm-options-trader-guide.md)

## Environment Variables

These scripts now require Massive credentials and endpoint from environment variables:

- `MASSIVE_API_KEY` - Your Massive API key
- `MASSIVE_API_BASE_URL` - Massive API base URL (example: `https://api.massive.com`)
- `MASSIVE_HTTP_TIMEOUT_SECONDS` - Optional timeout (default: `20`)

PowerShell example:

```powershell
$env:MASSIVE_API_KEY="your_massive_key"
$env:MASSIVE_API_BASE_URL="https://api.massive.com"
```

Template file:

```powershell
Copy-Item ".\.env.example" ".\.env"
```

Then set real values in `.env` and load them into your environment before running scripts.

JSON output is pretty-formatted by default.

## Setup + Launch Scripts

Use these scripts to create a virtual environment, activate it, install dependencies, and launch `ttg-cli.py`.

Windows in Cursor/PowerShell (recommended):

```powershell
.\run-windows.ps1
```

If script execution is blocked:

```powershell
powershell -ExecutionPolicy Bypass -File ".\run-windows.ps1"
```

Windows (Git Bash/WSL):

```bash
bash "./run-windows.sh"
```

macOS/Linux:

```bash
bash "./run-mac.sh"
```

You can pass CLI args through either launcher:

```powershell
.\run-windows.ps1 itm --ticker AAPL --top-n 3
```

```bash
bash "./run-mac.sh" itm --ticker AAPL --top-n 3
```

Optional PowerShell shortcut command (`ttgai-start`) from any terminal:

```powershell
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
Add-Content $PROFILE 'function ttgai-start { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$CliArgs) powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\endpoints\ttg-quant-tools\run-windows.ps1" @CliArgs }'
. $PROFILE
```

Then run:

```powershell
ttgai-start
ttgai-start otm --ticker SPY --top-n 5
```

## Unified Launcher (One Script for Everything)

Use `ttg-cli.py` when you want one entry point for all tools.

Interactive mode (guided app screen):

```powershell
python ".\ttg-cli.py"
```

Interactive mode includes:

- Category menu (`Options` or `Stocks`)
- Tool menu inside each category
- Post-run navigation (`Run this tool again`, `Same settings, different ticker`, `Go back`, `Exit`)
- Options quick switch using same inputs (`Run OTM with same settings` / `Run ITM with same settings`)
- Support/Resistance in-terminal input guide with trading-style presets

Direct command mode (non-interactive):

```powershell
python ".\ttg-cli.py" itm --ticker AAPL --expiration-date 2026-03-20 --top-n 3
python ".\ttg-cli.py" otm --ticker AAPL --top-n 5
python ".\ttg-cli.py" support-resistance --ticker AAPL --multiplier 1 --timeframe day --start-date 2026-01-01 --end-date 2026-02-01
```

You can still run each script individually if preferred.

## Detailed Script Breakdown

### `options/top-itm-contracts.py`

Finds the highest-volume **in-the-money (ITM)** options contracts for an underlying ticker.

What it does:

- Validates and normalizes the input ticker (`AAPL`, `TSLA`, etc.).
- Optionally validates `--expiration-date` in `YYYY-MM-DD` format.
- Calls Massive last trade endpoint (`/v2/last/trade/{ticker}`) to get current underlying price.
- Calls Massive options snapshot endpoint (`/v3/snapshot/options/{ticker}`) to get option chain data.
- If `--expiration-date` is passed, filters contracts to that exact date.
- If `--expiration-date` is not passed, automatically selects the nearest expiration in the returned chain.
- Applies ITM logic:
  - Call ITM if `strike_price < underlying_price`
  - Put ITM if `strike_price > underlying_price`
- Sorts ITM contracts by daily volume descending and returns top N (`--top-n`, default `2`).

CLI arguments:

- `--ticker` (required): underlying ticker
- `--expiration-date` (optional): exact expiration to use
- `--top-n` (optional): number of contracts to return
- `--pretty` (optional): compatibility flag (output is already pretty by default)

Output:

- JSON with:
  - `ticker`
  - `underlying_price`
  - `options[]` entries containing:
    - `ticker`
    - `strike_price`
    - `volume`
    - `type`
    - `expiration_date`
    - `last_trade_price`
    - `implied_volatility`

Example:

```powershell
python ".\options\top-itm-contracts.py" --ticker AAPL --expiration-date 2026-03-20 --top-n 3
```

---

### `options/top-otm-contracts.py`

Finds the highest-volume **out-of-the-money (OTM)** options contracts for an underlying ticker.

What it does:

- Uses the same fetch and expiration-selection flow as the ITM script:
  - Underlying price from `/v2/last/trade/{ticker}`
  - Options snapshot from `/v3/snapshot/options/{ticker}`
  - Optional explicit expiration filter, otherwise nearest expiration
- Applies OTM logic:
  - Call OTM if `strike_price > underlying_price`
  - Put OTM if `strike_price < underlying_price`
- Sorts OTM contracts by daily volume descending and returns top N (`--top-n`).

CLI arguments:

- `--ticker` (required)
- `--expiration-date` (optional)
- `--top-n` (optional, default `2`)
- `--pretty` (optional): compatibility flag (output is already pretty by default)

Output:

- Same JSON shape as ITM script (`ticker`, `underlying_price`, and `options[]` list).

Example:

```powershell
python ".\options\top-otm-contracts.py" --ticker AAPL --top-n 5
```

---

### `stocks/support-resistance.py`

Fetches historical OHLC bars and calculates simple support/resistance levels from local extrema.

What it does:

- Validates date inputs (`--start-date`, `--end-date`) as `YYYY-MM-DD`.
- Calls Massive aggregates endpoint:
  - `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timeframe}/{start_date}/{end_date}`
  - Query params include:
    - `adjusted=true`
    - `limit=50000`
    - `sort=desc`
- Loads bars into a DataFrame.
- Runs `scipy.signal.find_peaks` on close prices:
  - Peaks from `c` for candidate resistance points
  - Peaks from `-c` for candidate support points
- Extracts close values at those points and returns the top 3 most frequent values for:
  - `support_levels`
  - `resistance_levels`
- By default, returns only key levels:
  - `support_levels`
  - `resistance_levels`
- Optionally includes cleaned bar records with `--include-data`:
  - `Date`, `t`, `o`, `h`, `l`, `c`, `v`
  - UTC ISO-style `Date` strings (`YYYY-MM-DDTHH:MM:SSZ`)

CLI arguments:

- `--ticker` (required)
- `--multiplier` (required integer)
- `--timeframe` (required, such as `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`)
- `--start-date` (required `YYYY-MM-DD`)
- `--end-date` (required `YYYY-MM-DD`)
- `--include-data` (optional): include full OHLC bar list in output (large payload)
- `--pretty` (optional): compatibility flag (output is already pretty by default)

Output:

- JSON with:
  - `support_levels`
  - `resistance_levels`
- Plus `data[]` OHLC bars only when `--include-data` is passed

Example:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 1 --timeframe day --start-date 2026-01-01 --end-date 2026-02-01
```

If you want full OHLC bars in the response:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 1 --timeframe day --start-date 2026-01-01 --end-date 2026-02-01 --include-data
```

## Notes

- All scripts return machine-friendly JSON to stdout.
- On errors, scripts print a JSON error object to stderr and exit with status code `1`.
- Set `MASSIVE_HTTP_TIMEOUT_SECONDS` if you want longer/shorter API timeouts.
