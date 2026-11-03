# Inherited-conditions protocol — frozen public inputs

**Status:** protocol frozen, data construction verified, and paired descriptive
results reported on 2026-11-03. No conditional model has been fit.

**Question:** within the current public-data reconstruction, how do starting
valuation and the effective federal funds rate relate descriptively to the next
calendar-year U.S. equity return, and does adding those conditions change the
interpretation of political-control group averages?

This is an **independent public-data extension**, not a reproduction of the seed
article’s Exhibit 1 and not a causal or live-trading study.

## Data freeze and eligible sample

Only the already captured files below may be used. Do not refresh or substitute
any source for this project.

| Input | Frozen local artifact | Source capture / artifact hash | Role |
| --- | --- | --- | --- |
| Primary outcome | `market_returns_monthly.csv` and common-sample CRSP output | `FF_MKT_001` raw SHA-256 `b03d39e4bb253dda0f14893db3b78e64b40b8d6549a0fc0fd4111dae84c98618` | Nominal CRSP-market-proxy annual return |
| Robustness outcome | Shiller-derived annual output | `SHILLER_001` raw SHA-256 `0df9392b7dacf91f756e92c8db508ad903c4588b43f3253680eec3dd8b40db68` | Nominal S&amp;P Composite dividend-reinvestment-style return reconstruction |
| Starting valuation | `shiller_monthly.csv`, `cape` field | normalized SHA-256 `2166bb40f7b20005fad7481cc3be6009bcb4d29983326e95f63780c4ef80d997` | Shiller workbook valuation context |
| Starting policy rate | `policy_rates_monthly.csv`, `policy_rate_percent` | normalized SHA-256 `08f81cb4e708272a38ddf16c949505ccbb2ecca0fb92fd700de6f1ed99558d47` | FRED `FEDFUNDS` effective-federal-funds-rate context |
| Political labels | reviewed `controls.csv` | SHA-256 `210ea006674d7b9ad4bf7687c70a5be02290e3f7243ef203e574b20112d09749` | Start-date descriptive classification |

The complete shared-return sample spans 1936–2022, but the policy-rate series
starts in July 1954. The inherited-conditions sample is therefore **68 complete
annual windows, 1955–2022**. The frozen source files contain all 68 required
October 1954–October 2021 CAPE observations and policy-rate observations.

## Timing rule

For each calendar-year return labeled `Y`:

| Element | Frozen convention |
| --- | --- |
| Return outcome | 31 December `Y-1` to 31 December `Y` |
| Political classification | reviewed state on 31 December `Y-1` (`window_start`) |
| CAPE observation | 31 October `Y-1` Shiller `cape` value |
| CAPE assumed availability date | 30 November `Y-1` |
| Policy-rate observation | 1 October `Y-1` FRED monthly `FEDFUNDS` value |
| Policy-rate assumed availability date | 1 November `Y-1` |

The one-month operational availability lag means neither input is selected from
the return period or on the decision date. It is an anti-look-ahead convention,
not proof of the sources’ historical release timestamps or real-time vintages.
The preserved data may contain later revisions. Consequently, results may be
called *chronologically aligned descriptive associations* but not live
point-in-time forecasts.

The valuation definition must be displayed exactly as **“Shiller workbook CAPE
field”**. It must not be silently renamed P/E or treated as the seed article’s
calculated P/E. The rate is in percent; returns are nominal decimal returns in
calculation and displayed as percentages.

## Dataset construction requirements

Build two separate `USER_SUPPLIED` QuantMeridian datasets, each carrying the
same 1955–2022 windows, reviewed controls, and joined fundamental records:

1. CRSP-market-proxy outcome dataset — primary extension result.
2. Shiller S&amp;P Composite dividend-reinvestment-style outcome dataset —
   robustness result.

Each joined fundamental record must preserve the observation date, the assumed
availability date, valuation definition, and a source note referencing both
`SHILLER_001` and `FEDFUNDS_001` with their frozen hashes. The module requires a
single source ID per combined fundamental row, so the pipeline must add a
clearly labeled composite provenance record rather than misattribute both values
to one source.

Before any result is reviewed, verify all of the following:

- exactly 68 windows and 68 eligible valuation/rate pairs in each dataset;
- no fundamental observation or assumed availability date is later than its
  window’s decision date;
- identical windows, controls, and joined fundamentals across outcome series;
- the existing 1936–2022 political-group result remains a separate full-sample
  descriptive analysis, rather than being silently replaced by the shorter
  covariate sample; and
- QuantMeridian parser and engine validation both pass.

## Analysis sequence

1. Produce a ledger and two inherited-condition scatterplots for the primary
   1955–2022 CRSP-market-proxy dataset: CAPE versus subsequent return and rate
   versus subsequent return.
2. Reproduce the same views with the Shiller outcome reconstruction. Keep the
   results side by side; do not select the series that favors a narrative.
3. Report sample count, distinct administrations, mixed-control diagnostics,
   and the frozen timing rule next to each figure.
4. Only after those descriptive outputs are inspected, decide whether a small
   pre-specified conditional or chronological-prediction exercise is useful.
   Any such model needs a separate protocol and must not be smuggled into this
   descriptive phase.

## Explicit exclusions

This phase does not estimate a presidential causal effect, test a party-winner
strategy, claim statistical power from annual rows, reuse the source article’s
four-year values, or make a real-time forecast claim. It does not add GDP,
inflation, or any other macroeconomic variable: the current data-access decision
limits the extension to the frozen CAPE and policy-rate fields.

## Construction record and completion

The two joined datasets and their manifests were generated solely from the frozen
artifacts. QuantMeridian parser/engine checks confirmed 68 included windows and
68 eligible CAPE/rate pairs in each dataset; their first and final fundamental
records are 1954-10-31 / 1954-11-30 and 2021-10-31 / 2021-11-30,
respectively.

The paired descriptive package is complete in
[inherited-conditions-analysis](inherited-conditions-analysis/README.md): it
contains reproducible CAPE-return and policy-rate-return figures, a
source-by-source result table, and instructions to regenerate the 68-row local
ledger. It deliberately leaves political adjustment, predictive testing, and
causal interpretation out of scope.
