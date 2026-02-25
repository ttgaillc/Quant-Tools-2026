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


def _color(text, code):
    if os.getenv("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


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


def _prompt_choice(prompt_text, valid_choices):
    valid = tuple(str(choice) for choice in valid_choices)
    while True:
        raw = _prompt_required(prompt_text).strip()
        if raw in valid:
            return raw
        print(f"Invalid choice. Use {'/'.join(valid)}.")


def _print_header():
    os.system("cls" if os.name == "nt" else "clear")
    print(_color("=" * 72, "36"))
    print(_color("TTG QUANT TOOLS - UNIFIED CLI", "1;36"))
    print(_color("LEARN FASTER. TRADE SMARTER. PROFIT SOONER.", "1;32"))
    print(_color("TrueTradingGroup.com", "36"))
    print(_color("Provided by TTG AI LLC | Tested and used by True Trading Group", "90"))
    print(_color("=" * 72, "36"))
    base_url_status = _color("set", "32") if os.getenv("MASSIVE_API_BASE_URL") else _color("missing", "31")
    api_key_status = _color("set", "32") if os.getenv("MASSIVE_API_KEY") else _color("missing", "31")
    print(f"MASSIVE_API_BASE_URL: {base_url_status}")
    print(f"MASSIVE_API_KEY: {api_key_status}")
    print("")


def _print_support_resistance_cheatsheet():
    print(_color("-" * 72, "90"))
    print(_color("SUPPORT/RESISTANCE INPUT GUIDE", "1;36"))
    print(_color("-" * 72, "90"))
    print("Timeframe choices : minute | hour | day | week | month | quarter | year")
    print("Multiplier       : whole number >= 1")
    print("Bar-size formula : multiplier x timeframe")
    print("")
    print(_color("Suggested presets by trading style", "1;36"))
    print(f"{'Style':<10} {'Timeframe':<10} {'Multiplier':<12} {'Typical lookback'}")
    print(_color("-" * 72, "90"))
    print(f"{'Scalper':<10} {'minute':<10} {'1 or 3':<12} {'1-3 trading days'}")
    print(f"{'Day':<10} {'minute':<10} {'5 or 15':<12} {'10-30 trading days'}")
    print(f"{'Swing':<10} {'day':<10} {'1':<12} {'3-12 months'}")
    print(f"{'Investor':<10} {'week/month':<10} {'1':<12} {'2-10 years'}")
    print("")
    print(_color("Examples", "1;36"))
    print(" - 5 + minute = 5-minute bars")
    print(" - 1 + day    = 1-day bars")
    print(" - 1 + week   = 1-week bars")
    print(_color("-" * 72, "90"))
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
    itm_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default behavior; kept for compatibility)",
    )

    otm_parser = subparsers.add_parser("otm", help="Top OTM options by volume")
    otm_parser.add_argument("--ticker", required=True, help="Underlying ticker, e.g. AAPL")
    otm_parser.add_argument("--expiration-date", required=False, help="Optional expiration date YYYY-MM-DD")
    otm_parser.add_argument("--top-n", type=int, default=2, help="How many contracts to return")
    otm_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default behavior; kept for compatibility)",
    )

    sr_parser = subparsers.add_parser("support-resistance", help="Support/resistance from OHLC bars")
    sr_parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    sr_parser.add_argument(
        "--multiplier",
        required=True,
        type=int,
        help="Bar size multiplier. Examples: 1 with day=1-day bars, 5 with minute=5-minute bars, 15 with minute=15-minute bars",
    )
    sr_parser.add_argument(
        "--timeframe",
        required=True,
        help="Timespan (case-insensitive), e.g. minute|hour|day|week|month|quarter|year",
    )
    sr_parser.add_argument("--start-date", required=True, type=_valid_date, help="Start date YYYY-MM-DD")
    sr_parser.add_argument("--end-date", required=True, type=_valid_date, help="End date YYYY-MM-DD")
    sr_parser.add_argument(
        "--include-data",
        action="store_true",
        help="Include full OHLC bar data in output (can be very large)",
    )
    sr_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default behavior; kept for compatibility)",
    )

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


def _run_support_resistance(ticker, multiplier, timeframe, start_date, end_date, include_data=False):
    module = _get_support_resistance_module()
    return module.calculate_support_resistance(
        ticker=ticker,
        multiplier=multiplier,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        include_data=include_data,
    )


def _run_itm_interactive_once(previous_settings=None, ticker_only=False, reuse_all=False):
    if reuse_all and previous_settings:
        ticker = previous_settings["ticker"]
        expiration_date = previous_settings["expiration_date"]
        top_n = previous_settings["top_n"]
    elif ticker_only and previous_settings:
        ticker = _prompt_required("Enter as single ticker symbol")
        expiration_date = previous_settings["expiration_date"]
        top_n = previous_settings["top_n"]
    else:
        ticker = _prompt_required("Enter as single ticker symbol")
        expiration_date = _prompt_optional_date("Expiration date")
        top_n = _prompt_positive_int("Top contracts to return", default=2)

    result = _run_itm(ticker=ticker, expiration_date=expiration_date, top_n=top_n)
    settings = {
        "ticker": ticker,
        "expiration_date": expiration_date,
        "top_n": top_n,
    }
    return result, settings


def _run_otm_interactive_once(previous_settings=None, ticker_only=False, reuse_all=False):
    if reuse_all and previous_settings:
        ticker = previous_settings["ticker"]
        expiration_date = previous_settings["expiration_date"]
        top_n = previous_settings["top_n"]
    elif ticker_only and previous_settings:
        ticker = _prompt_required("Enter as single ticker symbol")
        expiration_date = previous_settings["expiration_date"]
        top_n = previous_settings["top_n"]
    else:
        ticker = _prompt_required("Enter as single ticker symbol")
        expiration_date = _prompt_optional_date("Expiration date")
        top_n = _prompt_positive_int("Top contracts to return", default=2)

    result = _run_otm(ticker=ticker, expiration_date=expiration_date, top_n=top_n)
    settings = {
        "ticker": ticker,
        "expiration_date": expiration_date,
        "top_n": top_n,
    }
    return result, settings


