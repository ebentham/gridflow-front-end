# Per-brief recipe: vault + gridflow + vendor docs → content-briefs/&lt;vendor&gt;/_landing.md

**Purpose**: Per-vendor-hub runbook the Phase 8D executor follows for each of the 5 non-Elexon vendors. The output is a self-contained markdown brief that Claude Design can render against the Elexon hub visual reference (`site/hifi/data-sources/elexon.html`, produced by `templates/vendor-hub.html.j2`) without needing additional research.

This is the vendor-hub layer counterpart to `08C-BRIEF-RECIPE.md` (which targets per-dataset briefs).

## Scope: 5 vendor hubs (one brief each)

| Vendor key | Vault directory | Gridflow connector dir | Gridflow schema file | Vault dataset count | Output |
|---|---|---|---|---|---|
| `entsoe` | `~/quant-vault/30-vendors/entsoe/datasets/*.md` | `~/Python/gridflow/src/gridflow/connectors/entsoe/` | `schemas/entsoe.py` | **49** | `content-briefs/entsoe/_landing.md` |
| `entsog` | `~/quant-vault/30-vendors/entsog/datasets/*.md` | `~/Python/gridflow/src/gridflow/connectors/entsog/` | `schemas/entsog.py` | **33** | `content-briefs/entsog/_landing.md` |
| `gie`    | `~/quant-vault/30-vendors/gie/datasets/*.md`    | `~/Python/gridflow/src/gridflow/connectors/gie/`    | `schemas/gie.py`    | **8**  | `content-briefs/gie/_landing.md`    |
| `neso`   | `~/quant-vault/30-vendors/neso/datasets/*.md`   | `~/Python/gridflow/src/gridflow/connectors/neso/`   | `schemas/neso.py`   | **34** | `content-briefs/neso/_landing.md`   |
| `openmeteo` | `~/quant-vault/30-vendors/open-meteo/datasets/*.md` | `~/Python/gridflow/src/gridflow/connectors/openmeteo/` | `schemas/weather.py` | **6** | `content-briefs/openmeteo/_landing.md` |

**Naming asymmetry — pin this in your read_first**: Open-Meteo's vault directory uses a hyphen (`open-meteo/`) while every other on-disk identifier uses concatenated form (`openmeteo` in gridflow connector module, in `content-briefs/`, in build.py `vendor_id`, and in the brief slug). For Open-Meteo, glob with `open-meteo` for vault sources but emit `openmeteo` everywhere else. NESO's schema entry-point is `schemas/neso.py`; Open-Meteo's schema entry-point is `schemas/weather.py` (not `schemas/openmeteo.py`).

**GIE — single brief, two internal groups (AGSI + ALSI).** Per CONTEXT D-05 and Q-C resolved-here: GIE has 8 vault datasets covering AGSI (gas storage) and ALSI (LNG). The brief presents them as two top-level groups inside one hub. The `gie_agsi` / `gie_alsi` split in `build.py::COMING_SOON_VENDORS` is a build-config artefact (separate stub cards on the catalog) and is NOT a hub-design directive. The Phase 8D hub for `gie` covers both sub-products; the existing two COMING_SOON cards will be reconciled in Phase 10.

**ENTSO-G — single brief, multiple internal groups.** Per CONTEXT D-05 and Q-B resolved-here: ENTSO-G has 33 vault datasets. The brief presents 4-6 internal groups (Physical Flow / Nominations / Capacities / CMP / Auctions per D-05, plus any natural taxonomy the vault reveals). The brief is **one file** — splitting into transmission-vs-capacity-management hubs is a Phase 10 concern, not Phase 8D.

## Sources (mandatory triangulation)

For each vendor, the executor MUST consult **all three** source families:

1. **Upstream quant-vault** (always present): `~/quant-vault/30-vendors/<vault_vendor_dir>/datasets/*.md` — read every dataset file. From this derive: per-dataset listing rows (slug, title, freq, lag, rows), per-group taxonomy via dataset clustering, last_verified dates, vendor-API notes. The vault is the **single source of truth for per-dataset surface**; if a dataset exists in vault but not in gridflow, the brief still lists it but annotates `gridflow_connector_status: not_implemented`.

