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
6. [Inherited-conditions results](inherited-conditions-analysis/README.md) — paired figures, source-by-source table, ledger contract, and interpretation boundary.
7. [Initial public-series run](public-series-comparison-run.md) — actual shared-sample result and coverage disposition.
8. [Pipeline source decisions](pipeline/SOURCE_DECISIONS.md) — source authority, political-control review, and exact-replication gap.
9. [QuantMeridian PRES handoff](quantmeridian-module/HANDOFF.md) — application workflow and local import contract.

## Completed, verified work

| Area | Completion status | Durable location |
| --- | --- | --- |
| Research framing, limitations, and contribution plan | Complete for the current public-data phase | `research-brief.md` |
| Political-control review | Complete for the 1935–2023 annual decision dates; manual evidence is cited per interval | ignored `.local/inputs/controls.csv` plus its promotion manifest |
| Public CRSP-market-proxy baseline | Complete for 1936–2023 | `FF_MKT_001`; generated locally |
| Shiller S&P Composite robustness construction | Complete with explicit `P`/`D` formula and no-imputation cutoff | `SHILLER_001`; generated locally |
| Aligned comparison | Complete for 1936–2022, 87 annual observations | ignored `.local/output/public-series-comparison/` |
| Common-sample baseline | Complete; CRSP baseline is separately rebuilt through 2022 before group comparison | `crsp-market-proxy-common-sample-annual.json`; generated locally |
| QuantMeridian compatibility | All five generated datasets passed parser validation; the two inherited-condition datasets also passed engine validation | the three baseline variants plus two 1955–2022 inherited-condition datasets |
| Frozen political-configuration package | Complete; paired table, two portable figures, and interpretation boundary | `descriptive-analysis/README.md` |
| Seed Exhibit 1 schema recovery | Complete; publisher chart image archived locally and visible fields/timing documented without reusing the chart | `exact-replication-disposition.md` and ignored `sources/raw/` |
| Inherited-conditions descriptive package | Complete; paired 1955–2022 CAPE/rate figures, source-separated results table, and 68-row local ledger | `inherited-conditions-analysis/README.md` and ignored `.local/output/public-series-comparison/` |
| Pipeline verification | Offline test suite passes 28 tests; workspace validation has 0 errors and documented Shiller trailing-dividend warnings | `pipeline/tests/` and `.local/quality/report.json` |

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

### 1. Draft the director-facing research note from the completed packages

Use the political-configuration package and the inherited-conditions package as
separate, clearly labeled public reconstructions. Explain the seed article's
claim as a research lead, report the completed descriptive evidence without
overstating it, then add a distinct author-opinion section. The note should make
the data-access boundary and exact-replication closure prominent rather than
burying it in a footnote.

**Acceptance criterion:** every figure and numerical statement identifies
whether it comes from the seed article, the local public reconstruction, or the
newly documented inherited-conditions extension; conclusions follow only from
the stated evidence.

### 2. Decide whether a conditional or chronological-prediction exercise is justified

Do not begin an adjusted political model by default. First decide whether it
would add decision-relevant insight beyond the descriptive note, given 13
administrations, revised historical values, and the frozen CAPE/rate inputs. If
the answer is yes, create a new pre-specified protocol with outcome, timing,
comparators, uncertainty treatment, and a no-claim stopping rule.

**Acceptance criterion:** either a narrowly scoped protocol is approved before
any model output is inspected, or the handoff records the explicit choice to
stop at descriptive analysis.

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

## Reproduce the frozen public comparison

From the website repository:

```sh
cd docs/research/002_PresidentialImpact/pipeline
python3 -m venv .local/.venv
.local/.venv/bin/python -m pip install -e '.[shiller]'

# The controls file is a reviewed local artifact; do not regenerate it from
# candidate sources without completing the review process.
.local/.venv/bin/python -m presidential_data_pipeline.cli build-public-series-comparison \
  --config config/sources.toml \
  --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output-dir .local/output/public-series-comparison
```

Do not run `fetch` or substitute a new source in the current phase. The
data-access decision permits only the already captured local inputs. A future
refresh or licensed-data phase requires separate authorization and a new
research record.

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
