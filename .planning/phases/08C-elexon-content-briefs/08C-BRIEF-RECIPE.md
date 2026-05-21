# Per-brief recipe: vault + gridflow + vendor docs → content-briefs/elexon/<slug>.md

**Purpose**: This is the per-dataset runbook the Phase 8C-01 executor follows for each of the 33 Elexon datasets. The output is a self-contained markdown document that Claude Design can render against the fuelhh.html / system_prices.html visual reference without needing additional research.

> **2026-05-20 evening update (D-22 — Elexon-only Overview restoration):** The 3-paragraph `# Overview` section, removed by D-20 (see next callout), is **restored for Elexon briefs only** in a tighter concise form. Other vendors (Phase 9 ENTSO-E, Phase 10 ENTSO-G / GIE / NESO / Open-Meteo) remain on the D-20 format (no Overview) until they are separately retrofitted — the user's Claude Design budget is low this week. The new shape:
> - **# Overview:** 3 short paragraphs, ~110 words total (P1 ≈50w "what it is + use cases" · P2 ≈45w "how gridflow fetches + transforms" · P3 ≈20w "cadence + verification date"). Modeled on `authored-pages/elexon/fuelhh.html` lines 234-259.
> - **# Sample chart:** Per-dataset realistic shape wired to the `charts.js` `SHAPES` registry (`diurnal-load`, `diurnal-price`, `frequency`, `volatile-spikes`, etc.). Sparkline + priceLadder use `**Shape:**` + `**Params:**` lines; stackedArea with PSR-specific layers uses `**Series:**` (an explicit `series: [...]` JSON); barsH uses inline `**Items:**` (synthesized plausible domain values).
> - Structural check #5 now requires `# Overview` for Elexon briefs (restored). Other vendors keep it suspended for now.
>
> See `content-briefs/elexon/fuelhh.md` for the canonical Elexon-D-22 brief.

> **2026-05-20 update (post-POC verbosity learning — superseded for Elexon by D-22 above):** Brief format tightened after the 5-dataset POC batch (Phase 8D follow-on) showed Claude Design over-produces verbose Overview + Caveats sections from this recipe. The tightened format:
> - **Lede:** 1 short sentence, ~15–25 words. "What it is + how you use it for modelling." No second sentence unless genuinely additive.
> - **No `# Overview` section.** The lede + schema notes + sample-data caption already cover what the dataset is. The 3-paragraph Overview was being stripped from rendered pages as redundant with the hero lede. **D-22 reverses this for Elexon only — see callout above.**
> - **Caveats:** Each item compresses to 1 short sentence (rarely 2) + source citation. Maximum 6 items. The body is research-record-quality, not user-facing prose — Claude Design no longer renders Caveats as a standalone HTML section.
>
> Phase 9 (ENTSO-E, 49 briefs) and Phase 10 (4-vendor batch, 80 briefs) inherit this tightened format. The structural-check `# Overview` row below was **suspended** at D-20 (kept in legacy briefs that pre-date the tighten; new briefs MUST omit) and is **restored for Elexon only** at D-22. See `content-briefs/elexon/fuelhh.md` for the canonical tightened brief (now also Elexon-D-22 compliant).

## Sources (mandatory triangulation)

For each dataset, the executor MUST consult:

1. **Vault** (always present): `vault/elexon/<slug>.md` — read in full
2. **Gridflow Pydantic schema** (usually present): `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\schemas\elexon.py` — locate the `class Elexon<Slug>(BaseModel):` block; read all fields, types, validators, defaults
3. **Gridflow silver transformer** (usually present): `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\silver\elexon\<slug>.py` — locate the `class <Slug>Transformer:` or function; understand input → output mapping
4. **Gridflow connector** (always present): `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\connectors\elexon\endpoints.py` — find the registry entry for this slug; confirm path, params, pagination
5. **Vendor docs**: Fetch via WebFetch — Elexon BMRS Swagger UI at `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/<API_CODE>` (or the specific path for non-dataset endpoints). If the URL 404s or content is JS-only and unfetchable, note in `discrepancies_found` as `vendor_docs_unfetchable: <reason>` and proceed with vault + gridflow only.