2. **Gridflow main repo** (always present for vendors that are shipping): start at
   - `~/Python/gridflow/src/gridflow/connectors/<vendor>/` — `endpoints.py` for the canonical base URL, auth header pattern, rate-limit config; `client.py` for retry/auth behaviour. This is the source of truth for `BASE URL`, `AUTH`, `RATE LIMIT`, `FORMAT` hero cells.
   - `~/Python/gridflow/src/gridflow/schemas/<schema_file>` — count Pydantic classes that ship for this vendor; record the count for the stats strip.
   - `~/Python/gridflow/src/gridflow/silver/<vendor>/` — count silver transformers (one per dataset, usually).
   - This repo's `src/gridflow_front_end/build.py REAL_VENDORS` (ENTSO-E already populated) and `COMING_SOON_VENDORS` (the other 4 vendors; treat as drafts to override). The brief defines what each vendor's eventual `REAL_VENDORS["<vendor>"]["vendor_meta"]` block will look like in Phase 10 when the vendor is promoted out of COMING_SOON.

3. **Live vendor docs** (best-effort): Use `WebFetch` against the vendor's public API documentation URL:
   - `entsoe`: `https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html`
   - `entsog`: `https://transparency.entsog.eu/api/v1` (Swagger / OpenAPI definition page)
   - `gie`: `https://agsi.gie.eu/about` and `https://alsi.gie.eu/about` (both — single brief covers both)
   - `neso`: `https://carbon-intensity.github.io/api-definitions/` (already known to render server-side)
   - `openmeteo`: `https://open-meteo.com/en/docs` and the vendor's `/docs` JSON schema (most accessible API in the set)

   If a fetch fails (404, JavaScript-only landing shell, network error), annotate in frontmatter `sources_consulted` as `vendor_docs_unfetchable: <reason>` (Phase 8C convention; documented for all 33 Elexon briefs). The vault is treated as the canonical fallback for vendor-API details.

If any source is missing (e.g., no Pydantic schemas for a still-COMING_SOON vendor), note in frontmatter `sources_consulted` with an `(absent — reason: ...)` annotation. **Do not fabricate.**

## Output

Single markdown file at `content-briefs/<vendor>/_landing.md`. Sibling to per-dataset briefs (Phase 8C pattern). Underscore prefix sorts the landing brief to the top of an `ls`-style directory listing.

## Brief structure (required sections in this order)

### Frontmatter (YAML)

