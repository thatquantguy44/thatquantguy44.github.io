# Offline provider preparation

Updated: 2026-10-27 (America/New_York)

User choice: **Keep working offline for now.** Live provider requests, account setup, model calls, data downloads, and timestamp submissions are outside the current execution scope. This file records connection findings obtained before that choice and the offline work completed afterward.

## Current readiness

| Component | Observed state | What is available offline | What remains before a live session |
| --- | --- | --- | --- |
| Documents | Quartr returned an authentication/retry response twice; no company/document data were received | Local plain-text release packet builder and raw/normalized hashes | Successful provider read, original release provenance, audited retrieval/publication times, and extraction adapter |
| Model | No OpenAI/Anthropic API key was loaded in the inspected shell; that does not describe all user accounts | Provider-neutral output parsing, evidence checks, and a clearly labeled mock | Chosen provider, exact available snapshot, parameter compatibility, prices, request/usage adapter and a verified account |
| Prices | No supported market-data credentials were loaded; no suitable Alpaca plugin was returned by the targeted plugin search | Strict aggregation of supplied normalized minute bars | Verified feed/entitlements, symbol identity, pagination, as-of data availability and actual price adapter |
| Corporate actions | No source bound | Price return only when a caller explicitly attests `verified_none` | Distribution/split/merger/delisting support and a verified total-return convention |
| Universe | No source bound | Explicit missing-binding report | Complete point-in-time eligible universe, ordinary-share classification, stable IDs and 60-session liquidity inputs |
| Calendar | No archived exchange snapshot bound | Index-based scheduling from supplied session lists, including DST/early-close checks | Independently audited completeness and provenance of an actual calendar snapshot |
| Dictionary | No permission/version bound | A toy dictionary solely for synthetic tests | Permitted actual financial dictionary and its frozen normalization/hash |
| Independent timing | OpenSSL 4.0.3 is installed; no external receipt was acquired | Nonce-bearing RFC 3161 request generation, local signature/digest/nonce/pin/cutoff checks | Independently reviewed authority/trust anchor/clock policy, actual pre-cutoff receipts and source authentication |

Initial local HTTP reachability checks for public certificate/calendar pages failed DNS resolution. Those failures are not proof that the services are unavailable elsewhere. No escalation or further network probing was pursued after the offline choice.

Primary documentation examined before the offline choice:

- [Alpaca historical bars](https://docs.alpaca.markets/us/reference/stockbars) and [market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq): consolidated SIP and single-venue IEX coverage must be distinguished. Delayed historical consolidated prices are a possible outcome-evaluation route, subject to account verification; they do not establish a real-time entitlement or replace unavailable pre-forecast information.
- [Official OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna) and [structured-output guide](https://developers.openai.com/api/docs/guides/structured-outputs): documentation alone does not establish a snapshot's account availability or a frozen pricing configuration. No model or prices were bound.
- [FreeTSA's RFC 3161 examples](https://www.freetsa.org/index_en.php): inform the request/verification interface. No FreeTSA request was sent, certificate was bound, or independent timing was established.

## Reproduce the offline integration

From the repository root:

```sh
python3 docs/research/experiments/trading-study/pipeline.py readiness
python3 docs/research/experiments/trading-study/pipeline.py dry-run --out /tmp/ai-hype-synthetic-pipeline
python3 docs/research/experiments/trading-study/ledger.py verify --session /tmp/ai-hype-synthetic-pipeline/session
python3 -m unittest discover -s docs/research/experiments/trading-study -p 'test_*.py' -v
```

Use a fresh output directory each time. The integration run writes only synthetic artifacts and an explicitly development-mode ledger. It checks:

1. Selection of entry/exit sessions from the supplied calendar and a cutoff fixed before inference.
2. Matching 21 as-of total-return levels for the 20-session momentum feature.
3. A normalized release packet, source identity, and input hashes.
4. Dictionary/momentum/no-signal probabilities and a provider-neutral mock model response.
5. Literal citation/probability/output checks; invalid model output remains a failed condition with its raw bytes retained.
6. Opportunity and forecast appends, observed-volume VWAP aggregation, and a later outcome append.
7. Brier and cost arithmetic, local ledger integrity, and explicit `synthetic: true`, `empirical_evidence: false`, and `independent_timing_verified: false` labels.

The test suite runs the integration with Python socket creation and DNS resolution disabled. No API, scraping, account, or model transport is implemented in these helpers. Their normalized input objects are our own internal contracts, not a claim of compatibility with an untested vendor's raw wire format.

Literal citation checks establish that a quote appears in a supplied source. They do not establish that the model's economic interpretation follows from that quote; independent semantic review remains necessary.

Synthetic score/return numbers validate wiring only. They must not be used as results, comparisons, plots, or examples of real alpha in the article. No local test CA or mock source is allowed to populate a live manifest.

## Local timestamp request preparation

For a ledger record/head digest, generate a local request in a new path:

```sh
python3 docs/research/experiments/trading-study/receipts.py make-query --digest REPLACE_WITH_64_CHARACTER_SHA256 --out /tmp/ai-hype-local-request.tsq
```

Replace the digest placeholder with the exact lowercase hash. This command creates a SHA-256 request with a nonce and certificate request; it does **not** contact a timestamp service. It does not create a timestamp response or prove the digest existed before a cutoff.

If real query/response/certificate files are supplied later, the local `verify` subcommand requires the expected ledger digest, matching original query, response, pinned CA file hash, signer certificate, cutoff, and an explicitly supplied clock-error bound. It verifies both request/nonce correspondence and the expected digest, and rejects a signed generation time plus that bound at or after the cutoff.

These helpers require a local OpenSSL version supporting `ts` and `-CAstore`; they were tested on OpenSSL 4.0.3. Explicit trust files/directories are used. CA-file pinning hashes the **raw file bytes**, not a DER certificate fingerprint. Review the root provenance and clock bound independently; neither a caller's pin nor a locally self-signed certificate creates external trust. Revocation checks and long-term historical certificate-validation policy are not implemented. The helper and ledger therefore keep independent timing unverified.

Tests generate an untrusted CA/TSA and short-lived private keys in a temporary directory, sign a public synthetic digest locally, and delete that material afterward. Nothing is submitted externally or committed as a trusted authority.

## Future live binding

Keep `bindings.example.json` set to `offline_only`. To resume live setup, first establish the permitted provider accounts and dictionary use, then implement/audit transports and complete the existing bound-session checklist. No account authentication, installations, polling, model execution, timestamp submission, or paid subscription should occur automatically because offline tests pass.

The [parent research plan](../../ai-hype-research-brief.md) records the offline choice and remaining prerequisites. Priority 3's evidence matrix remains a useful next offline task using the research already available.
