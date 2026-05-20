---
source: neso
dataset_key: generation_pt24h
vendor: National Energy System Operator (NESO)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# NESO - National generation mix previous 24h (`generation_pt24h`)

## Overview

This dataset represents the GB generation mix share by fuel for each half hour. It answers what technologies are supplying electricity at a point in time and is a direct explanatory feature for carbon intensity, price regimes, and renewable penetration models. See [Carbon intensity](../../../20-domain/concepts/carbon-intensity.md) and [Settlement period](../../../20-domain/concepts/settlement-period.md).

---

## API endpoint

| Property | Value |
|----------|-------|
| Base URL | `https://api.carbonintensity.org.uk` |
| Path | `/generation/{from}/pt24h` |
| Method | GET |
| Auth | None; send `Accept: application/json` |
| Rate limit | Not documented by NESO; Gridflow config uses 10 req/s. |
| Pagination | None. Dynamic inputs are path segments, not query parameters. |
| Historical depth | Rolling previous 24h |
| Publication lag | As published by generation mix endpoint |
| Response format | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| from | string | Yes | Path parameter: Datetime in ISO8601 format YYYY-MM-DDThh:mmZ | 2024-01-15T00:00Z |

### Working curl example

```bash
curl --ssl-no-revoke -X GET \
  "https://api.carbonintensity.org.uk/generation/2024-01-15T00:00Z/pt24h" \
  -H "Accept: application/json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/neso/generation_pt24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
**Format**: Raw JSON, as received. Immutable after write, with `.meta.json` provenance sidecar.
**Granularity**: One file per API call; range and daily routes may produce one file per chunk/day/period.

### Bronze sample

```json
{"data":[{"from":"2026-04-21T23:30Z","to":"2026-04-22T00:00Z","generationmix":[{"fuel":"biomass","perc":8.7},{"fuel":"gas","perc":11.2},{"fuel":"wind","perc":46.1}]}]}
```

---

## Silver layer

**Path pattern**: `data/silver/neso/generation_pt24h/year=<YYYY>/month=<MM>/generation_pt24h_<YYYYMMDD>.parquet`
**Transformer class**: `gridflow.silver.neso.carbon_intensity.GenerationPt24HTransformer`
**Pydantic schema**: `gridflow.schemas.neso.GenerationMix`
**Dedup key**: `(timestamp_utc, fuel)`
**Point-in-time field**: `timestamp_utc`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | from | Half-hour period start. |
| period_end_utc | datetime[UTC] | Yes | to | Half-hour period end. |
| fuel | str | No | generationmix.fuel | Fuel type, e.g. gas, wind, solar. |
| generation_percentage | float | Yes | generationmix.perc | Share of generation mix in percent. |
| data_provider | str | No | derived | Always neso. |
| ingested_at | datetime[UTC] | No | derived | Silver transform timestamp. |

### Silver sample

```python
[{"timestamp_utc":"2026-04-21T23:30:00+00:00","period_end_utc":"2026-04-22T00:00:00+00:00","fuel":"biomass","generation_percentage":8.7,"data_provider":"neso","ingested_at":"2026-05-04T14:52:28+00:00"},{"timestamp_utc":"2026-04-21T23:30:00+00:00","period_end_utc":"2026-04-22T00:00:00+00:00","fuel":"wind","generation_percentage":46.1,"data_provider":"neso","ingested_at":"2026-05-04T14:52:28+00:00"}]
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

---

## Modelling notes

Use fuel percentages as features for carbon intensity, price, imbalance, and renewable regime models. Consider wide pivots by fuel and derived `clean_share`, `fossil_share`, `import_share`, and `renewable_share`.

---

## Links

- [Official API docs](https://carbon-intensity.github.io/api-definitions/)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py)
- [Endpoint metadata](../../../../../../Python/gridflow/src/gridflow/connectors/neso/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/neso/carbon_intensity.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/neso.py)
- [Gold view/builder](../../../../../../Python/gridflow/src/gridflow/gold/views/uk_imbalance_context.sql)
- [Domain: Carbon intensity](../../../20-domain/concepts/carbon-intensity.md)

