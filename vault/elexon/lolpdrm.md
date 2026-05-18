---
source: elexon
dataset_key: lolpdrm
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Loss of Load Probability and De-Rated Margin (`LOLPDRM`)

## Overview

Loss of Load Probability and De-Rated Margin (LOLPDRM) — the day-ahead reliability metrics published per settlement period. LOLP is the probability that demand exceeds available generation; de-rated margin is available MW above expected demand after de-rating intermittent capacity. These are the canonical operational reliability signals.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/LOLPDRM` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Day-ahead publication. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for lolpdrm. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for lolpdrm. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/LOLPDRM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-lolpdrm.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/lolpdrm/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/LOLPDRM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "LOLPDM",
      "publishTime": "2026-05-06T02:34:22Z",
      "publishingPeriodCommencingTime": "2026-05-06T02:30:00Z",
      "startTime": "2026-05-07T03:30:00Z",
      "settlementDate": "2026-05-07",
      "settlementPeriod": 10,
      "lossOfLoadProbability": 0.0,
      "deratedMargin": 17769.74
    },
    {
      "dataset": "LOLPDM",
      "publishTime": "2026-05-06T02:34:22Z",
      "publishingPeriodCommencingTime": "2026-05-06T02:30:00Z",
      "startTime": "2026-05-07T03:00:00Z",
      "settlementDate": "2026-05-07",
      "settlementPeriod": 9,
      "lossOfLoadProbability": 0.0,
      "deratedMargin": 17801.912
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/lolpdrm/year=YYYY/month=MM/lolpdrm_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.lolpdrm.LOLPDRMTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(settlement_date, settlement_period)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `loss_of_load_probability` | `float` | No | `lossOfLoadProbability` | Probability 0..1. |
| `derated_margin_mw` | `float` | No | `deratedMargin` | MW. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-07",
        "settlement_period": 10,
        "timestamp_utc": "2026-05-07T04:30:00+00:00",
        "loss_of_load_probability": 0.0,
        "derated_margin_mw": 17769.74,
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

- **De-rated margin** is post-derating intermittent capacity; differs from MELNGC's indicated margin.
- **LOLP unit**: probability (dimensionless 0..1).

---

## Implementation delta

- **No Pydantic schema** in `schemas/elexon.py`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/lolpdrm.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
