---
source: elexon
dataset_key: ndfd
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - National Demand Forecast (2-14 Day Ahead) (`NDFD`)

## Overview

National Demand Forecast (2–14 days ahead) — daily-issued demand forecast published for each delivery date 2–14 days into the future. NDFD provides the medium-term demand outlook used in capacity-margin and spark-spread analytics.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/NDFD` |
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
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for ndfd. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for ndfd. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/NDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json" \
  -o "/tmp/elexon-ndfd.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/ndfd/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/NDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "NDFD",
      "publishTime": "2026-04-01T13:45:00Z",
      "forecastDate": "2026-04-03",
      "demand": 27850
    },
    {
      "dataset": "NDFD",
      "publishTime": "2026-04-01T13:45:00Z",
      "forecastDate": "2026-04-04",
      "demand": 26150
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/ndfd/year=YYYY/month=MM/ndfd_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.demand_forecast.DemandForecastTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonDemandForecast`
**Dedup key**: _inline in transformer (see `silver/elexon/demand_forecast.py`)_
**Point-in-time field**: `issue_time`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `forecast_type` | `str` | No | _derived_ | `day_ahead` (NDF) or `2_14_day` (NDFD). |
| `national_demand_mw` | `float` | Yes | `nationalDemand` or `demand` | MW. |
| `transmission_demand_mw` | `float` | Yes | `transmissionSystemDemand` | MW. |
| `issue_time` | `datetime[UTC]` | Yes | _TODO_ | Forecast issue time. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "...",
        "settlement_period": "...",
        "timestamp_utc": "2026-04-03T00:00:00+00:00",
        "forecast_type": "2_14_day",
        "national_demand_mw": 27850,
        "transmission_demand_mw": "...",
        "issue_time": "...",
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

- **No `settlementPeriod`** in API — silver fills with placeholder 1 (full daily aggregate). Don't join NDFD on settlement_period — join on `forecast_date`.

---

## Implementation delta

- **Shared transformer** with NDF — see `ndf` page. NDFD records may not carry `settlementPeriod` in the API response; transformer fills with placeholder period 1 + `forecast_date → settlement_date`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/demand_forecast.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
