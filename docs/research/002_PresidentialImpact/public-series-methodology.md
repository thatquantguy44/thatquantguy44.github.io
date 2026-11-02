# Public market-series decision and robustness protocol

**Decision ID:** `PID-SERIES-001`

**Status:** frozen before reviewing the comparison output

**Applies to:** the 1936–2023 descriptive Presidential Impact reconstruction

## Decision

Use two explicitly different public reconstructions side by side:

| Role | Series | What it is | What it is not |
| --- | --- | --- | --- |
| Primary baseline | Kenneth R. French monthly `Mkt-RF + RF` | A long-run nominal, value-weighted CRSP U.S. market total-return proxy | The S&P 500 or the seed article's proprietary annual input |
| Robustness check | Shiller `P` and `D` columns | A nominal S&P Composite, dividend-reinvestment-style reconstruction | An official S&P 500 total-return index |

The comparison is a sensitivity check for whether high-level descriptive patterns are tied to a particular broad-equity construction. It is not an exact replication of the seed article and does not identify a causal political effect.

## Source and access policy

`FF_MKT_001` is the public Kenneth R. French Data Library monthly factor file. Its `Mkt-RF` series is the value-weighted return of CRSP firms less the one-month Treasury-bill rate; the pipeline adds `RF` back before compounding. The library provides monthly observations from July 1926, which covers every required annual endpoint.

`SHILLER_001` is the official Robert J. Shiller Yale workbook, retained as a hash-pinned raw capture. The pipeline uses its nominal price (`P`) and dividend (`D`) fields, never its real-price or CAPE values, for the return construction. `D` is a trailing annual dividend measure rather than a published monthly cash distribution. The reconstruction is therefore deliberately named an *approximation*:

\[
r_t = \frac{P_t + D_t/12}{P_{t-1}} - 1.
\]

The formula allocates the current source dividend measure evenly over twelve months and compounds the resulting monthly observations. It is transparent and reproducible, but not a substitute for a vendor-maintained S&P total-return index.

The runner requires a complete December observation with a published `D` value.
If the official workbook has a partially populated trailing year, the robustness
series and the aligned comparison stop at the prior complete December. It records
the source's last context date and every excluded incomplete-dividend month in
the comparison JSON rather than imputing a dividend or carrying the value forward.

FRED's `SP500` series is deliberately excluded from the long-run comparison. It is a daily, price-only S&P 500 close with a limited history, so it cannot support a 1936–2023 total-return study. It remains acceptable only as a recent-period price-level spot check. Exact S&P 500 total-return replication requires appropriately licensed index or terminal data.

## Shared conventions

- **Annual window:** prior December month-end through current December month-end. For example, the 1936 window is 1935-12-31 to 1936-12-31.
- **Political assignment:** `window_start`; each annual return is assigned from the reviewed political-control record active on the prior December 31 decision date.
- **Nominal return:** both public reconstructions are nominal. No inflation adjustment, transaction cost, tax, or investability assumption is introduced.
- **Data status:** every input is content-hashed in a replay manifest. Raw source captures and generated analysis outputs remain local/ignored; the code, config, and methodology are versioned.
- **Comparison unit:** one aligned annual observation per calendar year, followed by descriptive full-sample and political-configuration summaries. No p-values, causal claims, or model-selection rule is implied.

## Reproducible command

After fetching/parsing the public sources and exporting approved controls, run:

```sh
cd docs/research/002_PresidentialImpact/pipeline
PYTHONPATH=src python3 -m presidential_data_pipeline.cli build-public-series-comparison \
  --config config/sources.toml \
  --workspace .local \
  --controls .local/inputs/controls.csv \
  --output-dir .local/output/public-series-comparison \
  --decision-policy window_start
```

The command writes:

- `.local/normalized/shiller_total_return_monthly.csv` — the labeled, derived monthly robustness input;
- `crsp-market-proxy-annual.json` and `shiller-sp-composite-annual.json` — separate QuantMeridian-compatible datasets and manifests; and
- `public-series-comparison.csv` and `.json` — aligned annual observations plus summary statistics.

The baseline can extend beyond the robustness series when the official Shiller
workbook has a partially populated trailing year. Read `overlap` and
`robustness_source_completeness` in the JSON before comparing any group summary.

## Publication language guardrail

Use: “the public CRSP-market-proxy baseline and a Shiller S&P Composite dividend-reinvestment-style robustness reconstruction.”

Do not use: “S&P 500 total return,” “replication,” “proved,” “caused,” or “durable alpha” for these outputs.

## Primary references

- [Kenneth R. French Data Library, Fama/French factors](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html)
- [Robert J. Shiller online data](https://www.econ.yale.edu/~shiller/data.htm)
- [FRED S&P 500 (`SP500`) metadata](https://fred.stlouisfed.org/series/SP500)
- [S&P Dow Jones Indices licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing/)
