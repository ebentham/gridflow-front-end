---
source: neso
dataset_key: intensity_stats
vendor: National Energy System Operator (NESO)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# NESO - National carbon intensity statistics (`intensity_stats`)

## Overview

This dataset summarises GB carbon intensity over a requested time block rather than exposing every raw half hour. It answers how clean or carbon-heavy a period was in aggregate, useful for regime features, rolling labels, and QA against half-hour intensity series. See [Carbon intensity](../../../20-domain/concepts/carbon-intensity.md) and [Settlement period](../../../20-domain/concepts/settlement-period.md).

---

## API endpoint

| Property | Value |
|----------|-------|
| Base URL | `https://api.carbonintensity.org.uk` |
| Path | `/intensity/stats/{from}/{to}` |
| Method | GET |
| Auth | None; send `Accept: application/json` |
| Rate limit | Not documented by NESO; Gridflow config uses 10 req/s. |
| Pagination | None. Dynamic inputs are path segments, not query parameters. |
| Historical depth | TODO - official docs do not state earliest date; max 30 days per request |
| Publication lag | Derived from available intensity observations |
| Response format | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| from | string | Yes | Path parameter: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ | 2024-01-15T00:00Z |
| to | string | Yes | Path parameter: End datetime in ISO8601 format YYYY-MM-DDThh:mmZ | 2024-01-16T00:00Z |

### Working curl example

```bash
curl --ssl-no-revoke -X GET \
  "https://api.carbonintensity.org.uk/intensity/stats/2024-01-15T00:00Z/2024-01-16T00:00Z" \
  -H "Accept: application/json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/neso/intensity_stats/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
**Format**: Raw JSON, as received. Immutable after write, with `.meta.json` provenance sidecar.
**Granularity**: One file per API call; range and daily routes may produce one file per chunk/day/period.

### Bronze sample

```json
{"data":[{"from":"2024-01-15T00:00Z","to":"2024-01-16T00:00Z","intensity":{"max":250,"average":180,"min":120,"index":"moderate"}}]}
```

---

## Silver layer

**Path pattern**: `data/silver/neso/intensity_stats/year=<YYYY>/month=<MM>/intensity_stats_<YYYYMMDD>.parquet`
**Transformer class**: `gridflow.silver.neso.carbon_intensity.IntensityStatsTransformer`
**Pydantic schema**: `gridflow.schemas.neso.CarbonIntensityStats`
**Dedup key**: `(timestamp_utc, period_end_utc)`
**Point-in-time field**: `timestamp_utc`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | from | Stats block start. |
| period_end_utc | datetime[UTC] | Yes | to | Stats block end. |
| max_gco2_kwh | float | Yes | intensity.max | Maximum carbon intensity in block. |
| average_gco2_kwh | float | Yes | intensity.average | Average carbon intensity in block. |
| min_gco2_kwh | float | Yes | intensity.min | Minimum carbon intensity in block. |
| intensity_index | str | No | intensity.index | Docs category string. |
| data_provider | str | No | derived | Always neso. |
| ingested_at | datetime[UTC] | No | derived | Silver transform timestamp. |

### Silver sample

```python
[{"timestamp_utc":"2024-01-15T00:00:00+00:00","period_end_utc":"2024-01-16T00:00:00+00:00","max_gco2_kwh":250.0,"average_gco2_kwh":180.0,"min_gco2_kwh":120.0,"intensity_index":"moderate","data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"}]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- Official docs use UTC timestamps ending in `Z`; keep joins in UTC.
- The connector sends no query parameters; all documented inputs are path parameters.
- Actual carbon intensity values can be null or absent, especially before post-period estimates are available.
- For `intensity_period`, GB clock-change days can have 46 or 50 settlement periods in implementation even though official docs describe period 1-48.

---

## Implementation delta

- **`from` / `to` placeholders**: official docs and `config/sources.yaml` use `{from}` and `{to}`; `src/gridflow/connectors/neso/endpoints.py` uses `{from_dt}` and `{to_dt}` internally before formatting the same path.
- **`max_query_days`**: official docs allow 30 days for statistics; connector chunks with `max_query_days: 14`, which is conservative rather than incomplete.

---

## Modelling notes

Use averages/min/max as rolling carbon regime features. Do not mix block statistics with half-hour targets without aligning the block window and avoiding leakage.

---

## Links

- [Official API docs](https://carbon-intensity.github.io/api-definitions/)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py)
- [Endpoint metadata](../../../../../../Python/gridflow/src/gridflow/connectors/neso/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/neso/carbon_intensity.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/neso.py)
- [Gold view/builder](../../../../../../Python/gridflow/src/gridflow/gold/views/uk_imbalance_context.sql)
- [Domain: Carbon intensity](../../../20-domain/concepts/carbon-intensity.md)