If any source is missing (e.g., no Pydantic schema for the dataset), note in frontmatter `sources_consulted` with a "(absent — reason: ...)" annotation. Do not fabricate.

## Output

Single markdown file at `content-briefs/elexon/<slug>.md`.

## Brief structure (required sections in this order)

### Frontmatter (YAML)

```yaml
---
slug: <slug>
vendor: elexon
vendor_label: Elexon BMRS
api_code: <CODE>
last_verified: <YYYY-MM-DD from vault>
sources_consulted:
  - vault/elexon/<slug>.md
  - gridflow/src/gridflow/schemas/elexon.py::Elexon<ClassName> (lines X-Y)
  - gridflow/src/gridflow/silver/elexon/<slug>.py::<TransformerName>
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines X-Y, endpoint registration)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/... (fetched YYYY-MM-DD HH:MM:SS UTC)
discrepancies_found:
  - source_a: "vault Known-Issues #N"
    source_a_says: "..."
    source_b: "gridflow schemas/elexon.py L142"
    source_b_says: "..."
    orchestrator_recommendation: "trust gridflow"
  # (or empty list [] if none found — must explicitly declare)
ready_for_claude_design: true
checked_at: <ISO-8601 UTC>
---
```

### # Editorial layer

- **Short tagline** (italic-accent guidance): A 5–10 word phrase. Compose by reading vault Overview para 1 and distilling. Pattern: `{noun phrase} {accent-phrase}.` Accent phrase = last 1-3 words, intended to be wrapped in `<span class="italic fg-accent">...</span>` when rendered. Examples from reference outputs:
  - fuelhh: `Generation by fuel type, half-hourly.` (accent: "half-hourly.")
  - system_prices: `GB imbalance prices, settled half-hourly.` (accent: "settled half-hourly.")

- **Lede** (1 short sentence, ~15–25 words — tightened 2026-05-20): One sentence that does both jobs: "what it is + how you use it for modelling." Pattern: `{short noun phrase} — the canonical {modelling use 1}, {modelling use 2}, and {modelling use 3}.` Examples:
  - fuelhh: `Half-hourly GB generation by fuel type — the canonical observation series for generation mix, capacity factors, and emissions.`
  - system_prices: `GB cash-out prices per settlement period — the canonical signal for short-term power-market value and BSC imbalance settlement.`

  No second sentence unless it's genuinely additive (e.g. a defining cadence quirk the schema columns can't carry). Hard ceiling: 30 words.

- **Last-verified line**: `Verified against vendor docs: {YYYY-MM-DD} · {Vendor BMRS · CODE}`. Vendor doc URL goes inline.

### # Hero metadata (6 cells, 2×3 grid)

A markdown table with two columns: `Cell label` | `Value`. Cells: `SILVER PATH`, `API PATH`, `FREQUENCY`, `PUBLICATION LAG`, `VOLUME`, `PRIMARY KEY`. Each value should be short (≤80 chars); if the API PATH is long, note that Claude Design should render with `<br/>` line breaks and `font-size:10px`.

Values must be:
- SILVER PATH: `silver.<slug>` (short editorial form, never the full partitioned path)
- API PATH: from gridflow connector source (the canonical path string registered with the connector)
- FREQUENCY: from `site/hifi/data/elexon.json` manifest's `freq` field for this slug
- PUBLICATION LAG: from manifest's `lag` field, or vault's "Publication lag" row
- VOLUME: from manifest's `rows` field (verbatim string like "1.4M / mo")
- PRIMARY KEY: from gridflow transformer source (the `dedup_key` argument or equivalent)

