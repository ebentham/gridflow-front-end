---
source: elexon
dataset_key: agpt
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Actual Aggregated Generation Per Type (`AGPT / B1620`)

## Overview

Actual Aggregated Generation Per Type (AGPT, ENTSO-E B1620) — every PSR (Production-Storage Resource) type's aggregated MW output per settlement period. AGPT is the GB equivalent of the ENTSO-E B1620 series and is what feeds the GB row of pan-European generation transparency dashboards.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/AGPT` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years (since B-series rollout). |
| Publication lag  | Soon after each settlement period closes (B-series). |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for agpt. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for agpt. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-agpt.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/agpt/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "AGPT",
      "documentId": "NGET-EMFIP-AGPT-06476951",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:59:22Z",
      "businessType": "Production",
      "psrType": "Biomass",
      "quantity": 2974.0,
      "startTime": "2026-05-06T00:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 4
    },
    {
      "dataset": "AGPT",
      "documentId": "NGET-EMFIP-AGPT-06476951",
      "documentRevisionNumber": 1,
      "publishTime": "2026-05-06T02:59:22Z",
      "businessType": "Production",
      "psrType": "Hydro Pumped Storage",
      "quantity": 1.0,
      "startTime": "2026-05-06T00:30:00Z",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 4
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/agpt/year=YYYY/month=MM/agpt_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.agpt.AGPTTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(settlement_date, settlement_period, psr_type)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `psr_type` | `str` | No | `psrType` | ENTSO-E PSR type code. |
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
        "psr_type": "Biomass",
        "generation_mw": 2974.0,
        "business_type": "Production",
        "document_id": "NGET-EMFIP-AGPT-06476951",
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

- **PSR types** follow ENTSO-E codelist (B01-B25). Silver preserves codes; map to friendly names in gold.
- **`document_revision`** — same period+psr_type can be re-issued; latest revision wins.

---

## Implementation delta

- **No Pydantic schema** in `schemas/elexon.py`; silver enforces ENTSO-E PSR-typed output (`psr_type`, `business_type`, `document_id`, `document_revision`).
- **B-series (B1620)** — payload follows ENTSO-E document/timeseries shape but exposed via Elexon's flattened JSON.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/agpt.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
