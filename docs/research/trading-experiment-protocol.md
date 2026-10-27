# Prospective earnings-signal experiment

Protocol version: 0.1.0

Prepared: 2026-10-27 (America/New_York)

Parent plan: [AI hype research brief](ai-hype-research-brief.md)

Status: Research design and offline logging package. No universe, model, or data provider is bound; no real forecasts or trades have been made. [Package instructions](experiments/trading-study/README.md).

## Question and estimand

Does a frozen LLM earnings-release signal improve prospective probability forecasts over simple document sentiment and a conventional price-momentum rule?

Primary target: whether a stock's five-session total return exceeds SPY's total return over the identical entry/exit windows. SPY is a broad-market comparator, not a factor model. Do not call this target or its forecast accuracy risk-adjusted alpha.

Primary comparison: paired event-level Brier loss for the LLM versus the dictionary baseline. Lower is better. Secondary comparisons are LLM versus momentum and the constant 0.5 probability baseline. Predeclare these before collection; do not select the weakest baseline after seeing returns.

The economic analysis is a separate long-only paper-execution sensitivity study. The primary experiment concerns information arriving after the cohort and model are frozen; it is not a claim that old backtests have been decontaminated.

## Cohort and observation rule

Proposed cohort rule, to be applied once using a verified snapshot before freezing the session:

- Select one ordinary share class per issuer, choosing the most liquid eligible class first. Then select 30 issuers ranked by median daily dollar volume over the previous 60 completed regular sessions; break ties by stable security ID.
- Eligible securities are US domestic issuers' ordinary common shares listed on NYSE or Nasdaq, with prior-session close at least USD 5 and median daily dollar volume at least USD 20 million. These thresholds are study-design choices, not estimates of current liquidity.
- Exclude ETFs, funds, preferred stock, ADRs, warrants, units, and non-domestic issuers. Use stable security IDs plus CIK, not ticker strings alone. Retain the cohort if issuers later delist or become illiquid; preserve their event and outcome dispositions.
- Archive the complete eligible-universe snapshot, selection inputs, provider, as-of timestamp, ranking, and selected securities. A list reconstructed after outcomes is not an admissible prospective cohort.
- One event is the first qualifying original earnings release for each cohort issuer/fiscal period after session freeze. Log amendments, duplicate releases, missed events, and exclusions without replacing the original opportunity.

Use a fixed six-week (42-day) operational pilot beginning only after the session manifest is bound and frozen. Log all eligible opportunities over that interval; do not stop early because performance looks favorable. This duration is for pipeline evaluation, not a power guarantee or a promise of sufficient earnings events. Use issuer/date dependence, event counts, and a practical improvement threshold to plan a subsequent main study. A proposed planning threshold is a 0.01 reduction in paired Brier loss, declared as an analytical choice.

## Source packet and availability

Default document route: the original SEC earnings-release exhibit associated with an 8-K Item 2.02, checked against issuer IR when necessary. Archive raw bytes, normalized text, accession/document ID, fiscal period, URLs, document SHA-256, extraction version, and exact model input packet. Exclude call transcripts, later presentations, news summaries, and later revisions from this first signal.

[SEC submissions APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) provide filing metadata and are updated as submissions are disseminated. A filing-acceptance timestamp is not proof of when the earnings release first appeared elsewhere, or when our collector could read it. Use our actual retrieval times and retain the original timestamp fields with their source and timezone interpretation. Never silently treat a date-only field as a precise publication time.

For every source record, retain:

1. Provider-stated public-availability timestamp and its evidence; explicit `null` if not verifiable.
2. Collector first-seen timestamp.
3. Download-completed timestamp.
4. Packet-finalized timestamp and hash.

Operational availability is no earlier than the latest required input's download completion and packet finalization. All conditions receive the same frozen document text and the same predeclared price features. A vendor route such as Quartr can supply document bodies only after its original-document provenance, revisions, and our observed retrieval times have been checked; connector installation alone is not proof of point-in-time suitability.

Retain events with missing timestamps or documents in the opportunity log as failures or exclusions with reasons. They are not valid primary forecasts until eligibility and source timing are independently audited. No real data-source access is claimed by this protocol.

## Signal and baselines

All probability forecasts target stock return greater than SPY return over the same windows. Ties are target 0. Probabilities are uncalibrated forecasts to be evaluated; a model's stated confidence is not an empirical confidence interval.

| Condition | Frozen rule | Inputs |
| --- | --- | --- |
| `llm` | One model request returns `p_outperform` in [0,1], a short rationale, and verbatim source evidence | Exact release packet plus the common price features |
| `dictionary` | Let P/N be positive/negative token counts; score = (P-N)/(P+N+20); p = (1+score)/2 | Same normalized release, frozen financial dictionary |
| `momentum` | Let r20 be stock total return minus SPY total return over the previous 20 completed sessions; p = (1+clip(r20/0.10,-1,1))/2 | Same as-of price features supplied to all conditions |
| `no_signal` | p = 0.5 | No predictive information |

