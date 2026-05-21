---
source: elexon
dataset_key: bmunits_reference
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - BM Units Reference Data (`BMUNITS`)

## Overview

Reference data describing every registered Balancing Mechanism Unit — BM Unit ID, friendly name, fuel type, registered capacity, lead party, GSP group, and ENTSO-E EIC. This is slowly-changing master data used to enrich every per-unit dataset (BOALF, PN, UOU2T14D, etc.).

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/reference/bmunits/all` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | None — full snapshot returned in one call. |
| Historical depth | Current state only (point-in-time snapshot). |
| Publication lag  | Slowly-changing reference data; refreshed when BM Unit registrations change. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| _none_ | _none_ | _none_ | No query parameters required. | _n/a_ |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/reference/bmunits/all?format=json" \
  -o "/tmp/elexon-bmunits_reference.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/bmunits_reference/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/reference/bmunits/all?format=json:

```json
{
  "data": [
    {
      "nationalGridBmUnit": "ABERU-1",
      "elexonBmUnit": "E_ABERDARE",
      "eic": null,
      "fuelType": null,
      "leadPartyName": "UK Power Reserve Limited",
      "bmUnitType": "E",
      "fpnFlag": true,
      "bmUnitName": "Aberdare Power Station",
      "leadPartyId": "UKPR",
      "demandCapacity": "0.000",
      "generationCapacity": "15.400",
      "productionOrConsumptionFlag": "C",
      "transmissionLossFactor": "0.0162928",
      "workingDayCreditAssessmentImportCapability": "0.000",
      "nonWorkingDayCreditAssessmentImportCapability": "0.000",
      "workingDayCreditAssessmentExportCapability": "6.160",
      "nonWorkingDayCreditAssessmentExportCapability": "6.160",
      "creditQualifyingStatus": true,
      "demandInProductionFlag": false,
      "gspGroupId": "_K",
      "gspGroupName": "South Wales",
      "interconnectorId": null
    },
    {
      "nationalGridBmUnit": "ABRBO-1",
      "elexonBmUnit": "T_ABRBO-1",
      "eic": "48W00000ABRBO-19",
      "fuelType": "WIND",
      "leadPartyName": "Aberdeen Offshore Wind Farm",
      "bmUnitType": "T",
      "fpnFlag": true,
      "bmUnitName": "ABRBO-1",
      "leadPartyId": "ABERDEEN",
      "demandCapacity": "-2.000",
      "generationCapacity": "99.000",
      "productionOrConsumptionFlag": "P",
      "transmissionLossFactor": "-0.0323359",
      "workingDayCreditAssessmentImportCapability": "-0.800",
      "nonWorkingDayCreditAssessmentImportCapability": "-0.800",
      "workingDayCreditAssessmentExportCapability": "39.600",
      "nonWorkingDayCreditAssessmentExportCapability": "39.600",
      "creditQualifyingStatus": true,
      "demandInProductionFlag": false,
      "gspGroupId": null,
      "gspGroupName": null,
      "interconnectorId": null
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/bmunits_reference/year=YYYY/month=MM/bmunits_reference_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.bmunits.BMUnitsTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonBMUnit`
**Dedup key**: `(bm_unit_id)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `bm_unit_id` | `str` | No | `bmUnit` or `elexonBmUnit` | BM Unit identifier — preserve raw casing. |
| `bm_unit_name` | `str` | Yes | `name` or `bmUnitName` | Friendly name of the BM Unit. |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, COAL, NUCLEAR, WIND, etc.). |
| `registered_capacity_mw` | `float` | Yes | `registeredCapacity` or `generationCapacity` | MW. |
| `company_name` | `str` | Yes | `companyName` or `leadPartyName` | Lead party (operator) name. |
| `gsp_group_id` | `str` | Yes | `gspGroupId` | GSP group identifier. |
| `national_grid_bm_unit` | `str` | Yes | `nationalGridBmUnit` | ENTSO-E EIC for the BM Unit. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "bm_unit_id": "E_ABERDARE",
        "bm_unit_name": "Aberdare Power Station",
        "fuel_type": null,
        "registered_capacity_mw": "15.400",
        "company_name": "UK Power Reserve Limited",
        "gsp_group_id": "_K",
        "national_grid_bm_unit": "ABERU-1",
        "data_provider": "elexon",
        "ingested_at": "2026-05-08T12:00:00Z"
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Slowly-changing data** — re-fetch when the BM unit registry changes (typically a few times per year).
- **No pagination** — full snapshot returned in one call (~3000 rows).

---

## Implementation delta

- **Response is a JSON array** (no `{data: [...]}` envelope) — silver `BMUnitsTransformer` and connector handle this.
- **`ElexonBMUnit`** Pydantic schema declared.
- **No pagination** — `supports_pagination = False`.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/bmunits.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