```yaml
---
slug: _landing
vendor: <vendor>                # canonical vendor key: entsoe | entsog | gie | neso | openmeteo
vendor_label: <Display name>    # e.g. "ENTSO-E Transparency" — matches REAL_VENDORS[...].label pattern
brief_type: landing             # distinguishes from per-dataset briefs (which omit this key)
vault_dataset_count: N          # the count read directly from `ls vault/<dir>/datasets/*.md | wc -l`
last_verified: <YYYY-MM-DD>     # most recent last_verified found across the vault dataset files
sources_consulted:
  - quant-vault/30-vendors/<vault_dir>/datasets/  (N files: <comma-separated list or "see Datasets section">)
  - gridflow/src/gridflow/connectors/<vendor>/endpoints.py
  - gridflow/src/gridflow/connectors/<vendor>/client.py
  - gridflow/src/gridflow/schemas/<schema_file>  (M Pydantic classes; or "(absent — reason: silver-only)")
  - gridflow/src/gridflow/silver/<vendor>/  (K transformers)
  - gridflow-front-end/src/gridflow_front_end/build.py REAL_VENDORS/COMING_SOON_VENDORS  (existing vendor_meta or stub)
  - <live vendor docs URL>  (fetched YYYY-MM-DD HH:MM:SS UTC) | vendor_docs_unfetchable: <reason>
discrepancies_found:
  - source_a: "<file:line or "vault Known-Issues #N">"
    source_a_says: "..."
    source_b: "<file:line>"
    source_b_says: "..."
    orchestrator_recommendation: "trust gridflow | cosmetic | needs-info"
  # (or empty list [] only if every source aligns — must explicitly declare)
ready_for_claude_design: true
checked_at: <ISO-8601 UTC>
---
```

### # Editorial layer

- **H1 pattern** (italic-accent guidance): `{heading_prefix} <span class="italic">{heading_italic}.</span>` — e.g. for ENTSO-E: `ENTSO-E <span class="italic">Transparency.</span>`. The italic accent is a single word + trailing dot. Compose by reading the vendor's "what they call themselves" (ENTSO-E calls it "Transparency Platform"; ENTSO-G calls it "Transparency Platform"; GIE calls them "AGSI" / "ALSI"; NESO publishes the "Carbon Intensity API"; Open-Meteo brands as just "Open-Meteo"). Examples (provisional — refine from vault):
  - entsoe: `ENTSO-E` + `Transparency.` (already in REAL_VENDORS — lift verbatim)
  - entsog: `ENTSO-G` + `Transparency.`
  - gie: `GIE` + `Storage.` (covers AGSI + ALSI under the "Storage / LNG" umbrella) — verify against vault's framing
  - neso: `NESO` + `Carbon.` (matches "NESO Carbon Intensity" vendor_label in REAL_VENDORS; the API surface IS the carbon-intensity feed)
  - openmeteo: `Open-Meteo` + `Weather.` (or `Forecast.` — pick whichever aligns with the dominant vault framing)

- **Lede paragraph** (2–4 sentences, ≤60 words): Editorial voice matching Phase 8C briefs and the Elexon hub. Lead with WHO this vendor is (one sentence). Then WHAT they publish (one sentence). Optionally one more sentence on WHY it matters for energy trading. Pattern from REAL_VENDORS["elexon"].vendor_meta.lede: "The British electricity Balancing Mechanism Reporting Service. Settlement prices, generation by fuel, demand outturn, balancing actions, and BM unit metadata — documented as a static reference site over the gridflow ETL pipeline." Lift the existing `lede` from REAL_VENDORS["entsoe"]["vendor_meta"]["lede"] verbatim for ENTSO-E (already polished). The other four need fresh ledes.

- **CTAs** (two button labels): `Browse {N} dataset{s} ↓` (anchors to `#datasets`) and `Vendor docs ↗` (external link to `vendor_docs_url`). The template renders these automatically — the brief just records the dataset count `N` and the canonical docs URL.

### # Vendor metadata (6 cells, 2×3 grid)

A markdown table with two columns: `Cell label` | `Value`. Cells in this order (matches the template's grid):

| Cell label | Value |
|---|---|
| BASE URL | from `connectors/<vendor>/endpoints.py` — the canonical base host without scheme (e.g. `web-api.tp.entsoe.eu`). Word-break friendly. |
| AUTH | from `connectors/<vendor>/client.py` — describe the auth scheme in editorial form. Examples: `Public · no key required` (Elexon, NESO carbon API, Open-Meteo); `API key · query param securityToken` (ENTSO-E); `Public · OperatorKey query param` (ENTSO-G); `Public · no key required` (GIE). |
| RATE LIMIT | from `connectors/<vendor>/client.py` or `endpoints.py` rate-limit config. Use editorial form `N req/s · project default`. |
| FORMAT | from observation of bronze samples in vault. Examples: `JSON · ISO-8601 · UTC` (Elexon, NESO); `XML · GL_MarketDocument` (ENTSO-E); `JSON · ISO-8601 · timeZone:UCT` (ENTSO-G); `JSON · ISO-8601 · UTC` (GIE); `JSON · ISO-8601 · UTC` (Open-Meteo). |
| EARLIEST | earliest data-coverage date across all vault datasets for the vendor. Read each vault file's "Earliest data" / `earliest` line; pick the minimum. Format: `YYYY-MM-DD` or `YYYY` (year-only acceptable for legacy / pre-API archive depth). |
| TIMEZONE | the vendor's timezone convention. Examples: `UTC · SP 1–50` (Elexon); `UTC · PT15M / PT30M / PT60M` (ENTSO-E); `UCT · day periods` (ENTSO-G); `UTC · daily snapshots` (GIE); `UTC · 30-min settlement` (NESO); `UTC · hourly / 15-min` (Open-Meteo). |

All values must be ≤80 chars per the template's small-font cell layout. For long values (long base URLs), note in the brief that Claude Design should render with `<br/>` line breaks and `font-size:10px`.

### # Stats strip (4 cells)

A markdown table: `slot` | `value` | `label`. Slot semantics mirror the template's `stat-n` / `stat-l` pattern. The template renders Slots 1 and 2 from the manifest automatically (`{N} Datasets` and `{N} Categories`); Slots 3 and 4 come from `vendor_meta.stat_three_*` and `vendor_meta.stat_four_*`. The brief defines all four explicitly so Claude Design can validate. Pattern:

| slot | value | label | source |
|---|---|---|---|
| 1 | `{vault_dataset_count}` | `Datasets` | derived from vault file count |
| 2 | `{group_count}` | `Categor{ies}` | derived from your group definitions below |
| 3 | (CUSTOM per vendor — vendor-specific notable number) | (CUSTOM label) | something noteworthy from the vault or gridflow |
| 4 | (CUSTOM per vendor) | (CUSTOM label) | something noteworthy |

Examples to anchor Slot 3 and Slot 4:
- ENTSO-E already has `B25 · PSR types · production codes` and `EU · Bidding zones` in REAL_VENDORS — lift verbatim.
- ENTSO-G: `9 · Operator points` and `33 · Indicator endpoints` (or similar) — verify against vault.
- GIE: `~140 · Storage facilities` and `~70 · LNG terminals` (or AGSI+ALSI dataset counts) — verify against vault.
- NESO: `48 / day · GB settlement periods` and `gCO2/kWh · Reporting unit` — derive from carbon_intensity surface.
- Open-Meteo: `1940– · ERA5 reanalysis depth` and `Global · Coverage` — derive from vault.

### # About section (2-3 paragraphs)

Three short paragraphs of vendor context. Same editorial voice as Phase 8C lede paragraphs. Composition:

1. **Paragraph 1 — Who they are**: 2-3 sentences. Open with a `<code>` chip of the vendor key + plain-English definition. Compose from the vendor's official "about" framing (read via WebFetch if possible, or from vault). For ENTSO-E: "the pan-European TSO transparency platform"; for ENTSO-G: "the European gas-network transparency platform"; for GIE: "the European storage and LNG operators association"; for NESO: "the National Energy System Operator (carbon-intensity branch)"; for Open-Meteo: "the open weather-API provider, sponsored by Zürich-based Open-Meteo".

2. **Paragraph 2 — What they publish**: 2-3 sentences. Cover the data domains: generation/load/transmission/prices for ENTSO-E; physical-flow/capacities for ENTSO-G; storage/LNG for GIE; carbon-intensity series + 48h forecast for NESO; temperature/wind/solar/precipitation for Open-Meteo. Cite typical dataset counts.

3. **Paragraph 3 — Why it matters for energy trading**: 2-3 sentences. The "so what" — what trader workflows or backtests does this vendor feed? Cross-reference Elexon where natural (Open-Meteo + Elexon = wind/solar nowcast; ENTSO-G + Elexon = gas-burn vs CCGT generation; NESO carbon + Elexon fuelhh = MEF modelling).

Use inline `<code>` for technical identifiers (dataset slugs, endpoint paths, schema class names).

### # Groups (per vendor's natural taxonomy)

This is the heart of the brief — it drives the `#datasets` section of the rendered hub. Each group is a Jinja2 `manifest.groups[]` entry.

For each group:

**## Group: &lt;Group Name&gt;** (matches `group.name` in manifest)

- **Blurb** (1-2 sentences, ≤120 chars) — matches `group.blurb` in manifest. Same editorial register as Elexon's "Actual and forecast output from GB power stations."
- **Dataset table** — one row per vault dataset in this group:

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `<vault_slug>` | `<short title — same shape as elexon.json title field>` | `<freq>` | `<lag>` | `<rows>` |

Field meanings (mirrors `site/hifi/data/elexon.json` shape):
- `id` — vault filename stem (e.g. `actual_generation`, `aggregated_physical_flows`, `storage`, `carbon_intensity`, `forecast_solar`). For Open-Meteo, use concat-form not hyphen-form (the brief slug column matches the eventual `<vendor>.json` manifest, which lives in `site/hifi/data/<vendor>.json` and is shared across the front-end).
- `title` — short editorial title, ≤45 chars. Style: noun phrase ending in a single trailing modifier (e.g. "Generation by fuel type · half-hourly"). Lift from vault's H1 or first sentence and tighten.
- `freq` — publication frequency. Editorial form (e.g. `30 min`, `hourly`, `daily`, `monthly`, `~5 min`, `as published`).
- `lag` — publication lag. Editorial form (e.g. `~5 min`, `1 day`, `0`, `—`, `hours → weeks`).
- `rows` — typical volume. Editorial form (e.g. `1.4M / mo`, `44k / mo`, `1 snapshot`, `varies`). Estimate from vault Volume field or schema × frequency.

**Group taxonomy by vendor** (default — refine from vault):

- **entsoe** (49 datasets, 6 groups): `Generation` / `Load` / `Transmission & Cross-Border` / `Outages & Unavailabilities` / `Capacity & Auctions` / `Prices & Balancing`. The existing `entsoe.json` (if it has only 1 dataset, expand from vault) is a starting point. Verify against the vault's actual dataset shape; clusters may differ.
- **entsog** (33 datasets, 4-5 groups): `Physical Flow` / `Nominations & Renominations` / `Capacities` / `CMP (Congestion Management Procedures)` / `Auctions & Allocations`. Per CONTEXT D-05.
- **gie** (8 datasets, 2 groups): `Storage (AGSI)` / `LNG (ALSI)`. Per Q-C resolution: one brief, two groups.
- **neso** (34 datasets, 4 groups): `Carbon Intensity` / `Generation Mix` / `Regional Carbon` / `Reference & Statistics`. Refine from vault — NESO's surface may be larger or differently shaped than the 4-group default.
- **openmeteo** (6 datasets, 2-3 groups): `Forecast` / `Historical` (the natural 2-group split) OR `Wind & Solar` / `Demand` / `Reanalysis` if the variable split is more natural. Six datasets is small enough for a single group too.

**Row count invariant — verifiable**: For each vendor, `sum(len(group.datasets) for group in manifest.groups) == vault_dataset_count`. Every vault dataset appears in exactly one group. If a vault dataset cannot be assigned to a natural group, surface in `discrepancies_found` (`gridflow_taxonomy_gap: <slug>`).

### # Source map (which gridflow files define this vendor's surface)

A markdown table mapping each gridflow file to its purpose for this vendor. Pattern (lifted from Phase 8C dataset briefs' `sources_consulted` extended into hub scope):

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/<vendor>/endpoints.py` | Base URL, registered endpoints, rate-limit config | Cite line ranges for the per-endpoint registrations. |
| `connectors/<vendor>/client.py` | Auth, retries, request shape | Cite the auth scheme implementation. |
| `connectors/<vendor>/<extras>.py` (if any) | (e.g. `parsers.py` for ENTSO-E, `carbon_intensity.py` for NESO) | One line per extra module. |
| `schemas/<schema_file>` | Pydantic classes for typed silver columns | List class names if &lt; 10; cite the count if &gt; 10. Note absence if vendor has no Pydantic classes. |
| `silver/<vendor>/` | Per-dataset transformers | Cite count and list a few canonical class names. |
| `build.py REAL_VENDORS` / `COMING_SOON_VENDORS` | Vendor card / hub config | Cite line range and whether vendor is REAL or COMING_SOON. |

This section is the bridge between the editorial brief and the gridflow codebase — it lets Claude Design (and downstream readers) trace any claim back to source.

### # Cross-vendor links (3-5 cards)

A markdown list of vendor + dataset pairings that produce useful join surfaces. Pattern (one per card):

- **`<other_vendor>` · `<dataset_slug>`** — `<one-sentence "why these go together">`. Editorial citation: cross-vendor join idea.

Examples:
- For `entsog`: pair with `elexon` · `fuelhh` ("gas-burn vs CCGT generation"), `entsoe` · `actual_generation` ("EU-wide gas burn aggregation"), `gie` · `storage` ("flows into storage vs nominations").
- For `gie`: pair with `entsog` · `aggregated_physical_flows` ("inventory flows into storage vs nominations"), `elexon` · `fuelhh` ("storage withdrawal vs CCGT dispatch in GB").
- For `neso`: pair with `elexon` · `fuelhh` ("MEF modelling — per-fuel carbon intensity"), `elexon` · `system_prices` ("imbalance price vs grid carbon-intensity correlations").
- For `openmeteo`: pair with `elexon` · `fuelhh` ("wind/solar nowcast vs actual generation"), `elexon` · `windfor` ("public weather forecast vs Elexon wind forecast skill"), `neso` · `carbon_intensity` ("weather-driven carbon-intensity drivers").
- For `entsoe`: pair with `elexon` · `fuelhh` ("GB outturn vs EU-wide generation by PSR type"), `entsog` · `aggregated_physical_flows` ("power vs gas market coupling").

Pick the 3-5 most-useful pairings. Editorial voice; no salesy framing.

### # Caveats (3-5)

Numbered list (01, 02, 03...). Per caveat:
- **Title** (1 line, sentence case)
- **Body** (1-2 short paragraphs; inline `<code>` for identifiers; cross-reference internal sections)
- **Source citation**: which vault Known-Issues, which gridflow Implementation-Delta file, or "domain knowledge"

Hub-scope caveat ideas:
- Entitlement / API-key boundaries (ENTSO-E famously requires registration and gates many endpoints with HTTP 401 — see Phase 7 RECON-02 for the 33 deferred ENTSO-E surfaces).
- Vendor-side framing inconsistencies (GIE's AGSI vs ALSI separation; ENTSO-G's day-period vs hourly vs 15-minute dual conventions; Open-Meteo's free-vs-commercial API split).
- Coverage-depth limits (ENTSO-G's ~1-3 year operational data depth; Open-Meteo's ERA5 since 1940 vs short-horizon forecast).
- Cross-vendor unit mismatches (NESO publishes in `gCO2/kWh`; Elexon publishes generation in MW; joining requires explicit MWh conversion).
- Vendor-doc unfetchability if the live API docs failed to fetch (Phase 8C convention — every brief that failed vendor-doc fetch logged it).

### # Per-vendor cheatsheet (optional but recommended)

A compact at-a-glance table for Claude Design / reader use. Style mirrors Elexon's "Settlement runs" pill grid (per `system_prices.md` Dataset-specific section). Pattern:

For each vendor, one cheatsheet box. Example (for ENTSO-E):

- **PSR codes** — `B01` Biomass · `B02` Fossil brown coal · ... `B25` Other (lift from `connectors/entsoe/parsers.py` if codes are encoded; else cite vault).
- **Time resolutions** — `PT15M` 15 min · `PT30M` 30 min · `PT60M` hourly.
- **Bidding zones** — GB-now-out, EU-27 + Norway + Switzerland + UK pre-Brexit historical, ~50 zones.

For ENTSO-G: `operatorKey` patterns (UK-TSO-0001, IE-TSO-0002, etc — lift from `endpoints.py::DEFAULT_POINT_DIRECTIONS`). For GIE: facility-key conventions (UGS / LNG categories). For NESO: intensity-index labels (`very low` / `low` / `moderate` / `high` / `very high`). For Open-Meteo: variable groups (temperature, wind components, solar components).

If a cheatsheet doesn't apply, note in frontmatter `cheatsheet: omitted (reason: ...)` and drop the section.

### # Source-of-truth note

A short final paragraph (3-4 sentences) reminding the reader where editorial content originated. Pattern matching the Elexon hub's footer note: "Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.<vendor>`; values shown in charts are illustrative deterministic snapshots, not live <vendor_label> responses." The brief copies this verbatim with `<vendor>` and `<vendor_label>` substituted.

## Structural checks (10 — run after writing each brief, before commit)

The checks adapt Phase 8C's 12-check pattern to vendor-hub scope. Two Phase 8C checks (schema-row count; per-dataset structural items like sample-data 8-row table) are not applicable; their replacements (group count and per-group dataset count invariants) are below.

```bash
VENDOR="<vendor>"            # entsoe | entsog | gie | neso | openmeteo
VAULT_VENDOR_DIR="<dir>"     # entsoe | entsog | gie | neso | open-meteo  (hyphen for Open-Meteo!)
VAULT_PATH="/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/${VAULT_VENDOR_DIR}/datasets"
FILE="content-briefs/${VENDOR}/_landing.md"

# 1. File exists at expected path
[ -f "$FILE" ] || echo "FAIL: file missing at ${FILE}"

# 2. Frontmatter parses (PyYAML safe_load)
python -c "import yaml; yaml.safe_load(open('${FILE}').read().split('---')[1])" 2>&1 | grep -q Error && echo "FAIL: invalid frontmatter"

# 3. Required frontmatter keys present
for key in slug vendor vendor_label brief_type vault_dataset_count last_verified sources_consulted discrepancies_found ready_for_claude_design checked_at; do
  grep -q "^${key}:" "$FILE" || echo "FAIL: missing frontmatter key: ${key}"
done

# 4. sources_consulted has at least 3 entries (vault dir + gridflow + vendor docs)
sources_count=$(awk '/^sources_consulted:/{flag=1; next} /^[a-z_]+:/{flag=0} flag' "$FILE" | grep -c "^  -")
[ "$sources_count" -ge 3 ] || echo "FAIL: < 3 sources cited ($sources_count)"

# 5. All required sections present (in order)
for section in "# Editorial layer" "# Vendor metadata" "# Stats strip" "# About section" "# Groups" "# Source map" "# Cross-vendor links" "# Caveats"; do
  grep -qF "$section" "$FILE" || echo "FAIL: missing section: $section"
done

# 6. At least 2 groups defined
group_count=$(grep -cE '^## Group:' "$FILE")
[ "$group_count" -ge 2 ] || echo "FAIL: < 2 groups defined ($group_count)"

# 7. Per-dataset row count == vault dataset count (the core data-shape invariant)
expected=$(ls "${VAULT_PATH}"/*.md 2>/dev/null | wc -l)
# count dataset rows: lines matching | `slug` | inside any Group section
listed=$(awk '/^## Group:/{flag=1; next} /^# /{flag=0} flag' "$FILE" | grep -cE '^\| `[a-z_]+` \|')
[ "$listed" -eq "$expected" ] || echo "FAIL: dataset row count mismatch (brief=$listed, vault=$expected)"

# 8. Vendor metadata table has all 6 cells (BASE URL, AUTH, RATE LIMIT, FORMAT, EARLIEST, TIMEZONE)
for cell in "BASE URL" "AUTH" "RATE LIMIT" "FORMAT" "EARLIEST" "TIMEZONE"; do
  grep -qF "| ${cell} |" "$FILE" || echo "FAIL: missing vendor-metadata cell: ${cell}"
done

# 9. Stats strip has all 4 slots
for slot in 1 2 3 4; do
  awk '/^# Stats strip/{flag=1; next} /^# /{flag=0} flag' "$FILE" | grep -qE "^\| ${slot} \|" || echo "FAIL: missing stats-strip slot ${slot}"
done

# 10. At least 3 caveats numbered
caveat_count=$(grep -cE '^## 0[1-9]' "$FILE")
[ "$caveat_count" -ge 3 ] || echo "FAIL: < 3 caveats ($caveat_count)"
```

Two checks intentionally NOT carried over from Phase 8C:
- **Check 6 (schema rows ≥ 3)** — replaced by Check 6 (groups ≥ 2) and Check 7 (per-dataset row count == vault count). The vendor hub has no schema table.
- **Check 8 (4 related-dataset cards)** — replaced by Cross-vendor links subsection (Check 5 covers section presence; the link list shape is not invariant).

Failures → append to `.planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` with vendor + failed checks + 1-line reason. Do NOT commit. Continue to next vendor.

## Commit pattern (per successful brief)

```
docs(08D): landing-page brief for <vendor> · triangulated against vault + gridflow + vendor docs

<one-paragraph summary of what was found>:
- N vault datasets clustered into M groups
- K Pydantic classes / J silver transformers cited
- P discrepancies surfaced for downstream triage [if any]
- Vendor docs <fetched | unfetchable: reason>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
