---
source: elexon
dataset_key: mid
vendor: Elexon BMRS
last_verified: 2026-05-21
layer_coverage: bronze, silver
v2_fix_history:
  - date: 2026-05-20
    phase: gridflow-G5-W1.2
    pr: https://github.com/EBentham/gridflow/pull/7
    change: silver transformer now also recognises current-API field names (dataProvider, price) alongside legacy (dataProviderId, midPrice)
---

# Elexon - Market Index Data (`MID`)

## Overview

Market Index Data — published reference prices and volumes from accredited Market Index Data Providers (MIDPs), used by the BSC to derive the Power Exchange Reference Price. MID is the wholesale-market anchor that ties Balancing Mechanism cash-out prices to traded GB power prices.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/MID` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Half-hourly, aligned with each settlement period. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | string | Yes | The "from" start time or settlement date for the filter. | `2026-05-06T00:00Z` |
| `to` | string | Yes | The "to" start time or settlement date for the filter. | `2026-05-06T03:00Z` |
| `settlementPeriodFrom` | integer | No | The "from" settlement period for the filter. This should be an integer from 1-50 inclusive. | `1` |
| `settlementPeriodTo` | integer | No | The "to" settlement period for the filter. This should be an integer from 1-50 inclusive. | `48` |
| `dataProviders` | array | No | The data providers to query. If no data provider is selected both will be displayed. | `APXMIDP` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/MID?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-mid.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/mid/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/MID?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "MID",
      "startTime": "2026-05-06T03:00:00Z",
      "dataProvider": "APXMIDP",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 9,
      "price": 105.43,
      "volume": 1892.45
    },
    {
      "dataset": "MID",
      "startTime": "2026-05-06T03:00:00Z",
      "dataProvider": "N2EXMIDP",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 9,
      "price": 0.0,
      "volume": 0.0
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/mid/year=YYYY/month=MM/mid_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.mid.MIDTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonMID`
**Dedup key**: _inline in transformer (see `silver/elexon/mid.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `data_provider_id` | `str` | Yes | `dataProviderId` (legacy) / `dataProvider` (current) | MIDP code (e.g. APXMIDP). G5-W1.2: live API renamed to `dataProvider` 2026-05; transformer renames both. |
| `market_index_price` | `float` | Yes | `midPrice` (legacy) / `price` (current) | GBP/MWh. G5-W1.2: live API renamed to `price` 2026-05; transformer renames both. |
| `market_index_volume` | `float` | Yes | `volume` | MWh. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 9,
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "data_provider_id": "...",
        "market_index_price": "...",
        "market_index_volume": 1892.45,
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

- **Multiple data providers** per period (APXMIDP, NORDPOOLMIDP). Silver dedup does not currently include `data_provider_id` — verify whether you want one row per (period, provider) or pre-pick a primary provider in gold.

---

## Implementation delta

- **Param style**: docs require `from`/`to`; code matches.

### V2-FIX changelog

- **2026-05-20 — gridflow G5-W1.2 (PR #7)**: live Elexon API now returns
  `dataProvider` / `price` rather than the original `dataProviderId` /
  `midPrice`. Silver transformer extended to rename both shapes; pre-G5
  silver carried `null` on `data_provider_id` and `market_index_price`
  because the live bronze didn't match the original rename map (P1
  silent-null bug).

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/mid.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
