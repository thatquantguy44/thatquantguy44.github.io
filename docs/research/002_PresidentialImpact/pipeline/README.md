# Presidential Impact data pipeline

This is a small, standalone Python package for acquiring, preserving, checking
and assembling research inputs for the Presidential Impact project. It is not
coupled to QuantMeridian: copy this directory into another repository, install it
with `pip install -e .`, and supply a different configuration and output path.

The pipeline has four deliberate layers:

```text
explicit fetch → immutable raw files + manifest → normalized source tables
             → quality checks + reviewed political inputs → QuantMeridian JSON
```

No command fetches data implicitly. `fetch` records the URL, retrieval time,
HTTP headers and SHA-256 before any parser runs. `parse` and `build-annual` work
from those local raw files. Runtime data goes into `.local/`, which is ignored by
the research project; source code, configuration, tests and source decisions are
portable and versioned.

## Initial source policy

| ID | Role | Source | Status |
| --- | --- | --- | --- |
| `FF_MKT_001` | Long-run nominal total-return **market proxy** | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/Ken.french/data_library.html) | Implemented adapter; not an S&P 500 substitute |
| `FEDFUNDS_001` | Federal-funds-rate input | [Federal Reserve H.15](https://www.federalreserve.gov/datadownload/choose.aspx?rel=h15) via [FRED](https://fred.stlouisfed.org/series/FEDFUNDS) | Implemented adapter |
| `SHILLER_001` | Monthly valuation and S&P Composite context | [Robert J. Shiller online data](https://www.econ.yale.edu/~shiller/data.htm) | Download/archive adapter; feeds a separately labeled dividend-reinvestment-style robustness reconstruction |
| `HOUSE_GOV_001` | Congressional-party baseline | [U.S. House Party Government Since 1857](https://history.house.gov/Institution/Presidents-Coinciding/Party-Government/) | Candidate table only; reviewed controls required |
| `WIKI_CONGRESS_001` | Congress-level party-count cross-check | [Party divisions of United States Congresses](https://en.wikipedia.org/wiki/Party_divisions_of_United_States_Congresses) | SHA-256-pinned secondary snapshot; review-only |
| `CTRL_074_A` | Manual political-control evidence | Authoritative official-source bundle for the 74th Congress | Disabled from fetch/parse; available only when an approved control cites it |
| `CTRL_GOV_001` | Manual political-control evidence | Authoritative official-source bundle for the 1935–2025 control review | Disabled from fetch/parse; cited by reviewed control intervals |
| `S001` | Original seed article | [Fiduciary Trust article](https://www.fiduciarytrust.com/insights/article-detail/should-the-balance-of-power-in-washington-matter-to-investors) | Original page located; its cited proprietary annual return inputs are not acquired |

The article says its annual S&P 500 analysis uses BofA Global Research, Bloomberg
and FactSet. Those are not silently replaced. The Fama–French path is a public,
reproducible CRSP-market proxy for a separate reconstruction, with its own
`returnBasis` and source label. An exact S&P 500 replication requires licensed
series access and the article's unresolved assignment rules.

The House's published party-government table is useful for candidates, but its
own scope does not make it an exact day-level political-control history. The
pipeline therefore never invents political intervals. A researcher must approve
`inputs/controls.csv`, including dated Senate changes, ties and vacancy rules,
before analysis JSON can be built.

## Use

```sh
cd docs/research/002_PresidentialImpact/pipeline
python -m pip install -e .
# Needed only for the legacy Shiller .xls adapter.
python -m pip install -e '.[shiller]'

# Creates ignored raw/normalized/output locations and reviewable CSV templates.
presidential-data init --workspace .local

# Explicit network action; no credentials are required for the initial public sources.
presidential-data fetch --config config/sources.toml --workspace .local
presidential-data parse --config config/sources.toml --workspace .local
presidential-data validate --config config/sources.toml --workspace .local

# Produces a review-only candidate handoff. It is deliberately not valid
# controls.csv input and cannot be used to build the research dataset.
presidential-data prepare-control-review --config config/sources.toml --workspace .local

# Checks schema, intervals, allowed labels, and source IDs for any reviewed
# subset. It does not require the full 1935–2023 history yet.
presidential-data validate-controls --config config/sources.toml \
  --controls .local/inputs/controls.csv

# Reads only workbook rows marked APPROVED and writes a canonical controls.csv
# plus a replay manifest with the workbook and config hashes.
presidential-data export-approved-controls --config config/sources.toml \
  --workbook ../../../../outputs/002-presidential-impact/political_control_review_workbook.xlsx \
  --controls .local/inputs/controls.csv

# Requires researcher-reviewed controls before producing the JSON accepted by PRES.
presidential-data build-annual --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output .local/output/presidential-annual.json

# Writes the CRSP-market-proxy baseline and Shiller S&P Composite
# dividend-reinvestment-style robustness reconstruction side by side. This is
# a sensitivity analysis, not an exact S&P 500 replication.
presidential-data build-public-series-comparison --config config/sources.toml \
  --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output-dir .local/output/public-series-comparison
```

Run `python -m unittest discover -s tests -v` without a network connection. The
tests use generated fixtures and cover factor compounding, source fingerprints,
controls, response parsing and invalid data rejection.

The fetcher always verifies TLS certificates. On systems where Python lacks a
configured certificate store, it uses a standard system CA bundle when present;
set `PRESIDENTIAL_PIPELINE_CA_FILE` to a trusted bundle in another environment.

The initial public capture ran on 2026-10-31 and is retained only in the ignored
`.local/raw/` workspace, with its manifest. The project had
previously been offline-only; future captures still require an explicit fetch
action, and every result must be tied to the raw manifest before interpretation.

## Inputs and outputs

`inputs/controls.csv` uses half-open intervals and needs one row whenever the
president, House or Senate label changes. `inputs/terms.csv` is reserved for the
separate January-month-end presidential-period reconstruction; it remains empty
until the original chart's date and calculation rules are recovered.

`prepare-control-review` creates `inputs/control_review_candidates.csv` plus a
sidecar manifest. It narrows the House's Congress-year candidates to the annual
sample, then adds the Wikipedia snapshot's published party-count strings and
within-Congress variation hint for the same Congress. It is intentionally not
schema-compatible with `controls.csv`: verify dated intervals, presidential
identity, House/Senate changes, ties and vacancies before creating controls.

`validate-controls` is the promotion gate for approved rows: it validates their
schema, overlap rules, party labels, and source IDs. A control must cite a
catalog entry whose role is `manual_reviewed_political_control_evidence`; a
candidate or secondary cross-check cannot be promoted. It does not claim that a
partial file supplies every annual decision date;
`build-annual` performs that full-coverage check.

`export-approved-controls` makes the review workbook the source of truth for the
local controls file. It rejects unapproved rows, missing primary-source
locators/evidence notes/reviewer fields/timestamps, malformed values,
overlapping intervals, and ineligible source IDs. The generated
`controls.manifest.json` records the workbook and config hashes, controls hash,
and row-level review evidence used in the promotion. The annual replay manifest
then links that promotion manifest, review workbook, parsed-market status, and
raw fetch manifest when those artifacts are available.

`output/presidential-annual.json` follows the local JSON contract consumed by the
QuantMeridian PRES module. It contains no source data acquired by the module and
is always marked `USER_SUPPLIED` until an analyst independently verifies it.
Its `sources` records use the strict PRES shape (`id`, `title`, `locator`,
`note`); manual-bundle locators and content hashes remain inspectable inside the
source note and the replay manifest rather than adding incompatible JSON fields.

`build-public-series-comparison` writes the full baseline,
`crsp-market-proxy-annual.json`; an explicitly aligned baseline,
`crsp-market-proxy-common-sample-annual.json`; and the
`shiller-sp-composite-annual.json` robustness dataset, each with a replay
manifest. It also writes an aligned annual CSV/JSON comparison and the
intermediate `normalized/shiller_total_return_monthly.csv`. Use the
common-sample baseline—not the longer full baseline—for any side-by-side figure
or political group table. The Shiller construction is documented in the project-level
[public-series methodology](../public-series-methodology.md); it is prevented
from silently becoming the primary CRSP proxy by a source-ID gate.

Using the frozen local Shiller CAPE and FRED `FEDFUNDS` files, the same command
also writes `crsp-market-proxy-inherited-conditions-annual.json` and
`shiller-sp-composite-inherited-conditions-annual.json`, with separate replay
manifests, plus `inherited-conditions-join-audit.json` and a 68-row paired
`inherited-conditions-ledger.csv`. These are the 1955–2022 extension datasets,
not replacements for the 1936–2022 political-comparison datasets. Their timing,
one-month assumed-availability lag, and source-vintage limitation are frozen in
the [inherited-conditions protocol](../inherited-conditions-protocol.md).

The same command also writes `presidential-cycle-ledger.csv` and
`presidential-cycle-summary.json`. These provide a supplementary 1937–2022
four-year term-cycle view: every return is assigned to the president in office
on its calendar year's December 31, and every first-cycle-year observation is
flagged as an inauguration-transition window. The output preserves a separate
`presidentChangedWithinWindow` flag for successions. It is a display sensitivity
only: it does not replace the frozen `window_start` political-configuration
assignment. See the [cycle protocol](../presidential-cycle-protocol.md).

See [source decisions](SOURCE_DECISIONS.md), [quality rules](QUALITY.md), and
[the transfer guide](TRANSFER.md).
