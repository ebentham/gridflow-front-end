---
source: entsoe
dataset_key: cross_border_flows
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Physical Cross-Border Flows (A11)

## Overview

Hourly physical cross-border power flows between ENTSO-E bidding zones in MW
(metered or best estimate). Article 12.1.G of Regulation (EC) 543/2013.
Each TimeSeries describes the flow from `in_Domain` to `out_Domain`; the
reverse direction is published as a separate TimeSeries on a separate request.
Used as a feature for cross-border price-spread models, congestion analysis,
GB interconnector utilisation, and as a target for flow-forecasting.

→ Domain refs: [Cross-border flow](../../20-domain/markets/cross-border-flow.md)
[Bidding zone EIC codes](../../20-domain/concepts/eic-codes.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | Not formally documented — gridflow uses 1 req/s; back off on 429 |
| Pagination       | None (single XML document per call); split long windows client-side |
| Historical depth | From 2014-12-05 (ENTSO-E TP launch), border-dependent |
| Publication lag  | Hourly resolution, typically published within 1 hour of real time |
| Response format  | XML (`Publication_MarketDocument`) |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A11` |
| processType | (none) |
| businessType (request) | (none — server returns `A66` on TimeSeries) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A11 is a directional flow, so each border requires two requests
(one for each direction). Default UK-centric border pairs:

| in_Domain | out_Domain | Border name |
|-----------|------------|-------------|
| `10YGB----------A` | `10YFR-RTE------C` | GB → FR (IFA, IFA2, ElecLink) |
| `10YFR-RTE------C` | `10YGB----------A` | FR → GB |
| `10YGB----------A` | `10YBE----------2` | GB → BE (Nemo) |
| `10YGB----------A` | `10YNL----------L` | GB → NL (BritNed) |
| `10YGB----------A` | `10Y1001A1001A59C` | GB → IE (E/W Interconnector) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key (UUID) | `00000000-...` |
| `documentType` | str | Yes | `A11` (cross-border physical flow) | `A11` |
| `in_Domain` | str | Yes | Source zone EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination zone EIC | `10YFR-RTE------C` |
| `periodStart` | str | Yes | Inclusive UTC start `yyyymmddHHMM` | `202605060000` |
| `periodEnd` | str | Yes | Exclusive UTC end `yyyymmddHHMM` | `202605070000` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-cross_border_flows.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A11&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/cross_border_flows/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, as-received. Immutable — never modified after write.
**Granularity**: One file per (in_Domain, out_Domain, day) tuple

### Bronze sample

```xml
<?xml version="1.0" encoding="utf-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0">
  <mRID>1cc6d87479954899a9952cb35f5547b4</mRID>
  <type>A11</type>
  <createdDateTime>2026-05-08T18:05:24Z</createdDateTime>
  <period.timeInterval>
    <start>2026-05-06T00:00Z</start>
    <end>2026-05-07T00:00Z</end>
  </period.timeInterval>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>A66</businessType>
    <in_Domain.mRID codingScheme="A01">10YGB----------A</in_Domain.mRID>
    <out_Domain.mRID codingScheme="A01">10YFR-RTE------C</out_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <curveType>A03</curveType>
    <Period>
      <timeInterval>
        <start>2026-05-06T00:00Z</start>
        <end>2026-05-07T00:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>2967.4375</quantity></Point>
      <Point><position>2</position><quantity>2918.5925</quantity></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/cross_border_flows/year=YYYY/month=MM/cross_border_flows_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.cross_border_flows.CrossBorderFlowsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeCrossborderFlow`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code)`
**Point-in-time field**: `none` (no run-type semantics; revisions overwrite)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived from `Period.timeInterval.start` + `position` | Inclusive interval start |
| `in_area_code` | `str` | No | `TimeSeries.in_Domain.mRID` | EIC, never normalised |
| `out_area_code` | `str` | No | `TimeSeries.out_Domain.mRID` | EIC, never normalised |
| `flow_mw` | `float` | No | `Point.quantity` | MW (Measure_Unit `MAW`) |
| `resolution` | `str` | No | `Period.resolution` | ISO code verbatim (e.g. `PT60M`, `PT15M`); not normalised |
| `data_provider` | `str` | No | derived | Always `"entsoe"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | UTC now at silver write |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "flow_mw": 2967.4375,
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:05:30Z",
    },
    {
        "timestamp_utc": "2026-05-06T01:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "flow_mw": 2918.5925,
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

- A11 is **directional**. Net flow on a border requires both directions
  fetched and subtracted; one direction may show 0 / be absent.
- Resolution typically `PT60M` for legacy borders, but ENTSO-E publishes some
  as `PT15M` post-2024 — silver does not normalise resolution.
- `<curveType>A03</curveType>` (variable-resolution curve) is the common case;
  positions correspond to ordinal hours from `Period.timeInterval.start`.
- `quantity_Measure_Unit.name` is `MAW` (megawatt) — note the unusual ENTSO-E
  spelling. Treat as MW.
- Server-set `businessType` `A66` (settlement total) is on the TimeSeries; do
  not pass `businessType` in the request — it is ignored / can cause empties.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A11, processType=none, businessType=none-in-request, domain=in_Domain+out_Domain)`. Matches `connectors/entsoe/endpoints.py` `cross_border_flows` entry. PASS.
- **Live validation 2026-05-08:** GB → FR for 2026-05-06, returned `Publication_MarketDocument` with 1 TimeSeries, 24 hourly points. PASS.
- **Schema field set (G5-W3, 2026-05):** `EntsoeCrossborderFlow` now declares all seven columns the transformer emits — `timestamp_utc`, `in_area_code`, `out_area_code`, `flow_mw`, `resolution`, `data_provider`, `ingested_at` (`resolution` and `ingested_at` were added per the schema docstring; they previously drifted from the V1 §13 declaration). The silver Parquet column set matches the schema declaration.

---

## Modelling notes

- Used as feature for GB interconnector utilisation models, day-ahead price
  spread models, and congestion-rent models.
- Net interconnector flow = `flow_mw(GB→X) − flow_mw(X→GB)` per timestamp;
  consume both directions.
- Quality filter: drop rows where the same `(timestamp_utc, in, out)` appears
  with multiple revisions, keep latest by `ingested_at` (already done in
  silver via `unique(..., keep="last")`).

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/cross_border_flows.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](../../../../) (none)
