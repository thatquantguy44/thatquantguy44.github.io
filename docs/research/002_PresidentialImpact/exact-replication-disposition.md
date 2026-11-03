# Exact-replication disposition matrix

**Purpose:** distinguish what the seed article actually documents from what this
project can reproduce. This record governs publication language; it is not a
new return calculation.

**Current disposition:** exact replication is **closed by the 2026-11-03
data-access decision**. The project will use only its currently captured public
data and reviewed controls. The public 1936–2022 package is an independent
reconstruction, not a substitute for the seed article’s 1936–2023 S&amp;P 500
analysis.

## Evidence recovered

The official Fiduciary Trust article is still available at its
[article page](https://www.fiduciarytrust.com/insights/article-detail/should-the-balance-of-power-in-washington-matter-to-investors).
On 2026-11-03, the linked Exhibit 1 image was retrieved from the publisher's
asset host and archived locally under ignored `sources/raw/`. Its SHA-256 is
`b63850e57e8555ae9ff5b1a4bfcc3435fa49c8e5204abe6a39d8e9848affcfe5`.
The image is review evidence only and is not committed or republished here.

The recovered exhibit resolves the **visible schema** for the
administration-period comparison:

- rows begin in 1973 and then occur at four-year intervals through 2021;
- the columns are balance of power, subsequent four-year cumulative total
  return for the S&amp;P 500, calculated P/E ratio (price divided by real earnings),
  and effective federal funds rate; and
- the official caption says the alignment uses January month-end data and the
  2021 S&amp;P 500 return runs through September 2024.

Those observations are source metadata, not permission to treat the visible
chart as a machine-readable source table or to reproduce it as this project’s
own figure.

## Disposition by replication target

| Target | What the source establishes | Missing requirement for an exact reproduction | Current project status | Permitted label now |
| --- | --- | --- | --- | --- |
| 1936–2023 political-configuration averages | Six narrative configurations; approximate values; annual S&amp;P 500 comparison; cited data providers are BofA Global Research, Bloomberg, and FactSet | Exact S&amp;P series and return type, annual endpoint convention, control-assignment date, chamber/tie/vacancy treatment, group membership, averaging rule, full table, and source permissions | Not reproducible | `independent public reconstruction` only |
| 2008 exclusion sensitivity | Removing 2008 moves the Republican president / Democratic Congress average from about 9% to 10.7% | Full original observation set, category membership, and exact annual-return construction | Not reproducible | Source-reported sensitivity; do not compare numerically to our output |
| Exhibit 1 administration-period comparison | Four-year schema, start-year cadence, balance-of-power labels, January alignment note, visible variables, and truncated 2021 endpoint | Machine-readable values, exact January dates, total-return series/vendor, P/E construction/vintage, effective-funds-rate series/vintage, political label rule, and partial-period convention | Partially specified; calculation not reproducible | `source-schema recovery`, not replication |
| Claim that fundamentals have a stronger association than political control | The author’s stated interpretation | A pre-defined association statistic, matched sample, specification, uncertainty method, and source values | Not a reproduced claim | Attributed author interpretation only |
| Six-to-nine-month market-leading statement | The author’s stated explanatory assertion | Supporting evidence, outcome definition, lead/lag method, and period | Outside core replication; unverified | Attributed statement only |

## Locked comparison boundary

The public research artifacts must continue to make these distinctions:

| Item | Seed article | Project’s public reconstruction |
| --- | --- | --- |
| Market series | Described as S&amp;P 500; underlying cited provider contributions are not recoverable here | CRSP-market-proxy baseline plus a labeled Shiller S&amp;P Composite robustness reconstruction |
| Annual coverage | 1936–2023 | Shared sensitivity sample: 1936–2022 |
| Political assignment | Not specified in the available source | Reviewed control record at the prior 31 December (`window_start`) |
| Output | Narrative approximate averages and an unavailable underlying chart/table | Reproducible group table, figures, source manifests, and limits |
| Interpretation | Editorial market commentary | Descriptive historical grouping only; no political causal or investable claim |

No amount of tuning the public reconstruction after seeing its results can close
these gaps. The two tracks should remain separate in the paper.

## Data-access decision and closed track

The research owner has decided that no licensed vendor data, article workbook,
or additional source acquisition will be pursued for this project. All future
analysis must use the already captured public inputs, reviewed political-control
file, and generated local outputs. Source files may be reprocessed for
reproducibility, but the project must not silently refresh to a later vintage or
substitute a newly acquired source.

Accordingly, the exact-replication track is closed rather than merely blocked.
Do not call any result `matched`, imply access to BofA/Bloomberg/FactSet data,
or present a visually similar chart as the original exhibit. If new access is
ever granted, treat it as a separately authorized research phase with a new
decision record; do not revise this project's historical status retroactively.

## Paper-ready use today

The article can now accurately say: the original article’s four-year exhibit
uses January-month-end alignment, P/E based on price divided by real earnings,
and the effective federal funds rate; however, this project intentionally uses
its separately labeled public reconstruction because the original calculation
record and licensed market inputs are outside its data-access scope. That is a
useful evidence boundary—not a shortcoming to conceal.
