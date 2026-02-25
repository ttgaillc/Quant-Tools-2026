# Support/Resistance Tool: Trader Guide

This guide explains what `stocks/support-resistance.py` does, how to interpret its output as a trader, and where it is useful (and not useful) in real trading workflows.

## What This Tool Actually Does

At a high level, the script:

1. Pulls historical OHLCV bars from Massive.
2. Detects local turning points in close prices.
3. Returns up to 3 candidate support levels and 3 candidate resistance levels.
4. Optionally returns full underlying bars if you pass `--include-data`.

It is a **structure-mapping helper**, not an entry signal by itself.

## Data and Inputs

Command arguments:

- `--ticker`: symbol (example: `AAPL`)
- `--multiplier`: bar size multiplier (example: `1`)
- `--timeframe`: bar unit (`minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`)
- `--start-date`: inclusive start date (`YYYY-MM-DD`)
- `--end-date`: inclusive end date (`YYYY-MM-DD`)
- `--include-data`: include full OHLC bars in output (optional, large payload)

Environment:

- `MASSIVE_API_KEY` (required)
- `MASSIVE_API_BASE_URL` (required)
- `MASSIVE_HTTP_TIMEOUT_SECONDS` (optional, default `20`)

## Internal Logic (Step by Step)

The script currently performs the following process:

1. **Fetch bars** from Massive aggregate endpoint using:
   - `adjusted=true`
   - `limit=50000`
   - `sort=desc`
2. **Load into pandas** as a DataFrame.
3. **Find local highs/lows** on `close` (`c`) using SciPy:
   - `find_peaks(df["c"], distance=20)` for resistance candidates
   - `find_peaks(-df["c"], distance=20)` for support candidates
4. **Rank levels** by how often the exact candidate prices appear.
5. Return JSON with:
   - `support_levels`
   - `resistance_levels`
   - optional `data` (bars) only if `--include-data` is used

## How Traders Should Interpret the Output

Treat each level as a **zone**, not an exact price.

Practical interpretation:

- **Support level**: area where downside previously stalled.
- **Resistance level**: area where upside previously stalled.
- **Closest level to current price** is usually most actionable.
- **Confluence matters**: level quality improves when aligned with trend, VWAP, prior day high/low, or volume profile.

## High-Value Use Cases

### 1) Pre-market map building

Use the script before open to define likely reaction zones:

- nearest overhead resistance
- nearest underlying support
- likely expansion path between zones

### 2) Pullback entries in trend

In an uptrend:

- wait for pullback into script-derived support zone
- require confirmation (reclaim, strong candle close, volume expansion)
- place invalidation below zone, not at exact tick

In a downtrend:

- inverse logic at resistance

### 3) Breakout and retest framework

- breakout through resistance
- wait for retest hold
- execute with clear invalidation under retest zone

### 4) Profit targeting and scaling

Use the next opposing level as first objective:

- long from support -> first scale near resistance
- short from resistance -> first scale near support

### 5) Multi-timeframe alignment

Run multiple windows/timeframes to rank level importance:

- higher-timeframe levels (day/week) = stronger context
- lower-timeframe levels (minute/hour) = better execution precision

## Parameter Selection Guide (Trader-Focused)

Think of the key variables like this:

- `ticker`: the instrument you are mapping (for example `SPY`, `AAPL`)
- `timeframe`: candle unit (`minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`)
- `multiplier`: number of units per bar (`1` = every bar, `5` + `minute` = 5-minute bars)
- `start-date` / `end-date`: how far back and through when you want structure analyzed

## How Different Trader Types Use This Tool

### 1) Scalper (very short holding period)

Typical choices:

- `timeframe=minute`
- `multiplier=1` or `5`
- `start-date` = last 1-3 trading days
- `end-date` = today

Why: focuses on immediate intraday reaction zones without old data dominating.

Example:

```powershell
python ".\stocks\support-resistance.py" --ticker SPY --multiplier 1 --timeframe minute --start-date 2026-02-23 --end-date 2026-02-25
```

### 2) Day Trader

Typical choices:

- `timeframe=minute`
- `multiplier=5` or `15`
- `start-date` = recent 5-20 trading days
- `end-date` = today

Why: balances intraday precision with enough history for recurring session levels.

Example:

```powershell
python ".\stocks\support-resistance.py" --ticker SPY --multiplier 5 --timeframe minute --start-date 2026-02-01 --end-date 2026-02-25
```

### 3) Swing Trader

Typical choices:

- `timeframe=day`
- `multiplier=1`
- `start-date` = 3-12 months back
- `end-date` = today

Why: captures medium-term pivots that drive multi-day to multi-week swings.

Example:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 1 --timeframe day --start-date 2025-08-01 --end-date 2026-02-25
```

### 4) Investor (longer horizon)

Typical choices:

- `timeframe=week` or `month`
- `multiplier=1`
- `start-date` = 2-5 years back
- `end-date` = today

Why: highlights major structural zones for staged entries, adds, trims, and risk budgeting.

Example:

```powershell
python ".\stocks\support-resistance.py" --ticker QQQ --multiplier 1 --timeframe week --start-date 2022-01-01 --end-date 2026-02-25
```

## Risk and Limitations (Important)

This script is useful, but it has structural constraints you should account for:

1. **Close-only pivots**
   - Uses close prices (`c`) rather than intrabar highs/lows.
   - Can miss wick-based rejection levels.

2. **Fixed peak spacing**
   - `distance=20` is static across all timeframes.
   - "20 bars" means very different market time across minute vs day charts.

3. **Exact-price counting**
   - Ranking uses exact float price frequency.
   - Markets often react in zones, not exact repeated prints.

4. **Potential truncation on large ranges**
   - API request uses `limit=50000`.
   - Very large windows on small timeframes may not include full history.

5. **No built-in trade filter**
   - No trend filter, no volatility regime filter, no volume confirmation.
   - You must layer your own execution rules.

## Practical Trade Workflow

Use this sequence to avoid over-trading around raw levels:

1. Run script and map nearby support/resistance.
2. Mark them as zones on chart (for example +/- 0.1%-0.4% depending on volatility).
3. Define bias (trend, market regime, news context).
4. Wait for confirmation at zone:
   - rejection + close
   - reclaim
   - breakout + hold
5. Set invalidation beyond zone.
6. Use opposing level for first target.
7. Manage risk with fixed R multiple or ATR-based stop model.

## Example Commands

Day-trade oriented:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 5 --timeframe minute --start-date 2026-02-01 --end-date 2026-02-25
```

Swing oriented:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 1 --timeframe day --start-date 2025-08-01 --end-date 2026-02-25
```

Include full bar data only when needed:

```powershell
python ".\stocks\support-resistance.py" --ticker AAPL --multiplier 5 --timeframe minute --start-date 2026-02-01 --end-date 2026-02-25 --include-data
```

Unified CLI:

```powershell
python ".\ttg-cli.py" support-resistance --ticker AAPL --multiplier 1 --timeframe day --start-date 2026-01-01 --end-date 2026-02-01
```

## Output Fields Reference

- `support_levels`: up to 3 support candidates
- `resistance_levels`: up to 3 resistance candidates
- `data` (optional): cleaned OHLCV bars used in analysis, included only when `--include-data` is passed
  - `Date`, `t`, `o`, `h`, `l`, `c`, `v`

## Bottom Line

Use this tool to **frame market structure**, not to auto-fire trades.  
Its highest value comes from combining levels with:

- trend context
- confirmation triggers
- disciplined risk management
- multi-timeframe confluence

That combination turns static levels into a repeatable trading process.
