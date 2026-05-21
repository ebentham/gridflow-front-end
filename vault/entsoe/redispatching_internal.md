---
source: entsoe
dataset_key: redispatching_internal
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Redispatching: Internal (A63 / businessType A85)

## Overview

Internal-zone redispatching activations — measures within a single bidding
zone to relieve internal grid constraints. Article 13.1.A of Regulation (EC)
543/2013. Sister dataset to `redispatching_cross_border`. Used in models of
internal congestion frequency, internal redispatch cost, and as a feature
for system-stress prediction.

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
| documentType | `A63` |
| processType | (none) |
| businessType | `A85` (internal redispatch) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair, but with `in_Domain == out_Domain` for internal) |

### Cross-zonal parameters

A63/A85 is logically per-zone; the connector uses `zone_pair` style with
`in_Domain == out_Domain` (e.g. GB→GB) so the same request signature handles
internal and external. Default UK-centric set: `(GB, GB)`, `(FR, FR)`,
`(NL, NL)`, etc.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A63` | `A63` |
| `businessType` | str | Yes | `A85` for internal | `A85` |
| `in_Domain` | str | Yes | Zone EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Same zone EIC | `10YGB----------A` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-redispatching_internal.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A63&businessType=A85&in_Domain=10YGB----------A&out_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000"
```

(Validation used GB→FR for the standard test border; production code calls
GB→GB / FR→FR per zone.)

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/redispatching_internal/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample

Live call 2026-05-08: Acknowledgement, Reason 999 —
`REDISPATCHING_INTERNAL_R3 [13.1.A] (10YGB----------A)`. A populated
response would carry TimeSeries with `<businessType>A85</businessType>`.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/redispatching_internal/year=YYYY/month=MM/redispatching_internal_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.RedispatchingInternalTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

Same H6 quantity envelope: `timestamp_utc`, `in_area_code`, `out_area_code`,
`quantity_mw`, `business_type`, `resolution`, `data_provider`, `ingested_at`.

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T17:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YGB----------A",
        "quantity_mw": 400.0,
        "business_type": "A85",
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

- **EMPTY-by-design** on most days for most zones — internal redispatch is
  event-driven.
- The Reason text for an empty response carries only one EIC
  (`(10YGB----------A)`) even though the request used both `in_Domain` and
  `out_Domain` — the API treats this as a single-zone query when in == out.
- Distinguished from `redispatching_cross_border` only by `businessType`.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A63, processType=none, businessType=A85, domain=in_Domain+out_Domain)`. Matches code `endpoints.py:165-171`.
- **Live validation 2026-05-08:** GB→FR (standard test border) returned Acknowledgement, Reason 999, single-zone interpretation `(10YGB----------A)`. **EMPTY** — cause: "border has zero allocation in window" (no internal GB redispatch published that day).
- Disambiguation: this page = **businessType=A85** (internal); sister page (`redispatching_cross_border`) = **businessType=A46**.

---

## Modelling notes

- Internal redispatch is the primary measure of in-zone constraint pressure.
  Useful as a daily count (`internal_redispatch_events_today`) regressor for
  imbalance-volatility models.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
