# Run Presidential Impact in QuantMeridian

The module lives in the existing `market_terminal` repository. Start its normal
development server using the dependencies already installed:

```sh
cd "/Users/joshualutkemuller/Documents/Quant Sandbox/platforms/market_terminal"
npm run dev
```

Open the local URL printed by Vite and select **PRES — Presidential Impact**
under Markets, or append `/presidential-impact` to that URL. The default is
`http://localhost:5173/presidential-impact`; Vite may choose another free port.
The module is enabled through the existing module configuration.

1. Choose **Load illustrative dataset** to exercise the workflow. Every number
   and political interval in that example is fictional.
2. Download the JSON template; replace its observations, intervals, windows and
   source metadata with your admitted research inputs. Set `kind` to
   `USER_SUPPLIED` only after replacing the fictional content. This label does
   not verify the data. Follow [the contract](DATA_CONTRACT.md).
3. Import the local JSON file (maximum 5 MiB). Choose annual or presidential
   periods, cumulative or annualized returns, and endpoint/partial-window rules.
   Inspect the ledger and missing-data explanations before interpreting a chart.
4. Compare a separate 2008/custom-year exclusion against the retained full sample.
   Presidential sensitivities remove whole overlapping periods.
5. Add your own interpretation in the author-opinion field. Download CSV and the
   run manifest, plus SVG or PNG figures for the report. Export the sensitivity
   manifest separately if used.

Inputs and notes are browser-memory only; refreshing or leaving the page clears
them. Export the manifest to preserve the normalized dataset, configuration,
calculations, sources and commentary for replay. Its local timestamp and hashes
are not independent source verification. Preserve the module source as well:
the embedded code revision and raw-upload hash are explicitly unknown.

No provider credentials or live data are needed for this workflow. Existing
terminal-wide services may display unavailable statuses when unconfigured; the
PRES calculation engine uses only the dataset you explicitly load.

The module does not yet acquire historical data, reproduce the seed article,
fit conditional models, estimate uncertainty or test forecasts. Those remain
research work, described in `docs/research/002_PresidentialImpact/research-brief.md`
in the research repository. The original article's missing exhibit and conventions remain the
next source-admission dependency.
