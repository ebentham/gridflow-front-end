---
source: entsoe
dataset_key: congestion_income
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Congestion Income (A25, businessType=B10)

## Overview

Income earned by TSOs from implicit allocations and flow-based market
coupling — the "congestion rent" arising from price differences across
constrained borders. Article 12.1.E of Regulation (EC) 543/2013. One of
**four A25 variants**, distinguished by `businessType=B10`. Used to study
implicit-allocation revenue, capacity-investment economics, and as the
counterpart to `auction_revenue` for explicit auctions.

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
| Publication lag  | After settlement |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A25` |
| processType | (none) |
| businessType | `B10` (implicit / flow-based congestion income) |
| `contract_MarketAgreement.Type` | `A01` (daily) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A25/B10 is directional. Default UK-centric pairs.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A25` | `A25` |
| `businessType` | str | Yes | `B10` | `B10` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` | `A01` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-congestion_income.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B10&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/congestion_income/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08: Acknowledgement, Reason 999 —
`IMPL_ALLOC_CONG_INCOME_FLOW_BASED [12.1.E] (10YGB----------A,
10YFR-RTE------C)`. Retried 30-day: also EMPTY.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/congestion_income/year=YYYY/month=MM/congestion_income_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.CongestionIncomeTransformer`
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
| `business_type` | `str` | No | TS `businessType` | Default "" in canonical. `B10`. |
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
        "amount_eur": 320000.0,
        "business_type": "B10",
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

- **EUR-amount**, uses `EntsoeTransmissionMarketAmount`.
- The data-item label `IMPL_ALLOC_CONG_INCOME_FLOW_BASED` confirms this is
  income from *implicit* and *flow-based* coupling (SDAC, CWE, Nordic), not
  from explicit auctions (which are `auction_revenue`).
- GB-FR (post-Brexit): GB no longer participates in flow-based coupling, so
  income is reported by the EU side only and may not appear under
  `in_Domain=GB`.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A25, processType=none, businessType=B10, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code `endpoints.py:269-279`.
- **Live validation 2026-05-08 GB→FR daily and 30-day:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (post-Brexit GB-FR is not in EU implicit / flow-based coupling).
- **Disambiguation from other A25 variants:**
  - `auction_revenue`: `businessType=B07`, EUR (revenue from **explicit** auctions).
  - `transfer_capacity_use`: `businessType=B05` + `Auction.Category=A01`, MW.
  - **`congestion_income`** (this page): `businessType=B10`, EUR (income from **implicit** / flow-based coupling).
  - `net_positions`: `businessType=B09`, **`domain_style=zone`** (single zone), MW.

---

## Modelling notes

- Pair with day-ahead-price spread = `price(out) − price(in)`; for an
  implicit-allocation border, congestion_income is theoretically related to
  `(price_spread × NTC_used)`. Useful as a reasonableness check on
  market-coupling outcomes.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
