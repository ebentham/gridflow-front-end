---
source: entsog
dataset_key: tariff_simulations
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Tariff Simulations

## Overview

Simulated tariff costs for representative product types.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/tariffsSimulations` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset` |
| Historical depth | TODO |
| Publication lag  | TODO |
| Response format  | JSON |
| Time zone | `timeZone=UCT` (ENTSOG's spelling) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | date | Yes | Window start | `2026-05-06` |
| `to` | date | Yes | Window end | `2026-05-06` |
| `timeZone` | str | Yes | `UCT` | `UCT` |
| `countryKey` | str | No | Filter to one country (recommended) | `UK` |
| `limit` | int | No | `-1` returns all | `-1` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/tariffsSimulations?from=2026-05-06&to=2026-05-06&timeZone=UCT&countryKey=UK&forceDownload=true&limit=1000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/tariff_simulations/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call.

### Bronze sample

```json
{
  "meta": {
    "limit": 1000,
    "offset": 0,
    "count": 1,
    "total": 1000
  },
  "tariffsSimulations": [
    {
      "directionKey": "exit",
      "operator": "BBL company",
      "operatorPointDirection": "uk-tso-0004itp-00207exit",
      "countryCode": "NL",
      "connection": " BBL company -> National Gas TSO",
      "connectionRemarks": null,
      "fromBZ": "Netherlands",
      "toBZ": "UK",
      "tariffCapacityType": "Firm",
      "tariffCapacityUnit": "kWh/h",
      "tariffCapacityRemarks": null,
      "productType": "Yearly",
      "operatorCurrency": "EUR",
      "productSimulationCostInLocalCurrency": "365000",
      "productSimulationCostInEURO": "365000",
      "productSimulationCostRemarks": "",
      "exchangeRateReferenceDate": "N/A",
      "remarks": null,
      "tariffPeriodRemarks": null,
      "displayOrder": 1,
      "pointType": null,
      "idPointType": null,
      "isArchived": false,
      "id": "321Z000000000088FFirmYearlyUK-TSO-0004ITP-00207exit2025-10-01T04:00:00+00:00__2026-10-01T04:00:00+00:00",
      "dataSet": 3,
      "indicator": null,
      "periodType": null,
      "periodFrom": "2025-10-01T06:00:00+02:00",
      "periodTo": "2026-10-01T06:00:00+02:00",
      "operatorKey": "UK-TSO-0004",
      "tsoEicCode": "21X-NL-B-A0A0A-Q",
      "operatorLabel": null,
      "pointKey": "ITP-00207",
      "pointLabel": "Bacton (BBL)",
      "tsoItemIdentifier": "21Z000000000088F",
      "direction": null,
      "unit": null,
      "itemRemarks": null,
      "generalRemarks": null,
      "value": null,
      "lastUpdateDateTime": "2025-07-01T14:08:43+02:00",
      "isUnlimited": null,
      "interruptionType": null,
      "restorationInformation": null,
      "capacityType": null,
      "capacityBookingStatus": null,
      "flowStatus": null
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/tariff_simulations/year=YYYY/month=MM/tariff_simulations_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass TariffSimulationsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else all non-`timestamp_utc` columns
**Point-in-time field**: `last_update_date_time` or `publication_date_time` (UMM)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| direction_key | str | Yes | directionKey |  |
| operator | str | Yes | operator |  |
| operator_point_direction | str | Yes | operatorPointDirection |  |
| country_code | str | Yes | countryCode |  |
| connection | str | Yes | connection |  |
| connection_remarks | str | Yes | connectionRemarks |  |
| from_bz | str | Yes | fromBZ |  |
| to_bz | str | Yes | toBZ |  |
| tariff_capacity_type | str | Yes | tariffCapacityType |  |
| tariff_capacity_unit | str | Yes | tariffCapacityUnit |  |
| tariff_capacity_remarks | str | Yes | tariffCapacityRemarks |  |
| product_type | str | Yes | productType |  |
| operator_currency | str | Yes | operatorCurrency |  |
| product_simulation_cost_in_local_currency | str | Yes | productSimulationCostInLocalCurrency |  |
| product_simulation_cost_in_euro | str | Yes | productSimulationCostInEURO |  |
| product_simulation_cost_remarks | str | Yes | productSimulationCostRemarks |  |
| exchange_rate_reference_date | datetime[UTC] | Yes | exchangeRateReferenceDate |  |
| remarks | str | Yes | remarks |  |
| tariff_period_remarks | str | Yes | tariffPeriodRemarks |  |
| display_order | str | Yes | displayOrder |  |
| point_type | str | Yes | pointType |  |
| id_point_type | str | Yes | idPointType |  |
| is_archived | bool | Yes | isArchived |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| indicator | str | Yes | indicator |  |
| period_type | str | Yes | periodType |  |
| period_from | datetime[UTC] | Yes | periodFrom |  |
| period_to | datetime[UTC] | Yes | periodTo |  |
| operator_key | str | Yes | operatorKey |  |
| tso_eic_code | str | Yes | tsoEicCode |  |
| operator_label | str | Yes | operatorLabel |  |
| point_key | str | Yes | pointKey |  |
| point_label | str | Yes | pointLabel |  |
| tso_item_identifier | str | Yes | tsoItemIdentifier |  |
| direction | str | Yes | direction |  |
| unit | str | Yes | unit |  |
| item_remarks | str | Yes | itemRemarks |  |
| general_remarks | str | Yes | generalRemarks |  |
| value | float | Yes | value |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| is_unlimited | bool | Yes | isUnlimited |  |
| interruption_type | str | Yes | interruptionType |  |
| restoration_information | str | Yes | restorationInformation |  |
| capacity_type | str | Yes | capacityType |  |
| capacity_booking_status | str | Yes | capacityBookingStatus |  |
| flow_status | str | Yes | flowStatus |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "direction_key": "exit",
        "operator": "BBL company",
        "operator_point_direction": "uk-tso-0004itp-00207exit",
        "country_code": "NL",
        "connection": " BBL company -> National Gas TSO",
        "connection_remarks": null,
        "from_bz": "Netherlands",
        "to_bz": "UK",
        "tariff_capacity_type": "Firm",
        "tariff_capacity_unit": "kWh/h",
        "tariff_capacity_remarks": null,
        "product_type": "Yearly",
        "operator_currency": "EUR",
        "product_simulation_cost_in_local_currency": "365000",
        "product_simulation_cost_in_euro": "365000",
        "product_simulation_cost_remarks": "",
        "exchange_rate_reference_date": "N/A",
        "remarks": null,
        "tariff_period_remarks": null,
        "display_order": 1,
        "point_type": null,
        "id_point_type": null,
        "is_archived": false,
        "id": "321Z000000000088FFirmYearlyUK-TSO-0004ITP-00207exit2025-10-01T04:00:00+00:00__2026-10-01T04:00:00+00:00",
        "data_set": 3,
        "indicator": null,
        "period_type": null,
        "period_from": "2025-10-01T06:00:00+02:00",
        "period_to": "2026-10-01T06:00:00+02:00",
        "operator_key": "UK-TSO-0004",
        "tso_eic_code": "21X-NL-B-A0A0A-Q",
        "operator_label": null,
        "point_key": "ITP-00207",
        "point_label": "Bacton (BBL)",
        "tso_item_identifier": "21Z000000000088F",
        "direction": null,
        "unit": null,
        "item_remarks": null,
        "general_remarks": null,
        "value": null,
        "last_update_date_time": "2025-07-01T14:08:43+02:00",
        "is_unlimited": null,
        "interruption_type": null,
        "restoration_information": null,
        "capacity_type": null,
        "capacity_booking_status": null,
        "flow_status": null,
        "data_provider": "entsog",
        "ingested_at": "2026-05-08T18:00:00+00:00"
    }
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **`countryKey` filter recommended**: tariffs without country filter return tens of thousands of rows. The connector defaults to `countryKey=UK`.
- **Mixed currencies and units**: `operatorCurrency` varies (RON, EUR, GBP, etc.). Both local-currency and EUR-converted columns are present (`applicableTariffPerEURKWhDValue` etc.). `exchangeRateReferenceDate` records when the EUR conversion was sampled.
- **Most rows have many null fields**: tariffs are sparse — different tariff lines populate different cost columns. Don't drop nulls.
- **Periods**: `productPeriodFrom`/`productPeriodTo` may be null for "evergreen" tariff entries.

- **Indicator string is exact-case**: the connector sends the exact human-readable form (`Physical Flow`, `Nomination`, `Available through UIOLI long-term`). Sending lowercase or hyphen variants returns 404.
- **`timeZone=UCT` (note typo)**: ENTSOG documents the parameter as `timeZone=UCT` rather than `UTC`. The connector spells it the vendor's way. The response `meta.timezone` echoes back `CET` regardless of the request value.
- **`pointDirection` filter**: built as `operatorKey + pointKey + directionKey` concatenated with no separator (e.g. `UK-TSO-0001ITP-00005exit`). Multi-value lists are comma-joined.
- **Missing data returns HTTP 404**: ENTSOG returns `HTTP 404` with body `{"message":"No result found"}` when an indicator/window/point combination has no rows. This is the vendor's empty convention, not a true failure. The connector's retry policy must let 404 surface.
- **Field-case duplicates**: live records may carry both `isCamRelevant` and `isCAMRelevant` shape (or `isCmpRelevant`/`isCMPRelevant`) depending on indicator. The generic silver transformer `_normalise_column_names` collapses these via `pl.coalesce` into one snake_case column.
- **Datetime placeholders**: `lastUpdateDateTime` and `originalPeriodFrom` may be empty strings, `"-"`, `"N/A"`, or human-formatted strings (`"Jan 15 2024 06:00AM"`). `parse_entsog_datetime` returns `None` for unparseable values rather than raising.
- **`directionKey` casing varies**: lowercase (`entry`/`exit`) in `/operationalData`; capitalised (`Exit`) in `/cmpUnsuccessfulRequests`. Don't compare with `==` across families.
- **Period offset is +02:00 (CET)**: even with `timeZone=UCT`, `periodFrom` carries `+02:00` (CEST in summer / `+01:00` in winter). The silver transformer's `parse_entsog_datetime` converts to UTC.


---

## Implementation delta

- **Vendor empty convention**: HTTP 404 + `{"message":"No result found"}`.
- **Generic transformer**: dynamic schema; columns derived from live response.


---

## Modelling notes

TODO

---

## Links

- [Official API docs (PDF)](https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/TP_REG715_Documentation_TP_API%20-%20v2.1.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsog/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsog/generic.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsog.py)
- [Gold view/builder](none)
