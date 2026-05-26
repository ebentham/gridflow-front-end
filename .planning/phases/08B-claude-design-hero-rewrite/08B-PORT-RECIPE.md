# Port recipe: vault → authored-pages/elexon/<slug>.html

**Purpose**: This is the runbook the Phase 8B-01 executor follows for each of the 31 Elexon datasets. The two reference outputs are `authored-pages/elexon/fuelhh.html` (Claude-Design, ~619 lines) and `authored-pages/elexon/system_prices.html` (AI-port, ~624 lines, user-verified 2026-05-19). Both passed visual verification. Follow this recipe exactly per dataset.

## Inputs per dataset

- `vault/elexon/<slug>.md` — authoritative content source (YAML frontmatter + structured sections)
- `site/hifi/data/elexon.json` — vendor manifest (group, freq, lag, rows for each slug — use this for stat-strip values when vault is silent)
- `authored-pages/elexon/system_prices.html` — structural template (the **closer** of the two references; uses exactly the same `<head>` + `<style>` + structural HTML)

## Output per dataset

- `authored-pages/elexon/<slug>.html` (source of truth)
- `site/hifi/data-sources/elexon/<slug>.html` (copy — survives subsequent `gridflow-build` runs **only after Task 1 wires the override path**; until then, manual copy)

## Strict invariants (verified per port — see "Structural checks" below)

1. `<meta name="viewport" content="width=device-width, initial-scale=1" />` — NOT `width=1280`. Mobile-safe is non-negotiable (Phase 8B D-04).
2. All sidebar anchors resolve to real `<section id>` elements.
3. `<title>` is `<slug> · Elexon BMRS · Gridflow`.
4. `data-page="dataset"`, `data-root="../../"`, `data-screen-label="Dataset · <slug>"` on `<body>`.
5. CSS link is `../../assets/theme.css`. JS links are `../../assets/charts.js` and `../../assets/site.js`.
6. Embedded `<style>` block is **byte-identical** to system_prices.html (same schema-table, data-table, run-grid/fuel-grid, sidebar, caveat-item, related-grid rules). Copy it verbatim — do not "improve" any CSS.
7. Hero grid uses `grid-template-columns: 1.35fr 1fr; gap: 56px; align-items: end;` — copy from system_prices verbatim.
8. Metadata card uses `grid-template-columns: 1fr 1fr` (2-column 3-row 2×3 grid) — copy from system_prices verbatim.
9. Sample chart uses one of charts.js's named helpers: `stackedArea` | `sparkline` | `barsH` | `heatmap` | `priceLadder` | `donut` (see `site/hifi/assets/charts.js`).
10. Scrollspy + tab-toggle `<script>` blocks at end of body are **byte-identical** to system_prices.html (only the tab-group name string changes).

## Per-section porting rules

### Breadcrumb + Hero

