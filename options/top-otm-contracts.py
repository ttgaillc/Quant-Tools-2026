import argparse
import datetime as dt
import json
import os
import sys

import requests

MASSIVE_API_BASE_URL = os.getenv("MASSIVE_API_BASE_URL")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
MASSIVE_HTTP_TIMEOUT_SECONDS = int(os.getenv("MASSIVE_HTTP_TIMEOUT_SECONDS", "20"))


def validate_expiration_date(value):
    if value is None:
        return None
    clean = value.strip()
    if not clean or clean.lower() == "string":
        return None
    try:
        dt.datetime.strptime(clean, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Invalid expiration date format. Use YYYY-MM-DD.") from exc
    return clean

def get_underlying_price(ticker):
    if not MASSIVE_API_BASE_URL:
        raise RuntimeError("Missing MASSIVE_API_BASE_URL in environment")
    if not MASSIVE_API_KEY:
        raise RuntimeError("Missing MASSIVE_API_KEY in environment")

    url = f"{MASSIVE_API_BASE_URL.rstrip('/')}/v2/last/trade/{ticker}"
    response = requests.get(url, params={"apiKey": MASSIVE_API_KEY}, timeout=MASSIVE_HTTP_TIMEOUT_SECONDS)
    data = response.json()
    if "results" in data:
        return data["results"]["p"]
    raise RuntimeError(f"Error fetching last trade for {ticker}: {data}")

def get_options_chain(ticker):
    url = f"{MASSIVE_API_BASE_URL.rstrip('/')}/v3/snapshot/options/{ticker}"
    params = {"limit": 100, "apiKey": MASSIVE_API_KEY}
    response = requests.get(url, params=params, timeout=MASSIVE_HTTP_TIMEOUT_SECONDS)
    data = response.json()
    if "results" in data:
        return data["results"]
    raise RuntimeError(f"Error fetching options chain for {ticker}: {data}")

def filter_otm_options(options, underlying_price):
    otm_options = []
    for option in options:
        strike_price = option["details"]["strike_price"]
        contract_type = option["details"]["contract_type"]
        if (contract_type == "call" and strike_price > underlying_price) or (contract_type == "put" and strike_price < underlying_price):
            otm_options.append(option)
    return otm_options

def sort_by_volume(options):
    return sorted(options, key=lambda x: x["day"]["volume"] if "day" in x and "volume" in x["day"] else 0, reverse=True)

def get_top_options(options, top_n):
    return options[:top_n]

def get_top_otm_options(ticker, expiration_date=None, top_n=2):
    normalized_ticker = ticker.upper().strip()
    validated_expiration = validate_expiration_date(expiration_date)

    underlying_price = get_underlying_price(normalized_ticker)
    options_chain = get_options_chain(normalized_ticker)

    if validated_expiration:
        options_chain = [option for option in options_chain if option["details"]["expiration_date"] == validated_expiration]
        if not options_chain:
            raise RuntimeError("No options contracts found for the given expiration date.")
    else:
        options_chain = sorted(options_chain, key=lambda x: x["details"]["expiration_date"])
        if options_chain:
            closest_expiration_date = options_chain[0]["details"]["expiration_date"]
            options_chain = [option for option in options_chain if option["details"]["expiration_date"] == closest_expiration_date]

    otm_options = filter_otm_options(options_chain, underlying_price)

    if not otm_options:
        raise RuntimeError("No OTM options found.")

    sorted_options = sort_by_volume(otm_options)
    top_options = get_top_options(sorted_options, top_n=top_n)

    return {
        "ticker": normalized_ticker,
        "underlying_price": underlying_price,
        "options": [
            {
                "ticker": option["details"]["ticker"],
                "strike_price": option["details"]["strike_price"],
                "volume": option["day"]["volume"] if "day" in option and "volume" in option["day"] else "N/A",
                "type": option["details"]["contract_type"],
                "expiration_date": option["details"]["expiration_date"],
                "last_trade_price": option["day"]["close"] if "day" in option and "close" in option["day"] else "N/A",
                "implied_volatility": option["implied_volatility"] if "implied_volatility" in option else "N/A",
            }
            for option in top_options
        ],
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch top OTM options contracts by volume.")
    parser.add_argument("--ticker", required=True, help="Underlying ticker, e.g. AAPL")
    parser.add_argument("--expiration-date", required=False, help="Optional expiration date YYYY-MM-DD")
    parser.add_argument("--top-n", type=int, default=2, help="How many contracts to return")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default behavior; kept for compatibility)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        result = get_top_otm_options(
            ticker=args.ticker,
            expiration_date=args.expiration_date,
            top_n=max(1, args.top_n),
        )
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
