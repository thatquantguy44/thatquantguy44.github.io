# Presidential research pipeline handoff

MarketMedallion owns new presidential research pipeline work under spec 016.
[MarketMedallion PR #21](https://github.com/thatquantguy44/market-medallion/pull/21)
and [QuantMeridian PR #220](https://github.com/thatquantguy44/QuantMeridian/pull/220)
have merged. The existing standalone pipeline remains here as the reproducibility
and rollback reference. Removing the duplicate executable code requires a
separate reviewed change; preserve published research, protocols and old exports.

The 2026-11-03 study can be rebuilt offline from the selected retained archive,
review workbook and official control evidence. Install
MarketMedallion and its declared dependencies, then invoke:

```sh
python -m market_data_pipeline presidential import-frozen \
  --donor-pipeline /path/to/this/research/pipeline \
  --workbook /path/to/political_control_review_workbook.xlsx \
  --workspace /absolute/new/private/workspace
```

The destination must not exist. The importer selects only the pinned study
inputs, preserves the original capture manifests and timestamps, checks the
workbook/controls/evidence hashes, and makes no provider request. It does not
copy the donor `.local` directory, credentials, virtual environment or database.
Check the resulting selection with `presidential check --workspace ...`. The
separately enabled QuantMeridian local reader selects a published snapshot;
PRES does not execute the donor pipeline.

The frozen donor and receiving pipeline have been compared locally: the five
datasets agree, and all seven supporting outputs match, including 86 cycle
rows. These checks do not authenticate the original HTTP Shiller transport,
independently certify political-control evidence, recover release vintages, or
make the proxy an exact S&P 500 replication. Live retrieval, new vintages,
redistribution and hosted access need separate source and operational decisions.
Use the original archived standalone release to reproduce legacy outputs if the
receiving branch is unavailable; do not overwrite or delete the retained study.
