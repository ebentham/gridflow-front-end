---
source: entsoe
dataset_key: congestion_management_costs
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Costs of Congestion Management (A92)

## Overview

Daily congestion-management costs paid by TSOs (in EUR) — the financial
total of redispatching plus countertrading actions per zone. Article 13.1.C
of Regulation (EC) 543/2013. Used to monetise congestion at the bidding-zone
level and as a target for congestion-cost forecast models.

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
| Historical depth | 2015 onward |
| Publication lag  | D-1 to weekly |
| Response format  | XML |

### ENTSO-E parameter tuple

| Field | Value |
|-------|-------|
| documentType | `A92` |
| processType | (none) |
| businessType (request) | (none) |
| domain-param-name | `in_Domain` only (single zone, `domain_style="zone"`) |

### Single-domain parameters (NOT cross-zonal)

A92 is **single-zone** despite the connector's `zone_pair`-style invocation
in some test paths. The official API treats `in_Domain` as the bidding zone
whose congestion costs are reported. The connector currently calls the API
with `in_Domain == out_Domain` (e.g. `10YGB----------A` for both) which
the server interprets as a single-zone request.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A92` | `A92` |
| `in_Domain` | str | Yes | Bidding zone EIC | `10YGB----------A` |
| `out_Domain` | str | (mirrored) | Same EIC as `in_Domain` | `10YGB----------A` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-congestion_management_costs.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A92&in_Domain=10YGB----------A&out_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/congestion_management_costs/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day) — published in EUR.

### Bronze sample

Live 2026-05-08: Acknowledgement, Reason 999 — `COSTS_OF_CONGESTION_MANAGEMENT_R3
[13.1.C] (10YGB----------A)`. A populated payload reports
`<quantity_Measure_Unit.name>EUR</quantity_Measure_Unit.name>` with
`<Point><quantity>...</quantity></Point>` carrying the daily cost.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/congestion_management_costs/year=YYYY/month=MM/congestion_management_costs_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.CongestionManagementCostsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketAmount`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | period + position | |
| `in_area_code` | `str` | No | `in_Domain.mRID` | Zone EIC |
| `out_area_code` | `str` | No | `out_Domain.mRID` | Mirrors `in_area_code` |
| `amount_eur` | `float` | No | `Point.quantity` | EUR (note: amount, not MW) |
| `business_type` | `str` | No | TS `businessType` | Default "" in canonical. |
| `resolution` | `str` | No | `Period.resolution` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | `"entsoe"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YGB----------A",
        "amount_eur": 125000.0,
        "business_type": "",
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

- **Currency, not power.** Use the `EntsoeTransmissionMarketAmount` schema
  (`amount_eur`) — the transformer correctly switches from `quantity_mw` to
  `amount_eur` via `_H6AmountTransformer`.
- Often published with weekly or longer cadence (not daily) — empty daily
  responses do not necessarily indicate the absence of cost.
- Single-zone (`domain_style=zone` per the `congestion_management_costs` entry in `endpoints.py`) — passing different
  `in_Domain`/`out_Domain` may be ignored or cause confusing empties.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A92, processType=none, businessType=none-in-request, domain=in_Domain only)`. Matches code — the `congestion_management_costs` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08 GB for 2026-05-06:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (publication cadence weekly/monthly; no GB cost record for that single day).
- A92 is the only `domain_style="zone"` dataset in this batch; matches advisor's note that A92 should NOT be treated as cross-zonal.

---

## Modelling notes

- Stitch with A63 + A91 to get the full congestion-management story —
  redispatch volumes, countertrading volumes, and the EUR-cost.
- Use as target for cost forecasting models conditioned on weather, NTC, and
  load-forecast features.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
