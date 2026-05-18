---
source: elexon
dataset_key: fuelinst
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Instantaneous Generation Outturn by Fuel Type (`FUELINST`)

## Overview

Instantaneous (5-minute) generation outturn by fuel type (FUELINST) — the same fuel split as FUELHH but published at 5-minute resolution. FUELINST is what drives near-real-time stack-and-fuel monitoring; the half-hour aggregates feed FUELHH.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/FUELINST` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | 5-minute publication cadence. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for fuelinst. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for fuelinst. | `2026-05-06T03:00Z` |
| `settlementDateFrom` | string | No | As per Elexon Swagger spec for fuelinst. | `2026-05-06` |
| `settlementDateTo` | string | No | As per Elexon Swagger spec for fuelinst. | `2026-05-07` |
| `settlementPeriod` | array | No | List of Settlement Periods | `24` |
| `fuelType` | array | No | Fuel Type e.g. NUCLEAR | `CCGT` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-fuelinst.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/fuelinst/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "FUELINST",
      "publishTime": "2026-05-06T03:00:00Z",
      "startTime": "2026-05-06T02:55:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "fuelType": "BIOMASS",
      "generation": 2712
    },
    {
      "dataset": "FUELINST",
      "publishTime": "2026-05-06T03:00:00Z",
      "startTime": "2026-05-06T02:55:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "fuelType": "CCGT",
      "generation": 7527
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/fuelinst/year=YYYY/month=MM/fuelinst_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.fuelinst.FuelInstTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(timestamp_utc, fuel_type)`
**Point-in-time field**: `published_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, COAL, NUCLEAR, WIND, etc.). |
| `generation_mw` | `float` | No | `generation` | MW. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "fuel_type": "BIOMASS",
        "generation_mw": 2712,
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

- **5-minute resolution** — silver drops `settlement_date`/`settlement_period`. The instantaneous timestamp is `timestamp_utc` derived from `startTime`.

---

## Implementation delta

- **No Pydantic schema**: `schemas/elexon.py` has `ElexonGenerationByFuel` (used elsewhere) but no dedicated `ElexonFuelInst`. Silver `FuelInstTransformer` enforces inline.
- **`fuelinst` does not produce a settlement_date or settlement_period in silver output** — transformer drops those (output is `timestamp_utc`, `fuel_type`, `generation_mw`).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/fuelinst.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