### # Stats strip (4 cells)

Markdown table: `slot` | `value` | `label`. Pattern (unit-suffix in mono):
- Slot 1 (default): freq value · "Frequency"
- Slot 2 (default): lag value · "Publication lag"
- Slot 3 (CUSTOM per dataset): something noteworthy — schema count, row count, settlement runs count, codelist count
- Slot 4 (default): schema column count · "Schema columns"

For Slot 3, identify what's notable about the dataset. Examples:
- system_prices → "7 / Reconciliation runs"
- fuelhh → "1.4M / Rows / month"
- agpt → "32 / PSR types"
- bmunits_reference → "1200+ / Active BM units"

### # Sidebar siblings

A markdown list: 4-6 sibling slugs from the same group in `elexon.json` (semantically related). One slug per line.

### # Overview — **RESTORED 2026-05-20 evening (D-22) for Elexon only**

> **For Elexon briefs:** required. For all other vendors: still omitted (until separately retrofitted).

The 3-paragraph Overview is restored in a concise form for Elexon. Total target ~110 words, modeled on the rendered Overview in `authored-pages/elexon/fuelhh.html` (lines 234-259).

**Paragraph 1 (≈50 words) — "What it is + use cases":**

Open with an inline `<code>{slug}</code>` chip and a single declarative sentence stating what the dataset is. Follow with one sentence enumerating modelling use cases (forecast-error analysis, cash-out attribution, capacity-factor work, etc.). Use the brief's existing Lede as the seed; expand by one sentence with a use-case the Lede doesn't already cover.

**Paragraph 2 (≈45 words) — "How Gridflow fetches and transforms it":**

State the API path (`<code>/datasets/XYZ</code>`), the fetch param style (`publishDateTimeFrom` / `publishDateTimeTo`, `measurementDateTimeFrom`, `DATE_PATH`, `SETTLEMENT_DATE_PERIOD`, etc.), and the transformer name (`<code>XYZTransformer</code>`). Mention the Pydantic schema if one exists; otherwise note "no Pydantic class; shape enforced by the transformer's `output_cols`". Sources: brief's `discrepancies_found` frontmatter + Hero metadata + Schema citation.

**Paragraph 3 (≈20 words) — "Cadence + verification date":**

Single sentence stating refresh frequency and publication lag (from `# Hero metadata`), then "Verified against vendor docs on {last_verified}". That's it.

**Canonical example (fuelhh):**

```markdown
# Overview

1. <code>fuelhh</code> is the half-hourly GB generation outturn aggregated by fuel type — the realised MWh in each settlement period split by fuel category (CCGT, coal, nuclear, wind, solar, biomass, interconnectors). It is the canonical observation series for the GB generation mix and underpins capacity-factor analytics and emissions reporting.

2. Gridflow fetches it from <code>/datasets/FUELHH</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze, is validated against the <code>ElexonFuelHH</code> Pydantic schema, and written to the silver parquet partition via <code>FuelHHTransformer</code>.

3. Refreshed every 30 minutes with ~5 minute publication lag. Verified against vendor docs on 2026-05-08.
```

Hard caps:
- Maximum 120 words across all three paragraphs.
- No bullet lists, no second h2, no "Notable" sidecar — Overview is plain prose only.

For non-Elexon vendors (Phase 9 ENTSO-E, Phase 10 ENTSO-G/GIE/NESO/Open-Meteo), this section is still **omitted** until they are separately retrofitted in a later D-XX decision.

### # Sample chart

Markdown subsections:
- **Type**: one of `stackedArea` | `sparkline` | `barsH` | `heatmap` | `priceLadder` | `donut`. Decision tree:
  - Fuel/PSR/category mix over time → `stackedArea`
  - SBP/SSP or buy/sell ladder → `priceLadder`
  - Single time series → `sparkline`
  - Horizontal bar rank → `barsH`
  - Hour-of-day or day-of-week pattern → `heatmap`
  - "What fraction" displays → `donut`
