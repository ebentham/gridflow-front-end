---
source: elexon
dataset_key: netbsad
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Net Balancing Services Adjustment Data (`NETBSAD`)

## Overview

Net Balancing Services Adjustment Data (NETBSAD) — net price-adjustment and volume-adjustment terms applied to BSP/SSP so the cash-out prices reflect the cost of balancing services other than energy actions in BOALF. NETBSAD is computed from the disaggregated DISBSAD components.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/NETBSAD` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Same cadence as system prices. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | string | Yes | The "from" start time or settlement date for the filter. | `2026-05-06T00:00Z` |
| `to` | string | Yes | The "to" start time or settlement date for the filter. | `2026-05-06T03:00Z` |
| `settlementPeriodFrom` | integer | No | The "from" settlement period for the filter. This should be an integer from 1-50 inclusive. | `1` |
| `settlementPeriodTo` | integer | No | The "to" settlement period for the filter. This should be an integer from 1-50 inclusive. | `48` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/NETBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-netbsad.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/netbsad/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/NETBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "NETBSAD",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 9,
      "netBuyPriceCostAdjustmentEnergy": 0.0,
      "netBuyPriceVolumeAdjustmentEnergy": 0.0,
      "netBuyPriceVolumeAdjustmentSystem": 0.0,
      "buyPricePriceAdjustment": 0.0,
      "netSellPriceCostAdjustmentEnergy": 0.0,
      "netSellPriceVolumeAdjustmentEnergy": 0.0,
      "netSellPriceVolumeAdjustmentSystem": 0.0,
      "sellPricePriceAdjustment": 0.0
    },
    {
      "dataset": "NETBSAD",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "netBuyPriceCostAdjustmentEnergy": 0.0,
      "netBuyPriceVolumeAdjustmentEnergy": 0.0,
      "netBuyPriceVolumeAdjustmentSystem": 0.0,
      "buyPricePriceAdjustment": 0.0,
      "netSellPriceCostAdjustmentEnergy": 0.0,
      "netSellPriceVolumeAdjustmentEnergy": 0.0,
      "netSellPriceVolumeAdjustmentSystem": 0.0,
      "sellPricePriceAdjustment": 0.0
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/netbsad/year=YYYY/month=MM/netbsad_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.netbsad.NETBSADTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: `(settlement_date, settlement_period)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `net_buy_price_adjustment` | `float` | Yes | `netBuyPriceAdjustment` | GBP/MWh adjustment to BSP. |
| `net_sell_price_adjustment` | `float` | Yes | `netSellPriceAdjustment` | GBP/MWh adjustment to SSP. |
| `net_buy_volume_adjustment` | `float` | Yes | `netBuyVolumeAdjustment` | MWh. |
| `net_sell_volume_adjustment` | `float` | Yes | `netSellVolumeAdjustment` | MWh. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 9,
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "net_buy_price_adjustment": "...",
        "net_sell_price_adjustment": "...",
        "net_buy_volume_adjustment": "...",
        "net_sell_volume_adjustment": "...",
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

- **Computed from DISBSAD** — the netting is at the API level. Local recomputation requires summing DISBSAD components; can disagree at edges due to rounding.

---

## Implementation delta

- **Param style**: docs require `from`/`to`; code matches.
- **No Pydantic schema** in `schemas/elexon.py`; silver transformer enforces shape.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/netbsad.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
