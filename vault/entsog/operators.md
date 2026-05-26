---
source: entsog
dataset_key: operators
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Operators

## Overview

All transmission system operators (TSOs).

This is a reference / inventory dataset — no time dimension, but
inventory does change weekly when ENTSOG approves new operators or points.
The connector schedule is `weekly` in `config/sources.yaml`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/operators` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset` — pagination is REQUIRED for full inventory; iterate offsets until `count < limit` or fall back to `limit=-1` for a single all-records pull |
| Historical depth | n/a (snapshot) |
| Publication lag  | Vendor inventory updates daily |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `limit` | int | Yes | Page size; `-1` returns all | `1000` |
| `offset` | int | No | Page offset (0-based) | `0` |
| `hasData` | bool / int | No | Restrict to operators with operational data | `1` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/operators?limit=100&offset=0&hasData=1"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/operators/<year>/<month>/<day>/raw_<uuid>.json` (one snapshot per weekly schedule)
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call (full inventory).

### Bronze sample

```json
{
  "meta": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 100
  },
  "operators": [
    {
      "operatorLogoUrl": "",
      "operatorKey": "---ASO-0001",
      "operatorLabel": "Aggregated Counterpa",
      "operatorLabelLong": "Aggregated Counterparties",
      "operatorTooltip": "Aggregated Counterparties|                ",
      "operatorCountryKey": "--",
      "operatorCountryLabel": "None",
      "operatorCountryFlag": null,
      "operatorTypeLabel": "ASO",
      "operatorTypeLabelLong": "Artificial Operator",
      "participates": "0",
      "membershipLabel": "Unaffiliated",
      "tsoEicCode": null,
      "tsoDisplayName": null,
      "tsoShortName": null,
      "tsoLongName": null,
      "tsoStreet": null,
      "tsoBuildingNumber": null,
      "tsoPostOfficeBox": null,
      "tsoZipCode": null,
      "tsoCity": null,
      "tsoContactName": null,
      "tsoContactPhone": null,
      "tsoContactEmail": null,
      "tsoContactUrl": null,
      "tsoContactRemarks": null,
      "tsoGeneralWebsiteUrl": null,
      "tsoGeneralWebsiteUrlRemarks": null,
      "tsoTariffInformationUrl": null,
      "tsoTariffInformationUrlRemarks": "Regulation (EU) 2017/460, Article 29&30 Information",
      "tsoTariffCalculatorUrl": null,
      "tsoTariffCalculatorUrlRemarks": "Regulation (EC) No 715/2009, Annex I Point 3.4.(6) information",
      "tsoCapacityInformationUrl": null,
      "tsoCapacityInformationUrlRemarks": null,
      "tsoGasQualityURL": null,
      "tsoGasQualityURLRemarks": "Regulation (EU) No 2015/703, Article 16 information",
      "tsoAccessConditionsUrl": null,
      "tsoAccessConditionsUrlRemarks": null,
      "tsoContractDocumentsUrl": null,
      "tsoContractDocumentsUrlRemarks": null,
      "tsoMaintainanceUrl": null,
      "tsoMaintainanceUrlRemarks": null,
      "gasDayStartHour": null,
      "gasDayStartHourRemarks": null,
      "multiAnnualContractsIsAvailable": null,
      "multiAnnualContractsRemarks": null,
      "annualContractsIsAvailable": null,
      "annualContractsRemarks": null,
      "halfAnnualContractsIsAvailable": null,
      "halfAnnualContractsRemarks": null,
      "quarterlyContractsIsAvailable": null,
      "quarterlyContractsRemarks": null,
      "monthlyContractsIsAvailable": null,
      "monthlyContractsRemarks": null,
      "dailyContractsIsAvailable": null,
      "dailyContractsRemarks": null,
      "withinDayContractsIsAvailable": null,
      "withinDayContractsRemarks": null,
      "availableContractsRemarks": null,
      "firmCapacityTariffIsApplied": null,
      "firmCapacityTariffUnit": null,
      "firmCapacityTariffRemarks": null,
      "interruptibleCapacityTariffIsApplied": null,
      "interruptibleCapacityTariffUnit": null,
      "interruptibleCapacityTariffRemarks": null,
      "auctionIsApplied": null,
      "auctionTariffIsApplied": null,
      "auctionCapacityTariffUnit": null,
      "auctionRemarks": null,
      "commodityTariffIsApplied": null,
      "commodityTariffUnit": null,
      "commodityTariffPrice": null,
      "commodityTariffRemarks": null,
      "othersTariffIsApplied": null,
      "othersTariffRemarks": null,
      "generalTariffInformationRemarks": null,
      "generalCapacityRemark": null,
      "firstComeFirstServedIsApplied": null,
      "firstComeFirstServedRemarks": null,
      "openSubscriptionWindowIsApplied": null,
      "openSubscriptionWindowRemarks": null,
      "firmTechnicalRemark": null,
      "firmBookedRemark": null,
      "fir
... [truncated]
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/operators.parquet` (single-file overwrite — `reference_dataset=True`)
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass OperatorsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else inventory key (e.g. `point_key`, `operator_key`)
**Point-in-time field**: `last_update_date_time` (records carry per-row update timestamps)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| operator_logo_url | str | Yes | operatorLogoUrl |  |
| operator_key | str | Yes | operatorKey |  |
| operator_label | str | Yes | operatorLabel |  |
| operator_label_long | str | Yes | operatorLabelLong |  |
| operator_tooltip | str | Yes | operatorTooltip |  |
| operator_country_key | str | Yes | operatorCountryKey |  |
| operator_country_label | str | Yes | operatorCountryLabel |  |
| operator_country_flag | str | Yes | operatorCountryFlag |  |
| operator_type_label | str | Yes | operatorTypeLabel |  |
| operator_type_label_long | str | Yes | operatorTypeLabelLong |  |
| participates | str | Yes | participates |  |
| membership_label | str | Yes | membershipLabel |  |
| tso_eic_code | str | Yes | tsoEicCode |  |
| tso_display_name | str | Yes | tsoDisplayName |  |
| tso_short_name | str | Yes | tsoShortName |  |
| tso_long_name | str | Yes | tsoLongName |  |
| tso_street | str | Yes | tsoStreet |  |
| tso_building_number | str | Yes | tsoBuildingNumber |  |
| tso_post_office_box | str | Yes | tsoPostOfficeBox |  |
| tso_zip_code | str | Yes | tsoZipCode |  |
| tso_city | str | Yes | tsoCity |  |
| tso_contact_name | str | Yes | tsoContactName |  |
| tso_contact_phone | str | Yes | tsoContactPhone |  |
| tso_contact_email | str | Yes | tsoContactEmail |  |
| tso_contact_url | str | Yes | tsoContactUrl |  |
| tso_contact_remarks | str | Yes | tsoContactRemarks |  |
| tso_general_website_url | str | Yes | tsoGeneralWebsiteUrl |  |
| tso_general_website_url_remarks | str | Yes | tsoGeneralWebsiteUrlRemarks |  |
| tso_tariff_information_url | str | Yes | tsoTariffInformationUrl |  |
| tso_tariff_information_url_remarks | str | Yes | tsoTariffInformationUrlRemarks |  |
| tso_tariff_calculator_url | str | Yes | tsoTariffCalculatorUrl |  |
| tso_tariff_calculator_url_remarks | str | Yes | tsoTariffCalculatorUrlRemarks |  |
| tso_capacity_information_url | str | Yes | tsoCapacityInformationUrl |  |
| tso_capacity_information_url_remarks | str | Yes | tsoCapacityInformationUrlRemarks |  |
| tso_gas_quality_url | str | Yes | tsoGasQualityURL |  |
| tso_gas_quality_url_remarks | str | Yes | tsoGasQualityURLRemarks |  |
| tso_access_conditions_url | str | Yes | tsoAccessConditionsUrl |  |
| tso_access_conditions_url_remarks | str | Yes | tsoAccessConditionsUrlRemarks |  |
| tso_contract_documents_url | str | Yes | tsoContractDocumentsUrl |  |
| tso_contract_documents_url_remarks | str | Yes | tsoContractDocumentsUrlRemarks |  |
| tso_maintainance_url | str | Yes | tsoMaintainanceUrl |  |
| tso_maintainance_url_remarks | str | Yes | tsoMaintainanceUrlRemarks |  |
| gas_day_start_hour | str | Yes | gasDayStartHour |  |
| gas_day_start_hour_remarks | str | Yes | gasDayStartHourRemarks |  |
| multi_annual_contracts_is_available | str | Yes | multiAnnualContractsIsAvailable |  |
| multi_annual_contracts_remarks | str | Yes | multiAnnualContractsRemarks |  |
| annual_contracts_is_available | str | Yes | annualContractsIsAvailable |  |
| annual_contracts_remarks | str | Yes | annualContractsRemarks |  |
| half_annual_contracts_is_available | str | Yes | halfAnnualContractsIsAvailable |  |
| half_annual_contracts_remarks | str | Yes | halfAnnualContractsRemarks |  |
| quarterly_contracts_is_available | str | Yes | quarterlyContractsIsAvailable |  |
| quarterly_contracts_remarks | str | Yes | quarterlyContractsRemarks |  |
| monthly_contracts_is_available | str | Yes | monthlyContractsIsAvailable |  |
| monthly_contracts_remarks | str | Yes | monthlyContractsRemarks |  |
| daily_contracts_is_available | str | Yes | dailyContractsIsAvailable |  |
| daily_contracts_remarks | str | Yes | dailyContractsRemarks |  |
| within_day_contracts_is_available | str | Yes | withinDayContractsIsAvailable |  |
| within_day_contracts_remarks | str | Yes | withinDayContractsRemarks |  |
| available_contracts_remarks | str | Yes | availableContractsRemarks |  |
| firm_capacity_tariff_is_applied | str | Yes | firmCapacityTariffIsApplied |  |
| firm_capacity_tariff_unit | str | Yes | firmCapacityTariffUnit |  |
| firm_capacity_tariff_remarks | str | Yes | firmCapacityTariffRemarks |  |
| interruptible_capacity_tariff_is_applied | str | Yes | interruptibleCapacityTariffIsApplied |  |
| interruptible_capacity_tariff_unit | str | Yes | interruptibleCapacityTariffUnit |  |
| interruptible_capacity_tariff_remarks | str | Yes | interruptibleCapacityTariffRemarks |  |
| auction_is_applied | str | Yes | auctionIsApplied |  |
| auction_tariff_is_applied | str | Yes | auctionTariffIsApplied |  |
| auction_capacity_tariff_unit | str | Yes | auctionCapacityTariffUnit |  |
| auction_remarks | str | Yes | auctionRemarks |  |
| commodity_tariff_is_applied | str | Yes | commodityTariffIsApplied |  |
| commodity_tariff_unit | str | Yes | commodityTariffUnit |  |
| commodity_tariff_price | float | Yes | commodityTariffPrice |  |
| commodity_tariff_remarks | str | Yes | commodityTariffRemarks |  |
| others_tariff_is_applied | str | Yes | othersTariffIsApplied |  |
| others_tariff_remarks | str | Yes | othersTariffRemarks |  |
| general_tariff_information_remarks | str | Yes | generalTariffInformationRemarks |  |
| general_capacity_remark | str | Yes | generalCapacityRemark |  |
| first_come_first_served_is_applied | str | Yes | firstComeFirstServedIsApplied |  |
| first_come_first_served_remarks | str | Yes | firstComeFirstServedRemarks |  |
| open_subscription_window_is_applied | str | Yes | openSubscriptionWindowIsApplied |  |
| open_subscription_window_remarks | str | Yes | openSubscriptionWindowRemarks |  |
| firm_technical_remark | str | Yes | firmTechnicalRemark |  |
| firm_booked_remark | str | Yes | firmBookedRemark |  |
| firm_available_remark | str | Yes | firmAvailableRemark |  |
| interruptible_total_remark | str | Yes | interruptibleTotalRemark |  |
| interruptible_booked_remark | str | Yes | interruptibleBookedRemark |  |
| interruptible_available_remark | str | Yes | interruptibleAvailableRemark |  |
| tso_general_remarks | str | Yes | tsoGeneralRemarks |  |
| balancing_model | str | Yes | balancingModel |  |
| b_m_hourly_imbalance_tolerance_is_applied | str | Yes | bMHourlyImbalanceToleranceIsApplied |  |
| b_m_hourly_imbalance_tolerance_is_information | str | Yes | bMHourlyImbalanceToleranceIsInformation |  |
| b_m_hourly_imbalance_tolerance_is_remarks | str | Yes | bMHourlyImbalanceToleranceIsRemarks |  |
| b_m_daily_imbalance_tolerance_is_applied | str | Yes | bMDailyImbalanceToleranceIsApplied |  |
| b_m_daily_imbalance_tolerance_is_information | str | Yes | bMDailyImbalanceToleranceIsInformation |  |
| b_m_daily_imbalance_tolerance_is_remarks | str | Yes | bMDailyImbalanceToleranceIsRemarks |  |
| b_m_additional_daily_imbalance_tolerance_is_applied | str | Yes | bMAdditionalDailyImbalanceToleranceIsApplied |  |
| b_m_additional_daily_imbalance_tolerance_is_information | str | Yes | bMAdditionalDailyImbalanceToleranceIsInformation |  |
| b_m_additional_daily_imbalance_tolerance_is_remarks | str | Yes | bMAdditionalDailyImbalanceToleranceIsRemarks |  |
| b_m_cumulated_imbalance_tolerance_is_applied | str | Yes | bMCumulatedImbalanceToleranceIsApplied |  |
| b_m_cumulated_imbalance_tolerance_is_information | str | Yes | bMCumulatedImbalanceToleranceIsInformation |  |
| b_m_cumulated_imbalance_tolerance_is_remarks | str | Yes | bMCumulatedImbalanceToleranceIsRemarks |  |
| b_m_additional_cumulated_imbalance_tolerance_is_applied | str | Yes | bMAdditionalCumulatedImbalanceToleranceIsApplied |  |
| b_m_additional_cumulated_imbalance_tolerance_is_information | str | Yes | bMAdditionalCumulatedImbalanceToleranceIsInformation |  |
| b_m_additional_cumulated_imbalance_tolerance_is_remarks | str | Yes | bMAdditionalCumulatedImbalanceToleranceIsRemarks |  |
| b_m_status_information | str | Yes | bMStatusInformation |  |
| b_m_status_information_frequency | str | Yes | bMStatusInformationFrequency |  |
| b_m_penalties | str | Yes | bMPenalties |  |
| b_m_cash_out_regime | str | Yes | bMCashOutRegime |  |
| b_m_remarks | str | Yes | bMRemarks |  |
| grid_transport_model_type | str | Yes | gridTransportModelType |  |
| grid_transport_model_type_remarks | str | Yes | gridTransportModelTypeRemarks |  |
| grid_conversion_factor_capacity_default | str | Yes | gridConversionFactorCapacityDefault |  |
| grid_conversion_factor_capacity_default_remaks | str | Yes | gridConversionFactorCapacityDefaultRemaks |  |
| grid_gross_calorific_value_default_value | float | Yes | gridGrossCalorificValueDefaultValue |  |
| grid_gross_calorific_value_default_value_to | str | Yes | gridGrossCalorificValueDefaultValueTo |  |
| grid_gross_calorific_value_default_unit | str | Yes | gridGrossCalorificValueDefaultUnit |  |
| grid_gross_calorific_value_default_remarks | str | Yes | gridGrossCalorificValueDefaultRemarks |  |
| grid_gas_source_default | str | Yes | gridGasSourceDefault |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| transparency_information_url | str | Yes | transparencyInformationURL |  |
| transparency_information_url_remarks | str | Yes | transparencyInformationUrlRemarks |  |
| transparency_guidelines_information_url | str | Yes | transparencyGuidelinesInformationURL |  |
| transparency_guidelines_information_url_remarks | str | Yes | transparencyGuidelinesInformationUrlRemarks |  |
| tso_umm_rss_feed_url_gas | str | Yes | tsoUmmRssFeedUrlGas |  |
| tso_umm_rss_feed_url_other | str | Yes | tsoUmmRssFeedUrlOther |  |
| include_umm_in_acer_rss_feed | str | Yes | includeUmmInAcerRssFeed |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "operator_logo_url": "",
        "operator_key": "---ASO-0001",
        "operator_label": "Aggregated Counterpa",
        "operator_label_long": "Aggregated Counterparties",
        "operator_tooltip": "Aggregated Counterparties|                ",
        "operator_country_key": "--",
        "operator_country_label": "None",
        "operator_country_flag": null,
        "operator_type_label": "ASO",
        "operator_type_label_long": "Artificial Operator",
        "participates": "0",
        "membership_label": "Unaffiliated",
        "tso_eic_code": null,
        "tso_display_name": null,
        "tso_short_name": null,
        "tso_long_name": null,
        "tso_street": null,
        "tso_building_number": null,
        "tso_post_office_box": null,
        "tso_zip_code": null,
        "tso_city": null,
        "tso_contact_name": null,
        "tso_contact_phone": null,
        "tso_contact_email": null,
        "tso_contact_url": null,
        "tso_contact_remarks": null,
        "tso_general_website_url": null,
        "tso_general_website_url_remarks": null,
        "tso_tariff_information_url": null,
        "tso_tariff_information_url_remarks": "Regulation (EU) 2017/460, Article 29&30 Information",
        "tso_tariff_calculator_url": null,
        "tso_tariff_calculator_url_remarks": "Regulation (EC) No 715/2009, Annex I Point 3.4.(6) information",
        "tso_capacity_information_url": null,
        "tso_capacity_information_url_remarks": null,
        "tso_gas_quality_url": null,
        "tso_gas_quality_url_remarks": "Regulation (EU) No 2015/703, Article 16 information",
        "tso_access_conditions_url": null,
        "tso_access_conditions_url_remarks": null,
        "tso_contract_documents_url": null,
        "tso_contract_documents_url_remarks": null,
        "tso_maintainance_url": null,
        "tso_maintainance_url_remarks": null,
        "gas_day_start_hour": null,
        "gas_day_start_hour_remarks": null,
        "multi_annual_contracts_is_available": null,
        "multi_annual_contracts_remarks": null,
        "annual_contracts_is_available": null,
        "annual_contracts_remarks": null,
        "half_annual_contracts_is_available": null,
        "half_annual_contracts_remarks": null,
        "quarterly_contracts_is_available": null,
        "quarterly_contracts_remarks": null,
        "monthly_contracts_is_available": null,
        "monthly_contracts_remarks": null,
        "daily_contracts_is_available": null,
        "daily_contracts_remarks": null,
        "within_day_contracts_is_available": null,
        "within_day_contracts_remarks": null,
        "available_contracts_remarks": null,
        "firm_capacity_tariff_is_applied": null,
        "firm_capacity_tariff_unit": null,
        "firm_capacity_tariff_remarks": null,
        "interruptible_capacity_tariff_is_applied": null,
        "interruptible_capacity_tariff_unit": null,
        "interruptible_capacity_tariff_remarks": null,
        "auction_is_applied": null,
        "auction_tariff_is_applied": null,
        "auction_capacity_tariff_unit": null,
        "auction_remarks": null,
        "commodity_tariff_is_applied": null,
        "commodity_tariff_unit": null,
        "commodity_tariff_price": null,
        "commodity_tariff_remarks": null,
        "others_tariff_is_applied": null,
        "others_tariff_remarks": null,
        "general_tariff_information_remarks": null,
        "general_capacity_remark": null,
        "first_come_first_served_is_applied": null,
        "first_come_first_served_remarks": null,
        "open_subscription_window_is_applied": null,
        "open_subscription_window_remarks": null,
        "firm_technical_remark": null,
        "firm_booked_remark": null,
        "firm_available_remark": null,
        "interruptible_total_remark": null,
        "interruptible_booked_remark": null,
        "interruptible_available_remark": null,
        "tso_general_remarks": null,
        "balancing_model": null,
        "b_m_hourly_imbalance_tolerance_is_applied": null,
        "b_m_hourly_imbalance_tolerance_is_information": null,
        "b_m_hourly_imbalance_tolerance_is_remarks": null,
        "b_m_daily_imbalance_tolerance_is_applied": null,
        "b_m_daily_imbalance_tolerance_is_information": null,
        "b_m_daily_imbalance_tolerance_is_remarks": null,
        "b_m_additional_daily_imbalance_tolerance_is_applied": null,
        "b_m_additional_daily_imbalance_tolerance_is_information": null,
        "b_m_additional_daily_imbalance_tolerance_is_remarks": null,
        "b_m_cumulated_imbalance_tolerance_is_applied": null,
        "b_m_cumulated_imbalance_tolerance_is_information": null,
        "b_m_cumulated_imbalance_tolerance_is_remarks": null,
        "b_m_additional_cumulated_imbalance_tolerance_is_applied": null,
        "b_m_additional_cumulated_imbalance_tolerance_is_information": null,
        "b_m_additional_cumulated_imbalance_tolerance_is_remarks": null,
        "b_m_status_information": null,
        "b_m_status_information_frequency": null,
        "b_m_penalties": null,
        "b_m_cash_out_regime": null,
        "b_m_remarks": null,
        "grid_transport_model_type": null,
        "grid_transport_model_type_remarks": null,
        "grid_conversion_factor_capacity_default": null,
        "grid_conversion_factor_capacity_default_remaks": null,
        "grid_gross_calorific_value_default_value": null,
        "grid_gross_calorific_value_default_value_to": null,
        "grid_gross_calorific_value_default_unit": null,
        "grid_gross_calorific_value_default_remarks": null,
        "grid_gas_source_default": null,
        "last_update_date_time": "2015-11-09T00:11:00+01:00",
        "transparency_information_url": null,
        "transparency_information_url_remarks": null,
        "transparency_guidelines_information_url": null,
        "transparency_guidelines_information_url_remarks": "Regulation (EC) No 715/2009, Annex I Chapter 3 information",
        "tso_umm_rss_feed_url_gas": null,
        "tso_umm_rss_feed_url_other": null,
        "include_umm_in_acer_rss_feed": null,
        "id": "1---ASO-0001",
        "data_set": "1",
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

