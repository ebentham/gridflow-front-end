---
source: entsoe
dataset_key: redispatching_cross_border
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Redispatching: Cross-Border (A63 / businessType A46)

## Overview

Cross-border redispatching activations — measures taken by neighbouring TSOs
to relieve transmission constraints by reducing generation in one zone and
increasing it in another. Article 13.1.A of Regulation (EC) 543/2013.
Used to study congestion frequency, redispatch costs, and as a feature for
forecasting flow constraints.

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
| Publication lag  | D-1 after settlement |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A63` |
| processType | (none) |
| businessType | `A46` (cross-border redispatch) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A63/A46 is directional. Use UK-centric pairs as for A11.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A63` | `A63` |
| `businessType` | str | Yes | `A46` for cross-border | `A46` |
| `in_Domain` | str | Yes | EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC `yyyymmddHHMM` | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-redispatching_cross_border.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A63&businessType=A46&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/redispatching_cross_border/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (in_Domain, out_Domain, day).

### Bronze sample

Live call 2026-05-08 (GB→FR, 2026-05-06): `Acknowledgement_MarketDocument`
with Reason 999 — `No matching data found for Data item
REDISPATCHING_CROSS_BORDER_R3 [13.1.A] (10YGB----------A,
10YFR-RTE------C)`. Populated payload would be a `Publication_MarketDocument`
with TimeSeries containing `<businessType>A46</businessType>` and a
`<flowDirection>` block per redispatch event.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/redispatching_cross_border/year=YYYY/month=MM/redispatching_cross_border_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.RedispatchingCrossBorderTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

Same as the H6 quantity envelope: `timestamp_utc`, `in_area_code`,
`out_area_code`, `quantity_mw`, `business_type`, `resolution`,
`data_provider`, `ingested_at`.

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T07:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 250.0,
        "business_type": "A46",
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

- **EMPTY-by-design for most days.** A63/A46 only publishes on days when a
  cross-border redispatch action was *executed*. The vast majority of GB-→-FR
  trading days have zero redispatch and return Reason 999.
- Sister dataset `redispatching_internal` differs **only** by `businessType`
  (A85 internal vs A46 cross-border). Keep both around — they are not aliases.
- Direction depends on which zone bore the increase vs decrease — cross-check
  TS `flowDirection` field when present.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A63, processType=none, businessType=A46, domain=in_Domain+out_Domain)`. Matches code `endpoints.py:158-164`.
- **Live validation 2026-05-08 GB→FR for 2026-05-06:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (no cross-border redispatch published that day, expected).
- Sanity check NL→DE for the same window also returned EMPTY — A46 cross-border events are inherently sparse, not a query-shape error.
- This dataset shares `documentType=A63` with `redispatching_internal`. Disambiguation: this page = **businessType=A46** (cross-border); sister page = **businessType=A85** (internal).

---

## Modelling notes

- Used as a *binary* feature (`redispatch_cross_border_present`) most often —
  presence of redispatch is rare and informative.
- Pair with `congestion_management_costs` (A92) for £/MWh impact estimation.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
