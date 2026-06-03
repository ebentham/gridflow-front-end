---
source: entsoe
dataset_key: outages_offshore_grid
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Unavailability of offshore grid infrastructure (A79)

## Overview

Outage notifications for offshore grid assets — offshore HV cables, hub
infrastructure, offshore-to-onshore transformers. Distinct from
`outages_transmission` (A78) which covers onshore / cross-border assets.
Used to flag offshore wind curtailment risk and offshore-hub-related
flow constraints. Currently sparse — many zones report no offshore grid
outages at all.

→ [Outages transmission](outages_transmission.md), [Wind/solar forecast](wind_solar_forecast.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None |
| Historical depth | recent (offshore grid is a young dataset) |
| Publication lag  | T+~1h |
| Response format  | XML — root `Unavailability_MarketDocument` |
| Document type    | A79 |
| Process type     | n/a |
| Business type    | **none required** — distinct from other outage datasets |
| Domain param name| `BiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A79` | `A79` |
| `BiddingZone_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm`, 30-day window | `202604010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605010000` |
| `DocStatus` | str | no | A05/A09/A13 status filter | |
| `mRID` | str | no | Specific notification | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A79&BiddingZone_Domain=10YGB----------A&periodStart=202604010000&periodEnd=202605010000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB 30-day window: HTTP 200, **EMPTY** (Ack 999 "UNAVAILABILITY_OF_OFFSHORE_GRID [10.1.C]"). No GB offshore grid outages reported.
- BE 30-day window: HTTP 200, **EMPTY** (Ack 999, same).
- NL 30-day window: HTTP 200, **EMPTY** (Ack 999, same).

A79 is structurally extremely sparse — even zones with offshore wind
(BE, NL, DE, DK) frequently return empty. The dataset is a placeholder
for future offshore grid hub publications under TYNDP / North Sea Wind
Power Hub schemes.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/outages_offshore_grid/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (schematic — hypothetical PASS shape)

```xml
<Unavailability_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-2:unavailibilitydocument:5:0">
  <type>A79</type>
  <docStatus><value>A05</value></docStatus>
  <TimeSeries>
    <biddingZone_Domain.mRID>10YBE----------2</biddingZone_Domain.mRID>
    <Asset_RegisteredResource>
      <mRID>...</mRID><name>MOG-MODULAR-OFFSHORE</name>
    </Asset_RegisteredResource>
    <Available_Period>
      <timeInterval>...</timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>500</quantity></Point>
    </Available_Period>
  </TimeSeries>
</Unavailability_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/outages_offshore_grid/year=YYYY/month=MM/outages_offshore_grid_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.outages_h7.OutagesOffshoreGridTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeOutagesOffshoreGrid`
**Dedup key**: `(timestamp_utc, area_code, asset_mrid, timeseries_mrid)`
**Point-in-time field**: `ingested_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Available_Period | tz-aware UTC |
| area_code | str | No | `<biddingZone_Domain.mRID>` | EIC |
| asset_mrid | str | No | `<Asset_RegisteredResource><mRID>` | Default "" in canonical. Asset EIC. |
| asset_name | str | No | `<Asset_RegisteredResource><name>` | Default "" in canonical. |
| outage_type | str | No | derived from `<businessType>` | Default "" in canonical. "planned" / "unplanned" — may be empty. |
| unavailable_mw | float | No | `<Point><quantity>` | MW |
| business_type | str | No | `<businessType>` | Default "" in canonical. Raw — may be absent. |
| document_mrid | str | No | root `<mRID>` | Default "" in canonical. |
| document_status | str | No | `<docStatus><value>` | Default "" in canonical. A05/A09/A13. |
| timeseries_mrid | str | No | TimeSeries `<mRID>` | Default "" in canonical. |
| resolution | str | No | parsed | Default "" in canonical. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-04-15T00:00:00+00:00",
        "area_code": "10YBE----------2",
        "asset_mrid": "ABC123",
        "asset_name": "MOG-MOD",
        "outage_type": "",
        "unavailable_mw": 500.0,
        "business_type": "",
        "document_mrid": "DOC-001",
        "document_status": "A05",
        "timeseries_mrid": "1",
        "resolution": "1:00:00",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:00:00+00:00",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **No `BusinessType` parameter** — A79 is the only outage dataset where `BusinessType` is absent from `extra_params` in `endpoints.py`. Adding it produces an Acknowledgement.
- **Structurally sparse.** Even GB / BE / NL offshore-wind heavy zones return EMPTY — A79 only fires when offshore grid hub assets have outage notifications, which are rare (offshore grid hubs are still partly hypothetical).
- **30-day window minimum** as for other outages.
- **Outage status codes** (DocStatus): `A05` Active, `A09` Cancelled, `A13` Withdrawn.
- `outage_type` is **nullable / empty-string** in silver because A79 does not always have a `businessType` element; downstream models should treat empty as "unspecified".

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §10.1.C): `(documentType=A79, processType=n/a, BusinessType=n/a, BiddingZone_Domain)`.
  - Code: `("A79", None, **no BusinessType**, domain_style="bidding_zone")` → `BiddingZone_Domain`.
  - **Match** — code correctly omits the BusinessType parameter for A79.
- Pydantic schema permits empty `outage_type` (default `""`) reflecting the absent businessType.

---

## Modelling notes

- Currently of low predictive value — dataset publication too sparse.
- Useful for future offshore-grid scenario builds when publication coverage improves.
- Watch for the dataset becoming richer as North Sea hub plans materialise.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/outages_h7.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
