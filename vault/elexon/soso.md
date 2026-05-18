---
source: elexon
dataset_key: soso
vendor: Elexon BMRS
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Elexon - SO-SO Prices (Cross-Border Interconnector Trading) (`SOSO`)

## Overview

SO-SO prices — the prices and volumes traded between transmission system operators across GB interconnectors (Moyle, IFA, IFA2, BritNed, NSL, ElecLink, NEMO, Greenlink, Eleclink, Viking). SOSO is the canonical interconnector-trading reference series.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/SOSO` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Day-ahead and as trades are agreed. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for soso. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for soso. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/SOSO?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json" \
  -o "/tmp/elexon-soso.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/soso/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/SOSO?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "SOSO",
      "publishTime": "2026-05-06T23:03:10Z",
      "senderIdentification": "10X1001A1001A515",
      "receiverIdentification": "10X1001A1001A59Q",
      "contractIdentification": "NG_20260507_0100_32",
      "resourceProvider": "10X1001A1001A515",
      "tradeDirection": "Bid",
      "tradeQuantity": 25.0,
      "tradePrice": 120.27,
      "traderUnit": "EWIC_NG",
      "startTime": "2026-05-07T01:00:00Z",
      "endTime": "2026-05-07T02:00:00",
      "settlementDate": "2026-05-07"
    },
    {
      "dataset": "SOSO",
      "publishTime": "2026-05-06T23:03:10Z",
      "senderIdentification": "10X1001A1001A515",
      "receiverIdentification": "10X1001A1001A59Q",
      "contractIdentification": "NG_20260507_0100_31",
      "resourceProvider": "10X1001A1001A515",
      "tradeDirection": "Bid",
      "tradeQuantity": 25.0,
      "tradePrice": 114.27,
      "traderUnit": "EWIC_NG",
      "startTime": "2026-05-07T01:00:00Z",
      "endTime": "2026-05-07T02:00:00",
      "settlementDate": "2026-05-07"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/soso/year=YYYY/month=MM/soso_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.soso.SOSOTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: _inline in transformer (see `silver/elexon/soso.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `contract_identification` | `str` | No | `contractIdentification` | SOSO contract MRID. |
| `sender_identification` | `str` | Yes | `senderIdentification` | Sender TSO identifier. |
| `receiver_identification` | `str` | Yes | `receiverIdentification` | Receiver TSO identifier. |
| `resource_provider` | `str` | Yes | `resourceProvider` | Resource provider. |
| `trade_direction` | `str` | Yes | `tradeDirection` | Direction code (sell/buy). |
| `trade_quantity_mw` | `float` | Yes | `tradeQuantity` | MW. |
| `trade_price` | `float` | Yes | `tradePrice` | GBP/MWh. |
| `trader_unit` | `str` | Yes | `traderUnit` | Trader unit identifier. |
| `start_time` | `datetime[UTC]` | Yes | `startTime` | Trade start time. |
| `end_time` | `datetime[UTC]` | Yes | `endTime` | Trade end time. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-07",
        "settlement_period": "...",
        "timestamp_utc": "2026-05-07T00:00:00+00:00",
        "contract_identification": "NG_20260507_0100_32",
        "sender_identification": "10X1001A1001A515",
        "receiver_identification": "10X1001A1001A59Q",
        "resource_provider": "10X1001A1001A515",
        "trade_direction": "Bid",
        "trade_quantity_mw": 25.0,
        "trade_price": 120.27,
        "trader_unit": "EWIC_NG",
        "start_time": "2026-05-07T01:00:00Z",
        "end_time": "2026-05-07T02:00:00",
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

- **Max-1-day query window enforced** — see Implementation delta.
- **Per-interconnector**: the dataset covers all GB ICs; filter by `senderIdentification`/`receiverIdentification` in gold.

---

## Implementation delta

- **Vendor-enforced max 1-day query window — RESOLVED in V2 (2026-05-09).** `ENDPOINTS["soso"].max_chunk_hours = 23` matches the same fix applied to REMIT. Boundary re-verified live 2026-05-09: 23h request → HTTP 200, 25h request → HTTP 400. See gridflow commit `fix(V2-C):` and [remit.md](./remit.md#changelog).
- **No Pydantic schema** in `schemas/elexon.py`.

---

## Changelog

- **2026-05-09 — V2-FIX-03.** `max_chunk_hours=23` (paired with REMIT). See [remit.md](./remit.md#changelog) for shared evidence.
- **2026-05-08 — V1.** Live-validated; vendor 1-day cap surfaced.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/soso.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
