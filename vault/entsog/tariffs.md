---
source: entsog
dataset_key: tariffs
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Tariffs

## Overview

Full tariff data per operator and point — unit prices, multipliers, currency.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/tariffsFulls` |
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
  "https://transparency.entsog.eu/api/v1/tariffsFulls?from=2026-05-06&to=2026-05-06&timeZone=UCT&countryKey=UK&forceDownload=true&limit=1000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/tariffs/<year>/<month>/<day>/raw_<uuid>.json`
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
  "tariffsFulls": [
    {
      "directionKey": "exit",
      "operator": "Transgaz",
      "operatorPointDirection": "ro-tso-0001itp-00153exit",
      "countryCode": null,
      "connection": null,
      "connectionRemarks": null,
      "fromBZ": null,
      "toBZ": null,
      "productPeriodFrom": null,
      "productPeriodTo": null,
      "tariffCapacityType": null,
      "tariffCapacityUnit": "kWh/h",
      "productType": "Yearly",
      "multiplier": null,
      "multiplierFactorRemarks": null,
      "discountForInterruptibleCapacityValue": null,
      "discountForInterruptibleCapacityRemarks": null,
      "seasonalFactor": null,
      "seasonalFactorRemarks": null,
      "operatorCurrency": "RON",
      "applicableTariffPerLocalCurrencyKWhDValue": null,
      "applicableTariffPerLocalCurrencyKWhDUnit": null,
      "applicableTariffPerLocalCurrencyKWhHValue": null,
      "applicableTariffPerLocalCurrencyKWhHUnit": null,
      "applicableTariffPerEURKWhDValue": null,
      "applicableTariffPerEURKWhDUnit": null,
      "applicableTariffPerEURKWhHValue": null,
      "applicableTariffPerEURKWhHUnit": null,
      "applicableTariffRemarks": null,
      "applicableTariffInCommonUnitValue": null,
      "applicableTariffInCommonUnitUnit": null,
      "applicableTariffInCommonUnitRemarks": null,
      "applicableCommodityTariffLocalCurrency": "0.0018",
      "applicableCommodityTariffEURO": "0.00035677",
      "applicableCommodityTariffRemarks": null,
      "exchangeRateReferenceDate": "2025-06-06T22:25:29+02:00",
      "remarks": null,
      "tariffPeriodRemarks": null,
      "displayOrder": null,
      "pointType": null,
      "idPointType": null,
      "isArchived": null,
      "id": "121Z0000000002798RO-TSO-0001ITP-00153exit2025-10-01T04:00:00+00:00__2026-10-01T04:00:00+00:00",
      "dataSet": 1,
      "indicator": null,
      "periodType": null,
      "periodFrom": "2025-10-01T06:00:00+02:00",
      "periodTo": "2026-10-01T06:00:00+02:00",
      "operatorKey": "RO-TSO-0001",
      "tsoEicCode": "21X-RO-A-A0A0A-S",
      "operatorLabel": null,
      "pointKey": "ITP-00153",
      "pointLabel": "Ruse (BG) / Giurgiu (RO)",
      "tsoItemIdentifier": "21Z0000000002798",
      "direction": null,
      "unit": null,
      "itemRemarks": null,
      "generalRemarks": null,
      "value": null,
      "lastUpdateDateTime": "2025-06-07T06:56:45+02:00",
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

**Path pattern**: `data/silver/entsog/tariffs/year=YYYY/month=MM/tariffs_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass TariffsTransformer)`
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
| product_period_from | str | Yes | productPeriodFrom |  |
| product_period_to | str | Yes | productPeriodTo |  |
| tariff_capacity_type | str | Yes | tariffCapacityType |  |
| tariff_capacity_unit | str | Yes | tariffCapacityUnit |  |
| product_type | str | Yes | productType |  |
| multiplier | str | Yes | multiplier |  |
| multiplier_factor_remarks | str | Yes | multiplierFactorRemarks |  |
| discount_for_interruptible_capacity_value | float | Yes | discountForInterruptibleCapacityValue |  |
| discount_for_interruptible_capacity_remarks | str | Yes | discountForInterruptibleCapacityRemarks |  |
| seasonal_factor | float | Yes | seasonalFactor |  |
| seasonal_factor_remarks | str | Yes | seasonalFactorRemarks |  |
| operator_currency | str | Yes | operatorCurrency |  |
| applicable_tariff_per_local_currency_k_wh_d_value | float | Yes | applicableTariffPerLocalCurrencyKWhDValue |  |
| applicable_tariff_per_local_currency_k_wh_d_unit | str | Yes | applicableTariffPerLocalCurrencyKWhDUnit |  |
| applicable_tariff_per_local_currency_k_wh_h_value | float | Yes | applicableTariffPerLocalCurrencyKWhHValue |  |
| applicable_tariff_per_local_currency_k_wh_h_unit | str | Yes | applicableTariffPerLocalCurrencyKWhHUnit |  |
| applicable_tariff_per_eurk_wh_d_value | float | Yes | applicableTariffPerEURKWhDValue |  |
| applicable_tariff_per_eurk_wh_d_unit | str | Yes | applicableTariffPerEURKWhDUnit |  |
| applicable_tariff_per_eurk_wh_h_value | float | Yes | applicableTariffPerEURKWhHValue |  |
| applicable_tariff_per_eurk_wh_h_unit | str | Yes | applicableTariffPerEURKWhHUnit |  |
| applicable_tariff_remarks | str | Yes | applicableTariffRemarks |  |
| applicable_tariff_in_common_unit_value | float | Yes | applicableTariffInCommonUnitValue |  |
| applicable_tariff_in_common_unit_unit | str | Yes | applicableTariffInCommonUnitUnit |  |
| applicable_tariff_in_common_unit_remarks | str | Yes | applicableTariffInCommonUnitRemarks |  |
| applicable_commodity_tariff_local_currency | str | Yes | applicableCommodityTariffLocalCurrency |  |
| applicable_commodity_tariff_euro | str | Yes | applicableCommodityTariffEURO |  |
| applicable_commodity_tariff_remarks | str | Yes | applicableCommodityTariffRemarks |  |
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
        "operator": "Transgaz",
        "operator_point_direction": "ro-tso-0001itp-00153exit",
        "country_code": null,
        "connection": null,
        "connection_remarks": null,
        "from_bz": null,
        "to_bz": null,
        "product_period_from": null,
        "product_period_to": null,
        "tariff_capacity_type": null,
        "tariff_capacity_unit": "kWh/h",
        "product_type": "Yearly",
        "multiplier": null,
        "multiplier_factor_remarks": null,
        "discount_for_interruptible_capacity_value": null,
        "discount_for_interruptible_capacity_remarks": null,
        "seasonal_factor": null,
        "seasonal_factor_remarks": null,
        "operator_currency": "RON",
        "applicable_tariff_per_local_currency_k_wh_d_value": null,
        "applicable_tariff_per_local_currency_k_wh_d_unit": null,
        "applicable_tariff_per_local_currency_k_wh_h_value": null,
        "applicable_tariff_per_local_currency_k_wh_h_unit": null,
        "applicable_tariff_per_eurk_wh_d_value": null,
        "applicable_tariff_per_eurk_wh_d_unit": null,
        "applicable_tariff_per_eurk_wh_h_value": null,
        "applicable_tariff_per_eurk_wh_h_unit": null,
        "applicable_tariff_remarks": null,
        "applicable_tariff_in_common_unit_value": null,
        "applicable_tariff_in_common_unit_unit": null,
        "applicable_tariff_in_common_unit_remarks": null,
        "applicable_commodity_tariff_local_currency": "0.0018",
        "applicable_commodity_tariff_euro": "0.00035677",
        "applicable_commodity_tariff_remarks": null,
        "exchange_rate_reference_date": "2025-06-06T22:25:29+02:00",
        "remarks": null,
        "tariff_period_remarks": null,
        "display_order": null,
        "point_type": null,
        "id_point_type": null,
        "is_archived": null,
        "id": "121Z0000000002798RO-TSO-0001ITP-00153exit2025-10-01T04:00:00+00:00__2026-10-01T04:00:00+00:00",
        "data_set": 1,
        "indicator": null,
        "period_type": null,
        "period_from": "2025-10-01T06:00:00+02:00",
        "period_to": "2026-10-01T06:00:00+02:00",
        "operator_key": "RO-TSO-0001",
        "tso_eic_code": "21X-RO-A-A0A0A-S",
        "operator_label": null,
        "point_key": "ITP-00153",
        "point_label": "Ruse (BG) / Giurgiu (RO)",
        "tso_item_identifier": "21Z0000000002798",
        "direction": null,
        "unit": null,
        "item_remarks": null,
        "general_remarks": null,
        "value": null,
        "last_update_date_time": "2025-06-07T06:56:45+02:00",
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
