---
source: elexon
dataset_key: temp
vendor: Elexon BMRS
last_verified: 2026-05-21
layer_coverage: bronze, silver
v2_fix_history:
  - date: 2026-05-20
    phase: gridflow-G5-W1.4
    pr: https://github.com/EBentham/gridflow/pull/7
    change: silver transformer now carries vendor measurementDate through as `measurement_date` (Date)
  - date: 2026-05-20
    phase: gridflow-G5-W4
    pr: https://github.com/EBentham/gridflow/pull/7
    change: ElexonTemp Pydantic schema declared
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
**Pydantic schema**: `gridflow.schemas.elexon.ElexonTemp` (added 2026-05-20, gridflow G5-W4).
**Dedup key**: `(timestamp_utc)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `measurement_date` | `date` | No | `measurementDate` | G5-W1.4: vendor measurement-date carried through to silver. |
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
- **Pydantic schema declared** as of gridflow G5-W4: `ElexonTemp`.

### V2-FIX changelog

- **2026-05-20 — gridflow G5-W1.4 (PR #7)**: silver transformer now casts
  `measurementDate` to a Date column and includes it in `output_cols`.
  Previously the field was renamed but dropped before write — schema
  table claimed the field existed, code silently omitted it (P2
  schema-vs-output mismatch bug).
- **2026-05-20 — gridflow G5-W4 (PR #7)**: `ElexonTemp` Pydantic class
  added to `schemas/elexon.py`.

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
