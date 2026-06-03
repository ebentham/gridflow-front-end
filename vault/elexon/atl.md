---
source: elexon
dataset_key: atl
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Actual Total Load Per Bidding Zone (`ATL / B0610`)

## Overview

Actual Total Load Per Bidding Zone (ATL, ENTSO-E B0610) — the realised total load for the GB bidding zone per settlement period. ATL is what the EU transparency platform consumes for GB load.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/ATL` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Soon after each settlement period closes (B-series). |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for atl. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for atl. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/ATL?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-atl.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/atl/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/ATL?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "ATL",
      "documentId": "NGET-EMFIP-ATL-06475722",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:55:04Z",
      "startTime": "2026-05-06T01:00:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 5,
      "quantity": 25774.0
    },
    {
      "dataset": "ATL",
      "documentId": "NGET-EMFIP-ATL-06475721",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:25:04Z",
      "startTime": "2026-05-06T00:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 4,
      "quantity": 26368.0
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/atl/year=YYYY/month=MM/atl_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.atl.ATLTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonATL` — validated fail-soft on the full frame at write time (VTA-SCHEMA-01: invalid rows are logged and counted, never dropped).
**Dedup key**: `(settlement_date, settlement_period)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `total_load_mw` | `float` | No | `quantity` | MW. |
| `business_type` | `str` | Yes | `businessType` | ENTSO-E business type. |
| `document_id` | `str` | Yes | `documentId` | ENTSO-E document MRID. |
| `document_revision` | `int` | Yes | `documentRevisionNumber` | Document revision number. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 5,
        "timestamp_utc": "2026-05-06T02:00:00+00:00",
        "total_load_mw": 25774.0,
        "business_type": "...",
        "document_id": "NGET-EMFIP-ATL-06475722",
        "document_revision": 1,
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

- **Total load** is one number per period (no PSR split).

---

## Implementation delta

- **Same B-series** as AGPT (B0610).
- **Pydantic schema** `ElexonATL` exists in `schemas/elexon.py` and is applied via `BaseSilverTransformer._validate_against_schema` (fail-soft).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/atl.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
