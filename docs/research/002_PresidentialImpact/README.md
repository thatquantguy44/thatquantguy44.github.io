# 002 — Presidential Impact

**Status: active topic; research plan and first local analysis module prepared.** AI-hype research is paused in
[001_AIHype](../001_AIHype/README.md).

Approach: **replicate the seed article's core analysis, add the inherited-conditions
extension, then develop a clearly labeled personal interpretation.**

Extension question: **How much additional information do presidential and
congressional labels provide about US equity returns beyond the conditions an
administration inherits?**

The starting material is the user-supplied Fiduciary Trust International article
*Should the balance of power in Washington matter to investors?*, attributed to
Carin Pai, CFA, and dated October 16, 2024. It is a research lead, not an
independently checked dataset or an established conclusion.

- [Replication, extension and personal-interpretation plan](research-brief.md)
- [Seed-source provenance and verification gaps](sources/source-notes.md)
- [Source metadata](sources/S001-source.json)
- [Portable data pipeline](pipeline/README.md)
- [QuantMeridian module specification](quantmeridian-module/SPEC.md)
- [Run the Presidential Impact module](quantmeridian-module/HANDOFF.md)
- [Implementation checks and limitations](quantmeridian-module/VALIDATION.md)

The proposed personal contribution is an attributed reconstruction plus a
transparent comparison of political labels, inherited fundamentals and predictive
usefulness, with an explicit outlier/dependence audit and the author's own voice.
Exact replication depends on recovering the original definitions and data;
substitute-data work must be labeled an independent reconstruction. The intended
audience is an investment director; a concise memo and inspectable appendix would
precede any broader article.

The QuantMeridian **PRES** module supports local JSON intake, descriptive returns,
inherited-condition figures, sensitivities and replayable exports. Its fictional
example exercises the tooling; it supplies no historical findings. Conditional
models and predictive evaluation remain future work.

The separate portable pipeline stages public source files with immutable raw
archives, source hashes and quality checks before writing the module's local JSON
format. Its public market series is explicitly a CRSP-market proxy; a licensed
S&P 500 source remains necessary for an exact reconstruction of the article.

No literature search, market-data acquisition, historical numerical reproduction
or model estimation has been performed for this new topic. The next research step is to
obtain the original exhibit/calculation definitions and choose a reproducible
return and political-control convention.
