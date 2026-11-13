# Presidential research pipeline handoff

MarketMedallion is the receiving owner for new presidential research pipeline
work. The cross-repository `feat/pres-data-integration` branches implement the
local handoff under MarketMedallion `specs/spec016`; this handoff is not a claim
that those branches have already merged or been released. The existing standalone
pipeline remains here as the reproducibility and rollback reference until the
coordinated release is accepted. Removing the duplicate executable code requires a
separate reviewed change; preserve published research, protocols and old exports.

The 2026-11-03 study can be rebuilt offline from the selected retained archive,
review workbook and official control evidence. On the receiving branch, install
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
