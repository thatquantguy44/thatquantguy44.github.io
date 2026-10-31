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
| `SHILLER_001` | Monthly valuation and S&P Composite context | [Robert J. Shiller online data](https://www.econ.yale.edu/~shiller/data.htm) | Download/archive adapter; parser is an optional `xlrd` extra |
| `HOUSE_GOV_001` | Congressional-party baseline | [U.S. House Party Government Since 1857](https://history.house.gov/Institution/Presidents-Coinciding/Party-Government/) | Candidate table only; reviewed controls required |
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
presidential-data validate --workspace .local

# Requires researcher-reviewed controls before producing the JSON accepted by PRES.
presidential-data build-annual --workspace .local \
  --controls .local/inputs/controls.csv \
  --decision-policy window_start \
  --output .local/output/presidential-annual.json
```

Run `python -m unittest discover -s tests -v` without a network connection. The
tests use generated fixtures and cover factor compounding, source fingerprints,
controls, response parsing and invalid data rejection.

The fetcher always verifies TLS certificates. On systems where Python lacks a
configured certificate store, it uses a standard system CA bundle when present;
set `PRESIDENTIAL_PIPELINE_CA_FILE` to a trusted bundle in another environment.

The initial four-source public capture ran on 2026-10-31 and is retained only in
the ignored `.local/raw/` workspace, with its manifest. The project had
previously been offline-only; future captures still require an explicit fetch
action, and every result must be tied to the raw manifest before interpretation.

## Inputs and outputs

`inputs/controls.csv` uses half-open intervals and needs one row whenever the
president, House or Senate label changes. `inputs/terms.csv` is reserved for the
separate January-month-end presidential-period reconstruction; it remains empty
until the original chart's date and calculation rules are recovered.

`output/presidential-annual.json` follows the local JSON contract consumed by the
QuantMeridian PRES module. It contains no source data acquired by the module and
is always marked `USER_SUPPLIED` until an analyst independently verifies it.

See [source decisions](SOURCE_DECISIONS.md), [quality rules](QUALITY.md), and
[the transfer guide](TRANSFER.md).
