# Top ITM Options Tool: Trader Guide

This guide explains what `options/top-itm-contracts.py` does, how to use it from a trader perspective, and where it is strongest or weakest in live decision-making.

## What This Script Is Built For

The script finds high-volume **in-the-money (ITM)** options for a ticker and returns the top N contracts by reported daily volume.

In practice, this helps you identify where options flow is concentrated in contracts with higher intrinsic value and generally higher delta than OTM alternatives.

It is best used as a **flow/context scanner**, not a standalone execution signal.

## Inputs and Data Source

### CLI inputs

- `--ticker` (required)
- `--expiration-date` (optional, `YYYY-MM-DD`)
- `--top-n` (optional, default `2`)
- `--pretty` (optional compatibility flag; output is already pretty by default)

### Environment

- `MASSIVE_API_KEY` (required)
- `MASSIVE_API_BASE_URL` (required)
- `MASSIVE_HTTP_TIMEOUT_SECONDS` (optional, default `20`)

### API calls

1. Last trade for underlying:
   - `/v2/last/trade/{ticker}`
2. Options snapshot:
   - `/v3/snapshot/options/{ticker}`
   - with `limit=100`

## Core Logic

The script flow is:

1. Normalize ticker to uppercase.
2. Validate optional expiration date.
3. Fetch current underlying price from last trade.
4. Fetch option snapshot list.
5. If expiration is provided, filter to that date.
6. If not provided, automatically choose the nearest expiration date from returned data.
7. Classify ITM:
   - Call ITM if `strike < underlying_price`
   - Put ITM if `strike > underlying_price`
8. Sort remaining contracts by daily volume descending.
9. Return top N.

## ITM Interpretation for Traders

ITM contracts usually imply:

- higher intrinsic value
- higher directional sensitivity (higher delta on average)
- generally lower gamma explosiveness than far OTM contracts

What high ITM volume can mean:

- larger directional participation by participants seeking stock-like exposure
- hedging or rolling activity around key levels
- increased attention near specific strikes/expirations

What it does **not** guarantee:

- that flow is opening (vs closing)
- bullish or bearish intent without side context
- sustainable follow-through in underlying

## Trader Use Cases

### 1) Directional conviction scan

Use top ITM list to identify strikes where participants are willing to pay for intrinsic exposure, then confirm with:

- price trend
- volume regime in underlying
- nearby event risk

### 2) Strike selection reference

If you already have bullish or bearish bias, top ITM volume can be used as a liquidity-aware shortlist before execution.

### 3) Expiration selection sanity check

Running with explicit `--expiration-date` helps you compare activity by tenor and avoid accidental focus on very near-dated contracts.

### 4) Regime monitoring

Repeated scans over time can reveal migration of concentration between strikes and expirations (useful for tactical bias shifts).

## How Different Trader Types Use This Tool

Key input meanings:

- `--ticker`: underlying symbol to scan
- `--expiration-date`: which expiration to analyze (omit to auto-use nearest expiry)
- `--top-n`: how many contracts to return

### 1) Scalper

How they use it:

- keep `--expiration-date` empty to focus on nearest expiry flow
- use small `--top-n` (for example 3-5) for fast shortlist
- look for contracts aligning with opening range or VWAP setups

Example:

```powershell
python ".\options\top-itm-contracts.py" --ticker SPY --top-n 5
```

### 2) Day Trader

How they use it:

- often compare nearest expiry vs same-week expiry
- use `--top-n` 5-10 to see where volume concentrates intraday
- combine with chart structure before execution

Example:

```powershell
python ".\options\top-itm-contracts.py" --ticker SPY --expiration-date 2026-02-27 --top-n 8
```

### 3) Swing Trader

How they use it:

- target explicit expirations 2-8 weeks out
- focus on ITM contracts for more stable delta exposure
- use results as strike shortlist, then validate OI/spread

Example:

```powershell
python ".\options\top-itm-contracts.py" --ticker AAPL --expiration-date 2026-04-17 --top-n 6
```

### 4) Investor

How they use it:

- use longer-dated expirations (where available) for lower turnover positioning
- focus on liquid ITM strikes for stock-replacement style exposure
- treat output as research input, not standalone allocation signal

Example:

```powershell
python ".\options\top-itm-contracts.py" --ticker QQQ --expiration-date 2026-12-18 --top-n 10
```

## Practical Workflow

1. Choose ticker and targeted expiration (or compare multiple expirations).
2. Run script with `--top-n` 5 to 10.
3. Overlay returned strikes on chart and current option chain.
4. Validate liquidity (bid/ask spread, OI, depth) externally.
5. Execute only if aligned with setup and risk plan.

## Example Commands

Explicit expiration:

```powershell
python ".\options\top-itm-contracts.py" --ticker AAPL --expiration-date 2026-03-20 --top-n 5
```

Nearest expiration (auto):

```powershell
python ".\options\top-itm-contracts.py" --ticker AAPL --top-n 5
```

Unified CLI:

```powershell
python ".\ttg-cli.py" itm --ticker AAPL --expiration-date 2026-03-20 --top-n 5
```

## Output Reference

Response fields:

- `ticker`: normalized underlying symbol
- `underlying_price`: last trade price used for ITM classification
- `options[]`:
  - `ticker`
  - `strike_price`
  - `volume`
  - `type`
  - `expiration_date`
  - `last_trade_price`
  - `implied_volatility`

## Limitations to Respect

1. **Only first 100 snapshot results are requested (`limit=100`)**
   - can miss true highest-volume contracts if full chain is larger.

2. **No open interest filter**
   - volume without OI context can be noisy.

3. **No spread/liquidity quality checks**
   - top volume does not equal tight execution quality.

4. **Nearest-expiration default can bias to ultra-short tenor**
   - useful for 0DTE workflows, less useful for swing workflows unless explicit date is passed.

5. **Classification depends on one underlying print**
   - using last trade can misclassify near-ATM contracts during fast movement.

6. **No side-of-trade intelligence**
   - script ranks activity, not aggressor direction.

## Bottom Line

Use this scanner to locate **where ITM participation is concentrated**, then combine with:

- underlying trend/structure
- volatility and event context
- execution quality checks
- defined risk and invalidation

That combination converts raw contract rankings into a usable trading process.
