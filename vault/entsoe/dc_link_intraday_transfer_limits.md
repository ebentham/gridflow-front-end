---
source: entsoe
dataset_key: dc_link_intraday_transfer_limits
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — DC Link Intraday Transfer Limits (A93)

## Overview

Intraday transfer-limit values for DC interconnector links (e.g. IFA, BritNed,
NSL, Viking Link, IFA2, ElecLink, NEMO). Article 11.3 of Regulation (EC)
543/2013. Limits are typically updated within the trading day as DC link
operators reassess capability against ramp constraints, AC system state, and
maintenance. Used as a real-time feature for short-horizon flow models.

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
| Historical depth | 2014-12-05 onward (intraday updates only published when capability changes) |
| Publication lag  | Intraday revisions throughout the trading day |
| Response format  | XML |

### ENTSO-E parameter tuple

| Field | Value |
|-------|-------|
| documentType | `A93` |
| processType | (none) |
| businessType (request) | (none) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A93 is per-DC-link (border-pair). Same default UK-centric border table as
A11 / A61.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A93` | `A93` |
| `in_Domain` | str | Yes | EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC `yyyymmddHHMM` | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-dc_link_intraday_transfer_limits.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A93&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/dc_link_intraday_transfer_limits/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (in_Domain, out_Domain, day).

### Bronze sample

Live call on 2026-05-08 returned `Acknowledgement_MarketDocument` with
Reason 999 — `No matching data found for Data item
CB_CAPACITY_FOR_DC_LINKS_INTRADAY_R3 [11.3] (10YGB----------A,
10YFR-RTE------C)`. A populated response would mirror A61 structure with
`<businessType>A28</businessType>` and one or more revised intraday limits.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/dc_link_intraday_transfer_limits/year=YYYY/month=MM/dc_link_intraday_transfer_limits_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.DcLinkIntradayTransferLimitsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | period + position | |
| `in_area_code` | `str` | No | `in_Domain.mRID` | EIC |
| `out_area_code` | `str` | No | `out_Domain.mRID` | EIC |
| `quantity_mw` | `float` | No | `Point.quantity` | DC link transfer limit MW |
| `business_type` | `str` | No | TS `businessType` | Default "" in canonical. Usually `A28`. |
| `resolution` | `str` | No | `Period.resolution` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | `"entsoe"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T13:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 1850.0,
        "business_type": "A28",
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

- **EMPTY-by-design for many borders.** Article 11.3 only requires a publication
  when a DC link operator revises a previously published intraday limit. A
  PT24H "no revisions" day returns `Acknowledgement_MarketDocument` with
  Reason 999 (`No matching data found`).
- The Reason text spells the article reference: `[11.3]` and the data-item
  string `CB_CAPACITY_FOR_DC_LINKS_INTRADAY_R3` — useful diagnostic.
- Variable resolution and asymmetric publication times — silver does not
  align across borders.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A93, processType=none, businessType=none-in-request, domain=in_Domain+out_Domain)`. Matches code — the `dc_link_intraday_transfer_limits` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08 GB→FR for 2026-05-06:** Acknowledgement, Reason 999, no data published. **EMPTY** — cause: "border has zero allocation in window" (no DC-link revision recorded that day).
- Empty result is expected and not a code defect; consumers should treat absence as "no revision" rather than 0.

---

## Modelling notes

- Intraday limit revisions are rare events — feature engineer as
  `limit_revision_present_today` (binary) and `limit_diff_vs_ntc` (delta from
  the day-ahead A61 NTC) when present.
- Useful in cascade-failure / outage models where DC ramp limits matter.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