- **Title**: e.g., "SBP & SSP · 24-hour snapshot"
- **Subtitle**: e.g., "Price ladder · £/MWh · UTC · 6 May 2026"

**D-22 chart-shape contract (Elexon).** Pick **one** of the four shape-spec keys based on chart type:

- **`Shape:` + `Params:`** (sparkline / priceLadder) — name a key from the `charts.js` `SHAPES` registry and a JSON object of overrides. Available shapes: `diurnal-load`, `diurnal-solar`, `diurnal-wind`, `diurnal-price`, `diurnal-temp`, `flat-baseload`, `frequency`, `bipolar-flow`, `volatile-spikes`. Example:
  ```
  - **Shape:** `diurnal-load`
  - **Params:** `{"peak": 42000, "trough": 26000, "noise": 0.04, "seed": 13}`
  ```
- **`Series:`** (stackedArea with PSR-correct or domain-specific layers — agpt, agws) — an array of `{name, color, shape, params?}` objects, one per stacked layer. Example: agpt has 5 layers (Wind Onshore, Wind Offshore, Solar, Biomass, Pumped Storage) with shape + params per layer.
- **(unspecified — legacy default)** (stackedArea where the default GB fuel mix renders well — fuelhh, fuelinst, fou2t14d, uou2t14d) — just specify `Type: stackedArea` and `Seed:`. The `charts.js` legacy path generates the realistic GB fuel mix.
- **`Items:`** (barsH) — an inline array of `{label, value, color?, display?}` synthesized with plausible domain values (e.g. top-10 BMU names, fuel categories, interconnector codes). Embedded directly in `data-opts` of the HTML page.

