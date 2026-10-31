# Data quality rules

The pipeline checks the properties that could silently change the research result:

| Dataset | Grain / key | Required checks | Failing consequence |
| --- | --- | --- | --- |
| Monthly market returns | month | unique valid month; finite factor values; no missing month within an annual return | affected annual window is not built |
| Federal-funds rate | month | unique valid month; finite percent; no future value | term input is unavailable |
| Political controls | dated half-open interval | unique ID; valid dates; no overlap; allowed party values; source ID present | analysis JSON is rejected |
| Source manifest | raw file version | SHA-256, URL, timestamp, parser name, output lineage | output is not marked reproducible |

The annual return builder compounds month returns within each calendar year and
requires an explicit prior December endpoint. It never interpolates missing
months, treats unavailable political control as a party label, or silently changes
return basis. It emits warnings for incomplete source coverage and stops before
writing a research dataset when a required rule fails.

`validate` writes machine-readable results with check IDs and severity. Tests cover
the stable rules above; no hard-coded return-level expectations are used because
source revisions can be legitimate and must be investigated rather than accepted
automatically.

For Shiller's historical context table, source-marked `NA` CAPE observations are
emitted as blank values, never as zero. The price observation remains available;
any analysis needing CAPE must explicitly exclude or otherwise handle those rows.