For dictionary sentiment, use a legally usable frozen Loughran–McDonald dictionary version and record its SHA-256 and license posture. Its [official distribution](https://sraf.nd.edu/loughranmcdonald-master-dictionary/) specifies academic and commercial usage terms; do not assume a public blog project qualifies for academic licensing. Resolve permitted use before acquiring or redistributing a dictionary. The package does not bundle a word list. Tokenization is uppercase ASCII alphabetic tokens (`[A-Z]+`), repeated occurrences count, no stemming or negation adjustment, and zero matched words gives p = 0.5. The smoothing constant 20 and momentum scale 0.10 are fixed design assumptions; do not tune them on prospective outcomes.

Freeze the exact model/snapshot, system/user prompt, temperature, reasoning/token limits, seed support, tools, output parser, and prices. No browsing, new data retrieval, memory of earlier outcomes, or manual forecast revision is allowed during inference. If a snapshot cannot be pinned, record the limitation and start a new series when the provider changes the model. Do not splice model versions into one unchanged treatment.

One request per event, maximum proposed charge USD 0.50 with a 120-second inference deadline; use provider-specific worst-case charge reservation before dispatch. Invalid output, timeout, unavailable inputs, and budget failure get explicit statuses and null probabilities. No best-of-n sampling or repair calls. Preserve raw response, usage, charge, and errors. Unknown costs stay unknown. Baselines must be calculated for every eligible event even when the LLM fails.

## Timing and entry/exit rule

Use UTC in machine records and `America/New_York` for exchange-calendar interpretation and presentation. Pin and hash the official session calendar, including holidays, DST, early closes, and unexpected closures. The [NYSE calendar](https://www.nyse.com/trade/hours-calendars) documents regular-session hours and exceptions; do not approximate sessions with weekdays or a fixed UTC offset.

1. Register the opportunity and freeze its packet before inference. Preserve missed or failed opportunities too.
2. Define the prediction cutoff as 10 minutes before the first regular-session open that occurs at least 10 minutes after packet finalization. Freeze the selected session and its cutoff at registration; a slow or failed model must not move its own target to a more convenient session.
3. Append all four forecasts, including failures, before the cutoff. Late records remain in the log and are classified late; do not backdate them or silently move them into the next session's primary sample.
4. Entry price proxy is the share-volume-weighted price in minutes 5 through 10 after that session's open, using a pinned minute-bar convention and eligible-trade rules.
5. Exit uses the identical minute window five regular-session indices later: entry session j, exit session j+5. This is five intervening session-to-session intervals, not five calendar days.
6. Stock and SPY must use identical windows. A halt, missing window, or unavailable volume/price data produces an explicit unavailable outcome; do not carry a stale price forward or drop the opportunity.

The entry/exit windows are research execution proxies, not guaranteed fills. Waiting until the next eligible session sacrifices some immediate news reaction but avoids assuming that processing completed before an earlier price was executable. Document event-to-entry latency and missed opportunities.

Future split/dividend data may be used to construct realized labels after the fact, but may not leak into as-of forecasting features. Preserve raw prices and corporate-action records, and use a provider-verified total-return convention that handles distributions, splits, mergers, and delisting proceeds. Latest adjusted close alone is insufficient documentation of that convention.

## Economics and costs

Secondary paper rule: allocate one independent unit of capital to each eligible event. Buy the stock only when p > 0.55; otherwise remain in cash. No shorts, leverage, broker orders, or live capital. Keep failed-forecast opportunities in the allocation denominator with no position, and report coverage. Show buy-every-event, SPY-over-the-window, and cash comparators.

Cash gross return is assumed zero for this small event study; identify it as an assumption. Primary transaction-cost scenario is 10 basis points on entry and 10 on exit, applied to traded notional on each side, not a flat fee subtracted from cash events. Stress scenarios are 0, 25, and 50 basis points per side. These are assumed costs, not measured spreads or quotes. Do not double-count any explicitly observed execution charge.

With proportional side cost c on traded notional and stock gross total-return factor G, one unit of prefunded capital buys `1/(1+c)` units of stock notional. The simplified final net factor is `G*(1-c)/(1+c)`, so net return is that factor minus 1. This sensitivity assumes distributions are reinvested in G without interim transaction charges; document that convention and any corporate-action exceptions in the price adapter. Actual research/model fees and human effort are reported separately per forecast and in a stated capital-cost scenario, since USD-per-call costs cannot be subtracted from returns without specifying capital.

Report event-level payoff proxies and coverage first. Overlapping event allocations do not form a self-financing portfolio automatically. Do not annualize an average event return or report portfolio Sharpe/drawdown until a separate capital, overlap, cash, rebalancing, and corporate-action ledger is implemented and frozen. Market-relative return is not proof of factor-adjusted alpha.

## Outcomes, missingness, and inference

Let y = 1 when stock total return > SPY total return over the prescribed windows, otherwise 0. Brier loss is `(p-y)^2`. Primary summary is the mean within-event difference `loss_llm - loss_dictionary`; negative favors the LLM.

- Report opportunity counts, eligibility, source-timing issues, failures, late forecasts, missing outcomes, and valid probabilities for each condition.
- On events with both protocol-compliant valid probabilities, audited timing, and outcomes, report paired Brier differences and sample membership. Missing/unknown compliance is not a verified pass. This conditional sample is not the full operational performance of a system with failures.
- Also report an explicitly labeled operational policy: on missing, failed, late, or policy-noncompliant forecasts use p = 0.5, without rewriting the raw forecast; report this policy over eligible opportunities with observable outcomes. Report unknown compliance separately and show the same fallback treatment as a conservative sensitivity, rather than silently excluding those records. Report how many eligible outcomes remain unknown and bound losses for those outcomes where feasible.
- For economics, missing forecasts imply no trade; missing realized outcomes remain unknown rather than zero returns. Keep their attempted costs and status in coverage reporting.
- Secondary metrics: calibration/reliability plots with adequate counts, rank relationship between score and market-relative return, and cost sensitivity. A tiny pilot cannot support stable calibration bins or a durable-alpha claim.
- Dependence: events from the same issuer and same/nearby market dates are correlated; holding windows overlap. Main-study intervals should account for issuer clustering and calendar blocks at least as long as the horizon. Freeze a suitable resampling/model specification after pipeline diagnostics and before main-study outcomes; a naive event-IID interval is not acceptable.
- Use one primary comparison. Clearly label other comparisons, horizons, cost scenarios, and subgroup slices as secondary; disclose all variants, including negative results.

Historical exercises may be labeled development/backtest diagnostics only. They do not become prospective because a model is instructed to role-play an earlier date. [Lookahead-bias research](https://arxiv.org/abs/2512.23847v2) and the [Federal Reserve's data-vintage study](https://www.federalreserve.gov/econres/feds/total-recall-evaluating-the-macroeconomic-knowledge-of-large-language-models.htm) motivate these controls; they do not establish contamination or profitability for this experiment.

## Append-only record contract

The [logging utility](experiments/trading-study/README.md) records a frozen session, then an ordered stream of `opportunity`, `prediction`, `outcome`, and `annotation` events. It supplies the current UTC receipt timestamp; payloads cannot supply a replacement receipt time. Append operations validate the existing hash chain, reject duplicate IDs, use a process lock, flush the record, and never edit earlier lines. Outcomes and corrections are new events linked to prior record IDs.

The prediction record contains all four conditions, model status/usage/cost, raw response hash, source/packet hashes, cutoff, exact entry/exit windows, and an explicit timing classification. No future outcome fields are accepted in a prediction. Failed/late forecasts remain visible. Outcomes cannot be appended before the exit window ends, and a second outcome is not a silent correction: use an annotation plus a versioned re-analysis.

A local hash chain detects edits only against a retained head; anyone controlling the filesystem can rewrite a whole chain and recompute hashes. Local receipt timestamps are clock claims, not independent proof of pre-outcome existence. Before treating live records as independently verified prospective evidence, obtain a trusted external receipt of each prediction hash or a batch head before the cutoff, preserve its verification material, and audit timing. The utility does not create or validate such external receipts and does not contact an external service. Until then, records are locally timestamped candidates only.

Corrections never overwrite forecasts. Annotate the error with reason, affected IDs, and discovery time; preserve the original analysis and apply any correction policy uniformly across conditions. Store live data, manifests, receipts, and transcripts in the package's ignored `sessions/` directory or an approved private location. The repository's `docs/` website exclusion does not make tracked research data private.

## Binding and readiness checklist

- [x] Specify signal, baselines, prospective timing, labels, and economic assumptions.
- [x] Prepare a frozen-session template, prompt, prediction schema, and local append-only logging utility.
- [ ] Verify/licence the universe, document, minute-bar, corporate-action, benchmark, dictionary, and calendar inputs; freeze the cohort and their hashes.
- [ ] Bind the model, prices, complete prompt/input builder, baseline implementations, and collection/execution adapters.
- [ ] Independently audit sample timestamps, source extraction, corporate actions, formulas, logging, and the first complete synthetic end-to-end run.
- [ ] Bind a trusted timestamp/receipt method before claiming independently verified prospective results.
- [ ] Freeze the live session manifest; collect the six-week operational pilot without outcome-driven changes.
- [ ] Evaluate pilot coverage and precision, then freeze a fresh main-study design if supported.

No live series starts merely by saving this protocol. The logging package can be tested entirely offline. Missing sources are explicit configuration gaps, not reasons to invent a universe, timestamp, forecast, price, or result.
