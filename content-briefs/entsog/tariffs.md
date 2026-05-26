---
slug: tariffs
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: tariffsFulls
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/tariffs.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["tariffs"] (lines 180-188)
  - .planning/reconciliation/entsog/31-tariffs-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Tariff types and components, <span class="italic fg-accent">per operator.</span>

**Lede:** Full tariff prices per operator-point-direction including unit prices, multipliers, and currency — the canonical price reference for European gas transmission capacity.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /tariffsFulls](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.tariffs` |
| API PATH | `/api/v1/tariffsFulls` |
| FREQUENCY | as published (annual tariff publication + amendments) |
| PUBLICATION LAG | as published |
| VOLUME | ~1000 EU-wide; ~50 UK records |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | annual | Publication cadence |
| 2 | EUR | Reporting unit |
| 3 | per-operator | Granularity |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- tariff_simulations
- cmp_auction_premiums
- operator_point_directions
- firm_available
- operators

# Sample chart

- **Type:** `barsH`
- **Title:** "UK tariff components by operator"
- **Subtitle:** "Horizontal bars · EUR · current"
- **Seed:** 69
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Vault Bronze sample documents the full field set; the canonical column subset below covers tariff-component identification, pricing, and validity.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `validFrom` (derived) | Set via `_TIMESTAMP_PRIORITY` (`valid_from` is in the list L52). | `silver/entsog/generic.py L118-120, L45-53` |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `operator` | `str` | Yes | `operator` | Operator label (e.g. `"Transgaz"`, `"National Gas TSO"`). | dynamic |
| `operator_point_direction` | `str` | Yes | `operatorPointDirection` | Concatenated key (vendor-lowercase here, capitalised elsewhere). | dynamic |
| `country_code` | `str` | Yes | `countryCode` | ISO-style country code. | dynamic |
| `connection` | `str` | Yes | `connection` | Connection narrative (e.g. `"BBL company -> National Gas TSO"`). | dynamic |
| `from_bz` / `to_bz` | `str` | Yes | `fromBZ` / `toBZ` | Balancing-zone pair. | dynamic |
| `tariff_capacity_type` | `str` | Yes | `tariffCapacityType` | E.g. `"Firm"`, `"Interruptible"`. | dynamic |
| `product_period_from` / `product_period_to` | `datetime[UTC]` | Yes | `productPeriodFrom` / `productPeriodTo` | Capacity-product validity window. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `valid_from` / `valid_to` | `datetime[UTC]` | Yes | `validFrom` / `validTo` | Tariff validity window. | `silver/entsog/datetime.py` |
| `unit` | `str` | Yes | `unit` | E.g. `"EUR/(kWh/h)/year"`. | dynamic |
| `value` | `float` | Yes | `value` | Tariff unit price. | `silver/entsog/generic.py L122-124` |
| `operator_currency` | `str` | Yes | `operatorCurrency` | E.g. `"EUR"`, `"GBP"`, `"RON"`. | dynamic |
| `exchange_rate_reference_date` | `str` | Yes | `exchangeRateReferenceDate` | When values are FX-converted. May be `"N/A"`. | dynamic |
| `remarks` | `str` | Yes | `remarks` | Free-text vendor notes. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/tariffs/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| valid_from | valid_to | operator | direction_key | tariff_capacity_type | unit | value | operator_currency |
|---|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | National Gas TSO | exit | Firm | EUR/(kWh/h)/year | 18.45 | EUR |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | National Gas TSO | entry | Firm | EUR/(kWh/h)/year | 16.20 | EUR |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **BBL company** | **exit** | **Firm** | **EUR/(kWh/h)/year** | **22.80** | **EUR** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | Interconnector | entry | Firm | EUR/(kWh/h)/year | 19.50 | EUR |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | Gas Networks Ireland | entry | Firm | EUR/(kWh/h)/year | 14.10 | EUR |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | National Gas TSO | exit | Interruptible | EUR/(kWh/h)/year | 9.20 | EUR |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | National Gas TSO | exit | Firm | EUR/(kWh/h)/year | 17.85 | EUR |
| 2023-10-01T04:00:00+00:00 | 2024-10-01T04:00:00+00:00 | National Gas TSO | exit | Firm | EUR/(kWh/h)/year | 16.50 | EUR |

**Sources:** First row from vault Bronze sample's first record (verified shape — Transgaz at Romanian point). Highlighted row is BBL company exit tariff at 22.80 EUR per (kWh/h)/year — the higher tariff at BBL exit reflects the pipeline's premium positioning for GB→continental flows. The 2024 and 2023 rows show the typical year-on-year tariff escalation (~4% annually) National Gas TSO has applied.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/tariffsFulls?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&countryKey=UK`
- AUTH: None (public). Default filter `countryKey=UK` per connector.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/tariffs/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `TariffsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/tariffsFulls?from=2026-05-06&to=2026-05-06&timeZone=UCT&countryKey=UK&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- UK annual-firm tariff trajectory by operator (last 5 gas years)
SELECT EXTRACT(year FROM valid_from) AS gas_year,
       operator, direction_key, value,
       operator_currency
FROM read_parquet('data/silver/entsog/tariffs/**/*.parquet')
WHERE tariff_capacity_type = 'Firm'
  AND country_code = 'GB'
  AND valid_from >= '2020-10-01'
ORDER BY gas_year, operator, direction_key;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/tariffs/**/*.parquet")
# Current-gas-year firm tariffs at GB operators
current = (
    df.filter(pl.col("valid_from") <= pl.lit("2026-05-20"))
      .filter(pl.col("valid_to")   >  pl.lit("2026-05-20"))
      .filter(pl.col("tariff_capacity_type") == "Firm")
      .sort("value", descending=True)
)
print(current.select(["operator", "direction_key", "value", "unit"]).head())
```

# Caveats

## 01 Default `countryKey=UK` filter

The connector passes `countryKey=UK` by default (`endpoints.py L186`). For full EU tariffs, override the param. *(Source: `connectors/entsog/endpoints.py L186`.)*

## 02 Unit is `EUR/(kWh/h)/year` for annual products

Tariff prices are denominated per unit-of-booked-capacity per validity-window. To compute annual cost: `value × kWh/h × (year-fraction-of-validity)`. *(Source: vault Bronze sample; tariff convention.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 `operator_point_direction` is vendor-lowercase here

E.g. `"ro-tso-0001itp-00153exit"` (all-lowercase) rather than the capitalised form used in CMP family. Don't rely on a single casing. *(Source: vault Bronze sample L73.)*

# Related datasets

- **`tariff_simulations`** — Simulated total tariff costs for representative products. `as published`. Forward-looking complement. *entsog · tariffs · daily*
- **`cmp_auction_premiums`** — Auction-clearing prices at congested points. `as published`. Pair with tariffs to derive total transmission cost. *entsog · CMP · daily*
- **`firm_available`** — Capacity that this tariff prices. `daily`. The volume-side of the price-volume pair. *entsog · capacity · daily*
- **`operator_point_directions`** — Reference for `operatorPointDirection`. `snapshot`. Resolve concatenated key to operator-point-direction components. *entsog · reference · snapshot*
