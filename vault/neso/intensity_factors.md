---
source: neso
dataset_key: intensity_factors
vendor: National Energy System Operator (NESO)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# NESO - Generation fuel emission factors (`intensity_factors`)

## Overview

This reference endpoint gives carbon intensity factors by fuel type. It explains how generation technologies are weighted inside the Carbon Intensity methodology and is useful for validating model-derived emissions estimates or deriving generation-mix carbon proxies. See [Carbon intensity](../../../20-domain/concepts/carbon-intensity.md) and [Settlement period](../../../20-domain/concepts/settlement-period.md).

---

## API endpoint

| Property | Value |
|----------|-------|
| Base URL | `https://api.carbonintensity.org.uk` |
| Path | `/intensity/factors` |
| Method | GET |
| Auth | None; send `Accept: application/json` |
| Rate limit | Not documented by NESO; Gridflow config uses 10 req/s. |
| Pagination | None. Dynamic inputs are path segments, not query parameters. |
| Historical depth | Static reference endpoint |
| Publication lag | Static reference data |
| Response format | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| None | - | - | No query string or path parameters. | - |

### Working curl example

```bash
curl --ssl-no-revoke -X GET \
  "https://api.carbonintensity.org.uk/intensity/factors" \
  -H "Accept: application/json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/neso/intensity_factors/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
**Format**: Raw JSON, as received. Immutable after write, with `.meta.json` provenance sidecar.
**Granularity**: One file per API call; range and daily routes may produce one file per chunk/day/period.

### Bronze sample

```json
{"data":[{"Gas (Combined Cycle)":394,"Wind":0,"Solar":0}]}
```

---

## Silver layer

**Path pattern**: `data/silver/neso/intensity_factors/intensity_factors.parquet`
**Transformer class**: `gridflow.silver.neso.carbon_intensity.IntensityFactorsTransformer`
**Pydantic schema**: `gridflow.schemas.neso.CarbonIntensityFactor`
**Dedup key**: `(fuel)`
**Point-in-time field**: `none`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| fuel | str | No | raw object key | Normalised to lowercase snake_case. |
| factor_gco2_kwh | float | Yes | raw object value | Fuel carbon factor in gCO2/kWh. |
| data_provider | str | No | derived | Always neso. |
| ingested_at | datetime[UTC] | No | derived | Silver transform timestamp. |

### Silver sample

```python
[{"fuel":"gas_combined_cycle","factor_gco2_kwh":394.0,"data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"},{"fuel":"wind","factor_gco2_kwh":0.0,"data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"}]
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

No discrepancies found.

---

## Modelling notes

Use as a static lookup to convert generation mix into approximate carbon intensity features. Version/staleness matters because factor changes can silently shift labels.

---

## Links

- [Official API docs](https://carbon-intensity.github.io/api-definitions/)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py)
- [Endpoint metadata](../../../../../../Python/gridflow/src/gridflow/connectors/neso/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/neso/carbon_intensity.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/neso.py)
- [Gold view/builder](../../../../../../Python/gridflow/src/gridflow/gold/views/uk_imbalance_context.sql)
- [Domain: Carbon intensity](../../../20-domain/concepts/carbon-intensity.md)