- **Toggles**: usually `24h` / `7d` / `30d` chips (with `24h` active)
- **Seed**: an integer 1-99 for chart variety (still used as fallback for any path that doesn't set its own seed in params).

### # Schema (per-column table)

Markdown table: `Column` | `Type` | `Nullable` | `Source field` | `Notes` | `Gridflow citation`. One row per Pydantic field. Required:
- Column = silver column name (`snake_case`)
- Type = exact Python type from Pydantic (preserve `Optional[str]`, `datetime[UTC]`, etc.)
- Nullable = `Yes` if `Optional[...]` or has `= None` default; else `No`
- Source field = the API field name (`camelCase` in vendor JSON) the column derives from, or `_derived_`
- Notes = 1-2 sentences. Mention range constraints (`ge=`, `le=`, regex), vendor-managed value lists, derivation logic
- Gridflow citation = file:line. Format: `schemas/elexon.py L142` or `silver/elexon/<slug>.py L78`

Below the table, partition-info subsections:
- PARQUET PATH: `data/silver/elexon/<slug>/year=YYYY/month=MM/`
- PARTITION BY: `settlement_date (year + month)` (or as per gridflow)
- DEDUP KEY: from gridflow transformer

### # Sample data (8 rows)

A markdown table with realistic rows. Sources, in priority order:
1. Gridflow test fixtures (look in `gridflow/tests/fixtures/elexon/` or similar — if available)
2. Vault Silver Sample section (the Python dict in the Silver layer subsection)
3. Vault Bronze Sample (raw JSON — transform fields to silver shape)
4. Synthesized — use plausible domain values respecting Pydantic constraints; note as synthesised in citation

Each row labels the source via a footnote: `[1] gridflow tests/fixtures/elexon/<slug>_silver.parquet (commit abc123)` or `[2] vault Silver Sample (live 2026-05-09)` or `[3] synthesised — respects schema constraints (price ge=-500, le=10000; period 1..50)`.

Highlight one row as the "interesting" case (peak hour, P-derivation, edge case) and explain why in a caption below the table.

### # Dataset-specific section (conditional)

Pick one based on dataset shape:

- **Fuel/PSR-type/bidding-zone codelists** → pill grid (mirrors fuelhh "Fuel types" with colored swatches per code). Use the gridflow `bmunits` connector or vendor docs to enumerate codes.
- **Settlement-run-affected** (most settlement endpoints) → run-types grid (II / SF / R1 / R2 / R3 / RF / DF — mirrors system_prices "Settlement runs")
- **Notification/regulatory feeds** (`pn`, `remit`, `soso`, `nonbm`) → skip entirely; note `dataset_specific_section: omitted` in frontmatter, drop the sidebar anchor
- **Reference data** (`bmunits_reference`) → pill grid for BM-unit categories (Generator / Supplier / Interconnector / Storage / etc.)

If unsure, skip and note in frontmatter as `dataset_specific_section: omitted (reason: ...)`.

### # API & ingestion

Two subsections (cards):

**Card 1: Endpoint + Auth**
- ENDPOINT: full URL with `<br/>` line breaks for readability
- AUTH: paraphrase from vault API endpoint > Auth row; link `elexonportal.co.uk` for registration if mentioned

**Card 2: Bronze + Transformer**
- BRONZE PATH: e.g., `data/bronze/elexon/<slug>/<year>/<month>/<day>/raw_<uuid>.json` (from vault Bronze layer Path pattern)
- TRANSFORMER: full Python path from gridflow source

Then three code-example tabs:

**Tab 1: Example URL** — realistic API URL with example date/params (from vendor docs and gridflow connector)

**Tab 2: DuckDB · SQL** — 4-8 line `SELECT` using `read_parquet('data/silver/elexon/<slug>/**/*.parquet')` with a useful `WHERE` and `ORDER BY`. Dataset-appropriate.

**Tab 3: Python · parquet** — 4-10 line polars snippet doing something dataset-appropriate (pivot fuel-mix wide, daily-mean-price, max-min spread, etc.)

### # Caveats (3-6) — **tightened 2026-05-20**

Numbered list (01, 02, 03...). **Each caveat compresses to 1 short sentence (rarely 2) + source citation.** The brief is now a research record; Claude Design no longer renders Caveats as a standalone HTML section, so the body doesn't need to "read well" — it needs to be a terse, citable fact.

Per caveat:
- **Title** (1 line, sentence case — same as before)
- **Body** (1 sentence, max 2 — tightened. Inline `<code>` for identifiers, no rhetorical setup)
- **Source citation**: which vault Known-Issue, which gridflow Implementation-Delta, or "domain knowledge (BSC settlement / DST / API limits)"

Example (fuelhh, tightened):
```
## 01 Settlement period range is 1..50

DST days have 46 (spring) or 50 (autumn) settlement periods. Validator `ge=1, le=50`. *(Source: `schemas/elexon.py L83`.)*
```

Sources, priority order (unchanged):
1. Vault Known Issues section
2. Vault Implementation Delta section (non-cosmetic deltas)
3. Vault Changelog (the V2-FIX-* fixes)
4. Gridflow source code (validators, transformer logic, connector retries)
5. Domain knowledge

### # Related datasets (4 cards)

Markdown list. Per card:
- **Slug** (mono identifier)
- **Title** (short)
- **Frequency chip** (`30 min`, `~5 min`, etc.)
- **Editorial 1-liner**: why a user of `<this dataset>` would want this related one
- **Tagline at bottom**: `elexon · <group> · <freq>`

Pick the 4 most-semantically-related Elexon datasets (same group, paired data, different granularity, upstream/downstream in pipeline).

---

## Structural checks (run after writing each brief, before commit)

```bash
SLUG="<slug>"
FILE="content-briefs/elexon/${SLUG}.md"

# 1. File exists
[ -f "$FILE" ] || echo "FAIL: file missing"

# 2. Frontmatter parses (uses python yaml lib)
python -c "import yaml; yaml.safe_load(open('${FILE}').read().split('---')[1])" 2>&1 | grep -q Error && echo "FAIL: invalid frontmatter"

# 3. Required frontmatter keys present
for key in slug vendor api_code last_verified sources_consulted discrepancies_found ready_for_claude_design checked_at; do
  grep -q "^${key}:" "$FILE" || echo "FAIL: missing frontmatter key: ${key}"
done

# 4. sources_consulted has >= 3 entries (vault + gridflow + vendor)
sources_count=$(awk '/^sources_consulted:/{flag=1; next} /^[a-z_]+:/{flag=0} flag' "$FILE" | grep -c "^  -")
[ "$sources_count" -ge 3 ] || echo "FAIL: < 3 sources cited ($sources_count)"

# 5. All required sections present (in order — D-22: `# Overview` RESTORED for Elexon only)
for section in "# Editorial layer" "# Hero metadata" "# Stats strip" "# Sidebar siblings" "# Overview" "# Sample chart" "# Schema" "# Sample data" "# API & ingestion" "# Caveats" "# Related datasets"; do
  grep -qF "$section" "$FILE" || echo "FAIL: missing section: $section"
done
# 5b. D-22 (2026-05-20 evening, Elexon-only) — Overview is required again for Elexon briefs.
#     For other vendors keep the D-20 omit rule until they are retrofitted separately.
#     (If running this check against an ENTSO-E / ENTSO-G / GIE / NESO / Open-Meteo brief,
#     remove "# Overview" from the section list above.)

# 6. Schema has at least 3 rows (excluding header + separator) — check by counting | at row starts
schema_rows=$(awk '/^# Schema/{flag=1; next} /^# /{flag=0} flag && /^\|/' "$FILE" | grep -v '^|--' | grep -v '^| Column' | wc -l)
[ "$schema_rows" -ge 3 ] || echo "FAIL: schema rows < 3 ($schema_rows)"

# 7. At least 3 caveats numbered
caveat_count=$(grep -cE '^## 0[1-9]' "$FILE")
[ "$caveat_count" -ge 3 ] || echo "FAIL: < 3 caveats ($caveat_count)"

# 8. Related datasets has 4 cards (slug entries)
related_count=$(awk '/^# Related datasets/{flag=1; next} /^# /{flag=0} flag' "$FILE" | grep -cE '^- \*\*')
[ "$related_count" -ge 3 ] || echo "FAIL: < 3 related datasets ($related_count)"

# 9. Inline <code> chip usage (signal of editorial polish)
code_count=$(grep -cE '<code|`[a-z_]' "$FILE")
[ "$code_count" -ge 5 ] || echo "FAIL: insufficient inline code chips ($code_count, want >= 5)"

# 10. ready_for_claude_design: true is set
grep -q '^ready_for_claude_design: true' "$FILE" || echo "FAIL: ready flag not true"

# 11. last_verified matches vault's last_verified
VAULT_LV=$(grep -E '^last_verified:' "vault/elexon/${SLUG}.md" | awk '{print $2}')
BRIEF_LV=$(grep -E '^last_verified:' "$FILE" | head -1 | awk '{print $2}')
[ "$VAULT_LV" = "$BRIEF_LV" ] || echo "FAIL: last_verified mismatch (vault=$VAULT_LV, brief=$BRIEF_LV)"

# 12. discrepancies_found is a list (key present, value is `[]` or list items)
grep -qE '^discrepancies_found:\s*(\[\]|$)' "$FILE" || echo "FAIL: discrepancies_found malformed"
```

Failures → append to `.planning/phases/08C-elexon-content-briefs/BRIEF-LOG.md` with slug + failed checks + 1-line reason. Do NOT commit. Continue to next slug.

## Commit pattern (per successful brief)

```
docs(08C): content brief for <slug> · triangulated against vault + gridflow + vendor docs

<one-paragraph summary of what was found, including discrepancy count>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
