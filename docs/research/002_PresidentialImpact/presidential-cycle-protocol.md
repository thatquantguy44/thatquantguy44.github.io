# Presidential four-year cycle protocol

**Protocol ID:** `PID-CYCLE-001`
**Status:** frozen supplementary descriptive display
**Inputs:** existing captured public inputs and reviewed local controls only

## Purpose

Show each annual return in the regular four-year presidential term cycle in two
consistent ways:

1. **All-four-years view.** Assign every calendar-year return to the president
   in office on that return year's December 31, then place the return in cycle
   year 1, 2, 3, or 4.
2. **Inauguration-transition view.** Show the exact same return observations
   and assignment, but visibly flag every cycle-year-1 return. The flag records
   that the new regular term does not begin until January 20.

This is a presentation and interpretation safeguard, not a new test of a
political effect. The primary political-control analysis continues to use the
frozen `window_start` assignment defined in
[PID-SERIES-001](public-series-methodology.md).

## Eligibility and time convention

The Twentieth Amendment moved the beginning of a President's regular term to
noon on January 20. The cycle ledger therefore begins in **1937**, the first
such regular term in the project sample. The 1936 annual return is excluded
rather than retrofitted to a rule that did not govern it. The official
[National Archives record of the Twentieth Amendment](https://www.archives.gov/electoral-college/provisions)
is the authority for that term-date convention.

For an annual return in calendar year `Y`:

```text
termStartYear = Y - ((Y - 1) mod 4)
termCycleYear = Y - termStartYear + 1
party/president = reviewed control record in force on Y-12-31
inaugurationTransition = (termCycleYear == 1)
presidentChangedWithinWindow = president at prior Dec. 31 != president at Y-12-31
```

The term-cycle designation is regular/electoral, not a claim that every
individual president served a full four-year term. The separate
`presidentChangedWithinWindow` flag preserves deaths, resignations, successions,
and other changes in the supplied control history.

## Fixed sample and outcomes

The package uses the aligned 1936–2022 public-series comparison, after which
the pre-1937 observation is excluded. The resulting display sample has:

| Item | Value |
| --- | ---: |
| Calendar-return years | 1937–2022 |
| Annual return observations | 86 |
| Cycle-year-1 inauguration-transition observations | 22 |
| Windows with a president change between annual endpoints | 14 |
| Excluded pre-January-20 observation | 1936 |

Each observation carries both frozen public return constructions:

- **Public CRSP-market-proxy baseline:** compounded Kenneth French `Mkt-RF + RF`.
- **Shiller S&P Composite dividend-reinvestment-style robustness reconstruction:**
  the documented project approximation, not an official S&P 500 total-return
  index.

No source is fetched, refreshed, or added for this package.

## Display rules

The figures show D and R only as the reviewed party field of the president in
office at December 31. A vertical segment is the observed minimum-to-maximum
range in that party/cycle cell; a diamond is its arithmetic mean. The figures
disclose counts and keep both market constructions side by side. The ledger
retains every annual outcome and its associated best/worst observation.

The inauguration-transition treatment changes **no value, count, party label,
or mean**. It highlights cycle year 1 with a neutral background. It is
deliberately distinct from actual within-window president changes: some
cycle-year-1 windows are an inauguration date transition even when the same
president was re-elected.

## Interpretation boundary

- Do not call the views a presidential effect, policy exposure estimate,
  forecast, backtest, or trading rule.
- Do not compare them with the primary `window_start` political table as though
  they are competing causal assignments; they answer different descriptive
  questions.
- Do not treat annual rows as independent presidential observations. Party and
  cycle cells have 10–12 annual rows and repeated administrations.
- Report both public return constructions and the full underlying ledger when
  discussing a cell's average, range, or best/worst year.

## Reproduce

The portable pipeline command below writes the ignored local ledger and JSON
summary used by the publication figures:

```sh
cd docs/research/002_PresidentialImpact/pipeline
PYTHONPATH=src .local/.venv/bin/python -m presidential_data_pipeline.cli \
  build-public-series-comparison \
  --config config/sources.toml \
  --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output-dir .local/output/public-series-comparison
```

The generated files are:

- `.local/output/public-series-comparison/presidential-cycle-ledger.csv`
- `.local/output/public-series-comparison/presidential-cycle-summary.json`

The static figures and their source-by-source reading guide are in
[presidential-cycle-analysis](presidential-cycle-analysis/README.md).
