from __future__ import annotations

import argparse
from pathlib import Path

from .assemble import (
    BuildError,
    build_annual_dataset,
    build_public_series_comparison,
    write_dataset,
    write_public_series_comparison,
)
from .config import ConfigError, load_config
from .fetch import FetchError
from .pipeline import (
    ReviewError,
    fetch_then_record,
    initialize_workspace,
    parse_sources,
    prepare_control_review,
    validate_controls_file,
    validate_workspace,
)
from .review_workbook import ReviewWorkbookError, export_approved_controls


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
    comparison = subcommands.add_parser("build-public-series-comparison")
    comparison.add_argument("--config", required=True, type=Path)
    comparison.add_argument("--workspace", required=True, type=Path)
    comparison.add_argument("--controls", required=True, type=Path)
    comparison.add_argument("--output-dir", required=True, type=Path)
    comparison.add_argument("--decision-policy", required=True, choices=("window_start", "calendar_year_start"))
    review = subcommands.add_parser("prepare-control-review")
    review.add_argument("--config", required=True, type=Path)
    review.add_argument("--workspace", required=True, type=Path)
    review.add_argument("--output", type=Path)
    validate_controls = subcommands.add_parser("validate-controls")
    validate_controls.add_argument("--config", required=True, type=Path)
    validate_controls.add_argument("--controls", required=True, type=Path)
    export_controls = subcommands.add_parser("export-approved-controls")
    export_controls.add_argument("--config", required=True, type=Path)
    export_controls.add_argument("--workbook", required=True, type=Path)
    export_controls.add_argument("--controls", required=True, type=Path)
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
        if arguments.command == "build-public-series-comparison":
            normalized = arguments.workspace / "normalized"
            primary, primary_manifest, robustness, robustness_manifest, _, comparison = build_public_series_comparison(
                config,
                normalized / "market_returns_monthly.csv",
                normalized / "shiller_monthly.csv",
                arguments.controls,
                arguments.decision_policy,
            )
            write_dataset(arguments.output_dir / "crsp-market-proxy-annual.json", primary, primary_manifest)
            write_dataset(arguments.output_dir / "shiller-sp-composite-annual.json", robustness, robustness_manifest)
            write_public_series_comparison(arguments.output_dir, comparison)
            print(
                "Wrote both public reconstructions, the derived Shiller monthly table, "
                f"and aligned comparison outputs to {arguments.output_dir}."
            )
            return 0
        if arguments.command == "prepare-control-review":
            candidates = arguments.workspace / "normalized" / "political_candidates.csv"
            wikipedia_crosscheck = arguments.workspace / "normalized" / "wikipedia_congress_crosscheck.csv"
            output = arguments.output or arguments.workspace / "inputs" / "control_review_candidates.csv"
            result = prepare_control_review(config, candidates, wikipedia_crosscheck, output)
            print(f"Wrote {result['candidates']} review-only political candidates to {result['output']}.")
            return 0
        if arguments.command == "validate-controls":
            report = validate_controls_file(config, arguments.controls)
            for issue in report["issues"]:
                print(f"{issue['severity']}: {issue['check_id']} ({issue['location']}): {issue['message']}")
            print(f"Control validation found {report['errors']} error(s) and {report['warnings']} warning(s).")
            return 1 if report["errors"] else 0
        if arguments.command == "export-approved-controls":
            result = export_approved_controls(config, arguments.workbook, arguments.controls)
            print(f"Exported {result['controls']} APPROVED control interval(s) to {result['output']}.")
            return 0
    except (ConfigError, BuildError, FetchError, ReviewError, ReviewWorkbookError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    raise AssertionError(f"Unhandled command {arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
