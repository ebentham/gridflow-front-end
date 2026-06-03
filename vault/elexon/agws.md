---
source: elexon
dataset_key: agws
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Actual or Estimated Wind and Solar Power Generation (`AGWS / B1630`)

## Overview

Actual or Estimated Wind and Solar Power Generation (AGWS, ENTSO-E B1630) — wind/solar split of generation per settlement period. AGWS uses the same ENTSO-E PSR taxonomy as AGPT but is restricted to renewable categories.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/AGWS` |
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
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for agws. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for agws. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-agws.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/agws/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "AGWS",
      "documentId": "NGET-EMFIP-AGWS-20861078",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:58:21Z",
      "businessType": "Wind generation",
      "psrType": "Wind Onshore",
      "quantity": 1238.414,
      "startTime": "2026-05-06T00:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 4
    },
    {
      "dataset": "AGWS",
      "documentId": "NGET-EMFIP-AGWS-20861078",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:58:21Z",
      "businessType": "Wind generation",
      "psrType": "Wind Offshore",
      "quantity": 4153.834,
      "startTime": "2026-05-06T00:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 4
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/agws/year=YYYY/month=MM/agws_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.agws.AGWSTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonAGWS` — validated fail-soft on the full frame at write time (VTA-SCHEMA-01: invalid rows are logged and counted, never dropped).
**Dedup key**: `(settlement_date, settlement_period, psr_type)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `psr_type` | `str` | No | `psrType` | Elexon's human-readable PSR *label* (e.g. "Wind Onshore", "Wind Offshore"), stored as-is — NOT an ENTSO-E B-code. |
| `generation_mw` | `float` | No | `quantity` | MW. |
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
        "settlement_period": 4,
        "timestamp_utc": "2026-05-06T01:30:00+00:00",
        "psr_type": "Wind Onshore",
        "generation_mw": 1238.414,
        "business_type": "Wind generation",
        "document_id": "NGET-EMFIP-AGWS-20861078",
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

- **Same gotchas as AGPT** — limited to wind/solar PSR types.
- **Cross-source representation differs.** Elexon stores human-readable PSR *labels*; ENTSO-E's `wind_solar_forecast` stores the raw B-code. The same concept is represented two ways across sources — downstream joins must not assume a shared code domain.

---

## Implementation delta

- **Same B-series/ENTSO-E lineage** as AGPT (B1630).
- **Pydantic schema** `ElexonAGWS` exists in `schemas/elexon.py` and is applied via `BaseSilverTransformer._validate_against_schema` (fail-soft).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/agws.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
