# Initial public-series robustness run

**Run scope:** descriptive market-series sensitivity only

**Methodology:** [`PID-SERIES-001`](public-series-methodology.md)

**Decision policy:** `window_start`

**Result status:** usable for planning and source-selection discussion; not an S&P 500 replication or causal political finding

## Replayed inputs

The local run used the reviewed political-control file and public-source raw
manifest recorded by the portable pipeline. The two dataset replay manifests
record the exact inputs and output hashes. The generated files remain in the
ignored local workspace:

- `.local/output/public-series-comparison/crsp-market-proxy-annual.manifest.json`
- `.local/output/public-series-comparison/shiller-sp-composite-annual.manifest.json`
- `.local/output/public-series-comparison/public-series-comparison.json`

The run used `FF_MKT_001` for the CRSP-market-proxy baseline and `SHILLER_001`
for the alternative reconstruction. It did not acquire the seed article's
licensed BofA, Bloomberg, FactSet, or official S&P index inputs.

## Aligned 1936–2022 result

| Measure | Result |
| --- | ---: |
| Annual observations | 87 |
| CRSP-market-proxy arithmetic mean | 12.15% |
| Shiller reconstruction arithmetic mean | 12.03% |
| Mean difference (Shiller minus CRSP proxy) | -0.12 percentage points |
| Median difference (Shiller minus CRSP proxy) | +0.47 percentage points |
| Pearson correlation of annual returns | 0.980 |

The two public constructions move closely over the aligned sample, but they do
not coincide. This supports reporting the source construction as a sensitivity
dimension, not selecting whichever series best supports a political narrative.

## Coverage disposition

The CRSP-proxy baseline has annual windows through 2023. The current official
Shiller workbook capture has context through 2023-09-30, but its trailing
dividend field is blank from 2023-07-31 through 2023-09-30. Because a complete
2023 dividend-return observation cannot be constructed without imputing those
values, the robustness output and aligned comparison end on 2022-12-31. The
comparison JSON explicitly records the three excluded months.

Do not present the 87-observation comparison as a 1936–2023 analysis, and do
not fill the 2023 dividend values, splice a vendor index, or use the 2023 CRSP
value when comparing the two series.

## Next use in the write-up

Use this result in a small “series choice” methods panel. Any political-control
group table or figure should show both series on this shared 1936–2022 sample,
state group counts, and retain the 2023 CRSP-only observation as out of the
robustness comparison.
