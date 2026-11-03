# Source decisions

## Research question and grain

The annual reconstruction's outcome unit is a calendar return ending on December
31. The political assignment date is not assumed: `build-annual` requires an
explicit, dated control interval supplied in `inputs/controls.csv`. The separate
presidential-period exhibit uses January month-end data according to the original
article, but its exact window/return rules are not yet recovered, so no term
output is generated.

## Controlling-source decisions

The Fiduciary Trust article, located at the URL recorded in the pipeline README,
states that its 1936–2023 annual S&P 500 results use BofA Global Research,
Bloomberg and FactSet. Those are the controlling inputs for an exact replication.
They are unavailable in this project. Do not call a reconstruction based on the
Fama–French public file an S&P 500 replication.

The public Fama–French adapter compounds monthly `Mkt-RF + RF`, in percent, to a
nominal total-return index. It is a CRSP-derived broad US common-stock market
proxy and can support a transparent alternative analysis. It is not the article's
index or necessarily its annual return methodology.

`PID-SERIES-001` freezes the public-series comparison before its results are
reviewed. The Fama–French reconstruction is the primary public baseline. A
separate Shiller S&P Composite dividend-reinvestment-style approximation is a
robustness input only: it compounds `(P_t + D_t/12) / P_(t-1) - 1`, where `D` is
the workbook's trailing annual dividend field. This is not an official S&P 500
total-return index. The full definitions, labels, command and publication
guardrails are in `../public-series-methodology.md`.

FRED's public `SP500` series is excluded from this long-run comparison: it is a
daily, price-only series with limited history. It may be used only as a recent
price-level cross-check. Exact S&P 500 total-return reproduction requires a
licensed series with an explicit permitted-use decision.

The original article says its presidential-period exhibit uses Robert Shiller and
the Board of Governors of the Federal Reserve System. The Shiller source exposes
monthly S&P Composite price/dividend/earnings and valuation context. The FRED
adapter obtains the monthly federal-funds series with source metadata. Both are
inputs to a prospective reconstruction, not proof that their resulting values
match the missing exhibit.

On 2026-10-31, the official Yale Shiller host refused HTTPS but served the same
official file over HTTP. The catalog consequently records the HTTP endpoint
explicitly rather than silently using a third-party mirror. That transport is
not confidential or authenticated; the pipeline records the retrieved payload's
SHA-256, timestamp, and response metadata, and any production or publication
use should independently review the retained file before relying on it.

The House party-government chart supplies a Congress-level baseline. Its own
notes distinguish party composition from later changes; the Senate's official
party division history reports intra-Congress changes. The pipeline therefore
stores a House-derived candidate table, requires human-reviewed combined control
intervals, and preserves `UNKNOWN`/`TIED` rather than inferring a majority.

`prepare-control-review` narrows those candidates to the Congress-year records
that overlap the annual reconstruction's December 31 decision dates. It does not
invent day-level boundaries or create a controls-shaped file: its CSV and
manifest are explicitly review-only. The reviewer must establish dated,
half-open intervals and record primary sources before `build-annual` can run.

The Wikipedia party-divisions table is separately ingested as a hash-pinned,
community-edited secondary snapshot. Its published Senate/House party counts,
vacancies, trifecta labels, and within-Congress count-variation hints enrich the
review packet. They do not determine control: count strings can contain ranges
or alternatives, and the table does not supply a complete event-date history.
It must remain `SECONDARY_CROSSCHECK_ONLY` and cannot be promoted to
`controls.csv` without primary-source review.

### Congress 74 review bundle

`CTRL_074_A` is a disabled, manual evidence bundle for the reviewed 74th
Congress interval. It records authoritative institutional historical
compilations rather than original congressional journals or election
certificates, so it must not be described as a primary-source bundle.

Its locators cover the National Archives presidential date record, the Senate
party-division history, the House 74th Congress profile, the House
party-government table, and the House Speakers list. The House Speakers page
was captured at `2026-10-31T17:54:33Z`; its payload SHA-256 is
`dd79cf46562091e216dccc7dfbf1ffb4fecf6561a94e8c930bd4d04c0b42dce3`.
Every locator in this manual bundle has its own content-pinned capture in
`config/sources.toml`; the source loader rejects a manual bundle with an
unpinned locator. The snapshot supports the documented same-day 1936-06-04
transition from Speaker Byrns to Speaker Bankhead. It does not turn the House
profile's election-day party count into a daily membership series.

The bundle remains `enabled = false`: it has no parser, is not fetched or
validated as a market/policy source, and enters an annual research artifact only
when an approved `controls.csv` interval explicitly uses `CTRL_074_A`.

### General dated-control bundle

`CTRL_GOV_001` generalizes the same evidence approach across the remaining
Congress intervals. It combines official historical compilations from the
National Archives (presidential terms), the Senate Historical Office (dated
party division), and the House Office of the Historian (party government). The
three retained source captures are individually content-pinned in
`config/sources.toml`; their local filenames are not relied on as provenance.

The control definition is the party holding institutional majority or
organization, rather than a simple party-count label. In the 107th Congress,
this gives three Senate-control intervals: Democratic until 2001-01-20,
Republican until 2001-06-06, then Democratic to the end of the Congress. The
Senate's 2002-11-12 entry records a 49/49/2 balance and explicitly says that
Democrats maintained control; it is retained in the evidence note as a
composition event, not emitted as a Republican-control interval. Presidential
successions and inaugurations are split at the dates in the National Archives
record. As with `CTRL_074_A`, the bundle is disabled from automated source loops
and is only emitted when a reviewed control record cites it.

## Data permissions and change control

Raw downloads remain outside version control. Each is retained with a checksum,
retrieval timestamp, request URL and response headers. A changed checksum is a
new observation of the source, not an overwrite. Parsing code is versioned; each
output carries input file hashes and the config hash. The 2026-11-03
data-access decision closes the commercial-source and additional-acquisition
path for this project: do not add a vendor source or refresh a public capture to
a newer vintage. Reprocess the existing archived inputs only; any later source
expansion is a separately authorized research phase.
