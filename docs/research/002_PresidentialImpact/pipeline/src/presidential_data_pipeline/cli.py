from __future__ import annotations

import argparse
from pathlib import Path

from .assemble import BuildError, build_annual_dataset, write_dataset
from .config import ConfigError, load_config
from .fetch import FetchError
from .pipeline import fetch_then_record, initialize_workspace, parse_sources, validate_workspace


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="presidential-data", description="Portable provenance-first data pipeline")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "parse", "validate"):
        command = subcommands.add_parser(name)
        command.add_argument("--config", required=True, type=Path)
        command.add_argument("--workspace", required=True, type=Path)
        if name in {"fetch", "parse"}:
            command.add_argument("--source", action="append", default=[])
    init = subcommands.add_parser("init")
    init.add_argument("--workspace", required=True, type=Path)
    build = subcommands.add_parser("build-annual")
    build.add_argument("--config", required=True, type=Path)
    build.add_argument("--workspace", required=True, type=Path)
    build.add_argument("--controls", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    build.add_argument("--decision-policy", required=True, choices=("window_start", "calendar_year_start"))
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "init":
            initialize_workspace(arguments.workspace)
            print(f"Initialized {arguments.workspace}")
            return 0
        config = load_config(arguments.config)
        if arguments.command == "fetch":
            records = fetch_then_record(arguments.workspace, config, arguments.source)
            print(f"Fetched {len(records)} source artifact(s); parse them in a separate step.")
            return 0
        if arguments.command == "parse":
            statuses = parse_sources(arguments.workspace, config, arguments.source)
            failures = [item for item in statuses if item["status"] == "FAILED"]
            print(f"Parsed {len(statuses) - len(failures)} source(s); {len(failures)} source(s) require attention.")
            return 1 if failures else 0
        if arguments.command == "validate":
            report = validate_workspace(arguments.workspace, config)
            print(f"Validation found {report['errors']} error(s) and {report['warnings']} warning(s).")
            return 1 if report["errors"] else 0
        if arguments.command == "build-annual":
            market = arguments.workspace / "normalized" / "market_returns_monthly.csv"
            dataset, manifest = build_annual_dataset(config, market, arguments.controls, arguments.decision_policy)
            write_dataset(arguments.output, dataset, manifest)
            print(f"Wrote {arguments.output} and its replay manifest.")
            return 0
    except (ConfigError, BuildError, FetchError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    raise AssertionError(f"Unhandled command {arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
