import argparse
import datetime as dt
import json
import logging
import os
import sys

import pandas as pd
import requests
from scipy.signal import find_peaks

MASSIVE_API_BASE_URL = os.getenv("MASSIVE_API_BASE_URL")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
MASSIVE_HTTP_TIMEOUT_SECONDS = int(os.getenv("MASSIVE_HTTP_TIMEOUT_SECONDS", "20"))


def fetch_massive_data(ticker, multiplier, timeframe, start_date, end_date):
    if not MASSIVE_API_BASE_URL:
        raise RuntimeError("Missing MASSIVE_API_BASE_URL in environment")
    if not MASSIVE_API_KEY:
        raise RuntimeError("Missing MASSIVE_API_KEY in environment")

    capitalize_ticker = ticker.upper().strip()
    url = f"{MASSIVE_API_BASE_URL.rstrip('/')}/v2/aggs/ticker/{capitalize_ticker}/range/{multiplier}/{timeframe}/{start_date}/{end_date}"
    params = {
        "apiKey": MASSIVE_API_KEY,
        "adjusted": True,
        "limit": 50000,
        "sort": "desc",
    }
    try:
        response = requests.get(url, params=params, timeout=MASSIVE_HTTP_TIMEOUT_SECONDS)
    except requests.Timeout:
        raise RuntimeError("Timed out fetching data from Massive.com")
    except requests.RequestException:
        raise RuntimeError("Network error fetching data from Massive.com")

    if response.status_code != 200:
        raise RuntimeError(f"Error fetching data from Massive.com: {response.status_code} {response.text}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Invalid response from Massive.com")

    if "results" not in data:
        raise RuntimeError("No data found for the given parameters")

    return pd.DataFrame(data["results"])

def find_support_resistance(df):
    peaks, _ = find_peaks(df["c"], distance=20)
    troughs, _ = find_peaks(-df["c"], distance=20)
    resistance_prices = df["c"].iloc[peaks].values
    support_prices = df["c"].iloc[troughs].values
    support_levels = pd.Series(support_prices).value_counts().nlargest(3).index.tolist()
    resistance_levels = pd.Series(resistance_prices).value_counts().nlargest(3).index.tolist()
    return support_levels, resistance_levels

def calculate_support_resistance(ticker, multiplier, timeframe, start_date, end_date):
    df = fetch_massive_data(ticker, multiplier, timeframe, start_date, end_date)
    support_levels, resistance_levels = find_support_resistance(df)
    df["Date"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    response_columns = ["Date", "t", "o", "h", "l", "c", "v"]
    df_clean = df[response_columns].replace({pd.NA: None, pd.NaT: None, float("inf"): None, float("-inf"): None})
    data_records = df_clean.where(pd.notnull(df_clean), None).to_dict(orient="records")

    return {
        "data": data_records,
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
    }


def _valid_date(date_string):
    try:
        dt.datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{date_string}'. Use YYYY-MM-DD.") from exc
    return date_string


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch stock OHLC bars and compute support/resistance levels.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--multiplier", required=True, type=int, help="Range multiplier, e.g. 1")
    parser.add_argument("--timeframe", required=True, help="Timespan, e.g. minute|hour|day|week|month")
    parser.add_argument("--start-date", required=True, type=_valid_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, type=_valid_date, help="End date (YYYY-MM-DD)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    try:
        result = calculate_support_resistance(
            ticker=args.ticker,
            multiplier=args.multiplier,
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        print(json.dumps(result, indent=2 if args.pretty else None, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
