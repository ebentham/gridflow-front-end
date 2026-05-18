---
source: elexon
dataset_key: fou2t14d
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - 2-14 Day Ahead Generation Availability by Fuel (`FOU2T14D`)

## Overview

2-14 day-ahead generation availability aggregated by fuel type (FOU2T14D). Issued daily, this dataset gives a fuel-resolved view of MW availability for each delivery date in the next two weeks. Used for medium-term margin and capacity-factor projections.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/FOU2T14D` |
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
| `fuelType` | array | No | As per Elexon Swagger spec for fou2t14d. | `CCGT` |
| `publishDate` | string | No | The publish date for filtering. This must be in the format yyyy-MM-dd. | `2026-05-06` |
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for fou2t14d. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for fou2t14d. | `2026-05-06T03:00Z` |
| `biddingZone` | array | No | As per Elexon Swagger spec for fou2t14d. | `GB` |
| `interconnector` | boolean | No | As per Elexon Swagger spec for fou2t14d. | `false` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/FOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-fou2t14d.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/fou2t14d/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/FOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "FOU2T14D",
      "fuelType": "BIOMASS",
      "publishTime": "2026-05-06T03:00:00Z",
      "systemZone": null,
      "forecastDate": "2026-05-08",
      "forecastDateTimezone": "Europe/London",
      "outputUsable": 2931,
      "biddingZone": null,
      "interconnectorName": null,
      "interconnector": false
    },
    {
      "dataset": "FOU2T14D",
      "fuelType": "CCGT",
      "publishTime": "2026-05-06T03:00:00Z",
      "systemZone": null,
      "forecastDate": "2026-05-08",
      "forecastDateTimezone": "Europe/London",
      "outputUsable": 22274,
      "biddingZone": null,
      "interconnectorName": null,
      "interconnector": false
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/fou2t14d/year=YYYY/month=MM/fou2t14d_YYYYMMDD_run<available_at>.parquet`
**Write mode**: append-only revision-preserving Silver files (`APPEND_ONLY = True`).
**Transformer class**: `gridflow.silver.elexon.fou2t14d.FOU2T14DTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: _inline in transformer (see `silver/elexon/fou2t14d.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` or `forecastDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, COAL, NUCLEAR, WIND, etc.). |
| `output_usable_mw` | `float` | No | `outputUsable` | MW. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-08",
        "settlement_period": "...",
        "timestamp_utc": "2026-05-08T00:00:00+00:00",
        "fuel_type": "BIOMASS",
        "output_usable_mw": 2931,
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

- **Forecast horizon**: data is for delivery dates 2-14 days ahead. The settlement_date in silver is the *future delivery date*, not the publish date.

---

## Implementation delta

- **`forecastDate → settlement_date` mapping**: API uses `forecastDate` for the future delivery date; silver renames to `settlement_date` to match the canonical schema column.
- **No Pydantic schema** in `schemas/elexon.py`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/fou2t14d.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
