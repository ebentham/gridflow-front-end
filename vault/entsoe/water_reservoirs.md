---
source: entsoe
dataset_key: water_reservoirs
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Water reservoirs and hydro storage plants (A72/A16)

## Overview

Aggregated weekly water-reservoir filling level (energy stored in MWh) per
bidding zone. Published once per week. Used as a slow-moving structural
driver of hydro-rich price markets (Nordic, Iberian, Italian) — low
filling rates strengthen prices on multi-week horizons. Resolution `P7D`,
unit MWh.

→ [Domain: Hydro](../../../20-domain/concepts/hydro.md)

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
| Historical depth | ~2014 onwards (varies by area) |
| Publication lag  | weekly publication, T+~1 week |
| Response format  | XML — root `GL_MarketDocument`, resolution `P7D`, unit `MWH` |
| Document type    | A72 |
| Process type     | A16 (realised) |
| Business type    | n/a (TimeSeries businessType=A01 typical) |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A72` | `A72` |
| `processType` | str | yes | `A16` | `A16` |
| `in_Domain` | EIC | yes | Bidding zone | `10YNO-1--------2` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202604010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605010000` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A72&processType=A16&in_Domain=10YNO-1--------2&periodStart=202604010000&periodEnd=202605010000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB 1-day window: HTTP 200, **EMPTY** (Ack 999 "AGGREGATE_FILLING_RATE_OF_WATER_RESERVOIRS_R3 [16.1.D]"). GB is hydro-light and does not publish A72.
- ES 1-day window: HTTP 200, **EMPTY** — too short (P7D resolution).
- NO-1 30-day window: HTTP 200, **PASS** — `GL_MarketDocument`, 1 TimeSeries with weekly Points. `quantity_Measure_Unit.name = MWH`. Quantity ~10176 MWh per week.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/water_reservoirs/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (NO-1 truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <type>A72</type>
  <process.processType>A16</process.processType>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>A01</businessType>
    <inBiddingZone_Domain.mRID codingScheme="A01">10YNO-1--------2</inBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MWH</quantity_Measure_Unit.name>
    <Period>
      <timeInterval>
        <start>2026-03-29T22:00Z</start><end>2026-05-03T22:00Z</end>
      </timeInterval>
      <resolution>P7D</resolution>
      <Point><position>1</position><quantity>10176</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/water_reservoirs/year=YYYY/month=MM/water_reservoirs_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.water_reservoirs.WaterReservoirsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeWaterReservoirs`
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: `ingested_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Period start | Weekly resolution P7D |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| reservoir_mwh | float | No | `<Point><quantity>` | Unit `MWH` per the response (renamed from `value`) |
| resolution | str | No | parsed | Default "" in canonical. `P7D` typical. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-03-29T22:00:00+00:00",
        "area_code": "10YNO-1--------2",
        "reservoir_mwh": 10176.0,
        "resolution": "7 days, 0:00:00",
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

- **Use a 30-day window minimum** — P7D resolution means a 1-day window returns no data even when the zone publishes.
- **GB / DE-LU / IE-SEM EMPTY** — these zones have no significant hydro reservoir reporting. Hydro markets: NO, SE, ES, IT, FR, AT, CH, DK-2.
- Unit is **MWh** not MW — different dimensionality from generation datasets. Don't sum across with generation series.
- Some zones report energy (MWh), others percentage filling — the silver schema uses `reservoir_mwh` consistent with the Norwegian / Iberian publication convention.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §16.1.D): `(documentType=A72, processType=A16, businessType=n/a, in_Domain)`.
  - Code: `("A72", "A16", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- Default `DEFAULT_ZONES` in `endpoints.py` is GB-centric (GB, FR, NL, BE, DE-LU, IE-SEM) — none of these has meaningful hydro reservoirs. To get useful data, the caller must pass a Nordic / Iberian zone via `**params`. Flag as a config gap (not a code bug).

---

## Modelling notes

- Slow-moving feature for medium-term price models (Nordic / Iberian).
- Combine with snowpack / precipitation forecasts for hydro-driven price regimes.
- Differential ratio vs five-year median is the standard hydrological balance feature.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/water_reservoirs.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
