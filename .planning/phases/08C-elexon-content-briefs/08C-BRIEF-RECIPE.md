# Per-brief recipe: vault + gridflow + vendor docs → content-briefs/elexon/<slug>.md

**Purpose**: This is the per-dataset runbook the Phase 8C-01 executor follows for each of the 33 Elexon datasets. The output is a self-contained markdown document that Claude Design can render against the fuelhh.html / system_prices.html visual reference without needing additional research.

> **2026-05-20 update (post-POC verbosity learning):** Brief format tightened after the 5-dataset POC batch (Phase 8D follow-on) showed Claude Design over-produces verbose Overview + Caveats sections from this recipe. The tightened format:
> - **Lede:** 1 short sentence, ~15–25 words. "What it is + how you use it for modelling." No second sentence unless genuinely additive.
> - **No `# Overview` section.** The lede + schema notes + sample-data caption already cover what the dataset is. The 3-paragraph Overview was being stripped from rendered pages as redundant with the hero lede.
> - **Caveats:** Each item compresses to 1 short sentence (rarely 2) + source citation. Maximum 6 items. The body is research-record-quality, not user-facing prose — Claude Design no longer renders Caveats as a standalone HTML section.
>
> Phase 9 (ENTSO-E, 49 briefs) and Phase 10 (4-vendor batch, 80 briefs) inherit this tightened format. The structural-check `# Overview` row below is **suspended** (kept in legacy briefs that pre-date the tighten; new briefs MUST omit). See `content-briefs/elexon/fuelhh.md` for the canonical tightened brief.

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

### # Overview — **REMOVED 2026-05-20**

This section is no longer required and MUST be omitted from new briefs.

**Why removed:** Empirical evidence from the 5-dataset POC batch (entsoe / entsog / gie / neso / openmeteo, 2026-05-20) showed the rendered HTML "What this dataset is" section was straight-up redundant with the hero lede — the user stripped it from all 5 pages. The 3-paragraph Overview cost research time and produced no incremental value over the lede + schema + sample data.

**Where the old paragraph content goes instead:**
- Paragraph 1 ("what it is") → already in the **Lede**.
- Paragraph 2 ("how Gridflow fetches it") → in the **# API & ingestion** section's Card 1 / Card 2 (endpoint + transformer + bronze path are already there).
- Paragraph 3 ("cadence + provenance") → cadence is in the **# Hero metadata** table and **# Stats strip**; verification date is in frontmatter `last_verified`.

If a dataset has a genuinely load-bearing fact that doesn't fit anywhere else (rare — e.g. a complex bitemporal pattern), append it as a **2-sentence "Notable" callout** under the lede. Do NOT reintroduce a 3-paragraph block.

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
- **Seed**: an integer 1-99 for chart variety
- **Toggles**: usually `24h` / `7d` / `30d` chips (with `24h` active)

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

# 5. All required sections present (in order — `# Overview` removed 2026-05-20)
for section in "# Editorial layer" "# Hero metadata" "# Stats strip" "# Sidebar siblings" "# Sample chart" "# Schema" "# Sample data" "# API & ingestion" "# Caveats" "# Related datasets"; do
  grep -qF "$section" "$FILE" || echo "FAIL: missing section: $section"
done
# 5b. NEW (2026-05-20) — confirm legacy `# Overview` section is absent in new briefs
grep -qF "# Overview" "$FILE" && echo "WARN: legacy '# Overview' section present — should be removed per tightened recipe"

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