- **Breadcrumb**: `Gridflow / Data sources / Elexon BMRS / <slug>` — same shape as system_prices. Just swap `<slug>`.
- **Eyebrow chip row**: `Dataset · Elexon · <group>` (read `<group>` from vault's `dataset_key`-mapping in `site/hifi/data/elexon.json` — find the group containing this slug). Add freq/lag chip: `<freq> · <lag>`. Add "Illustrative snapshot" chip.
- **H1**: `<span class="fg-soft" ... mono>{slug}</span><br/>{editorial_tagline}`
  - **Editorial tagline rules**:
    - Compose a short editorial phrase, 5–10 words, capturing the dataset's purpose
    - Apply `<span class="italic fg-accent">...</span>` to the final 1–3 words (the "punch")
    - Examples already in use:
      - fuelhh: `Generation by fuel type, <em>half-hourly.</em>`
      - system_prices: `GB imbalance prices, <em>settled half-hourly.</em>`
    - Composition pattern: `{what} {accent-phrase}.` where the accent is a frequency/granularity/scope phrase
- **Lede paragraph** (`<p class="lede">`, max-width 600px): 2–4 sentences. Compose from vault's Overview section, condensed. Lead with the dataset's purpose; mention the canonical use; keep concrete (no marketing voice).
- **Verified line** (`<p class="tiny">`): `Verified against vendor docs: <last_verified> · <a>Elexon BMRS · <api_code> ↗</a>` where `<api_code>` is extracted from the vault H1 (the backtick-wrapped uppercase code, e.g. `FUELHH`, `DISEBSP`, `B1620`). The `<a href>` should be `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/<api_code>` for normal datasets, or the specific endpoint path if the vault's API endpoint section gives one (e.g., `/balancing/settlement/system-prices/-settlementDate-` for system_prices).

### Metadata card (6 cells, 2×3 grid)

| Cell | Source |
|---|---|
| SILVER PATH | `silver.<slug>` — short editorial form, NEVER the full partitioned path |
| API PATH | Extract from vault "API endpoint" table > Path row. If long, wrap with `<br/>` and use `font-size:10px; line-height:1.4;` |
| FREQUENCY | From manifest's `freq` field; mirror exactly |
| PUBLICATION LAG | From manifest's `lag` field, or vault's "Publication lag" row |
| VOLUME | From manifest's `rows` field — use the same string verbatim (e.g., "1.4M / mo", "~1.4k / mo") |
| PRIMARY KEY | From vault's "Dedup key:" line — wrap with `<br/>` if multi-column |

### Stats strip (4 cells)

Pick 4 stats that are TRUE and notable for the dataset. Pattern (mono-suffix for units):

- `<div class="stat-n">30<span style="font-size:18px; color:var(--ink-soft); margin-left:2px;">min</span></div>` (frequency)
- `<div class="stat-n">N</div>` (count)

Suggested defaults (modify per dataset):

| Slot | Default value | Default label |
|---|---|---|
| 1 | freq | Frequency |
| 2 | lag | Publication lag |
| 3 | dataset-specific count (rows/mo, schema cols, range) | dataset-specific label |
| 4 | schema columns count (count rows in vault silver schema table) | Schema columns |

For system_prices, slot 3 was "7 / Reconciliation runs" (notable because of BSC run types). For each port, identify what's notable about the dataset and use slot 3 to surface it.

### Sidebar

Two sections:

1. **On this page**: 6–8 anchor links. Standard set:
   - `Overview` (always)
   - `Snapshot chart` (always; href `#live-chart`)
   - `Schema` (always)
   - `Sample data` (always)
   - `<third section name>` (conditional — see "Third section" below)
   - `API & ingestion` (always)
   - `Caveats` (always)
   - `Related datasets` (always)
2. **Elexon BMRS**: `← All datasets` link to `../elexon.html`, then 4–6 sibling datasets. The current slug is `class="active"`. Pick siblings from the same group in `elexon.json` (semantically related). Make them `style="color:var(--ink-faint);"` for visual de-emphasis.

### Overview (3 paragraphs)

Adapt vault's Overview section into 3 paragraphs:
1. **What it is**: open with `<code class="mono" ...>{slug}</code> is the {one-line definition}`. Composed from vault Overview para 1.
2. **How Gridflow fetches it**: mention the endpoint path with inline `<code>`, the transformer class with inline `<code>`. Compose from vault's "Silver layer" > "Transformer class" line.
3. **Cadence + provenance**: refresh cadence, what the data is used for, verification date.

Use the **inline `<code>` chip pattern** for any technical identifier:
```html
<code class="mono" style="font-size:13px; background: var(--paper-deep); padding: 2px 6px; border: 1px solid var(--rule);">identifier</code>
```

For shorter identifiers inside dense prose, use `font-size: 12px`.

### Sample chart

Pick a chart helper from `site/hifi/assets/charts.js`. Decision tree:

| Dataset shape | Recommended helper | Example |
|---|---|---|
| Fuel/category mix over time | `stackedArea` | fuelhh, fuelinst |
| Prices over time (high/low) | `priceLadder` | system_prices, mid |
| Single-series time line | `sparkline` (sized large via opts) | indo, itsdo, freq, ndf, windfor |
| Horizontal bars (category rank) | `barsH` | agpt, agws (by PSR type), bmunits_reference |
| Calendar grid | `heatmap` | rare — only if dataset has clear day-of-week or hour-of-day pattern |
| Proportional split | `donut` | rare — for "what fraction is X" displays |

Wrap in the standard chart panel from system_prices (`<div class="chart">` with eyebrow, h2, chip row, snapshot-note). Use a fixed seed (between 1 and 99 — pick a different one per dataset for visual variety; document the seed in the data-opts).

### Schema table

Copy from vault's "Silver layer > Silver schema" table verbatim into the `<table class="schema-table">` structure. Per row:

- `<td class="col-name">{field_name} <span class="pk-badge">PK</span></td>` (add PK badge if the field is in the dedup key)
- `<td class="col-type">{python_type}</td>` — preserve square brackets exactly: `datetime[UTC]`, `Optional[str]`, etc.
- `<td style="text-align:center;" class="nullable">—</td>` for Nullable=No, `<td ... class="nullable">null</td>` for Nullable=Yes
- `<td class="col-note">{note}</td>` — use inline `<code class="mono">` for any identifier in the note text

Below the table, the partition-info card (3-column flex):
- PARQUET PATH (from vault's "Silver layer > Path pattern", stripped to `data/silver/elexon/<slug>/year=YYYY/month=MM/`)
- PARTITION BY (`settlement_date (year + month)` for most Elexon datasets; check vault if unsure)
- DEDUP KEY (from vault's "Dedup key:" line)

### Sample data

Build a `<table class="data-table">` with 6–10 illustrative rows. Source priority:

1. **Vault's "Silver sample"** Python dict — if present, mirror those rows exactly (good for accuracy)
2. **Vault's "Bronze sample"** — extract the most-visible fields, transform to silver shape
3. **Synthesize realistic-looking rows** — use plausible domain values (do NOT invent unrealistic numbers; reference the vault's column constraints like `ge=-500, le=10000`)

Highlight one row with `style="outline: 1px solid #3b6b4b; outline-offset: -1px;"` (the "interesting" or "edge case" row — peak hour, P-derivation, etc.).

Below the table, a `.tiny` caption: 1 sentence explaining what the rows show + 1 sentence calling out the highlighted row.

### Third section (conditional)

Pick based on dataset characteristics:

- **Fuel/PSR-type/bidding-zone codelist datasets**: pill grid (like fuelhh's "Fuel types"). Use `.fuel-grid` / `.fuel-pill` CSS already in the embedded `<style>`. Each pill: colored swatch + code + brief explainer.
- **Settlement-run-affected datasets** (most settlement endpoints): run-types grid (like system_prices's "Settlement runs"). Use `.run-grid` / `.run-pill` CSS already in the embedded `<style>`. 7 pills: II / SF / R1 / R2 / R3 / RF / DF.
- **Notification/regulatory feeds** (pn, remit, soso, nonbm): skip the third section entirely. Remove its sidebar anchor too. Keep sidebar at 7 anchors (drop the third-section one).
- **Reference data** (bmunits_reference): use the pill grid pattern for BM-unit categories (Generator / Supplier / Interconnector / etc.).

If unsure: skip it (better to omit than to fabricate).

### API & ingestion

Two cards side-by-side (existing pattern):

1. **ENDPOINT** card: full URL with `<br/>` line breaks for readability. Then **AUTH** with auth note from vault's API endpoint table (paraphrase, link `elexonportal.co.uk` for the registration URL).
2. **BRONZE PATH** card: from vault's "Bronze layer > Path pattern" (e.g., `data/bronze/elexon/<slug>/<year>/<month>/<day>/raw_<uuid>.json`). Then **TRANSFORMER** with the transformer class from vault's Silver layer section.

Below: tab group with 3 tabs (`Example URL`, `DuckDB · SQL`, `Python · parquet`). Use `data-tab-group="<slug>"` (replace per dataset). Inside each tab, a `<pre class="code dark">` block with realistic content:

- **Example URL**: actual API URL with example date/params
- **DuckDB · SQL**: 4–8 line SELECT using `read_parquet('data/silver/elexon/<slug>/**/*.parquet')` with a useful WHERE clause and ORDER BY
- **Python · parquet**: 4–10 line polars snippet that does something dataset-appropriate (e.g., pivot fuel-mix wide; mean price per day; max-min spread)

### Caveats

3–6 numbered caveats. Source priority:

1. **Vault's "Known issues and gotchas"** section — port each bullet into a caveat item
2. **Vault's "Implementation delta"** section — non-cosmetic deltas become caveats
3. **Domain knowledge** — settlement-period range (DST), sign conventions, etc.

Per caveat:
```html
<div class="caveat-item">
  <div class="caveat-num">0N</div>
  <div>
    <div style="font-weight: 500; margin-bottom: 6px;">{title}</div>
    <p class="small" style="margin: 0;">{prose with inline <code>}</p>
  </div>
</div>
```

The LAST caveat has `style="border-bottom: 1px solid var(--rule); padding-bottom: 16px;"` on the outer div.

### Related datasets

4 cards in a 2×2 grid. Pick semantically related datasets from the 33 Elexon list:

- Same group (e.g., other generation datasets if the current is generation)
- Direct companions (e.g., `netbsad` ↔ `system_prices` ↔ `disbsad`)
- Different-granularity siblings (e.g., `fuelhh` ↔ `fuelinst` for 30min vs 5min)

Each card uses the existing pattern from system_prices.html. Slugs, chips (freq), 1-sentence editorial blurb, vendor·group·freq tagline at bottom. The `href` is `<related-slug>.html` (same directory).

## Structural checks (run after writing each page, before commit)

The executor runs these checks on `authored-pages/elexon/<slug>.html` BEFORE committing. ANY failure → log to PORT-LOG.md and skip the commit (move to next dataset).

```bash
SLUG="<slug>"
FILE="authored-pages/elexon/${SLUG}.html"

# 1. Viewport must be device-width
grep -q '<meta name="viewport" content="width=device-width' "$FILE" || echo "FAIL: viewport"

# 2. Title contains slug
grep -q "<title>${SLUG} · Elexon BMRS · Gridflow</title>" "$FILE" || echo "FAIL: title"

# 3. Body data attributes present
grep -q 'data-page="dataset"' "$FILE" || echo "FAIL: data-page"
grep -q 'data-root="../../"' "$FILE" || echo "FAIL: data-root"
grep -q "data-screen-label=\"Dataset · ${SLUG}\"" "$FILE" || echo "FAIL: data-screen-label"

# 4. Theme and JS asset links
grep -q 'href="../../assets/theme.css"' "$FILE" || echo "FAIL: theme.css"
grep -q 'src="../../assets/charts.js"' "$FILE" || echo "FAIL: charts.js"
grep -q 'src="../../assets/site.js"' "$FILE" || echo "FAIL: site.js"

# 5. All sidebar anchors resolve
for anchor in $(grep -oP 'sidebar a\[href="\K#[a-z-]+' "$FILE" | sort -u 2>/dev/null || grep -oE 'href="#[a-z-]+"' "$FILE" | sort -u); do
  id=$(echo "$anchor" | sed 's/href="//; s/"//; s/#//')
  grep -q "id=\"${id}\"" "$FILE" || echo "FAIL: anchor #${id} has no matching section id"
done

# 6. Required sections present
for section_id in overview live-chart schema sample api caveats related; do
  grep -q "id=\"${section_id}\"" "$FILE" || echo "FAIL: missing section id=${section_id}"
done

# 7. Schema table has at least 3 rows (PK + non-PK rows)
schema_rows=$(grep -c 'class="col-name"' "$FILE")
[ "$schema_rows" -ge 3 ] || echo "FAIL: schema rows < 3 ($schema_rows)"

# 8. Caveats has at least 1 item
caveat_count=$(grep -c 'class="caveat-item"' "$FILE")
[ "$caveat_count" -ge 1 ] || echo "FAIL: no caveats"

# 9. Related has at least 1 card
related_count=$(grep -c 'class="row-link card flush"' "$FILE")
[ "$related_count" -ge 1 ] || echo "FAIL: no related datasets"

# 10. Vault-accuracy spot check (silver path consistency)
grep -q "silver.${SLUG}" "$FILE" || echo "FAIL: missing silver.${SLUG} in metadata card"

# 11. No template Jinja2 syntax leaked
! grep -qE '\{\{|\{%' "$FILE" || echo "FAIL: Jinja2 syntax leaked into authored HTML"

# 12. last_verified from vault present
LAST_VERIFIED=$(grep -E '^last_verified:' "vault/elexon/${SLUG}.md" | awk '{print $2}')
grep -q "${LAST_VERIFIED}" "$FILE" || echo "FAIL: last_verified ${LAST_VERIFIED} missing"
```

The executor wraps these into a function and runs after each port. If ANY check fails, the executor:
1. Appends the failure to `.planning/phases/08B-claude-design-hero-rewrite/PORT-LOG.md` with `slug`, `failed checks`, and `timestamp`
2. Does NOT commit
3. Continues to the next dataset

After all 31 are attempted, the SUMMARY (Task 33) tallies pass/fail counts and lists failing datasets for human triage.
