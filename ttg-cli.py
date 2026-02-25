import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
ITM_SCRIPT = ROOT_DIR / "options" / "top-itm-contracts.py"
OTM_SCRIPT = ROOT_DIR / "options" / "top-otm-contracts.py"
SUPPORT_RESISTANCE_SCRIPT = ROOT_DIR / "stocks" / "support-resistance.py"


def _load_module(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_itm_module():
    return _load_module(ITM_SCRIPT, "top_itm_contracts")


def _get_otm_module():
    return _load_module(OTM_SCRIPT, "top_otm_contracts")


def _get_support_resistance_module():
    return _load_module(SUPPORT_RESISTANCE_SCRIPT, "support_resistance")


def _valid_date(value):
    try:
        dt.datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc
    return value


def _prompt_required(prompt_text, default=None):
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw = input(f"{prompt_text}{suffix}: ").strip()
        if not raw and default is not None:
            return str(default)
        if raw:
            return raw
        print("Value is required.")


def _prompt_positive_int(prompt_text, default=2):
    while True:
        raw = _prompt_required(prompt_text, default=default)
        try:
            parsed = int(raw)
            if parsed < 1:
                raise ValueError()
            return parsed
        except ValueError:
            print("Enter a whole number >= 1.")


def _prompt_optional_date(prompt_text):
    while True:
        raw = input(f"{prompt_text} [optional, YYYY-MM-DD]: ").strip()
        if not raw:
            return None
        try:
            dt.datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")


def _print_header():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 72)
    print("TTG QUANT TOOLS - UNIFIED CLI")
    print("=" * 72)
    print(f"MASSIVE_API_BASE_URL: {'set' if os.getenv('MASSIVE_API_BASE_URL') else 'missing'}")
    print(f"MASSIVE_API_KEY: {'set' if os.getenv('MASSIVE_API_KEY') else 'missing'}")
    print("")


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Unified launcher for TTG quant tools (ITM, OTM, support/resistance)."
    )

    subparsers = parser.add_subparsers(dest="command")

    itm_parser = subparsers.add_parser("itm", help="Top ITM options by volume")
    itm_parser.add_argument("--ticker", required=True, help="Underlying ticker, e.g. AAPL")
    itm_parser.add_argument("--expiration-date", required=False, help="Optional expiration date YYYY-MM-DD")
    itm_parser.add_argument("--top-n", type=int, default=2, help="How many contracts to return")
    itm_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    otm_parser = subparsers.add_parser("otm", help="Top OTM options by volume")
    otm_parser.add_argument("--ticker", required=True, help="Underlying ticker, e.g. AAPL")
    otm_parser.add_argument("--expiration-date", required=False, help="Optional expiration date YYYY-MM-DD")
    otm_parser.add_argument("--top-n", type=int, default=2, help="How many contracts to return")
    otm_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    sr_parser = subparsers.add_parser("support-resistance", help="Support/resistance from OHLC bars")
    sr_parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    sr_parser.add_argument("--multiplier", required=True, type=int, help="Range multiplier, e.g. 1")
    sr_parser.add_argument("--timeframe", required=True, help="Timespan, e.g. minute|hour|day|week|month")
    sr_parser.add_argument("--start-date", required=True, type=_valid_date, help="Start date YYYY-MM-DD")
    sr_parser.add_argument("--end-date", required=True, type=_valid_date, help="End date YYYY-MM-DD")
    sr_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    return parser


def _run_itm(ticker, expiration_date=None, top_n=2):
    module = _get_itm_module()
    return module.get_top_itm_options(
        ticker=ticker,
        expiration_date=expiration_date,
        top_n=max(1, int(top_n)),
    )


def _run_otm(ticker, expiration_date=None, top_n=2):
    module = _get_otm_module()
    return module.get_top_otm_options(
        ticker=ticker,
        expiration_date=expiration_date,
        top_n=max(1, int(top_n)),
    )


def _run_support_resistance(ticker, multiplier, timeframe, start_date, end_date):
    module = _get_support_resistance_module()
    return module.calculate_support_resistance(
        ticker=ticker,
        multiplier=multiplier,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
    )


def _run_interactive():
    _print_header()
    print("Choose a tool:")
    print("1) Top ITM options")
    print("2) Top OTM options")
    print("3) Support/Resistance")
    print("")

    choice = _prompt_required("Enter choice (1/2/3)")
    print("")

    if choice == "1":
        ticker = _prompt_required("Ticker", default="AAPL")
        expiration_date = _prompt_optional_date("Expiration date")
        top_n = _prompt_positive_int("Top contracts to return", default=2)
        result = _run_itm(ticker=ticker, expiration_date=expiration_date, top_n=top_n)
    elif choice == "2":
        ticker = _prompt_required("Ticker", default="AAPL")
        expiration_date = _prompt_optional_date("Expiration date")
        top_n = _prompt_positive_int("Top contracts to return", default=2)
        result = _run_otm(ticker=ticker, expiration_date=expiration_date, top_n=top_n)
    elif choice == "3":
        ticker = _prompt_required("Ticker", default="AAPL")
        multiplier = _prompt_positive_int("Multiplier", default=1)
        timeframe = _prompt_required("Timeframe", default="day")
        start_date = _prompt_required("Start date", default="2026-01-01")
        end_date = _prompt_required("End date", default="2026-02-01")
        _valid_date(start_date)
        _valid_date(end_date)
        result = _run_support_resistance(
            ticker=ticker,
            multiplier=multiplier,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        raise RuntimeError("Invalid choice. Use 1, 2, or 3.")

    print("")
    print(json.dumps(result, indent=2, default=str))
    return 0


def main():
    try:
        if len(sys.argv) == 1:
            return _run_interactive()

        parser = _build_parser()
        args = parser.parse_args()
        if args.command is None:
            return _run_interactive()

        if args.command == "itm":
            result = _run_itm(
                ticker=args.ticker,
                expiration_date=args.expiration_date,
                top_n=args.top_n,
            )
        elif args.command == "otm":
            result = _run_otm(
                ticker=args.ticker,
                expiration_date=args.expiration_date,
                top_n=args.top_n,
            )
        elif args.command == "support-resistance":
            result = _run_support_resistance(
                ticker=args.ticker,
                multiplier=args.multiplier,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
            )
        else:
            raise RuntimeError(f"Unsupported command: {args.command}")

        pretty = getattr(args, "pretty", False)
        print(json.dumps(result, indent=2 if pretty else None, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
