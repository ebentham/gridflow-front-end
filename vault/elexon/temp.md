---
source: elexon
dataset_key: temp
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Temperature Data (`TEMP`)

## Overview

GB ambient temperature data — daily-published values used by NESO in demand-forecasting calibration. The dataset publishes one record per measurement date with the realised temperature plus seasonal-normal, low, and high reference values.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/TEMP` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Daily publication. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for temp. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for temp. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/TEMP?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json" \
  -o "/tmp/elexon-temp.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/temp/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/TEMP?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "TEMP",
      "measurementDate": "2026-04-01",
      "publishTime": "2026-04-01T15:45:00Z",
      "temperature": 10.6
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/temp/year=YYYY/month=MM/temp_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.temp.TempTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(timestamp_utc)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `publishDateTime` or `publishTime` | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `temperature` | `float` | Yes | `temperature` | Celsius — measured. |
| `normal_temperature` | `float` | Yes | `normal` | Celsius — seasonal normal. |
| `low_temperature` | `float` | Yes | `low` | Celsius — seasonal low. |
| `high_temperature` | `float` | Yes | `high` | Celsius — seasonal high. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-04-01T15:45:00Z",
        "temperature": 10.6,
        "normal_temperature": "...",
        "low_temperature": "...",
        "high_temperature": "...",
        "data_provider": "elexon",
        "ingested_at": "2026-05-08T12:00:00Z"
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Daily resolution** — one row per measurement date.
- **Reference temperatures** (normal/low/high) are seasonal climatology, not forecasts.

---

## Implementation delta

- **Daily publication** — empty within 3-hour windows.
- **No Pydantic schema** in `schemas/elexon.py`.
- **API field `measurementDate`** is not currently mapped to a silver field by the connector (`temp.py` mapping renames `publishDateTime → timestamp_utc`).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/temp.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