- **No date filter — pagination required**: reference endpoints accept `limit` + `offset`. Default `limit` is small; pass `limit=1000` (or the full inventory size) and iterate offset for full extracts.
- **`hasData=1` shrinks operatorPointDirections / operators**: filters out points/operators without any operational data. Useful as a discovery filter, but loses validity-period rows for points that recently went dormant.
- **Field-case duplicates**: `isCAMRelevant` (uppercase CAM) appears here while `isCamRelevant` appears in operationalData. Generic silver coalesces both into `is_cam_relevant`.
- **Reference data refresh schedule**: weekly in `config/sources.yaml`. Static-ish, but new points and operator changes do appear when ENTSOG approves them.
- **`bzKey` separators**: balancing zone keys often contain trailing dashes (`UK---------`) — preserve as-is, do not strip.


---

## Implementation delta

- **Pagination required**: full inventory may exceed default page size. Connector defaults to `limit=-1`; live validation used `limit=100` to demonstrate paging shape. For production fetches, prefer `limit=-1` or iterate `offset` in chunks.
- **`reference_dataset=True` write path**: silver writes directly to `<silver_dir>/<dataset>.parquet`, bypassing the date-partitioned layout used by operational datasets.

---

## Modelling notes

TODO — primarily used as join keys for operational datasets.

---

## Links

- [Official API docs (PDF)](https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/TP_REG715_Documentation_TP_API%20-%20v2.1.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsog/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsog/generic.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsog.py)
- [Gold view/builder](none)
