---
source: entsoe
dataset_key: countertrading
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Countertrading (A91)

## Overview

Countertrading actions between TSOs — explicit purchase of energy in one
zone and sale in another, contracted between TSOs to relieve cross-border
constraints. Article 13.1.B of Regulation (EC) 543/2013. Distinct from
A63 redispatching: countertrading uses a market trade rather than direct
generation control. Used in cross-border congestion-cost models and to
study the cost split between redispatch (A63) and countertrading (A91).

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
| Publication lag  | D-1 |
| Response format  | XML |

### ENTSO-E parameter tuple

| Field | Value |
|-------|-------|
| documentType | `A91` |
| processType | (none) |
| businessType (request) | (none) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A91 is between two zones. Use UK-centric border pairs from A11.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A91` | `A91` |
| `in_Domain` | str | Yes | Source zone EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Counterparty zone EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-countertrading.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A91&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/countertrading/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (in_Domain, out_Domain, day).

### Bronze sample

Live 2026-05-08: Acknowledgement, Reason 999 — `COUNTERTRADING_R3 [13.1.B]
(10YGB----------A, 10YFR-RTE------C)`. A populated payload is structurally
identical to A63 (TimeSeries with `<businessType>` describing the
countertrade direction).

---

## Silver layer

**Path pattern**: `data/silver/entsoe/countertrading/year=YYYY/month=MM/countertrading_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.CountertradingTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope: `timestamp_utc`, `in_area_code`, `out_area_code`,
`quantity_mw`, `business_type`, `resolution`, `data_provider`,
`ingested_at`.

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T18:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 200.0,
        "business_type": "",
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

- **EMPTY-by-design** for most days. Countertrading is a TSO-to-TSO action
  contracted only when warranted by congestion cost minimisation.
- A91 events tend to coincide with simultaneous A63 redispatch and A92
  congestion-cost publications.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A91, processType=none, businessType=none-in-request, domain=in_Domain+out_Domain)`. Matches code — the `countertrading` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08:** GB→FR for 2026-05-06 returned Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (no countertrading published that day, as expected).

---

## Modelling notes

- Combine with A63 redispatch and A92 cost data to study the *mix* of
  congestion-management instruments per border.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
