---
source: entsoe
dataset_key: actual_generation
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Actual generation per production type (A75/A16)

## Overview

Actual realised generation in MW for each EIC bidding zone broken down by
PSR (Primary Source) production type — coal, gas, wind onshore, wind
offshore, solar, hydro, nuclear, biomass, etc. Published per settlement
period (PT15M / PT30M / PT60M depending on zone). Used to back out the
realised fuel mix, regress wind/solar against weather drivers, and
cross-check with national TSO publications. Underpins residual-load
modelling — `actual_load - wind - solar` is a standard MEF feature.

→ [Cross-border flows](cross_border_flows.md), [Wind/solar forecast](wind_solar_forecast.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | not documented — code uses 1 req/s, polite default |
| Pagination       | None (response truncates at 200 TimeSeries with HTTP 400 reason 999) |
| Historical depth | 2014-12-05 onwards (varies by area) |
| Publication lag  | T+1 hour to T+24 hours depending on zone |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A75 |
| Process type     | A16 (realised) |
| Business type    | n/a (set per TimeSeries; A04 = consumption / A03 = generation) |
| Domain param name| `in_Domain` (single area) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | Always `A75` | `A75` |
| `processType` | str | yes | `A16` for realised | `A16` |
| `in_Domain` | EIC | yes | Bidding zone EIC | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202605060000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605070000` |
| `psrType` | str | no | Filter to one production type | `B16` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A75&processType=A16&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB (`10YGB----------A`): HTTP 200, **EMPTY** — `Acknowledgement_MarketDocument` reason 999 "No matching data found for AGGREGATED_GENERATION_PER_TYPE_R3 [16.1.B&C]". GB stopped publishing this dataset to ENTSO-E post-Brexit.
- DE-LU (`10Y1001A1001A82H`): HTTP 200, **PASS** — `GL_MarketDocument`, 17 TimeSeries (one per production type).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/actual_generation/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, as-received. Immutable.
**Granularity**: One XML file per (zone, day) — connector iterates over `DEFAULT_ZONES`.

### Bronze sample (DE-LU 2026-05-06, truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <mRID>...</mRID>
  <type>A75</type>
  <process.processType>A16</process.processType>
  <createdDateTime>2026-05-06T03:00Z</createdDateTime>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>A03</businessType>
    <inBiddingZone_Domain.mRID codingScheme="A01">10Y1001A1001A82H</inBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <MktPSRType><psrType>B19</psrType></MktPSRType>
    <Period>
      <timeInterval><start>2026-05-05T22:00Z</start><end>2026-05-06T22:00Z</end></timeInterval>
      <resolution>PT15M</resolution>
      <Point><position>1</position><quantity>0</quantity></Point>
      ...
    </Period>
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/actual_generation/year=YYYY/month=MM/actual_generation_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.actual_generation.ActualGenerationTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeActualGeneration`
**Dedup key**: `(timestamp_utc, area_code, production_type)`
**Point-in-time field**: none (revisions overwrite — keep="last" by sort)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | `<Period>` start + position * resolution | tz-aware UTC; PT15M / PT30M / PT60M resolution |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone code |
| area_name | str | No | derived | Default "" in canonical (EntsoeActualGeneration.area_name: str = ""). |
| production_type | str | No | `<MktPSRType><psrType>` | EIC PSR type (B01..B25) |
| generation_mw | float | No | `<Point><quantity>` | Renamed from `value`; MW (XML unit `MAW`) |
| data_provider | str | No | constant | "entsoe" |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-05T22:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "area_name": "",
        "production_type": "B19",
        "generation_mw": 0.0,
        "data_provider": "entsoe",
    },
    {
        "timestamp_utc": "2026-05-05T22:15:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "area_name": "",
        "production_type": "B16",
        "generation_mw": 1843.5,
        "data_provider": "entsoe",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB EMPTY post-Brexit.** GB ceased publishing aggregated generation to ENTSO-E after the GB exit from the IEM. Use Elexon `fuelhh` / `fuelinst` for GB fuel mix instead.
- Resolution varies by zone — DE/AT/FR are PT15M, others PT60M. Don't assume hourly when joining.
- Multiple revisions of the same period — silver dedup keeps the **last** seen row; there's no `published_at` timestamp surfaced in silver, so older revisions are silently overwritten on re-ingest.
- `area_name` is in the Pydantic schema but not populated by the transformer — defaults to "".
- A75 includes both generation (businessType A03) and consumption (A04) for storage units. Code keeps both rows; downstream gold should filter on `production_type` / sign.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §16.1.B): `(documentType=A75, processType=A16, businessType=n/a, in_Domain)`.
  - Code (`endpoints.py:DOC_TYPES["actual_generation"]`): `("A75", "A16", -, domain_style="in_domain")` → query param `in_Domain`.
  - **Match.**
- `psrType` is a documented optional filter (per-production-type query) but is not in `optional_params` — `unverified` for the connector. Caller can still pass via `**params` into `_optional_filter_params`.
- `area_name` field in `EntsoeActualGeneration` is unfilled by the transformer — `unverified` in silver output.

---

## Modelling notes

- Residual-demand and price models — `actual_load - actual_generation_renewables` is the standard residual-load feature.
- Wind/solar nowcast benchmarks — actual vs `wind_solar_forecast` for forecast skill.
- Production-type-conditional regressions (e.g. nuclear capacity factor).
- Filter on resolution before joining settlement-period datasets — DE-LU 15-min vs UK 30-min mismatch.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/actual_generation.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
