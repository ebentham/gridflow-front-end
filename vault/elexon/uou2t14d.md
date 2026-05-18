---
source: elexon
dataset_key: uou2t14d
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - 2-14 Day Ahead Generation Availability by BM Unit (`UOU2T14D`)

## Overview

2-14 day-ahead generation availability per BM Unit (UOU2T14D). The unit-level companion of FOU2T14D — every BM Unit's declared availability MW for every settlement period 2-14 days ahead. The vendor enforces a maximum 4-hour query window so the connector chunks requests accordingly.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/UOU2T14D` |
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
| `fuelType` | array | No | The fuel type to query. Add each fuel type separately. If no fuel types are supplied, all fuel types will be returned. | `CCGT` |
| `publishDateTimeFrom` | string | No | Start of the Publish Time range to query. If specified, PublishDateTimeTo must also be specified.
If both are omitted, latest published data is returned. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | End of the Publish Time range to query. If specified, PublishDateTimeFrom must also be specified.
If both are omitted, latest published data is returned. | `2026-05-06T03:00Z` |
| `bmUnit` | array | No | The BM units to query. Add each unit separately. Either the Elexon ID or the National Grid ID can be used.
If no BM unit is supplied all BM units will be returned. | `T_DRAXX-1` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/UOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-uou2t14d.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/uou2t14d/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/UOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "UOU2T14D",
      "fuelType": "BIOMASS",
      "nationalGridBmUnit": "DNBAR-1",
      "bmUnit": "2__NSMAE001",
      "publishTime": "2026-05-06T03:00:00Z",
      "forecastDate": "2026-05-08",
      "outputUsable": 36
    },
    {
      "dataset": "UOU2T14D",
      "fuelType": "BIOMASS",
      "nationalGridBmUnit": "DRAXX-1",
      "bmUnit": "T_DRAXX-1",
      "publishTime": "2026-05-06T03:00:00Z",
      "forecastDate": "2026-05-08",
      "outputUsable": 660
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/uou2t14d/year=YYYY/month=MM/uou2t14d_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.uou2t14d.UOU2T14DTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: _inline in transformer (see `silver/elexon/uou2t14d.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` or `forecastDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `bm_unit_id` | `str` | No | `bmUnit` | BM Unit identifier — preserve raw casing. |
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
        "bm_unit_id": "2__NSMAE001",
        "output_usable_mw": 36,
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

- **Vendor max-chunk-hours = 4** — wider queries return HTTP 400.
- **High row count** — multi-hundred-thousand rows for a single 4-hour query × 2-week horizon.

---

## Implementation delta

- **API max-chunk 4 hours**: `ElexonEndpoint.max_chunk_hours = 4` — connector enforces, vendor returns 400 for wider ranges.
- **`forecastDate → settlement_date`** mapping (same as FOU2T14D).
- **No Pydantic schema** in `schemas/elexon.py`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/uou2t14d.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
