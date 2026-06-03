---
source: elexon
dataset_key: tsdfd
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - 2-14 Day Ahead Transmission System Demand Forecast (`TSDFD`)

## Overview

2-14 Day-Ahead Transmission System Demand Forecast (TSDFD) — daily-published medium-term TSDF forecast.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/TSDFD` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Daily publication for 2-14 day horizon. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for tsdfd. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for tsdfd. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/TSDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json" \
  -o "/tmp/elexon-tsdfd.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/tsdfd/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/TSDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "TSDFD",
      "publishTime": "2026-04-01T13:45:00Z",
      "forecastDate": "2026-04-03",
      "demand": 28450
    },
    {
      "dataset": "TSDFD",
      "publishTime": "2026-04-01T13:45:00Z",
      "forecastDate": "2026-04-04",
      "demand": 26750
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/tsdfd/year=YYYY/month=MM/tsdfd_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.tsdfd.TSDFDTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonTSDFD` — validated fail-soft on the full frame at write time (VTA-SCHEMA-01: invalid rows are logged and counted, never dropped).
**Dedup key**: `(forecast_date)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `forecast_date` | `date` | No | `forecastDate` | Forecast delivery date. |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `forecast_demand_mw` | `float` | Yes | `demand` | MW. |
| `published_at` | `datetime[UTC]` | Yes | `publishTime` | Publication timestamp from API. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "forecast_date": "2026-04-03",
        "timestamp_utc": "2026-04-03T00:00:00+00:00",
        "forecast_demand_mw": 28450,
        "published_at": "2026-04-01T13:45:00Z",
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

- **2-14 day horizon** with sparse publication. Use 1-day-or-wider query window.

---

## Implementation delta

- **Daily publication** — empty within 3-hour windows.
- **`forecast_date` rather than `settlement_date`** in silver output (no settlement_period — daily aggregate).
- **Pydantic schema** `ElexonTSDFD` exists in `schemas/elexon.py` and is applied via `BaseSilverTransformer._validate_against_schema` (fail-soft).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/tsdfd.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
