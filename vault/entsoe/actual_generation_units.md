---
source: entsoe
dataset_key: actual_generation_units
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Actual generation per generation unit (A73/A16)

## Overview

Realised MW output **per individual generation unit** rather than per
production type. Identifies units by their EIC mRID and human-readable
name. The unit-level granularity is what makes A73 special — it's the
TSO-published equivalent of Elexon's `pn` (Physical Notifications) at
the level of the EIC unit registry. Used to calibrate plant-by-plant
must-run / capacity-factor models.

→ [Actual generation](actual_generation.md), [Installed capacity per unit](installed_capacity_units.md)

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
| Historical depth | 2014-12-05 onwards |
| Publication lag  | T+~1h |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A73 |
| Process type     | A16 (realised) |
| Business type    | n/a |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A73` | `A73` |
| `processType` | str | yes | `A16` | `A16` |
| `in_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202605060000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605070000` |
| `psrType` | str | no | Filter to one production type | `B16` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A73&processType=A16&in_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB 1-day window: HTTP 200, **EMPTY** (Ack 999 "ACTUAL_GENERATION_OUTPUT_PER_UNIT_R3 [16.1.A]"). Brexit-GB.
- DE-LU 1-day window: HTTP 200, **EMPTY** (Ack 999 same code) — DE-LU does not publish A73/A16 to ENTSO-E either; many continental TSOs publish only A75 aggregated.

A73/A16 is generally only available in zones where the TSO chooses to
publish per-unit realised flows; expect EMPTY across most European zones.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/actual_generation_units/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (DE-LU, EMPTY response)

```xml
<Acknowledgement_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-1:acknowledgementdocument:7:0">
  <Reason><code>999</code><text>No matching data found ...</text></Reason>
</Acknowledgement_MarketDocument>
```

When data is published, response root is `GL_MarketDocument` with one
`<TimeSeries>` per generation unit.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/actual_generation_units/year=YYYY/month=MM/actual_generation_units_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.actual_generation_units.ActualGenerationUnitsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeActualGenerationUnits`
**Dedup key**: `(timestamp_utc, area_code, unit_mrid)`
**Point-in-time field**: `ingested_at` (optional)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Period start + position * resolution | tz-aware UTC |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| production_type | str | No | `<MktPSRType><psrType>` | EIC PSR type |
| unit_mrid | str | No | `<registeredResource.mRID>` | Unit identifier — keep verbatim, no normalisation |
| unit_name | str | No | `<registeredResource.name>` | Default "" in canonical (str = ""). |
| generation_mw | float | No | `<Point><quantity>` | MW |
| resolution | str | No | parsed | Default "" in canonical (str = ""). Typical PT60M. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | Optional — populated when transformer runs |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "area_code": "10YGB----------A",
        "production_type": "B14",
        "unit_mrid": "48WSTN0000ABRBON",
        "unit_name": "ABRBO",
        "generation_mw": 100.5,
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

- **GB EMPTY** — GB stopped publishing per-unit data to ENTSO-E post-Brexit.
- **DE-LU EMPTY** — German TSOs publish unit-level data only via SMARD / national portals, not ENTSO-E.
- **`businessType` requirement (per plan):** plan flags A73/A16 as needing a `psrType` filter for "production-unit-level data". In practice the API accepts the call with no `psrType`; the EMPTY result is data availability, not a filter requirement. `psrType` is documented as **optional** in the API guide. Code does not include `psrType` in `optional_params` — flag as `unverified` for the connector caller.
- Unit mRIDs vary by TSO encoding (IGCC, EIC, internal). Treat as opaque strings.
- Re-publication: silver `keep="last"` overwrites earlier revisions.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §16.1.A): `(documentType=A73, processType=A16, businessType=n/a, in_Domain)`.
  - Code: `("A73", "A16", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- Plan-flagged: `psrType` not in `optional_params`. Documented as optional, not required — code is correct in not enforcing it. Flag as `unverified` for consumer ergonomics.

---

## Modelling notes

- Plant-level capacity-factor models — when data is available.
- Deviation from declared `pn` (Elexon) for outage-detection style features.
- For GB use Elexon `pn` / `boal` instead.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/actual_generation_units.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
