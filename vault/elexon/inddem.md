---
source: elexon
dataset_key: inddem
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Day and Day-Ahead Indicated Demand (`INDDEM`)

## Overview

Indicated Demand — the GB demand component of the NESO indicated-imbalance forecast. INDDEM, INDGEN, IMBALNGC, and MELNGC are published together to convey the day-ahead operational picture.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/INDDEM` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Day-ahead and intra-day. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `boundary` | string | No | As per Elexon Swagger spec for inddem. | `N` |
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for inddem. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for inddem. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/INDDEM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-inddem.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/inddem/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/INDDEM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "INDDEM",
      "demand": -46,
      "publishTime": "2026-05-06T02:47:00Z",
      "startTime": "2026-05-06T03:00:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 9,
      "boundary": "B1"
    },
    {
      "dataset": "INDDEM",
      "demand": -64,
      "publishTime": "2026-05-06T02:47:00Z",
      "startTime": "2026-05-06T03:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 10,
      "boundary": "B1"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/inddem/year=YYYY/month=MM/inddem_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.inddem.INDDEMTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonIndDem` — validated fail-soft on the full frame at write time (VTA-SCHEMA-01: invalid rows are logged and counted, never dropped).
**Dedup key**: _inline in transformer (see `silver/elexon/inddem.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `indicated_demand_mw` | `float` | Yes | `demand` | MW. |
| `boundary` | `str` | Yes | `boundary` | `N` (national) or `Z` (zonal). |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 9,
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "indicated_demand_mw": -46,
        "boundary": "B1",
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

- **Forecast revision behaviour** — multiple publishes per period; latest wins after dedup.

---

## Implementation delta

- **Pydantic schema** `ElexonIndDem` exists in `schemas/elexon.py` and is applied via `BaseSilverTransformer._validate_against_schema` (fail-soft).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/inddem.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