def _run_support_resistance_interactive_once(previous_settings=None, ticker_only=False):
    if ticker_only and previous_settings:
        ticker = _prompt_required("Enter as single ticker symbol")
        multiplier = previous_settings["multiplier"]
        timeframe = previous_settings["timeframe"]
        start_date = previous_settings["start_date"]
        end_date = previous_settings["end_date"]
    else:
        _print_support_resistance_cheatsheet()
        ticker = _prompt_required("Enter as single ticker symbol")
        multiplier = _prompt_positive_int(
            "Multiplier (whole number, >=1)",
            default=1,
        )
        timeframe = _prompt_required("Timeframe (minute/hour/day/week/month/quarter/year)", default="day")
        today = dt.date.today().strftime("%Y-%m-%d")
        start_date = _prompt_required("Start date (YYYY-MM-DD)", default="2026-01-01")
        end_date = _prompt_required("End date (YYYY-MM-DD)", default=today)
        _valid_date(start_date)
        _valid_date(end_date)

    result = _run_support_resistance(
        ticker=ticker,
        multiplier=multiplier,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        include_data=False,
    )
    settings = {
        "ticker": ticker,
        "multiplier": multiplier,
        "timeframe": timeframe,
        "start_date": start_date,
        "end_date": end_date,
    }
    return result, settings


def _post_run_action():
    print("")
    print("What would you like to do next?")
    print("1) Run this tool again")
    print("2) Same settings, different ticker")
    print("3) Go back")
    print("4) Exit")
    print("")
    return _prompt_choice("Enter choice (1/2/3/4)", ("1", "2", "3", "4"))


def _run_tool_with_navigation(run_once_callable):
    last_settings = None
    ticker_only = False

    while True:
        try:
            result, last_settings = run_once_callable(previous_settings=last_settings, ticker_only=ticker_only)
            ticker_only = False
            print("")
            print(json.dumps(result, indent=2, default=str))
        except Exception as exc:
            ticker_only = False
            print("")
            print(json.dumps({"error": str(exc)}), file=sys.stderr)

        action = _post_run_action()
        if action == "1":
            continue
        if action == "2":
            if last_settings is None:
                print("")
                print("Run this tool once first to save settings.")
                continue
            ticker_only = True
            continue
        if action == "3":
            return "back"
        return "exit"


def _run_options_tool_with_navigation(initial_tool):
    current_tool = initial_tool
    last_settings = None
    ticker_only = False
    reuse_all = False

    while True:
        try:
            if current_tool == "itm":
                result, last_settings = _run_itm_interactive_once(
                    previous_settings=last_settings,
                    ticker_only=ticker_only,
                    reuse_all=reuse_all,
                )
            else:
                result, last_settings = _run_otm_interactive_once(
                    previous_settings=last_settings,
                    ticker_only=ticker_only,
                    reuse_all=reuse_all,
                )
            ticker_only = False
            reuse_all = False
            print("")
            print(json.dumps(result, indent=2, default=str))
        except Exception as exc:
            ticker_only = False
            reuse_all = False
            print("")
            print(json.dumps({"error": str(exc)}), file=sys.stderr)

        opposite_tool = "OTM" if current_tool == "itm" else "ITM"
        print("")
        print("What would you like to do next?")
        print("1) Run this tool again")
        print("2) Same settings, different ticker")
        print(f"3) Run {opposite_tool} with same settings")
        print("4) Go back")
        print("5) Exit")
        print("")

        action = _prompt_choice("Enter choice (1/2/3/4/5)", ("1", "2", "3", "4", "5"))
        if action == "1":
            continue
        if action == "2":
            if last_settings is None:
                print("")
                print("Run this tool once first to save settings.")
                continue
            ticker_only = True
            continue
        if action == "3":
            if last_settings is None:
                print("")
                print("Run this tool once first to save settings.")
                continue
            current_tool = "otm" if current_tool == "itm" else "itm"
            reuse_all = True
            continue
        if action == "4":
            return "back"
        return "exit"


def _run_interactive():
    while True:
        _print_header()
        print("Choose a category:")
        print("1) Options")
        print("2) Stocks")
        print("3) Exit")
        print("")

        category = _prompt_choice("Enter choice (1/2/3)", ("1", "2", "3"))
        print("")

        if category == "3":
            return 0

        if category == "1":
            while True:
                _print_header()
                print("Options tools:")
                print("1) Top ITM options")
                print("2) Top OTM options")
                print("3) Go back")
                print("")

                tool_choice = _prompt_choice("Enter choice (1/2/3)", ("1", "2", "3"))
                print("")
                if tool_choice == "3":
                    break

                if tool_choice == "1":
                    nav = _run_options_tool_with_navigation("itm")
                else:
                    nav = _run_options_tool_with_navigation("otm")

                if nav == "exit":
                    return 0
        else:
            while True:
                _print_header()
                print("Stocks tools:")
                print("1) Support/Resistance")
                print("2) Go back")
                print("")

                tool_choice = _prompt_choice("Enter choice (1/2)", ("1", "2"))
                print("")
                if tool_choice == "2":
                    break

                nav = _run_tool_with_navigation(_run_support_resistance_interactive_once)
                if nav == "exit":
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
                include_data=args.include_data,
            )
        else:
            raise RuntimeError(f"Unsupported command: {args.command}")

        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
