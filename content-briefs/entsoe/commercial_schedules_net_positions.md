---
slug: commercial_schedules_net_positions
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A09 (removed — see ADR-019)
last_verified: 2026-05-11
entitlement_required: false
schema_class: "(absent — removed in V2 ADR-019, registry-duplicate of commercial_schedules)"
deprecated: true
sources_consulted:
  - vault/entsoe/commercial_schedules_net_positions.md (deprecated pointer page)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py (lines 155-159, removal comment)
  - .planning/reconciliation/entsoe/44-commercial-schedules-net-positions-no-silver-section.md (wontfix v3-candidate)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "vault/entsoe/commercial_schedules_net_positions.md (still exists in vault)"
    source_a_says: "Dataset is deprecated; status: deprecated; use commercial_schedules instead"
    source_b: "gridflow endpoints.py L155-159"
    source_b_says: "DOC_TYPES entry removed in V2 — registry-duplicate of commercial_schedules; identical EntsoeDocType, identical XML at request time"
    orchestrator_recommendation: "Treat as deprecated pointer page. Brief documents the removal explicitly so future readers understand why this slug existed and where to look instead."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Deprecated — registry duplicate of <span class="italic fg-accent">commercial_schedules.</span>

**Lede:** Deprecated pointer for the V2-removed `commercial_schedules_net_positions` slug — registered an identical EntsoeDocType to `commercial_schedules` (ADR-019). Use `commercial_schedules` instead.

**Verified line:** Verified against gridflow source 2026-05-20 · removed in V2 (ADR-019, 2026-05-09) · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.commercial_schedules_net_positions` (legacy parquet may exist) |
| API PATH | _removed in V2_ |
| FREQUENCY | n/a — deprecated |
| PUBLICATION LAG | n/a |
| VOLUME | n/a |
| PRIMARY KEY | _removed_ |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | DEPRECATED | Status |
| 2 | ADR-019 | Removal reference |
| 3 | A09 | Original DocumentType (now `commercial_schedules`) |
| 4 | 0 | Active Pydantic columns |

# Sidebar siblings

- commercial_schedules
- net_positions
- cross_border_flows
- net_transfer_capacity
- redispatching_cross_border

# Sample chart

- **Type:** `sparkline`
- **Title:** "Deprecated — see commercial_schedules"
- **Subtitle:** "no chart · n/a · n/a"
- **Seed:** 47
- **Toggles:** `n/a`

# Schema

**Removed in V2.** Per ADR-019, this slug had no distinct Pydantic schema — it shared `commercial_schedules`'s EntsoeDocType and returned the identical XML. The "net positions" interpretation was never implemented; the legacy transformer emitted the same per-direction rows as `CommercialSchedulesTransformer`. A future signed `net_position_mw` dataset would require pairing both zone-pair directions per period; track in v3 backlog.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| _no columns_ | n/a | n/a | n/a | Dataset removed; refer to `commercial_schedules.md` brief for schema. | `endpoints.py L155-159` (removal comment) |
| (legacy parquet on disk) | n/a | n/a | n/a | Historical files under `data/silver/entsoe/commercial_schedules_net_positions/...` may exist locally; no scheduled gold consumer reads them. | vault L29-32 |
| (replacement) | n/a | n/a | n/a | All consumers should read `silver.commercial_schedules` instead. | this brief |

**PARQUET PATH:** _removed; legacy data may exist under `data/silver/entsoe/commercial_schedules_net_positions/`_
**PARTITION BY:** _n/a_
**DEDUP KEY:** _n/a_

# Sample data

| timestamp_utc | note |
|---|---|
| _removed_ | Refer to `commercial_schedules` for actual schedule data. |
| _removed_ | Legacy parquet on disk preserves historical rows in the old (duplicate) shape. |
| _removed_ | No scheduled gold consumer reads the legacy partition. |

**Sources:** This dataset has no live or synthesised sample because it was removed in V2 (ADR-019, 2026-05-09). The corresponding XML payloads now arrive via `commercial_schedules`. The vault page exists only as a deprecation pointer for old links.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: _removed in V2; was identical to `commercial_schedules` (A09)_
- AUTH: n/a

**Card 2 — Bronze + Transformer**
- BRONZE PATH: _no longer ingested; replaced by `data/bronze/entsoe/commercial_schedules/...`_
- TRANSFORMER: _removed; `CommercialSchedulesNetPositionsTransformer` deleted in V2_

**Tab 1 — Example URL**

Use the `commercial_schedules` brief's example URL — the API call shape is identical. See `content-briefs/entsoe/commercial_schedules.md`.

**Tab 2 — DuckDB · SQL**
```sql
-- Read the replacement dataset instead
SELECT timestamp_utc, in_area_code, out_area_code, quantity_mw
FROM read_parquet('data/silver/entsoe/commercial_schedules/**/*.parquet')
WHERE in_area_code = '10YGB----------A'
ORDER BY timestamp_utc DESC LIMIT 24;
```

**Tab 3 — Python · polars**
```python
import polars as pl
# This dataset is removed — read commercial_schedules instead.
df = pl.read_parquet("data/silver/entsoe/commercial_schedules/**/*.parquet")
print(df.tail())
```

# Caveats

## 01 Removed in V2 (ADR-019)

This dataset key was removed because it registered an identical EntsoeDocType to `commercial_schedules` and returned the identical XML. The "net positions" interpretation was never implemented. *(Source: `endpoints.py L155-159` comment; vault deprecation note.)*

## 02 Use `commercial_schedules` for the underlying data

All consumers should read `silver.commercial_schedules`. The API call shape is identical. *(Source: vault L29-32.)*

## 03 Legacy parquet may exist locally — not used by gold

Historical files under `data/silver/entsoe/commercial_schedules_net_positions/...` may remain in some data directories. Deleting them is a separate cleanup; no scheduled gold consumer reads them. *(Source: vault L29-32.)*

## 04 A real signed net_position_mw is v3 backlog

A genuine "net positions" dataset would require pairing both zone-pair directions per period and emitting a single signed value. It should be added under a new dataset key when a downstream consumer needs it — tracked in v3. *(Source: vault L34-37.)*

## 05 Not entitlement-blocked

The underlying A09 endpoint (now `commercial_schedules`) is accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no 401 file for this slug.)*

# Related datasets

- **`commercial_schedules`** — Replacement for this dataset. `PT60M`. The active A09 surface; read this instead. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow per border. `PT60M`. The physical counterpart to commercial schedules. `entsoe · transmission · hourly`
- **`net_positions`** — Implicit-auction net positions per zone (A25/B09). `PT60M`. The genuine net-position surface — different DocumentType from this one. `entsoe · capacity · hourly`
- **`net_transfer_capacity`** — Day-ahead NTC cap. `PT60M`. The capacity constraint commercial schedules clear against. `entsoe · transmission · hourly`
