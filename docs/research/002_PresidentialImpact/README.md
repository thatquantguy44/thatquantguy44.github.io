# 002 — Presidential Impact

**Status: active topic; research plan and first local analysis module prepared.** AI-hype research is paused in
[001_AIHype](../001_AIHype/README.md).

Approach: **document the seed article's claims, conduct an independent
public-data reconstruction, add the inherited-conditions extension, then develop
a clearly labeled personal interpretation.**

Extension question: **How much additional information do presidential and
congressional labels provide about US equity returns beyond the conditions an
administration inherits?**

The starting material is the user-supplied Fiduciary Trust International article
*Should the balance of power in Washington matter to investors?*, attributed to
Carin Pai, CFA, and dated October 16, 2024. It is a research lead, not an
independently checked dataset or an established conclusion.

- [Replication, extension and personal-interpretation plan](research-brief.md)
- [Master handoff and next-work plan](MASTER_HANDOFF.md)
- [Frozen descriptive public-series analysis](descriptive-analysis/README.md)
- [Exact-replication disposition matrix](exact-replication-disposition.md)
- [Inherited-conditions protocol](inherited-conditions-protocol.md)
- [Inherited-conditions descriptive results](inherited-conditions-analysis/README.md)
- [Seed-source provenance and verification gaps](sources/source-notes.md)
- [Source metadata](sources/S001-source.json)
- [Portable data pipeline](pipeline/README.md)
- [QuantMeridian module specification](quantmeridian-module/SPEC.md)
- [Run the Presidential Impact module](quantmeridian-module/HANDOFF.md)
- [Implementation checks and limitations](quantmeridian-module/VALIDATION.md)

The proposed personal contribution is an attributed source comparison plus a
transparent public-data reconstruction of political labels, inherited
fundamentals and predictive usefulness, with an explicit outlier/dependence
audit and the author's own voice. The project has closed the exact-replication
track and will use only its captured public data; all results must be labeled an
independent reconstruction. The intended audience is an investment director; a
concise memo and inspectable appendix would precede any broader article.

The QuantMeridian **PRES** module supports local JSON intake, descriptive returns,
inherited-condition figures, sensitivities and replayable exports. Its fictional
example exercises the tooling; it supplies no historical findings. Conditional
models and predictive evaluation remain future work.

The separate portable pipeline stages public source files with immutable raw
archives, source hashes and quality checks before writing the module's local JSON
format. Its public market series is explicitly a CRSP-market proxy; no licensed
S&amp;P 500 source will be added to this project.

A public-source reconstruction now has a frozen CRSP-market-proxy baseline and a
separately labeled Shiller S&P Composite robustness reconstruction. The
reproducible, descriptive 1936–2022 comparison package—with group counts,
figures, and a within-window-control audit—is in
[descriptive-analysis](descriptive-analysis/README.md). The exact seed-article
replication track is closed by the project's data-access decision; see the
[master handoff](MASTER_HANDOFF.md) for the current scope, constraints,
commands, and acceptance criteria.

The frozen 1955–2022 inherited-conditions extension also has paired CAPE and
policy-rate descriptives, source-separated return results, portable static
figures, and a reproducible local ledger in
[inherited-conditions-analysis](inherited-conditions-analysis/README.md).
