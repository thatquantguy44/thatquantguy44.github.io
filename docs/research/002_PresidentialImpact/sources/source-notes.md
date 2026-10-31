# Presidential Impact — seed-source record

## S001

- **Title:** *Should the balance of power in Washington matter to investors?*
- **Publisher/byline in supplied text:** Fiduciary Trust International; Carin Pai, CFA, Head of Equities.
- **Publication date in supplied text:** October 16, 2024.
- **Material received:** user-pasted page text; no PDF was supplied.
- **Original URL:** [official Fiduciary Trust page](https://www.fiduciarytrust.com/insights/article-detail/should-the-balance-of-power-in-washington-matter-to-investors), located on October 31, 2026. The local raw archive remains the user-supplied paste.
- **Local archive:** an exact copy is retained under ignored `raw/`; the [metadata record](S001-source.json) contains its SHA-256.
- **Missing material:** chart image/data, downloadable PDF, full calculation definitions and underlying series.
- **Verification status:** unverified seed. No numerical claim is admitted as our finding.

The official page confirms the annual 1936–2023 S&P 500 comparison is attributed
to BofA Global Research, Bloomberg and FactSet. It describes Exhibit 1 as a
January-month-end calculation and cites Robert J. Shiller and the Board of
Governors of the Federal Reserve System; the 2021 return extends through
September 2024. These are source leads, not data already obtained or a claim
that access or redistribution rights have been established.

## Propositions and checks

| Seed proposition | Required check before reuse |
| --- | --- |
| Historical average annual returns differ across political-control configurations | Recover the actual table, return convention, assignment rules, sample membership and uncertainty |
| Starting valuations and policy rates have a stronger association with investment performance | Recover the missing exhibit and test the comparison on explicitly matched units and windows; a visual association is not causal identification |
| Excluding 2008 changes one category's average | Preserve the full sample and apply a consistent, prespecified sensitivity across all categories |
| A presidential-period exhibit uses January month-end alignment | Recover start/end dates, return construction and the treatment of partial terms rather than treating annual and term statistics as interchangeable |
| Markets lead economic conditions by an approximate horizon | Recover supporting evidence and definitions; do not use the unsourced sentence as an established forecasting rule |

The annual comparison covers 1936–2023 according to the text. The separate
presidential-period discussion refers to the last five decades without supplying
the full exhibit. Its caption labels a 2021 return while extending measurement
through September 2024; the original chart is needed to interpret this correctly.

Later related links and a 2026 footer are page chrome, not evidence that the
October 2024 analysis was updated. The raw paste is kept locally rather than
republished in the repository.

## Data-pipeline source plan

[The portable pipeline](../pipeline/README.md) now records public-source adapters,
raw-file provenance, quality checks and reviewed-control requirements. It supports
a transparent public CRSP-market proxy through the Fama–French Data Library,
but does not label that proxy as an S&P 500 replication. It also stages Shiller,
Federal Reserve/FRED and House historical sources for the separate inherited-
conditions analysis.

The House party-government chart is Congress-level; its own methodology does not
replace dated Senate changes, ties or vacancy policy. The pipeline emits it as a
review candidate and requires a researcher-approved combined-control file.

## Next source work

Capture the linked chart/PDF if available, recover the annual source table and
assignment rules, and select a licensed S&P 500 series if exact replication is
the goal. Any reproduced number, substitute dataset, derived calculation or
interpretive judgment should have a separate, inspectable record.
