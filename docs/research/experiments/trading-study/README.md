# Prospective trading research ledger

Read the [protocol](../../trading-experiment-protocol.md) for the signal, baselines, source timing, execution proxies, cost assumptions, and inference plan. The [parent brief](../../ai-hype-research-brief.md) tracks the article.

This is an offline preparation/logging package, not a live data collector, model API client, trading engine, or trusted timestamp service. Python 3.10+ on macOS/Linux, standard library only. No broker orders, paid calls, real forecasts, or price downloads are made by these utilities.

Current user preference: **offline work only**. The [offline setup and readiness notes](OFFLINE-SETUP.md) describe the new pure adapters, complete synthetic integration, local timestamp checks, and unresolved live bindings. Timestamp tests additionally require a compatible local OpenSSL installation; no service is contacted.

## Files

| File | Purpose |
| --- | --- |
| `manifest.example.json` | Explicitly unbound session configuration; valid for development only |
| `prompt.txt` | Proposed frozen LLM instructions |
| `prediction-log.schema.json` | JSON Schema for the four event payloads |
| `opportunity.template.json` | Empty source/timing/opportunity record |
| `prediction.template.json` | Empty four-condition forecast bundle; missing values are null |
| `outcome.template.json` | Empty realized-outcome record; not a fabricated zero return |
| `ledger.py` | Session freeze, validated append, chain audit, baseline/Brier/paper-return arithmetic helpers |
| `test_ledger.py` | Synthetic tests with clearly injected clocks and invented observations |
| `pipeline.py` | Offline scheduling, input/forecast parsing, baseline/price helpers, and synthetic integration |
| `offline-fixture.json` | Invented release, sessions, price levels, minute bars, toy dictionary, and mock response |
| `bindings.example.json` | Offline-only provider checklist with all live sources still unbound |
| `receipts.py` | Local RFC 3161 query creation and cryptographic consistency checks; no submission |
| `test_pipeline.py`, `test_receipts.py` | Network-disabled integration and local untrusted-CA tests |

Store real sessions, source packets, transcripts, and external receipts under ignored `sessions/` or another approved private location. Website exclusion of `docs/` does not make tracked files private on GitHub. The committed templates contain no predictions or market observations.

## Offline checks

From the repository root:

```sh
python3 -m unittest discover -s docs/research/experiments/trading-study -p 'test_*.py' -v
python3 docs/research/experiments/trading-study/ledger.py init --session /tmp/ai-hype-trading-dev --manifest docs/research/experiments/trading-study/manifest.example.json --mode development
python3 docs/research/experiments/trading-study/ledger.py verify --session /tmp/ai-hype-trading-dev
```

Use a fresh session path on subsequent checks; initialization refuses to overwrite a session. The result should show zero events, development mode, and `independent_timing_verified: false`. An unbound manifest is rejected with `--mode prospective` before a session directory is created.

To regenerate the payload schema into a new file and compare it with the committed version:

```sh
python3 docs/research/experiments/trading-study/ledger.py schema --out /tmp/ai-hype-prediction-schema.json
```

The schema describes field shape, required fields, enums, ranges, and extra-field rejection. It is not sufficient to validate cross-record chronology or study eligibility; `ledger.py` supplies those checks. The tests compare the committed schema against the code's contract.

## Binding a real session

Copy the manifest to a private location and fill the model/provider, exact parameters and current prices, cohort, dictionary permission/version, and hashes for the universe, calendar, prompt, input builder, baseline code, and collection adapter. Define the 42-day pilot dates, stable issuer IDs, source providers, and independent timestamp method. Archive source-selection evidence and the price/corporate-action convention.

Model parameters must include `temperature`, positive integer `max_input_tokens` and `max_output_tokens`, a nonempty `reasoning_configuration` object, `seed_support` (`supported`/`unsupported`), and `seed` (integer or explicit null). Model pricing must include `effective_at_utc`, nonnegative `input_usd_per_million` and `output_usd_per_million`, and explicit `reasoning_billing_policy`, `cache_billing_policy`, and `tool_billing_policy`. These are input assertions; the logger cannot verify provider prices or licences.

