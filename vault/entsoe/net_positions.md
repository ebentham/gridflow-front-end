---
source: entsoe
dataset_key: net_positions
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Implicit Auction Net Positions (A25, businessType=B09, single-zone)

## Overview

Net implicit-auction position per bidding zone, in MW — the algebraic sum
of cleared cross-zonal flows attributable to the zone after SDAC clearing.
Article 12.1.E of Regulation (EC) 543/2013. **The only A25 variant that
uses single-zone (`domain_style=zone`) parameters** rather than a
border-pair. Used as a feature for SDAC clearing analysis and zone-level
import/export economics.

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
| Publication lag  | After SDAC settlement |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A25` |
| processType | (none) |
| businessType | `B09` (implicit auction net position) |
| `contract_MarketAgreement.Type` | `A01` (daily) |
| domain-param-name | `in_Domain` only (`domain_style=zone`, single zone — connector mirrors `out_Domain` to `in_Domain`) |

### Single-domain parameters (NOT cross-zonal)

A25/B09 net_positions is **single-zone**. The connector's
`domain_style="zone"` (line `endpoints.py:284`) means `in_Domain` is the
zone whose net position is reported. The current curl form passes the same
EIC for both `in_Domain` and `out_Domain` to satisfy the connector's URL
builder.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A25` | `A25` |
| `businessType` | str | Yes | `B09` | `B09` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` | `A01` |
| `in_Domain` | str | Yes | Bidding zone EIC | `10YGB----------A` |
| `out_Domain` | str | (mirrored) | Same EIC | `10YGB----------A` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-net_positions.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B09&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/net_positions/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample

Live 2026-05-08 GB: Acknowledgement, Reason 999 —
`IMPLICIT_ALLOCATIONS_NET_POSITIONS [12.1.E] (10YGB----------A)` (note the
single EIC in the Reason text, confirming the single-zone interpretation).
Retried 30-day window: also EMPTY.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/net_positions/year=YYYY/month=MM/net_positions_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.NetPositionsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope. **Note**: the silver `out_area_code` will mirror
`in_area_code` since requests are single-zone.

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YGB----------A",
        "quantity_mw": -250.0,
        "business_type": "B09",
        "resolution": "PT60M",
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

- **Single-zone**, despite using a sister transformer that ordinarily handles
  zone-pair data. Set `in_Domain` only; the connector mirrors `out_Domain`
  internally.
- A negative `quantity_mw` indicates net export (zone is a net seller in
  SDAC clearing); positive = net import.
- Only published for SDAC zones. Post-Brexit GB is not in SDAC, so GB
  publishes EMPTY.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A25, processType=none, businessType=B09, contract_MarketAgreement.Type=A01, domain=in_Domain only — `domain_style=zone`)`. Matches code `endpoints.py:280-290`.
- **Live validation 2026-05-08 GB daily and 30-day:** Acknowledgement, Reason 999, single-EIC fingerprint `(10YGB----------A)`. **EMPTY** — cause: "border has zero allocation in window" (GB not in SDAC post-Brexit; would need a SDAC-participating zone to PASS).
- **Disambiguation from other A25 variants — this is the ONLY single-zone A25:**
  - `auction_revenue`: `businessType=B07`, zone_pair, EUR.
  - `transfer_capacity_use`: `businessType=B05` + `Auction.Category=A01`, zone_pair, MW.
  - `congestion_income`: `businessType=B10`, zone_pair, EUR.
  - **`net_positions`** (this page): `businessType=B09`, **`domain_style=zone`** (single zone), MW.

---

## Modelling notes

- Net position is the canonical measure of zone-level SDAC dependence.
  Useful as a regression target for "net importer / net exporter" regime
  classification models.
- For non-SDAC GB, surrogate via `cross_border_flows` (A11) summed across
  all interconnectors.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
