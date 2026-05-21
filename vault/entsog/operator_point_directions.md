---
source: entsog
dataset_key: operator_point_directions
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Operator Point Directions

## Overview

(operator, point, direction) tuples — the join key for operationalData and CMP queries.

This is a reference / inventory dataset — no time dimension, but
inventory does change weekly when ENTSOG approves new operators or points.
The connector schedule is `weekly` in `config/sources.yaml`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/operatorPointDirections` |
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
| `hasData` | bool / int | No | Restrict to (operator,point,direction) tuples with operational data | `1` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/operatorPointDirections?limit=100&offset=0&hasData=1"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/operator_point_directions/<year>/<month>/<day>/raw_<uuid>.json` (one snapshot per weekly schedule)
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call (full inventory).

### Bronze sample

```json
{
  "meta": {
    "limit": 100,
    "offset": 0,
    "count": 96,
    "total": 96
  },
  "operatorPointDirections": [
    {
      "pointKey": "ITP-00008",
      "pointLabel": "Melendugno - IT / TAP",
      "operatorKey": "AL-TSO-0001",
      "tsoEicCode": "21X000000001376X",
      "operatorLabel": "TAP",
      "directionKey": "entry",
      "validFrom": null,
      "validTo": null,
      "hasData": true,
      "isVirtualizedCommercially": false,
      "virtualizedCommerciallySince": null,
      "isVirtualizedOperationally": false,
      "virtualizedOperationallySince": null,
      "isPipeInPipe": false,
      "relatedOperators": null,
      "relatedPoints": null,
      "pipeInPipeWithTsoKey": "",
      "pipeInPipeWithTsoLabel": "",
      "isDoubleReporting": null,
      "doubleReportingWithTsoKey": "",
      "doubleReportingWithTsoLabel": "",
      "tsoItemIdentifier": "21Z000000000474A",
      "tpTsoItemLabel": "Melendugno ",
      "tpTsoValidFrom": "2020-12-21",
      "tpTsoValidTo": "2099-12-31",
      "tpTsoRemarks": "Commercial Operations at Melendugno IP started on 15 November 2020.",
      "tpTsoConversionFactor": "1.000000",
      "tpRmkGridConversionFactorCapacityDefault": "TAP markets capacity in KWh/d\n",
      "tpTsoGCVMin": "36.840000",
      "tpTsoGCVMax": "47.730000",
      "tpTsoGCVRemarks": "Range of TAP GCV as provided in TAP Network Code\n",
      "tpTsoGCVUnit": "MJ/nm3",
      "tpTsoEntryExitType": null,
      "multiAnnualContractsIsAvailable": true,
      "multiAnnualContractsRemarks": "TAP has in place 25  years GTAs and we will offer multiannual contracts through the Market Test procedure. \n",
      "annualContractsIsAvailable": true,
      "annualContractsRemarks": "TAP offers annual products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar.\n",
      "halfAnnualContractsIsAvailable": false,
      "halfAnnualContractsRemarks": "",
      "quarterlyContractsIsAvailable": true,
      "quarterlyContractsRemarks": "TAP offers quarterly products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar\n",
      "monthlyContractsIsAvailable": true,
      "monthlyContractsRemarks": "TAP offers monthly products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar.\n",
      "dailyContractsIsAvailable": true,
      "dailyContractsRemarks": "TAP offers daily products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar\n",
      "dayAheadContractsIsAvailable": false,
      "dayAheadContractsRemarks": "TAP currently does not offer WD capacity products.\n",
      "availableContractsRemarks": "",
      "sentenceCMPUnsuccessful": "Currently there are no request for firm capacity products on this point with a duration of one month or longer that weren't successfully fulfilled.",
      "sentenceCMPUnavailable": "Currently firm products with a duration of one month or longer are offered on this point in the regular allocation process.",
      "sentenceCMPAuction": "Currently there are no firm capacity products on this point with a duration of one month or longer auctioned having cleared with an auction premium.",
      "sentenceCMPMadeAvailable": "Currently no capacity has been made available on this point through the application of the congestion-management procedures",
      "lastUpdateDateTime": "2026-05-08T18:05:40+02:00",
      "isInvalid": false,
      "isCAMRelevant": true,
      "isCMPReleva
... [truncated]
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/operator_point_directions.parquet` (single-file overwrite — `reference_dataset=True`)
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass OperatorPointDirectionsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else inventory key (e.g. `point_key`, `operator_key`)
**Point-in-time field**: `last_update_date_time` (records carry per-row update timestamps)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| point_key | str | Yes | pointKey |  |
| point_label | str | Yes | pointLabel |  |
| operator_key | str | Yes | operatorKey |  |
| tso_eic_code | str | Yes | tsoEicCode |  |
| operator_label | str | Yes | operatorLabel |  |
| direction_key | str | Yes | directionKey |  |
| valid_from | datetime[UTC] | Yes | validFrom |  |
| valid_to | datetime[UTC] | Yes | validTo |  |
| has_data | bool | Yes | hasData |  |
| is_virtualized_commercially | bool | Yes | isVirtualizedCommercially |  |
| virtualized_commercially_since | str | Yes | virtualizedCommerciallySince |  |
| is_virtualized_operationally | bool | Yes | isVirtualizedOperationally |  |
| virtualized_operationally_since | str | Yes | virtualizedOperationallySince |  |
| is_pipe_in_pipe | bool | Yes | isPipeInPipe |  |
| related_operators | str | Yes | relatedOperators |  |
| related_points | str | Yes | relatedPoints |  |
| pipe_in_pipe_with_tso_key | str | Yes | pipeInPipeWithTsoKey |  |
| pipe_in_pipe_with_tso_label | str | Yes | pipeInPipeWithTsoLabel |  |
| is_double_reporting | bool | Yes | isDoubleReporting |  |
| double_reporting_with_tso_key | str | Yes | doubleReportingWithTsoKey |  |
| double_reporting_with_tso_label | str | Yes | doubleReportingWithTsoLabel |  |
| tso_item_identifier | str | Yes | tsoItemIdentifier |  |
| tp_tso_item_label | str | Yes | tpTsoItemLabel |  |
| tp_tso_valid_from | str | Yes | tpTsoValidFrom |  |
| tp_tso_valid_to | str | Yes | tpTsoValidTo |  |
| tp_tso_remarks | str | Yes | tpTsoRemarks |  |
| tp_tso_conversion_factor | float | Yes | tpTsoConversionFactor |  |
| tp_rmk_grid_conversion_factor_capacity_default | str | Yes | tpRmkGridConversionFactorCapacityDefault |  |
| tp_tso_gcv_min | str | Yes | tpTsoGCVMin |  |
| tp_tso_gcv_max | str | Yes | tpTsoGCVMax |  |
| tp_tso_gcv_remarks | str | Yes | tpTsoGCVRemarks |  |
| tp_tso_gcv_unit | str | Yes | tpTsoGCVUnit |  |
| tp_tso_entry_exit_type | str | Yes | tpTsoEntryExitType |  |
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
| day_ahead_contracts_is_available | str | Yes | dayAheadContractsIsAvailable |  |
| day_ahead_contracts_remarks | str | Yes | dayAheadContractsRemarks |  |
| available_contracts_remarks | str | Yes | availableContractsRemarks |  |
| sentence_cmp_unsuccessful | str | Yes | sentenceCMPUnsuccessful |  |
| sentence_cmp_unavailable | str | Yes | sentenceCMPUnavailable |  |
| sentence_cmp_auction | str | Yes | sentenceCMPAuction |  |
| sentence_cmp_made_available | str | Yes | sentenceCMPMadeAvailable |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| is_invalid | bool | Yes | isInvalid |  |
| is_cam_relevant | bool | Yes | isCAMRelevant |  |
| is_cmp_relevant | bool | Yes | isCMPRelevant |  |
| booking_platform_key | str | Yes | bookingPlatformKey |  |
| booking_platform_label | str | Yes | bookingPlatformLabel |  |
| booking_platform_url | str | Yes | bookingPlatformURL |  |
| virtual_reverse_flow | str | Yes | virtualReverseFlow |  |
| virtual_reverse_flow_remark | str | Yes | virtualReverseFlowRemark |  |
| t_so_country | str | Yes | tSOCountry |  |
| t_so_balancing_zone | str | Yes | tSOBalancingZone |  |
| cross_border_point_type | str | Yes | crossBorderPointType |  |
| e_u_relationship | str | Yes | eURelationship |  |
| connected_operators | str | Yes | connectedOperators |  |
| adjacent_tso_eic | str | Yes | adjacentTsoEic |  |
| adjacent_operator_key | str | Yes | adjacentOperatorKey |  |
| adjacent_country | str | Yes | adjacentCountry |  |
| point_type | str | Yes | pointType |  |
| id_point_type | str | Yes | idPointType |  |
| adjacent_zones | str | Yes | adjacentZones |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "point_key": "ITP-00008",
        "point_label": "Melendugno - IT / TAP",
        "operator_key": "AL-TSO-0001",
        "tso_eic_code": "21X000000001376X",
        "operator_label": "TAP",
        "direction_key": "entry",
        "valid_from": null,
        "valid_to": null,
        "has_data": true,
        "is_virtualized_commercially": false,
        "virtualized_commercially_since": null,
        "is_virtualized_operationally": false,
        "virtualized_operationally_since": null,
        "is_pipe_in_pipe": false,
        "related_operators": null,
        "related_points": null,
        "pipe_in_pipe_with_tso_key": "",
        "pipe_in_pipe_with_tso_label": "",
        "is_double_reporting": null,
        "double_reporting_with_tso_key": "",
        "double_reporting_with_tso_label": "",
        "tso_item_identifier": "21Z000000000474A",
        "tp_tso_item_label": "Melendugno ",
        "tp_tso_valid_from": "2020-12-21",
        "tp_tso_valid_to": "2099-12-31",
        "tp_tso_remarks": "Commercial Operations at Melendugno IP started on 15 November 2020.",
        "tp_tso_conversion_factor": "1.000000",
        "tp_rmk_grid_conversion_factor_capacity_default": "TAP markets capacity in KWh/d\n",
        "tp_tso_gcv_min": "36.840000",
        "tp_tso_gcv_max": "47.730000",
        "tp_tso_gcv_remarks": "Range of TAP GCV as provided in TAP Network Code\n",
        "tp_tso_gcv_unit": "MJ/nm3",
        "tp_tso_entry_exit_type": null,
        "multi_annual_contracts_is_available": true,
        "multi_annual_contracts_remarks": "TAP has in place 25  years GTAs and we will offer multiannual contracts through the Market Test procedure. \n",
        "annual_contracts_is_available": true,
        "annual_contracts_remarks": "TAP offers annual products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar.\n",
        "half_annual_contracts_is_available": false,
        "half_annual_contracts_remarks": "",
        "quarterly_contracts_is_available": true,
        "quarterly_contracts_remarks": "TAP offers quarterly products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar\n",
        "monthly_contracts_is_available": true,
        "monthly_contracts_remarks": "TAP offers monthly products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar.\n",
        "daily_contracts_is_available": true,
        "daily_contracts_remarks": "TAP offers daily products through the PRISMA Capacity Booking Platform according to the ENTSOG auction calendar\n",
        "day_ahead_contracts_is_available": false,
        "day_ahead_contracts_remarks": "TAP currently does not offer WD capacity products.\n",
        "available_contracts_remarks": "",
        "sentence_cmp_unsuccessful": "Currently there are no request for firm capacity products on this point with a duration of one month or longer that weren't successfully fulfilled.",
        "sentence_cmp_unavailable": "Currently firm products with a duration of one month or longer are offered on this point in the regular allocation process.",
        "sentence_cmp_auction": "Currently there are no firm capacity products on this point with a duration of one month or longer auctioned having cleared with an auction premium.",
        "sentence_cmp_made_available": "Currently no capacity has been made available on this point through the application of the congestion-management procedures",
        "last_update_date_time": "2026-05-08T18:05:40+02:00",
        "is_invalid": false,
        "is_cam_relevant": true,
        "is_cmp_relevant": true,
        "booking_platform_key": "PRISMA",
        "booking_platform_label": "PRISMA",
        "booking_platform_url": "https://platform.prisma-capacity.eu/",
        "virtual_reverse_flow": "Yes",
        "virtual_reverse_flow_remark": "",
        "t_so_country": "CH",
        "t_so_balancing_zone": "",
        "cross_border_point_type": "Cross-Border EU|Non-EU",
        "e_u_relationship": "within EU",
        "connected_operators": "SNAM RETE GAS",
        "adjacent_tso_eic": "21X-IT-A-A0A0A-7",
        "adjacent_operator_key": "IT-TSO-0001",
        "adjacent_country": "IT",
        "point_type": "Cross-Border Transmission IP within EU",
        "id_point_type": 0,
        "adjacent_zones": "Italy",
        "id": "5AL-TSO-0001ITP-00008entryIT-TSO-0001",
        "data_set": "5",
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
