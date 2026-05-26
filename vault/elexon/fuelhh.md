---
source: elexon
dataset_key: fuelhh
vendor: Elexon BMRS
last_verified: 2026-05-21
layer_coverage: bronze, silver
v2_fix_history:
  - date: 2026-05-20
    phase: gridflow-G5-W2.2
    pr: https://github.com/EBentham/gridflow/pull/7
    change: silver transformer now casts `published_at` to UTC datetime and includes it in output_cols (previously renamed but silently dropped before write)
---

# Elexon - Half-Hourly Generation Outturn by Fuel Type (`FUELHH`)

## Overview

Half-hourly generation outturn aggregated by fuel type (FUELHH) — the realised MWh in each settlement period split by fuel category (CCGT, coal, nuclear, wind, solar, biomass, etc.). FUELHH is the canonical observation series for GB generation mix and underpins capacity-factor analytics and emissions reporting.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/FUELHH` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Soon after each settlement period closes. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | No | As per Elexon Swagger spec for fuelhh. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | No | As per Elexon Swagger spec for fuelhh. | `2026-05-06T03:00Z` |
| `settlementDateFrom` | string | No | As per Elexon Swagger spec for fuelhh. | `2026-05-06` |
| `settlementDateTo` | string | No | As per Elexon Swagger spec for fuelhh. | `2026-05-07` |
| `settlementPeriod` | array | No | List of Settlement Periods | `24` |
| `fuelType` | array | No | Fuel Type e.g. NUCLEAR | `CCGT` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-fuelhh.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/fuelhh/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "FUELHH",
      "publishTime": "2026-05-06T03:00:00Z",
      "startTime": "2026-05-06T02:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "fuelType": "BIOMASS",
      "generation": 2821
    },
    {
      "dataset": "FUELHH",
      "publishTime": "2026-05-06T03:00:00Z",
      "startTime": "2026-05-06T02:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "fuelType": "CCGT",
      "generation": 7729
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/fuelhh/year=YYYY/month=MM/fuelhh_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.fuelhh.FuelHHTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonFuelHH`
**Dedup key**: `(settlement_date, settlement_period, fuel_type)`
**Point-in-time field**: `published_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, COAL, NUCLEAR, WIND, etc.). |
| `generation_mw` | `float` | No | `generation` | MW. |
| `published_at` | `datetime[UTC]` | Yes | `publishDateTime` (also `publishTime`) | Publication time. G5-W2.2: now cast to UTC-aware datetime and included in `output_cols`; previously the rename produced the column but it was dropped before write. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 8,
        "timestamp_utc": "2026-05-06T03:30:00+00:00",
        "fuel_type": "BIOMASS",
        "generation_mw": 2821,
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

- **Settlement period range 1..50** — DST handling required.
- **`fuelType` casing**: API returns uppercase (CCGT, COAL); transformer preserves casing.

---

## Implementation delta

- **No documented `from_param`/`to_param` override** needed — connector uses default `publishDateTimeFrom/To` which docs accept (alongside `settlementDateFrom/To`).
- **Schema**: `ElexonFuelHH` declared and matches silver output.

### V2-FIX changelog

- **2026-05-20 — gridflow G5-W2.2 (PR #7)**: silver transformer now casts
  `published_at` (renamed from `publishDateTime`) to a UTC-aware datetime
  and includes it in `output_cols`. Previously the column was renamed but
  the `select(output_cols)` step dropped it before write — schema declared
  `published_at: datetime | None` but Parquet never carried it (W2.2
  schema-vs-output silent-drop pattern). Acceptance test
  `test_published_at_emitted_when_bronze_carries_it` pins the fix.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/fuelhh.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