Prospective initialization checks that required bindings are present, the cohort has 30 unique issuer IDs, the prompt hash matches, and the collection window spans 42 days starting no earlier than the freeze date in New York. Independent audits must still verify the underlying evidence. Initialization does not authenticate a data provider or external receipt service.

```sh
python3 docs/research/experiments/trading-study/ledger.py init --session /private/path/session-001 --manifest /private/path/bound-manifest.json --mode prospective
```

Saving the protocol does not start this series. No bound live manifest has been created yet.

## Append and verify

Fill a copy of an event template using actual observed inputs; never append a blank template as an observation. Then:

```sh
python3 docs/research/experiments/trading-study/ledger.py append --session /private/path/session-001 --payload /private/path/opportunity.json
python3 docs/research/experiments/trading-study/ledger.py append --session /private/path/session-001 --payload /private/path/prediction.json
python3 docs/research/experiments/trading-study/ledger.py verify --session /private/path/session-001
```

The CLI assigns the current UTC receipt time; no argument permits supplying an earlier receipt. Internal clock injection exists only for synthetic tests. Append is serialized with a process lock and flushed to disk. Any malformed/truncated existing record blocks further appends; preserve the file for audit rather than deleting history.

Event order:

1. `opportunity`: original issuer/fiscal-period event, eligibility, raw document/packet hashes, source timestamps/evidence, common momentum feature, and fixed cutoff/price windows. Excluded or unresolved opportunities retain reasons and explicit nulls. A second original issuer/period must be recorded as excluded rather than treated as a fresh opportunity.
2. `prediction`: exactly one bundle per eligible opportunity containing all four conditions, with probabilities null on failure. Include actual model snapshot, request count, call times, response hash/reference, and known cost or null. No future-return fields or receipt-time overrides are allowed. Late forecasts and budget/request/deadline violations remain logged with flags.
3. `outcome`: append after the exit window ends. Record total-return values plus source-artifact hashes/references, or an explicit unavailable status and reason. Ties do not count as outperformance. Missing outcomes remain unknown, not zero.
4. `annotation`: corrections/receipts/audit findings reference an existing record ID and never replace its contents. Re-analysis of corrected data requires a separate versioned artifact preserving the original analysis.

`received_at_utc` records local receipt, not original publication. Payload hashes refer to artifacts that must actually be retained and audited; the utility does not retrieve or authenticate the files named by references. The code checks internal time relationships but does not authenticate the exchange calendar, source availability, or total-return calculation.

## What verification establishes

Every record contains a sequence number, receipt time, previous hash, payload, derived checks, and its own SHA-256. `verify` checks that chain, the frozen manifest/package fingerprints, duplicate rules, event references, and cross-record field/timing consistency. A changed protocol/package requires using its archived version or starting a new session.

Hash chaining is not notarization. A person with filesystem control can rewrite the entire chain and recompute hashes. Retain the head independently and obtain trusted receipts before the prediction cutoff; then audit the evidence before calling results independently verified prospective forecasts. `independent_timing_verified` deliberately remains false in utility output, including prospective mode.

Exit 0 means the requested operation or local chain check succeeded; it never certifies strategy validity. Exit 2 means a file, schema, reference, chronology, or configuration check failed. Preserve rejected payloads and record collector failures separately so attempted opportunities are not lost. The logger does not poll for opportunities or recover missed events automatically.

Arithmetic helpers implement the protocol's smoothed sentiment mapping, clipped momentum mapping, Brier loss, and prefunded long-only cost scenario. Missing probabilities/targets remain null for Brier loss. The paper-return helper treats a missing forecast as cash and an unavailable realized return as unknown; apply timing/compliance and sample rules before using it. Neither the helpers nor the stored outperformance label authenticate source prices or construct a self-financing portfolio.

## Next execution work

The synthetic integration is implemented; the real series remains unstarted. Continue offline per the user's choice. Future live work still requires verified data/model sources, vendor transports, input extraction and as-of/corporate-action adapters, independently trusted receipts, independent review, and a frozen live session. Pure helpers and mock responses are not provider-readiness proof. Report all opportunities and operational failures; do not equate a valid JSON chain with a profitable or adequately powered experiment.
