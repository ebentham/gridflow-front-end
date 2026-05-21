---
source: elexon
dataset_key: windfor
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Wind Generation Forecast (`WINDFOR`)

## Overview

Wind Generation Forecast — published per settlement period. Each row carries an initial-issue forecast and a latest-issue forecast in MW. WINDFOR is the canonical GB wind forecast against which actual wind output (FUELHH) is benchmarked.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/WINDFOR` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Multiple publishes per day. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for windfor. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for windfor. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR?publishDateTimeFrom=2026-05-05T00:00Z&publishDateTimeTo=2026-05-06T00:00Z&format=json" \
  -o "/tmp/elexon-windfor.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/windfor/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR?publishDateTimeFrom=2026-05-05T00:00Z&publishDateTimeTo=2026-05-06T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "WINDFOR",
      "publishTime": "2026-05-05T23:30:00Z",
      "startTime": "2026-05-04T20:00:00Z",
      "generation": 2983
    },
    {
      "dataset": "WINDFOR",
      "publishTime": "2026-05-05T23:30:00Z",
      "startTime": "2026-05-04T21:00:00Z",
      "generation": 3046
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/windfor/year=YYYY/month=MM/windfor_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.wind_forecast.WindForecastTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonWindForecast`
**Dedup key**: _inline in transformer (see `silver/elexon/wind_forecast.py`)_
**Point-in-time field**: `published_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | Yes | `settlementDate` | Settlement date (BST/GMT calendar). Nullable per ElexonWindForecast. |
| `settlement_period` | `int` | Yes | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). Nullable per ElexonWindForecast. |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `initial_forecast_mw` | `float` | Yes | `initialForecast` | MW. |
| `latest_forecast_mw` | `float` | Yes | `latestForecast` or `generation` | MW. |
| `published_at` | `datetime` | Yes | `publishTime` | Publication time of the forecast (Canonical: ElexonWindForecast.published_at). |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "...",
        "settlement_period": "...",
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "initial_forecast_mw": "...",
        "latest_forecast_mw": 2983,
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

- **Sparse publication** — multiple publishes per day; not strictly half-hourly.
- **`initial_forecast_mw` vs `latest_forecast_mw`** — first published forecast vs most-recent revision.

---

## Implementation delta

- **Sparse publication cadence** — empty within 3-hour windows; required at-least-1-day window in V1 validation.
- **`ElexonWindForecast` schema** allows `settlement_date` and `settlement_period` to be `None`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/wind_forecast.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
