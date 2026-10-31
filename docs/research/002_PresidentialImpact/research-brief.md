# Presidential Impact — initial research brief

## Question and original angle

**Working title: What did the president inherit—and what changed?**

First reconstruct the seed article's core descriptive comparisons as closely as
the available definitions and data permit. Then test whether presidential-party
and congressional-control classifications add useful information about US equity
returns beyond starting valuations, policy rates and macroeconomic conditions.
Keep the reproduced analysis, original extensions and personal interpretation
distinct, with visible uncertainty.

The user's intended audience is a new investment director. A useful personal
signature would combine clear visual storytelling, disciplined data-science
methods and a decision-relevant question: **what could an investor actually know
at the start of the investment window?** The result may be inconclusive.

## Seed and evidence boundary

The [seed-source record](sources/source-notes.md) describes the pasted Fiduciary
Trust International article dated October 16, 2024. Its numerical claims have
not been reproduced. The exhibit and underlying table are absent, and no original
page URL was supplied in the paste. The article's later navigation/footer dates
must not replace its publication date.

This brief proposes research. It contains no new performance estimate, causal
finding, investment recommendation or verified claim about which party is better
for markets. The existing offline-preparation constraint remains in effect.

## Research format: replication, extension and interpretation

The user has selected a replication-led project with their own presentation,
opinion and additional inherited-conditions angle. Most of the source's analytical
structure is a reasonable reconstruction target; exact numerical agreement is
conditional on recovering its inputs and conventions.

| Layer | Deliverable | Authorship and evidence boundary |
| --- | --- | --- |
| Replication | Reconstruct the article's political-category returns and presidential-period comparison | Attribute the starting analysis to Carin Pai/Fiduciary Trust International and distinguish their reported results from our calculations |
| Original extension | Test inherited conditions, incremental political information and robustness | Identify additional questions, data, methods and results as our work; separate explanation from prediction |
| Personal interpretation | Explain what the evidence changes about the investment question and why it matters | Label opinion and uncertainty; do not attribute a position to the user before they choose it or manufacture a conclusion before results exist |

Use **exact replication** only when the source series, windows, definitions and
calculations can be matched. Otherwise call the work an **independent
reconstruction** or **conceptual replication**, disclose substitutes and explain
why results may differ. Reproduce the analysis with our own calculations and
figures; a rewritten version of the original prose is not the research contribution.

### Replication targets

| Target | What to reconstruct | Inputs that must be recovered |
| --- | --- | --- |
| Political configurations | The source's annual-return comparisons for 1936–2023 | Index/return construction, political assignment rules, category membership, averaging convention and observations per category |
| Presidential periods | The exhibit pairing administration-period returns with beginning valuation and policy-rate measures | Missing chart, precise start/end dates, P/E definition, rate observation, cumulative/annualized convention and incomplete-period handling |
| Original crisis sensitivity | The article's reported exclusion of 2008, clearly labeled as its sensitivity variant | A matching full-sample baseline and the exact recomputation; keep the full sample primary in our extension |
| Strength of association | The proposition that fundamentals have stronger associations with returns than political control | A defined comparison on matched samples and windows; a visual ordering alone does not establish the proposition |

For every attempted reproduction, retain the source claim, our result, data and
definition differences, and a disposition: matched, matched within stated
rounding, differed, or not reproducible from available inputs. Do not force a match
by tuning definitions after seeing results. The market-leading-horizon statement
is a separate verification question, outside the first core replication pass.

### Where the personal voice belongs

Use a consistent narrative: **what the original reports → what our reconstruction
shows → what the extension adds → how the author interprets it**. Explain which
results were expected, which changed the interpretation, and what evidence would
change it again. Preserve favorable, unfavorable and inconclusive findings.

The working title supplies an interpretive lens, not an established conclusion.
A distinct visual style, transparent assumptions and a clear investment question
can supply flair without overstating what the data identify. An adjusted political
coefficient must not be presented as a president's causal contribution.

## Separate three questions

| Question | What the study could examine | Interpretation boundary |
| --- | --- | --- |
| Descriptive attribution | Returns grouped by presidential party and actual congressional control | Grouped historical outcomes do not identify what political control caused |
| Incremental explanation | Whether political variables add association beyond a restrained starting-conditions specification | Better in-sample fit is conditional association, with uncertainty and specification sensitivity |
| Prediction | Whether political information improves chronologically evaluated forecasts over the same fundamentals-only baseline | Forecast usefulness must use information available at the forecast origin; it does not establish causality |

Do not claim that adjusting for observed fundamentals isolates a presidential
causal effect. Subsequent rate moves, fiscal measures and economic outcomes may
be mechanisms, responses or confounders depending on the question; controlling
for them changes the interpretation.

