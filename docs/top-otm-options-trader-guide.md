# Top OTM Options Tool: Trader Guide

This guide explains what `options/top-otm-contracts.py` does, how to interpret it as a trader, and how to use it safely in real setups.

## What This Script Is Built For

The script finds high-volume **out-of-the-money (OTM)** options and returns the top N contracts by daily volume.

OTM flow is often associated with:

- speculative positioning
- event-driven convexity plays
- lower-premium directional bets

The script is best treated as an **attention and positioning map**, not a direct buy/sell trigger.

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

The script workflow:

1. Normalize ticker.
2. Validate optional expiration.
3. Fetch underlying last trade.
4. Fetch options snapshot.
5. If expiration is provided, filter to that date.
6. Otherwise select nearest expiration date in returned set.
7. Classify OTM:
   - Call OTM if `strike > underlying_price`
   - Put OTM if `strike < underlying_price`
8. Sort OTM contracts by daily volume descending.
9. Return top N.

## OTM Interpretation for Traders

OTM concentration can flag:

- directional speculation around catalysts
- momentum/chase behavior
- convexity demand (especially short-dated flow)

But high OTM volume alone does not imply edge. It can also represent:

- hedges
- spread legs
- closing activity
- low-quality lottery behavior

## Trader Use Cases

### 1) Event-driven setup prep

Before earnings, macro events, or key news windows:

- scan OTM concentration by expiration
- compare call vs put clustering
- define scenario trees and risk size before event

### 2) Momentum continuation confirmation

When price is already trending, OTM concentration near relevant strikes can support momentum narratives if underlying tape confirms.

### 3) Breakout mapping

Heavily traded OTM calls above spot can identify attention zones; heavily traded OTM puts below spot can identify downside fear zones.

### 4) Cheap convexity basket selection

If your process includes small-size convexity trades, this tool helps shortlist actively traded candidates before deeper chain analysis.

## How Different Trader Types Use This Tool

Key input meanings:

- `--ticker`: underlying symbol to scan
- `--expiration-date`: which expiration to analyze (omit to auto-use nearest expiry)
- `--top-n`: how many contracts to return

### 1) Scalper

How they use it:

- usually scan nearest expiry (leave `--expiration-date` empty)
- keep `--top-n` small to stay focused on the most active strikes
- use as a speed filter before momentum execution

Example:

```powershell
python ".\options\top-otm-contracts.py" --ticker SPY --top-n 5
```

### 2) Day Trader

How they use it:

- compare nearest expiry and same-week expiry
- monitor call/put concentration shifts during session
- use output to map likely attention strikes for intraday continuation/fade setups

Example:

```powershell
python ".\options\top-otm-contracts.py" --ticker SPY --expiration-date 2026-02-27 --top-n 8
```

### 3) Swing Trader

How they use it:

- set explicit expirations a few weeks out
- use OTM flow for directional confirmation, not primary trigger
- validate with trend structure and IV context before entering

Example:

```powershell
python ".\options\top-otm-contracts.py" --ticker NVDA --expiration-date 2026-04-17 --top-n 10
```

### 4) Investor

How they use it:

- monitor OTM activity as sentiment/risk appetite signal
- occasionally use output for covered-call/cash-secured-put research around key strikes
- avoid treating short-dated OTM volume as long-term thesis proof

Example:

```powershell
python ".\options\top-otm-contracts.py" --ticker QQQ --expiration-date 2026-06-19 --top-n 10
```

## Practical Workflow

1. Start with explicit expiration if your strategy is tenor-specific.
2. Pull top 5-10 contracts.
3. Separate by call/put and map strikes against chart structure.
4. Validate:
   - spread quality
   - open interest
   - IV regime and skew
5. Use strict position sizing; OTM decay and gamma risk can be extreme.

## Example Commands

Nearest expiration:

```powershell
python ".\options\top-otm-contracts.py" --ticker AAPL --top-n 5
```

Specific expiration:

```powershell
python ".\options\top-otm-contracts.py" --ticker AAPL --expiration-date 2026-03-20 --top-n 10
```

Unified CLI:

```powershell
python ".\ttg-cli.py" otm --ticker AAPL --top-n 5
```

## Output Reference

Response fields:

- `ticker`: normalized underlying symbol
- `underlying_price`: last trade used for OTM classification
- `options[]`:
  - `ticker`
  - `strike_price`
  - `volume`
  - `type`
  - `expiration_date`
  - `last_trade_price`
  - `implied_volatility`

## Risk and Limitations

1. **Snapshot request limit is 100 contracts**
   - highest-volume OTM contracts can be missed when chain is larger.

2. **No open-interest context**
   - volume alone cannot distinguish opening vs closing behavior.

3. **No bid/ask quality checks**
   - active contracts may still be expensive to execute.

4. **Nearest-expiration default can overemphasize short-dated noise**
   - great for intraday flow tracking, weaker for swing intent unless expiration is specified.

5. **Underlying classification is single-print based**
   - contracts near ATM can flip classification quickly in volatile tape.

6. **No trade direction inference**
   - high volume does not tell whether flow was buyer-initiated or seller-initiated.

## Position-Risk Notes (Important)

For OTM trading specifically:

- assume high probability of full premium loss unless proven otherwise
- size by predefined max loss, not conviction
- avoid using OTM volume as sole trigger
- treat OTM signals as secondary confirmation to primary price-based setup

## Bottom Line

Use this script to identify **where speculative attention is concentrated** in OTM contracts.  
Then combine with:

- chart structure and trend
- IV/skew and time-to-expiration
- execution quality checks
- strict risk controls

That is how OTM flow data becomes useful, rather than just noisy.
