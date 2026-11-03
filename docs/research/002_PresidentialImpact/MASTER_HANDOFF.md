# Master handoff — 002 Presidential Impact

**Use this document as the starting point for the next agent or research session.**

## Mission and current boundary

The project asks whether political-control labels add useful descriptive,
explanatory, or predictive information about U.S. equity returns beyond the
conditions an administration inherits. The seed article is a research lead, not
validated evidence. The work must clearly separate:

1. an exact reproduction of the article, if its inputs and definitions can be
   acquired;
2. the completed public-data reconstruction and robustness analysis; and
3. the author's own interpretation.

The current public-data work is **not** an S&P 500 total-return replication and
must never be presented as one or as evidence that political control causes
returns.

## Read this first

1. [Research brief](research-brief.md) — scope, article structure, and research sequence.
2. [Public-series methodology](public-series-methodology.md) — frozen source, return, window, and language rules.
3. [Frozen descriptive analysis](descriptive-analysis/README.md) — paired political-configuration results, figures, and interpretation boundary.
4. [Exact-replication disposition matrix](exact-replication-disposition.md) — recovered exhibit schema, missing inputs, and stopping rule.
5. [Inherited-conditions protocol](inherited-conditions-protocol.md) — frozen inputs, timing, sample, and no-look-ahead rules for the active extension.
6. [Initial public-series run](public-series-comparison-run.md) — actual shared-sample result and coverage disposition.
7. [Pipeline source decisions](pipeline/SOURCE_DECISIONS.md) — source authority, political-control review, and exact-replication gap.
8. [QuantMeridian PRES handoff](quantmeridian-module/HANDOFF.md) — application workflow and local import contract.

## Completed, verified work

| Area | Completion status | Durable location |
| --- | --- | --- |
| Research framing, limitations, and contribution plan | Complete for the current public-data phase | `research-brief.md` |
| Political-control review | Complete for the 1935–2023 annual decision dates; manual evidence is cited per interval | ignored `.local/inputs/controls.csv` plus its promotion manifest |
| Public CRSP-market-proxy baseline | Complete for 1936–2023 | `FF_MKT_001`; generated locally |
| Shiller S&P Composite robustness construction | Complete with explicit `P`/`D` formula and no-imputation cutoff | `SHILLER_001`; generated locally |
| Aligned comparison | Complete for 1936–2022, 87 annual observations | ignored `.local/output/public-series-comparison/` |
| Common-sample baseline | Complete; CRSP baseline is separately rebuilt through 2022 before group comparison | `crsp-market-proxy-common-sample-annual.json`; generated locally |
| QuantMeridian compatibility | All three generated datasets passed `parseResearchDataset` validation | `annual-crsp-market-proxy-1936-2023`, `annual-crsp-market-proxy-1936-2022`, and `annual-shiller-sp-composite-approximation-1936-2022` |
| Frozen political-configuration package | Complete; paired table, two portable figures, and interpretation boundary | `descriptive-analysis/README.md` |
| Seed Exhibit 1 schema recovery | Complete; publisher chart image archived locally and visible fields/timing documented without reusing the chart | `exact-replication-disposition.md` and ignored `sources/raw/` |
| Inherited-conditions data construction | Complete; two 1955–2022 joined datasets have 68 eligible CAPE/rate pairs and passed PRES parser/engine checks | ignored `.local/output/public-series-comparison/` and `inherited-conditions-protocol.md` |
| Pipeline verification | Offline test suite passes; workspace validation has 0 errors and documented Shiller trailing-dividend warnings | `pipeline/tests/` and `.local/quality/report.json` |

## Current empirical checkpoint

On the common 1936–2022 sample:

| Measure | Value |
| --- | ---: |
| Observations | 87 annual returns |
| CRSP-market-proxy mean | 12.15% |
| Shiller approximation mean | 12.03% |
| Mean difference, Shiller minus CRSP proxy | -0.12 percentage points |
| Correlation | 0.980 |

Interpretation: the two constructions are close enough that series choice must
be reported as a sensitivity, not selected opportunistically. The completed
political configuration table preserves the same ordering across both series,
but it remains descriptive: its small, dependent administration groups and
mixed-control windows cannot identify a political effect.

The configured official Shiller workbook returns price context through
2023-09-30 but no published trailing dividend from 2023-07-31 onward. The
pipeline therefore stops the dividend-return robustness series at the last
complete December, 2022-12-31. It never fills dividends, carries values forward,
or compares the CRSP-only 2023 observation with the shorter series.

