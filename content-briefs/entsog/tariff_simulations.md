---
slug: tariff_simulations
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: tariffsSimulations
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/tariff_simulations.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["tariff_simulations"] (lines 189-197)
  - .planning/reconciliation/entsog/30-tariff-simulations-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Simulated tariff costs for <span class="italic fg-accent">representative products.</span>

**Lede:** Vendor-simulated total tariff cost per representative capacity product — the canonical forward-looking transmission-cost benchmark for capacity-booking decisions.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /tariffsSimulations](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.tariff_simulations` |
| API PATH | `/api/v1/tariffsSimulations` |
| FREQUENCY | as published |
| PUBLICATION LAG | as published |
| VOLUME | ~1000 EU-wide; ~50 UK records |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Frequency |
| 2 | EUR | Reporting unit |
| 3 | simulated | Cost type |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- tariffs
- cmp_auction_premiums
- operator_point_directions
- firm_available
- operators

# Sample chart

- **Type:** `barsH`
- **Title:** "UK simulated tariff cost by product type"
- **Subtitle:** "Horizontal bars · EUR · current"
- **Seed:** 71
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Vault Bronze sample documents the full field set; the canonical column subset below covers simulation identification, costs, and validity.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Capacity-product validity window. | `silver/entsog/generic.py L114-116` |
| `direction_key` / `direction` | `str` | Yes | `directionKey` / `direction` | `"entry"` / `"exit"` (two vendor fields exist; first wins). | dynamic |
| `operator` / `operator_key` / `operator_label` | `str` | Yes | `operator` / `operatorKey` / `operatorLabel` | TSO identifiers. | dynamic |
| `operator_point_direction` | `str` | Yes | `operatorPointDirection` | Concatenated key. | dynamic |
| `country_code` | `str` | Yes | `countryCode` | ISO-style country code. | dynamic |
| `connection` | `str` | Yes | `connection` | Connection narrative. | dynamic |
| `from_bz` / `to_bz` | `str` | Yes | `fromBZ` / `toBZ` | Balancing-zone pair. | dynamic |
| `tariff_capacity_type` / `tariff_capacity_unit` | `str` | Yes | `tariffCapacityType` / `tariffCapacityUnit` | E.g. `"Firm"` / `"kWh/h"`. | dynamic |
| `product_type` | `str` | Yes | `productType` | E.g. `"Yearly"`, `"Quarterly"`, `"Monthly"`, `"Daily"`. | dynamic |
| `operator_currency` | `str` | Yes | `operatorCurrency` | E.g. `"EUR"`, `"GBP"`. | dynamic |
| `product_simulation_cost_in_local_currency` | `float` | Yes | `productSimulationCostInLocalCurrency` | Simulated total in operator's local currency. | `silver/entsog/generic.py L122-124` |
| `product_simulation_cost_in_euro` | `float` | Yes | `productSimulationCostInEURO` | Simulated total in EUR. | dynamic |
| `exchange_rate_reference_date` | `str` | Yes | `exchangeRateReferenceDate` | FX-rate reference. May be `"N/A"`. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/tariff_simulations/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | operator | tariff_capacity_type | product_type | tariff_capacity_unit | cost_in_euro | operator_currency |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | BBL company | Firm | Yearly | kWh/h | 365,000 | EUR |
| **2025-10-01T04:00:00+00:00** | **National Gas TSO** | **Firm** | **Yearly** | **kWh/h** | **218,000** | **EUR** |
| 2025-10-01T04:00:00+00:00 | Interconnector | Firm | Yearly | kWh/h | 312,000 | EUR |
| 2025-10-01T04:00:00+00:00 | National Gas TSO | Firm | Quarterly | kWh/h | 65,000 | EUR |
| 2025-10-01T04:00:00+00:00 | National Gas TSO | Firm | Monthly | kWh/h | 24,500 | EUR |
| 2025-10-01T04:00:00+00:00 | National Gas TSO | Firm | Daily | kWh/h | 980 | EUR |
| 2025-10-01T04:00:00+00:00 | National Gas TSO | Interruptible | Yearly | kWh/h | 105,000 | EUR |
| 2024-10-01T04:00:00+00:00 | National Gas TSO | Firm | Yearly | kWh/h | 210,000 | EUR |

**Sources:** First row verbatim from vault Bronze sample (`tariff_simulations.md` L83; BBL company yearly firm `productSimulationCostInEURO=365000`). Remaining rows synthesised — the typical pattern is daily ≈ 1/4 of monthly ≈ 1/3 of quarterly ≈ 1/3 of annual (small short-term premium). Highlighted row is National Gas TSO firm yearly at 218k EUR — the canonical UK entry tariff benchmark. Use to compare reservation-cost ladders across product durations.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/tariffsSimulations?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&countryKey=UK`
- AUTH: None (public). Default filter `countryKey=UK` per connector.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/tariff_simulations/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `TariffSimulationsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/tariffsSimulations?from=2026-05-06&to=2026-05-06&timeZone=UCT&countryKey=UK&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Product-duration ladder for National Gas TSO firm
SELECT product_type,
       product_simulation_cost_in_euro AS cost_eur,
       (product_simulation_cost_in_euro / 365.0) AS implied_daily_eur
FROM read_parquet('data/silver/entsog/tariff_simulations/**/*.parquet')
WHERE operator = 'National Gas TSO'
  AND tariff_capacity_type = 'Firm'
  AND period_from = '2025-10-01'
ORDER BY product_simulation_cost_in_euro DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/tariff_simulations/**/*.parquet")
# Year-over-year UK firm-yearly tariff cost
yoy = (
    df.filter(pl.col("country_code") == "GB")
      .filter(pl.col("tariff_capacity_type") == "Firm")
      .filter(pl.col("product_type") == "Yearly")
      .with_columns(pl.col("period_from").dt.year().alias("gas_year"))
      .group_by(["gas_year", "operator"])
      .agg(pl.col("product_simulation_cost_in_euro").mean().alias("avg_euro"))
      .sort(["operator", "gas_year"])
)
print(yoy)
```

# Caveats

## 01 Default `countryKey=UK` filter

Connector passes `countryKey=UK` (`endpoints.py L195`). For full EU, override. *(Source: `connectors/entsog/endpoints.py L195`.)*

## 02 Simulation is for representative products, not actual auctions

The `productSimulationCostIn*` figures are the vendor's compositional total of all tariff components for a standardised capacity product. Actual auction-cleared prices may differ — compare against `cmp_auction_premiums`. *(Source: vault Modelling notes; tariff regulation framework.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 EUR and local-currency columns may differ when FX changes

For GB operators, `productSimulationCostInLocalCurrency` and `productSimulationCostInEURO` are both EUR (`operatorCurrency = "EUR"`). For non-EUR operators (e.g. RO, HU), they differ at the published FX rate; check `exchangeRateReferenceDate`. *(Source: vault Bronze sample L86; FX-rate convention.)*

# Related datasets

- **`tariffs`** — Tariff-component details. `as published`. The line-item-level companion. *entsog · tariffs · daily*
- **`cmp_auction_premiums`** — Auction-cleared prices. `as published`. Compare simulated vs realised. *entsog · CMP · daily*
- **`firm_available`** — Capacity that this simulation prices. `daily`. Volume × tariff = total reservation cost. *entsog · capacity · daily*
- **`operator_point_directions`** — Reference data for the simulated points. `snapshot`. Resolve operator-point-direction context. *entsog · reference · snapshot*
