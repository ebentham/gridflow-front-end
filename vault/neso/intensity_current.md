---
source: neso
dataset_key: intensity_current
vendor: National Energy System Operator (NESO)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# NESO - Current national carbon intensity (`intensity_current`)

## Overview

This dataset represents GB electricity carbon intensity in gCO2/kWh for half-hour market periods. It answers how carbon-heavy scheduled consumption is expected or estimated to be, which is useful as a target, feature, or regime indicator for price, balancing, demand, and carbon-aware scheduling models. See [Carbon intensity](../../../20-domain/concepts/carbon-intensity.md) and [Settlement period](../../../20-domain/concepts/settlement-period.md).

---

## API endpoint

| Property | Value |
|----------|-------|
| Base URL | `https://api.carbonintensity.org.uk` |
| Path | `/intensity` |
| Method | GET |
| Auth | None; send `Accept: application/json` |
| Rate limit | Not documented by NESO; Gridflow config uses 10 req/s. |
| Pagination | None. Dynamic inputs are path segments, not query parameters. |
| Historical depth | Current half-hour only |
| Publication lag | Forecast available ahead of real time; actual estimate lags real time, exact lag not documented |
| Response format | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| None | - | - | No query string or path parameters. | - |

### Working curl example

```bash
curl --ssl-no-revoke -X GET \
  "https://api.carbonintensity.org.uk/intensity" \
  -H "Accept: application/json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/neso/intensity_current/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
**Format**: Raw JSON, as received. Immutable after write, with `.meta.json` provenance sidecar.
**Granularity**: One file per API call; range and daily routes may produce one file per chunk/day/period.

### Bronze sample

```json
{"data":[{"from":"2024-01-15T00:00Z","to":"2024-01-15T00:30Z","intensity":{"forecast":245,"actual":239,"index":"moderate"}},{"from":"2024-01-15T00:30Z","to":"2024-01-15T01:00Z","intensity":{"forecast":250,"actual":248,"index":"moderate"}}]}
```

---

## Silver layer

**Path pattern**: `data/silver/neso/intensity_current/year=<YYYY>/month=<MM>/intensity_current_<YYYYMMDD>.parquet`
**Transformer class**: `gridflow.silver.neso.carbon_intensity.IntensityCurrentTransformer`
**Pydantic schema**: `gridflow.schemas.neso.CarbonIntensity`
**Dedup key**: `(timestamp_utc)`
**Point-in-time field**: `timestamp_utc`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | from | Half-hour period start. |
| period_end_utc | datetime[UTC] | Yes | to | Half-hour period end. |
| forecast_gco2_kwh | float | Yes | intensity.forecast | Forecast carbon intensity in gCO2/kWh. |
| actual_gco2_kwh | float | Yes | intensity.actual | Estimated actual carbon intensity in gCO2/kWh; often null before actuals publish. |
| intensity_index | str | No | intensity.index | One of very low, low, moderate, high, very high in docs; stored as string. |
| data_provider | str | No | derived | Always neso. |
| ingested_at | datetime[UTC] | No | derived | Silver transform timestamp. |

### Silver sample

```python
[{"timestamp_utc":"2024-01-15T00:00:00+00:00","period_end_utc":"2024-01-15T00:30:00+00:00","forecast_gco2_kwh":245.0,"actual_gco2_kwh":239.0,"intensity_index":"moderate","data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"},{"timestamp_utc":"2024-01-15T00:30:00+00:00","period_end_utc":"2024-01-15T01:00:00+00:00","forecast_gco2_kwh":250.0,"actual_gco2_kwh":248.0,"intensity_index":"moderate","data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"}]
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

- **Distinct from `carbon_intensity`**: see [carbon_intensity](./carbon_intensity.md). `intensity_current` calls `/intensity` (no path params, current half-hour only); `carbon_intensity` calls `/intensity/{from}/{to}` (range, 14-day cap). Both share `parser_family=ParserFamily.INTENSITY` and silver schema `gridflow.schemas.neso.CarbonIntensity`. The `endpoint` value in `config/sources.yaml` for `carbon_intensity` says `/intensity` but the connector overrides it through `connectors/neso/endpoints.py::ENDPOINTS` — the path template dict is the source of truth; the YAML field is unused at request time.

---

## Modelling notes

Use `forecast_gco2_kwh` as an ex-ante feature and `actual_gco2_kwh` as an ex-post target or label. Filter null actuals before supervised training, join by `timestamp_utc` to Elexon prices, demand, generation, weather, and interconnector features.

---

## Links

- [Official API docs](https://carbon-intensity.github.io/api-definitions/)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py)
- [Endpoint metadata](../../../../../../Python/gridflow/src/gridflow/connectors/neso/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/neso/carbon_intensity.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/neso.py)
- [Gold view/builder](../../../../../../Python/gridflow/src/gridflow/gold/views/uk_imbalance_context.sql)
- [Domain: Carbon intensity](../../../20-domain/concepts/carbon-intensity.md)