## Next division of work — priority order

### 1. Produce paired inherited-conditions descriptives from the frozen public inputs

The exact-replication track is closed by the data-access decision recorded in
the [exact-replication matrix](exact-replication-disposition.md). The two
joined 1955–2022 datasets now exist and passed parser/engine checks. Use only
those frozen artifacts to generate the paired CAPE-return and policy-rate-return
scatterplots, ledgers, and a compact source-by-source result table. Do not fit a
model or inspect a political adjustment before this descriptive package is
complete.

**Acceptance criterion:** every covariate has a source, date, availability date,
definition, and limitation; the number of administrations, rather than rows, is
prominent in any uncertainty discussion.

### 2. Draft the director-facing research note after the inherited-conditions scope is frozen

Use the frozen descriptive analysis as one clearly labeled section. Separate
the seed article's result, the public reconstruction, and the author's opinion;
do not allow a chart from the public reconstruction to stand in for the
unrecovered source analysis.

**Acceptance criterion:** every figure and numerical statement identifies
whether it is from the seed article, the local public reconstruction, or a
newly documented extension.

### 3. Keep the exact-replication record closed

Do not request, buy, or add new sources for this project. Reprocess only the
existing captured data when verification requires it; retain its hashes and
vintages. Any future licensed-data work is a new, explicitly authorized phase.

## Non-negotiable research controls

- Call the primary series **“public CRSP-market-proxy baseline”**, never S&P 500.
- Call the second series **“Shiller S&P Composite dividend-reinvestment-style robustness reconstruction.”**
- Use the shared 1936–2022 sample for any side-by-side comparison. Do not
  impute Shiller dividends or add 2023 to only one series' group comparison.
- Keep annual assignment at `window_start` unless a new pre-results decision
  record authorizes a sensitivity. The annual return for year `Y` starts on the
  prior December 31.
- Preserve `CTRL_074_A` / `CTRL_GOV_001` as manual reviewed control evidence;
  House candidates and Wikipedia rows remain review-only cross-checks.
- Do not call resampling ranges causal confidence intervals, use row count as
  independent presidential observations, or assert durable alpha.
- Keep raw downloads, normalized CSVs, generated JSON, and local review
  workbooks out of Git. They belong in ignored `pipeline/.local/` with replay
  manifests.

## Reproduce or refresh the public comparison

From the website repository:

```sh
cd docs/research/002_PresidentialImpact/pipeline
python3 -m venv .local/.venv
.local/.venv/bin/python -m pip install -e '.[shiller]'

# Network is explicit; fetch only after deciding a new capture is appropriate.
.local/.venv/bin/python -m presidential_data_pipeline.cli fetch \
  --config config/sources.toml --workspace .local
.local/.venv/bin/python -m presidential_data_pipeline.cli parse \
  --config config/sources.toml --workspace .local
.local/.venv/bin/python -m presidential_data_pipeline.cli validate \
  --config config/sources.toml --workspace .local

# The controls file is a reviewed local artifact; do not regenerate it from
# candidate sources without completing the review process.
.local/.venv/bin/python -m presidential_data_pipeline.cli build-public-series-comparison \
  --config config/sources.toml \
  --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output-dir .local/output/public-series-comparison
```

If the Shiller source changes, preserve the new raw manifest and compare the
new source hash, latest complete dividend December, output hashes, and common
sample with the prior run before replacing the research record.

## Environment and repository map

- **Website/research repository:** this repository; current work is on
  `002-presidential-impact-finalization`.
- **QuantMeridian repository:** from this repository root,
  `../../platforms/market_terminal`; its PRES module imports one local JSON
  dataset at a time. Do not mix its unrelated branch work into this research
  commit without a scoped review.
- **Ignored runtime workspace:** `pipeline/.local/`. It contains raw captures,
  normalized tables, reviewed controls, output JSON/CSV, quality reports, and
  optional local virtual environment.

## Clean handoff checklist

Before ending a future session, record:

1. the branch and commit used;
2. every raw-source hash and retrieval timestamp changed;
3. the controls-manifest hash used;
4. dataset and comparison-manifest hashes;
5. commands/tests run and their results; and
6. any conclusion that became invalid because sources, time window, or rules
   changed.

If a future task requires authority to purchase/licence data, recruit external
participants, or publish conclusions, stop and request that authority rather
than assuming it.
