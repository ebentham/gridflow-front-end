---
slug: operators
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operators
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/operators.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["operators"] (lines 214-222)
  - .planning/reconciliation/entsog/28-operators-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** All European gas <span class="italic fg-accent">TSOs.</span>

**Lede:** Full ENTSO-G transmission system operator inventory — the canonical reference for resolving `operator_key` codes to country, balancing zone, and human TSO names.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operators](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.operators` (single-file snapshot) |
| API PATH | `/api/v1/operators` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change (vendor inventory updates daily) |
| VOLUME | ~100 EU-wide TSOs |
| PRIMARY KEY | `(operator_key)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | ~100 | Active TSOs |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- operator_point_directions
- connection_points
- balancing_zones
- interconnections
- aggregate_interconnections

# Sample chart

- **Type:** `barsH`
- **Title:** "TSOs per country · current inventory"
- **Subtitle:** "Horizontal bars · count · grouped by country"
- **Seed:** 47
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True` (`silver/entsog/generic.py L86, L169-191`), writing a single `operators.parquet` snapshot.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `operator_key` | `str` | Yes | `operatorKey` | TSO identifier (e.g. `UK-TSO-0001`). Inventory key. | dynamic |
| `operator_label` / `operator_label_long` | `str` | Yes | `operatorLabel` / `operatorLabelLong` | Short and long TSO names. | dynamic |
| `operator_tooltip` | `str` | Yes | `operatorTooltip` | Pipe-delimited combination of long label and notes. | dynamic |
| `operator_country_key` / `operator_country_label` | `str` | Yes | `operatorCountryKey` / `operatorCountryLabel` | ISO-style country and human name. | dynamic |
| `operator_country_flag` | `str` | Yes | `operatorCountryFlag` | Flag URL/path. | dynamic |
| `operator_type_label` / `operator_type_label_long` | `str` | Yes | `operatorTypeLabel` / `operatorTypeLabelLong` | E.g. `"TSO"` / `"Transmission System Operator"`. | dynamic |
| `operator_logo_url` | `str` | Yes | `operatorLogoUrl` | Logo URL. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/operators.parquet` (single-file reference dataset — `silver/entsog/generic.py L196-202`)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(operator_key)` — inventory key

# Sample data

| operator_key | operator_label | operator_label_long | operator_country_key | operator_country_label | operator_type_label |
|---|---|---|---|---|---|
| UK-TSO-0001 | National Gas TSO | National Gas Transmission | UK | United Kingdom | TSO |
| UK-TSO-0002 | PTL | Premier Transmission Ltd | UK | United Kingdom | TSO |
| UK-TSO-0003 | Interconnector | Interconnector (UK) Ltd | UK | United Kingdom | TSO |
| **UK-TSO-0004** | **BBL company** | **BBL Company V.O.F.** | **NL** | **Netherlands** | **TSO** |
| IE-TSO-0001 | GNI (UK) Ltd. | GNI (UK) Ltd. | UK | United Kingdom | TSO |
| IE-TSO-0002 | Gas Networks Ireland | Gas Networks Ireland | IE | Ireland | TSO |
| DE-TSO-0010 | bayernets | bayernets GmbH | DE | Germany | TSO |
| FR-TSO-0001 | GRTgaz | GRTgaz S.A. | FR | France | TSO |

**Sources:** Synthesised — vault's documented columns applied to canonical GB-and-neighbours operator records. Highlighted row is BBL company — note `operator_country_key="NL"` despite operator label appearing in GB-relevant `pointDirection` keys (BBL is a Dutch-registered operator running the UK-NL pipeline). Use this dataset to resolve country/zone metadata for cross-vendor joins.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operators?limit=-1&hasData=1`
- AUTH: None (public). `hasData=1` restricts to operators with operational data (recommended default).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/operators/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `OperatorsTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operators?limit=-1&hasData=1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Operators per country (current inventory)
SELECT operator_country_label,
       COUNT(*) AS tsos
FROM read_parquet('data/silver/entsog/operators.parquet')
GROUP BY 1
ORDER BY tsos DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ops = pl.read_parquet("data/silver/entsog/operators.parquet")
# Resolve operator keys mentioned in physical_flows
flows = pl.read_parquet("data/silver/entsog/physical_flows/**/*.parquet")
joined = flows.join(ops, on="operator_key", how="left")
print(joined.select(["point_key", "operator_label_long", "operator_country_label"]).unique().head())
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `operators.parquet` overwritten on each refresh, not partitioned. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L214-222` `reference=True`.)*

## 02 `hasData=1` recommended

Default `hasData=1` restricts to operators with operational data. Without it the inventory includes inactive/legacy TSOs. *(Source: vault Query-params; `endpoints.py L220`.)*

## 03 Pagination via `limit`+`offset`

No `from`/`to` accepted; full inventory only. Connector sets `limit=-1` for one-call extraction. *(Source: vault Query-params; `endpoints.py L214-222`.)*

## 04 Operator country may differ from operating zone

E.g. `UK-TSO-0004` (BBL company) has `operator_country_key="NL"` despite operating UK-relevant interconnection pipeline. Resolve operating zone via `operator_point_directions`. *(Source: vault Known Issues; cross-reference with `operator_point_directions`.)*

## 05 Empty windows return HTTP 404

ENTSO-G's empty-set convention applies even to reference endpoints. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

# Related datasets

- **`operator_point_directions`** — Operator-point-direction combos. `snapshot`. Adds the per-point context for each operator. *entsog · reference · snapshot*
- **`balancing_zones`** — Reference for balancing zones. `snapshot`. Resolve operating zone from operator metadata. *entsog · reference · snapshot*
- **`connection_points`** — Reference for points. `snapshot`. The point side of the operator-point-direction triple. *entsog · reference · snapshot*
- **`physical_flows`** — Operational data using these operator keys. `daily`. Primary downstream consumer. *entsog · operational · daily*
