---
source: elexon
dataset_key: market_depth
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Settlement Market Depth (`MARKET-DEPTH`)

## Overview

Settlement Market Depth — per settlement period summary of indicative imbalance, offer/bid volumes, and accepted balancing volumes. Market depth aggregates BOALF, DISBSAD, and IMBALNGC into a single per-period snapshot useful for liquidity analytics.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/balancing/settlement/market-depth/{settlementDate}` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years (matches settlement records). |
| Publication lag  | Aligned with settlement run progression. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `settlementDate` | string | Yes | The settlement date for the filter. This must be in the format yyyy-MM-dd. | `2026-05-06` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/market-depth/2026-05-06?format=json" \
  -o "/tmp/elexon-market_depth.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/market_depth/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/market-depth/2026-05-06?format=json:

```json
{
  "metadata": {
    "datasets": [
      "IMBALNGC",
      "BOD",
      "DISEBSP",
      "DISPTAV"
    ]
  },
  "data": [
    {
      "settlementDate": "2026-05-06",
      "settlementPeriod": 1,
      "indicatedImbalance": 1122,
      "offerVolume": 60440.0,
      "bidVolume": -64830.0,
      "totalAcceptedOfferVolume": 578.0084677419355,
      "totalAcceptedBidVolume": -616.25,
      "pricedAcceptedOffersVolume": 0.0,
      "pricedAcceptedBidsVolume": -469.39166666666665
    },
    {
      "settlementDate": "2026-05-06",
      "settlementPeriod": 2,
      "indicatedImbalance": 656,
      "offerVolume": 60567.5,
      "bidVolume": -64840.0,
      "totalAcceptedOfferVolume": 605.8404121863799,
      "totalAcceptedBidVolume": -641.704550703696,
      "pricedAcceptedOffersVolume": 7.916666666666667,
      "pricedAcceptedBidsVolume": -531.5335829617604
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/market_depth/year=YYYY/month=MM/market_depth_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.market_depth.MarketDepthTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(settlement_date, settlement_period)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `indicated_imbalance_mwh` | `float` | Yes | `indicatedImbalance` | MWh. |
| `offer_volume_mwh` | `float` | Yes | `offerVolume` | MWh. |
| `bid_volume_mwh` | `float` | Yes | `bidVolume` | MWh. |
| `total_accepted_offer_volume_mwh` | `float` | Yes | `totalAcceptedOfferVolume` | MWh. |
| `total_accepted_bid_volume_mwh` | `float` | Yes | `totalAcceptedBidVolume` | MWh. |
| `total_adjustment_sell_volume_mwh` | `float` | Yes | `totalAdjustmentSellVolume` | MWh. |
| `total_adjustment_buy_volume_mwh` | `float` | Yes | `totalAdjustmentBuyVolume` | MWh. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 1,
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "indicated_imbalance_mwh": 1122,
        "offer_volume_mwh": 60440.0,
        "bid_volume_mwh": -64830.0,
        "total_accepted_offer_volume_mwh": 578.0084677419355,
        "total_accepted_bid_volume_mwh": -616.25,
        "total_adjustment_sell_volume_mwh": "...",
        "total_adjustment_buy_volume_mwh": "...",
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

- **Aggregates BOALF/DISBSAD/IMBALNGC** — don't double-count when joining with the underlying datasets.

---

## Implementation delta

- **Path**: same shape pattern as `system_prices` (date appended at request time).
- **No Pydantic schema in `schemas/elexon.py`** for market_depth — silver enforces the column set inline.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/market_depth.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
