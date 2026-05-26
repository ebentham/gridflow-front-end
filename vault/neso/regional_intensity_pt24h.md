---
source: neso
dataset_key: regional_intensity_pt24h
vendor: National Energy System Operator (NESO)
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# NESO - Regional carbon intensity previous 24h (`regional_intensity_pt24h`)

## Overview

This dataset represents regional carbon intensity and regional generation mix for GB DNO or nation-level areas. It answers where electricity consumption is cleaner or dirtier within GB, useful for regional demand, siting, carbon-aware scheduling, and distribution-aware modelling. See [Carbon intensity](../../../20-domain/concepts/carbon-intensity.md) and [Settlement period](../../../20-domain/concepts/settlement-period.md).

---

## API endpoint

| Property | Value |
|----------|-------|
| Base URL | `https://api.carbonintensity.org.uk` |
| Path | `/regional/intensity/{from}/pt24h` |
| Method | GET |
| Auth | None; send `Accept: application/json` |
| Rate limit | Not documented by NESO; Gridflow config uses 10 req/s. |
| Pagination | None. Dynamic inputs are path segments, not query parameters. |
| Historical depth | Rolling previous 24h |
| Publication lag | Actual estimate not guaranteed; use forecast/index defensively |
| Response format | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| from | string | Yes | Path parameter: Datetime in ISO8601 format YYYY-MM-DDThh:mmZ | 2024-01-15T00:00Z |

### Working curl example

```bash
curl --ssl-no-revoke -X GET \
  "https://api.carbonintensity.org.uk/regional/intensity/2024-01-15T00:00Z/pt24h" \
  -H "Accept: application/json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/neso/regional_intensity_pt24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
**Format**: Raw JSON, as received. Immutable after write, with `.meta.json` provenance sidecar.
**Granularity**: One file per API call; range and daily routes may produce one file per chunk/day/period.

### Bronze sample

Period-keyed envelope: each `data[]` entry holds `from`/`to` plus a `regions[]`
list (≈18 GB regions). `intensity` and `generationmix` are nested **inside each
region**, not at the period level.

```json
{"data":[{"from":"2026-05-08T17:30Z","to":"2026-05-08T18:00Z","regions":[{"regionid":1,"dnoregion":"Scottish Hydro Electric Power Distribution","shortname":"North Scotland","intensity":{"forecast":0,"index":"very low"},"generationmix":[{"fuel":"biomass","perc":0},{"fuel":"coal","perc":0}]}]}]}
```

---

## Silver layer

**Path pattern**: `data/silver/neso/regional_intensity_pt24h/year=<YYYY>/month=<MM>/regional_intensity_pt24h_<YYYYMMDD>.parquet`
**Transformer class**: `gridflow.silver.neso.carbon_intensity.RegionalIntensityPt24HTransformer`
**Pydantic schema**: `gridflow.schemas.neso.RegionalIntensity`
**Dedup key**: `(timestamp_utc, regionid, shortname, postcode, fuel)`
**Point-in-time field**: `timestamp_utc`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | from | Half-hour period start. |
| period_end_utc | datetime[UTC] | Yes | to | Half-hour period end. |
| regionid | int | Yes | regionid | NESO region identifier. |
| dnoregion | str | No | dnoregion | DNO region name. |
| shortname | str | No | shortname | Short region label. |
| postcode | str | No | postcode | Outward postcode when returned or requested. |
| forecast_gco2_kwh | float | Yes | intensity.forecast | Regional forecast carbon intensity. |
| actual_gco2_kwh | float | Yes | intensity.actual | Not present in many official examples; nullable. |
| intensity_index | str | No | intensity.index | Docs category string. |
| fuel | str | No | generationmix.fuel | Regional generation mix fuel. |
| generation_percentage | float | Yes | generationmix.perc | Regional fuel share in percent. |
| data_provider | str | No | derived | Always neso. |
| ingested_at | datetime[UTC] | No | derived | Silver transform timestamp. |

### Silver sample

```python
[{"timestamp_utc":"2024-01-15T00:00:00+00:00","period_end_utc":"2024-01-15T00:30:00+00:00","regionid":13,"dnoregion":"UKPN London","shortname":"London","postcode":"RG10","forecast_gco2_kwh":120.0,"actual_gco2_kwh":None,"intensity_index":"low","fuel":"gas","generation_percentage":30.0,"data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"},{"timestamp_utc":"2024-01-15T00:00:00+00:00","period_end_utc":"2024-01-15T00:30:00+00:00","regionid":13,"dnoregion":"UKPN London","shortname":"London","postcode":"RG10","forecast_gco2_kwh":120.0,"actual_gco2_kwh":None,"intensity_index":"low","fuel":"wind","generation_percentage":40.0,"data_provider":"neso","ingested_at":"2026-05-04T00:00:00+00:00"}]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- Official docs use UTC timestamps ending in `Z`; keep joins in UTC.
- The connector sends no query parameters; all documented inputs are path parameters.
- Actual carbon intensity values can be null or absent, especially before post-period estimates are available.
- For `intensity_period`, GB clock-change days can have 46 or 50 settlement periods in implementation even though official docs describe period 1-48.

---

## Implementation delta

- **`from` / `to` placeholders**: official docs and `config/sources.yaml` use `{from}` and `{to}`; `src/gridflow/connectors/neso/endpoints.py` uses `{from_dt}` and `{to_dt}` internally before formatting the same path.
- **`actual`**: official regional examples include `forecast` and `index`; code supports nullable `actual_gco2_kwh` if the API returns it.
- **Period-keyed shape vs silver row builder — RESOLVED in V2 (2026-05-09).** See [regional_current](./regional_current.md) for full notes. Silver `_rows_from_region_period` now reads from whichever level (region or period) holds the data. Live re-validated 2026-05-09 via `fix(V2-B):` on `claude/lucid-mccarthy-9ed3e0`.

---

## Changelog

- **2026-05-09 — V2-FIX-02.** Period-keyed silver now populates carbon and mix fields. See [regional_current](./regional_current.md#changelog) for evidence.
- **2026-05-08 — V1.** Live-validated; bug surfaced + documented.

---

## Modelling notes

Use regional `forecast_gco2_kwh` and fuel mix as local carbon features. Join to regional weather, demand, and postcode/region mapping before training; filter missing `regionid`/`postcode` intentionally.

---

## Links

- [Official API docs](https://carbon-intensity.github.io/api-definitions/)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py)
- [Endpoint metadata](../../../../../../Python/gridflow/src/gridflow/connectors/neso/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/neso/carbon_intensity.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/neso.py)
- [Gold view/builder](../../../../../../Python/gridflow/src/gridflow/gold/views/uk_imbalance_context.sql)
- [Domain: Carbon intensity](../../../20-domain/concepts/carbon-intensity.md)

