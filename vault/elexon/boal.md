---
source: elexon
dataset_key: boal
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Bid Offer Acceptance Level Flagged (`BOALF`)

## Overview

Bid Offer Acceptance Levels Flagged (BOALF) — every accepted bid or offer instruction issued by the National Electricity System Operator (NESO) to a Balancing Mechanism Unit. Each acceptance carries level-from / level-to MW values that fully describe how the unit's output was redispatched. BOALF is the row-level audit trail behind the headline BSC settlement numbers and is a primary feature for any BM-unit dispatch model.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/BOALF` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Near real-time as acceptance instructions are issued. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | string | Yes | The "from" start time or settlement date for the filter. | `2026-05-06T00:00Z` |
| `to` | string | Yes | The "to" start time or settlement date for the filter. | `2026-05-06T03:00Z` |
| `settlementPeriodFrom` | integer | No | The "from" settlement period for the filter. This should be an integer from 1-50 inclusive. | `1` |
| `settlementPeriodTo` | integer | No | The "to" settlement period for the filter. This should be an integer from 1-50 inclusive. | `48` |
| `bmUnit` | array | No | The BM units to query. Add each unit separately. If no BM unit is selected all BM units will be displayed. | `T_DRAXX-1` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/BOALF?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-boal.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/boal/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/BOALF?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "BOALF",
      "settlementDate": "2026-05-06",
      "settlementPeriodFrom": 9,
      "settlementPeriodTo": 10,
      "timeFrom": "2026-05-06T03:00:00Z",
      "timeTo": "2026-05-06T03:30:00Z",
      "levelFrom": 480,
      "levelTo": 480,
      "acceptanceNumber": 217257,
      "acceptanceTime": "2026-05-06T02:31:00Z",
      "deemedBoFlag": false,
      "soFlag": true,
      "amendmentFlag": "ORI",
      "storFlag": false,
      "rrFlag": false,
      "nationalGridBmUnit": "MRWD-1",
      "bmUnit": "T_MRWD-1"
    },
    {
      "dataset": "BOALF",
      "settlementDate": "2026-05-06",
      "settlementPeriodFrom": 9,
      "settlementPeriodTo": 9,
      "timeFrom": "2026-05-06T03:00:00Z",
      "timeTo": "2026-05-06T03:14:00Z",
      "levelFrom": -2,
      "levelTo": -2,
      "acceptanceNumber": 1170,
      "acceptanceTime": "2026-05-06T02:46:00Z",
      "deemedBoFlag": false,
      "soFlag": false,
      "amendmentFlag": "ORI",
      "storFlag": false,
      "rrFlag": false,
      "nationalGridBmUnit": "AG-DUKP08",
      "bmUnit": "2__DUKPR008"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/boal/year=YYYY/month=MM/boal_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.boal.BOALTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonBOAL`
**Dedup key**: _inline in transformer (see `silver/elexon/boal.py`)_
**Point-in-time field**: `acceptance_time`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` or `settlementPeriodFrom` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `bm_unit_id` | `str` | No | `bmUnit` | BM Unit identifier — preserve raw casing. |
| `acceptance_number` | `int` | Yes | `acceptanceNumber` | Acceptance instruction number. |
| `acceptance_time` | `datetime[UTC]` | Yes | `acceptanceTime` | Time the acceptance was issued. |
| `deem_flag` | `bool` | No | `deemedBoFlag` | Deemed-bid/offer flag. |
| `so_flag` | `bool` | No | `soFlag` | System Operator flag. |
| `stor_flag` | `bool` | No | `storProviderFlag` or `storFlag` | STOR flag. |
| `rr_flag` | `bool` | No | `rrFlag` | Replacement Reserve flag. |
| `bid_offer_level_from` | `float` | Yes | `levelFrom` | MW. |
| `bid_offer_level_to` | `float` | Yes | `levelTo` | MW. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 9,
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "bm_unit_id": "T_MRWD-1",
        "acceptance_number": 217257,
        "acceptance_time": "2026-05-06T02:31:00Z",
        "deem_flag": false,
        "so_flag": true,
        "stor_flag": false,
        "rr_flag": false,
        "bid_offer_level_from": 480,
        "bid_offer_level_to": 480,
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

- **BM Unit IDs**: keep raw casing (e.g. `T_DRAXX-1`); do NOT normalise.
- **`settlementPeriodFrom`/`settlementPeriodTo`**: a single acceptance can span multiple periods. Silver maps `settlementPeriodFrom → settlement_period` (loses span info). Long-acceptance records may be deduped against shorter overlapping ones.
- **Acceptance number** is non-unique across (date, BM unit) — required for proper deduplication.

---

## Implementation delta

- **Path rename**: vault `endpoints.md` (pre-V1) listed path as `/datasets/BOAL`; docs and code use `/datasets/BOALF` (vendor renamed BOAL → BOALF). Vault page now corrected. Old `bod` and the original `boal` are in `EXCLUDED_ENDPOINTS`.
- **Param style**: docs require `from`/`to` (NOT `publishDateTimeFrom/To`); code uses `from_param="from", to_param="to"` — matches docs.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/boal.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
