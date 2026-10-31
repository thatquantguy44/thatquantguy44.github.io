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

## Data permissions and change control

Raw downloads remain outside version control. Each is retained with a checksum,
retrieval timestamp, request URL and response headers. A changed checksum is a
new observation of the source, not an overwrite. Parsing code is versioned; each
output carries input file hashes and the config hash. Before adding a commercial
source, record the licensing/permitted-use decision in the source config and
keep its adapter separate from the public-reconstruction path.
