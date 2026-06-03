---
source: entsoe
dataset_key: auction_revenue
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Auction Revenue (A25, businessType=B07)

## Overview

Revenue earned by TSOs from explicit cross-border capacity auctions, in EUR
per zone-pair and trading horizon. Article 12.1.A of Regulation (EC) 543/2013.
This is one of **four A25-document variants**, distinguished from the others
by `(businessType, auction.Type)` combinations. Used to build the
TSO-revenue side of congestion-cost models and to value capacity rights.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s default |
| Pagination       | None |
| Historical depth | 2014-12-05 onward |
| Publication lag  | After auction settlement |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A25` |
| processType | (none) |
| businessType | `B07` (auction revenue) |
| `contract_MarketAgreement.Type` | `A01` (daily) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A25/B07 is directional. Use UK-centric border pairs from A11.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A25` | `A25` |
| `businessType` | str | Yes | `B07` | `B07` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` | `A01` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-auction_revenue.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B07&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/auction_revenue/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day or longer-horizon window).

### Bronze sample

Live 2026-05-08: Acknowledgement, Reason 999 — `AUCTION_REVENUE [12.1.A]
(10YGB----------A, 10YFR-RTE------C)`. Retried 30-day window: still EMPTY.
Sanity NL→DE 30-day: also EMPTY. Populated payload would mirror A92
congestion costs structure (Amount-based time series in EUR).

---

## Silver layer

**Path pattern**: `data/silver/entsoe/auction_revenue/year=YYYY/month=MM/auction_revenue_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.AuctionRevenueTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketAmount`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | period + position | |
| `in_area_code` | `str` | No | `in_Domain.mRID` | EIC |
| `out_area_code` | `str` | No | `out_Domain.mRID` | EIC |
| `amount_eur` | `float` | No | `Point.quantity` | EUR |
| `business_type` | `str` | No | TS `businessType` | Default "" in canonical. `B07`. |
| `resolution` | `str` | No | `Period.resolution` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | `"entsoe"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "amount_eur": 45000.0,
        "business_type": "B07",
        "resolution": "P1D",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:05:30Z",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **EUR-amount, not MW.** Uses `EntsoeTransmissionMarketAmount` schema — the
  H6 transformer correctly switches to `amount_eur` via `_H6AmountTransformer`.
- Publication is sparse — many GB borders publish auction revenue weekly or
  monthly rather than per-day.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A25, processType=none, businessType=B07, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code — the `auction_revenue` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08 GB→FR daily and 30-day:** Acknowledgement, Reason 999. Sanity NL→DE 30-day: also EMPTY. **EMPTY** — cause: "border has zero allocation in window" (auction-revenue publication cadence is sparser than daily; the test windows did not overlap a published settlement).
- **Disambiguation from other A25 variants** (critical because A25 multiplexes four datasets):
  - **`auction_revenue`** (this page): `businessType=B07`, `contract_MarketAgreement.Type=A01`, `domain_style=zone_pair` (cross-border revenue per border), unit EUR.
  - `transfer_capacity_use`: `businessType=B05` + `Auction.Category=A01` + `contract_MarketAgreement.Type=A01`, zone_pair, unit MW (capacity USE, not money).
  - `congestion_income`: `businessType=B10` + `contract_MarketAgreement.Type=A01`, zone_pair, unit EUR (income from implicit/flow-based allocation, not from explicit auctions).
  - `net_positions`: `businessType=B09` + `contract_MarketAgreement.Type=A01`, **`domain_style=zone`** (single zone, NOT zone_pair), unit MW (net implicit-auction position).

---

## Modelling notes

- Pair with `total_capacity_allocated` (A26/A29) to get implied
  £/MW for the auction product; useful for capacity-rights valuation.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