## Competing propositions to investigate

1. **Incremental political information:** political classifications add useful
   explanatory or predictive information beyond inherited conditions.
2. **Inherited opportunity set:** apparent differences largely reflect starting
   valuations, rates, economic conditions and the particular periods represented.
3. **Measurement or concentration:** conventions, a few influential periods,
   incomplete terms or dependent observations drive an apparent ordering.

These are proposed alternatives, not ranked findings or a claim about consensus.
Specify in advance what observations would discriminate between them and what
would cause the thesis to be revised.

## Definitions and design decisions before analysis

| Decision | Required specification |
| --- | --- |
| Return | Price versus total return; nominal versus real; cumulative versus annualized; horizon and benchmark |
| Sampling frame | Keep the article's 1936–2023 annual comparisons separate from its presidential-period exhibit until both can be reconstructed |
| Decision time | Choose a primary election/inauguration/month-end convention and prespecified alternatives; do not select the best-looking window afterward |
| Political control | Track actual chamber/presidential control, midterms, succession and intra-window changes rather than assuming one start-of-term label persists |
| Inherited conditions | Define beginning valuation, policy rate and macro measures, their construction and contemporaneous availability/vintages |
| Partial periods | Identify the exhibit's 2021-start period ending September 2024 as incomplete; recover the original chart before interpreting its labeling or annualization |
| Comparisons | Use a restrained fundamentals-only baseline, then add political variables; separate explanatory fit from chronological predictive evaluation |
| Dependence | Assess administration clustering, persistent regimes and overlapping windows; do not treat every return row as an independent presidential observation |
| Sensitivity | Retain 2008 in the primary analysis; apply consistent prespecified crisis and leave-one-period-out checks across political categories |
| Data and reproducibility | Archive source versions, permissions, transformations, joins, as-of conventions, sample exclusions and all tested specifications |

The effective sample may be small for a rich specification. Establish data
coverage and independent units before choosing model complexity or uncertainty
methods; do not promise statistical power in advance of that inventory.

## Proposed flavor and presentation

- **Inherited-conditions panel:** show the starting state alongside subsequent
  returns, distinguishing descriptive association from any causal story.
- **Political timeline:** make chamber-control changes and investment windows
  visible instead of concealing them in a category average.
- **Contribution and robustness panel:** show whether an ordering depends on a
  particular administration, crisis or observation rule, using symmetric checks.
- **Incremental-information scorecard:** compare fundamentals-only and
  fundamentals-plus-politics specifications, with chronological prediction kept
  separate from explanation.

These are planned figures, not simulated results. The story should state what
would change the interpretation, preserve counterevidence, and distinguish
economic relevance from an attractive chart or a small p-value.

## Deliverables and next sequence

### Analysis tooling

The user authorized a specification and runnable first version in QuantMeridian
(`market_terminal`). The [PRES module specification](quantmeridian-module/SPEC.md)
defines the local dataset contract, scientific rules, figures, exports and
acceptance criteria. See [run instructions](quantmeridian-module/HANDOFF.md) and
the [validation record](quantmeridian-module/VALIDATION.md).

This first version enables independent descriptive reconstruction and
inherited-condition inspection. Source admission, exact replication, conditional
models, uncertainty estimation and chronological prediction remain explicit
research tasks. Tool delivery does not complete any empirical comparison below.

### Source pipeline

The [portable data pipeline](pipeline/README.md) separates public-source download,
raw-file archival, parsing, quality checks and QuantMeridian JSON assembly. It
records a public CRSP-market reconstruction separately from the seed article's
S&P 500 analysis and blocks output until political-control intervals are reviewed.
The [source decisions](pipeline/SOURCE_DECISIONS.md) define the proxy boundary and
commercial-data gap.

### Research sequence

1. Recover the original article/exhibit and calculation definitions; record
   exact locators, underlying sources and access limits.
2. Choose and document the replication's return, time unit and political
   classifications. Freeze the original-extension comparisons and sensitivity
   plan before inspecting their estimated results.
3. Build a source-backed dataset, reconstruct the seed's core descriptive
   comparisons, and retain the reproduction dispositions and any substitutions.
4. Add inherited-conditions analysis, incremental explanation and chronological
   predictive evaluation, retaining uncertainty, negative results and changes.
5. Prepare a proposed two-page director memo and reproducibility appendix. Keep
   source findings, reproduced calculations, new analysis and personal opinion
   visibly separate. A longer article can follow source and calculation review.

Open inputs include the director's preferred decision context and format, the
available licensed market-data access, and the original missing exhibit. None
needs to be guessed to complete the folder organization and initial scope.
