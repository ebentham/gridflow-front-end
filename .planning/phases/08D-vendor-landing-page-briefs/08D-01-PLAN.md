---
plan_id: 08D-01
phase: 08D
title: Vendor landing-page content briefs for 5 non-Elexon vendors (entsoe, entsog, gie, neso, openmeteo) + build-script override extension for vendor hubs
status: ready_to_execute
autonomous: true
executor_model: opus
wave: 1
estimated_duration_hours: 4-6
expected_commits: 8-10
requirements:
  - BUG-01
  - BUG-02
  - BUG-03
depends_on: []
recipe: 08D-LANDING-RECIPE.md
context: 08D-CONTEXT.md
references:
  - site/hifi/data-sources/elexon.html
  - templates/vendor-hub.html.j2
  - site/hifi/data/elexon.json
  - src/gridflow_front_end/build.py
  - content-briefs/elexon/system_prices.md
  - .planning/phases/08C-elexon-content-briefs/08C-BRIEF-RECIPE.md
  - quant-vault:/30-vendors/entsoe|entsog|gie|neso|open-meteo/datasets/
  - gridflow:/src/gridflow/connectors/entsoe|entsog|gie|neso|openmeteo/
  - gridflow:/src/gridflow/schemas/entsoe.py|entsog.py|gie.py|neso.py|weather.py
  - gridflow:/src/gridflow/silver/entsoe|entsog|gie|neso|openmeteo/
files_modified:
  - content-briefs/entsoe/_landing.md (new)
  - content-briefs/entsog/_landing.md (new)
  - content-briefs/gie/_landing.md (new)
  - content-briefs/neso/_landing.md (new)
  - content-briefs/openmeteo/_landing.md (new)
  - src/gridflow_front_end/build.py (build_vendor: hub-authored override block)
  - .planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md (new — failure log)
  - .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md (new — closure doc)
  - .planning/ROADMAP.md (Phase 8D progress row)
---

# Phase 8D / Plan 08D-01 — Vendor landing-page briefs (5 hubs) + build override

## Goal

After this plan executes:

1. `content-briefs/<vendor>/_landing.md` exists for each of `entsoe`, `entsog`, `gie`, `neso`, `openmeteo` — one markdown brief per vendor hub, triangulated against quant-vault + gridflow + live vendor docs, ready for the user to paste into Claude Design alongside the Elexon hub visual reference (`site/hifi/data-sources/elexon.html`).
2. `src/gridflow_front_end/build.py::build_vendor` checks for an authored vendor-hub HTML at `authored-pages/<vendor>/_landing.html` before rendering the templated hub, mirroring the per-dataset override already shipped in Phase 8B.
3. `.planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` documents per-vendor status, source-coverage stats, and aggregate discrepancy findings.
4. `.planning/ROADMAP.md` progress table reflects Phase 8D completion.

## Execution model

**Foreground sequential, single Claude Code session, opus-4.7** (per Q-A resolved in CONTEXT + advisor guidance). 5 briefs × deep research is the inverse shape of Phase 8C (33 briefs × shallow-per-brief); foreground sequential keeps quality tight without the variance of overnight background runs. If any single vendor brief exceeds context budget mid-stream, the executor may escalate that vendor to a background opus subagent (and note that escalation in the SUMMARY) — but the default is foreground.

The plan runs as **9 sequential tasks** across **3 waves**:

- **Wave 1** — Task 01 (preflight + dependency check), Task 02 (build-script override patch).
- **Wave 2** — Tasks 03–07: one brief per vendor (parallel-eligible if the executor is comfortable; sequential default for quality). Wave 2 depends on Wave 1 only because Task 01 verifies cross-repo accessibility.
- **Wave 3** — Tasks 08 (SUMMARY + ROADMAP update), 09 (final structural-checks rerun + close-out commit).

## Hard rules (carry from handover; restated here for the executor)

- Do NOT push the branch (~80 commits ahead of `main`; user pushes).
- Do NOT touch `authored-pages/elexon/fuelhh.html` or `authored-pages/elexon/system_prices.html` (sacred visual references).
- Do NOT modify `.planning/archive/08B-ai-ports/`, `CLAUDE.md`, `.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, or `.planning/research/*.md`.
- Do NOT use `--no-verify` on commits.
- Conventional commits only (`docs:`, `feat:`, `fix:`, `chore:`, `refactor:`, `test:`).
- No SaaS framing, no fake-live indicators, no emojis in files.
- Do NOT fabricate data — if a source is absent, declare it absent in frontmatter (Phase 8C discipline).
- Do NOT silently resolve discrepancies — every cross-source mismatch goes in `discrepancies_found` (Phase 8C discipline).

---

## Task 01 — Pre-flight + dependency check

<wave>1</wave>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\handovers\2026-05-20-phase-8d-landing-pages.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-CONTEXT.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 50-200 for vendor configs; lines 717-780 for build_vendor)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\templates\vendor-hub.html.j2 (full)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\site\hifi\data\elexon.json
</read_first>

<action>
1. Verify git branch: `git branch --show-current` must return `docs/v2-milestone-start`. If not, STOP.
2. Verify the working tree status: `git status --short` should show only the expected untracked files documented in handover (e.g. `.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, `.planning/research/*.md`, `.planning/STATE.md` if modified). No unexpected modified files. If unexpected M-flagged files appear, STOP and surface to BRIEF-LOG.md.
3. Confirm cross-repo paths are accessible:
   - `ls /c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/` must list at least: `entsoe`, `entsog`, `gie`, `neso`, `open-meteo` (note the hyphen on the last one).
   - `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/` must list at least: `entsoe`, `entsog`, `gie`, `neso`, `openmeteo`.
4. Capture the vault dataset counts (record in BRIEF-LOG.md or scratch). Expected: entsoe=49, entsog=33, gie=8, neso=34, open-meteo=6. Command per vendor: `ls /c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/<vault_dir>/datasets/*.md | wc -l`.
5. Confirm the Elexon hub visual reference renders cleanly by regenerating it:
   ```bash
   PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()"
   ```
   Then check that `site/hifi/data-sources/elexon.html` exists and contains the H1 string `Elexon <span class="italic">BMRS.</span>` (the visual model). If the build fails, STOP and log to BRIEF-LOG.md.
6. Create the per-vendor content-briefs subdirectories if they do not exist already:
   - `mkdir -p content-briefs/{entsoe,entsog,gie,neso,openmeteo}` (most already exist from the 2026-05-20 sample-brief work, but be idempotent).
7. Create empty failure log: `touch .planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` (idempotent).
</action>

<acceptance_criteria>
- `git branch --show-current` outputs exactly `docs/v2-milestone-start`.
- `ls /c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/{entsoe,entsog,gie,neso,open-meteo}/datasets/*.md | wc -l` returns `49 33 8 34 6` (or sum=130 across all five vendor directories).
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/{entsoe,entsog,gie,neso,openmeteo}/endpoints.py` returns 5 file paths with no errors.
- `site/hifi/data-sources/elexon.html` exists after build, and `grep -c 'class="italic">BMRS\.' site/hifi/data-sources/elexon.html` returns ≥1.
- All five `content-briefs/<vendor>/` directories exist (verifiable with `ls -d content-briefs/{entsoe,entsog,gie,neso,openmeteo}`).
- `.planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` exists (verifiable with `test -f`).
</acceptance_criteria>

If any check fails: write the failure to `.planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` and STOP. Otherwise proceed to Task 02.

---

## Task 02 — Build-script override extension for vendor hubs

<wave>1</wave>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (full file, with focus on lines 717-780 — the `build_vendor` function, especially the existing per-dataset override at lines 765-768)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-CONTEXT.md (specifically the "Build-script override extension" sub-section under `<specifics>`)
</read_first>

<action>
Edit `src/gridflow_front_end/build.py` to add a hub-level authored-override check before `render_vendor_hub`. Concretely, in the `build_vendor` function (around lines 775-778), replace this block:

```python
    hub_html = render_vendor_hub(env, manifest, vendor_id, vendor_label, vendor_cfg["vendor_meta"])
    hub_path = out_root / "data-sources" / f"{vendor_id}.html"
    hub_path.write_text(hub_html, encoding="utf-8")
    print(f"  wrote: data-sources/{vendor_id}.html")
```

…with this block:

```python
    hub_path = out_root / "data-sources" / f"{vendor_id}.html"
    authored_hub = AUTHORED_DIR / vendor_id / "_landing.html"
    if authored_hub.exists():
        shutil.copy(authored_hub, hub_path)
        print(f"  wrote: data-sources/{vendor_id}.html (authored hub)")
    else:
        hub_html = render_vendor_hub(env, manifest, vendor_id, vendor_label, vendor_cfg["vendor_meta"])
        hub_path.write_text(hub_html, encoding="utf-8")
        print(f"  wrote: data-sources/{vendor_id}.html")
```

This mirrors the per-dataset override pattern at lines 765-768 (`authored = AUTHORED_DIR / vendor_id / f"{doc.slug}.html"`). The convention: authored vendor hubs live at `authored-pages/<vendor>/_landing.html` to match the brief naming convention (`content-briefs/<vendor>/_landing.md`).

After the edit, verify with:

```bash
PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()" 2>&1 | tee /tmp/build.log
```

The build must:
- Exit code 0.
- Print `wrote: data-sources/elexon.html` (because no `authored-pages/elexon/_landing.html` exists yet, the templated path runs — same as before).
- Print `wrote: data-sources/elexon/fuelhh.html (authored)` (because `authored-pages/elexon/fuelhh.html` exists — confirms the per-dataset override still fires).

Commit the change:

```
fix(08D): extend build-script override path to support authored vendor hubs

build_vendor now checks AUTHORED_DIR/<vendor>/_landing.html before rendering the
templated vendor hub, mirroring the per-dataset override pattern from Phase 8B.
The Elexon hub continues to use the templated path (no authored _landing.html
exists for elexon); the four non-Elexon COMING_SOON vendors are unaffected (they
go through build_coming_soon_stubs, not build_vendor). The hub override fires
only once the Phase 8D briefs are Claude-Designed and dropped at the expected path.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `grep -c 'AUTHORED_DIR / vendor_id / "_landing.html"' src/gridflow_front_end/build.py` returns ≥1.
- `grep -c '(authored hub)' src/gridflow_front_end/build.py` returns ≥1.
- `PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()"` exits 0.
- After build, `site/hifi/data-sources/elexon.html` exists and contains the templated H1 string `Elexon <span class="italic">BMRS.</span>` (templated path still fires because no `authored-pages/elexon/_landing.html` exists).
- `git log -1 --format=%s` contains `fix(08D): extend build-script override path to support authored vendor hubs`.
- `git diff HEAD~1 src/gridflow_front_end/build.py | grep -c '^+'` shows a net positive line count consistent with a ~5 LoC addition (typically 5-7 added lines, 2-3 removed).
</acceptance_criteria>

If the build fails after the edit: revert with `git checkout HEAD -- src/gridflow_front_end/build.py`, log to BRIEF-LOG.md, and STOP. Otherwise proceed to Wave 2.

---

## Tasks 03-07 — Five vendor landing-page briefs

Tasks 03 through 07 follow a common shape (one task per vendor). Sequential by default; parallel-eligible if the executor is comfortable holding 5 vendor contexts in working memory. Each task produces exactly one brief file and exactly one commit.

**Shared per-task pattern** (the recipe-driven steps from `08D-LANDING-RECIPE.md`):

For each vendor:

1. **Read all sources** (per recipe "Sources" section):
   - All vault dataset files: `ls /c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/<vault_dir>/datasets/*.md` → read each.
   - Gridflow connector: `~/Python/gridflow/src/gridflow/connectors/<vendor>/endpoints.py` and `client.py` (plus any extras like `parsers.py` for ENTSO-E or `carbon_intensity.py` for NESO).
   - Gridflow schemas: `~/Python/gridflow/src/gridflow/schemas/<schema_file>` (note: openmeteo uses `weather.py`; gie uses `gie.py`).
   - Gridflow silver: `ls ~/Python/gridflow/src/gridflow/silver/<vendor>/` for the count + key class names.
   - `src/gridflow_front_end/build.py` REAL_VENDORS / COMING_SOON_VENDORS — read the existing vendor block.
   - WebFetch the vendor docs URL (per recipe table).
2. **Compose the brief** per `08D-LANDING-RECIPE.md` section order:
   - Frontmatter (YAML with all required keys)
   - `# Editorial layer` (H1 italic-accent pattern + lede + CTAs metadata)
   - `# Vendor metadata` (6-cell table)
   - `# Stats strip` (4-cell table)
   - `# About section` (2-3 paragraphs)
   - `# Groups` (one `## Group: <Name>` subsection per group, with blurb + dataset table)
   - `# Source map` (gridflow file → purpose table)
   - `# Cross-vendor links` (3-5 cards)
   - `# Caveats` (3-5 numbered)
   - `# Per-vendor cheatsheet` (optional; if applicable)
   - `# Source-of-truth note` (footer paragraph)
3. **Surface discrepancies** in frontmatter `discrepancies_found:` — vault vs gridflow vs vendor-docs cross-references. Never silently resolved. (Phase 8C convention.)
4. **Run the 10 structural checks** from `08D-LANDING-RECIPE.md`.
5. **If all pass**: `git add content-briefs/<vendor>/_landing.md` and commit with the per-brief template (see recipe "Commit pattern" section).
6. **If any fail**: append to `.planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` with vendor, failed checks, timestamp, 1-line reason. Do NOT commit. Continue to next vendor.

---

### Task 03 — content-briefs/entsoe/_landing.md (49 datasets, 6 groups)

<wave>2</wave>
<depends_on>[Task 01, Task 02]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md (full file)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md (per-dataset brief format reference — for editorial voice and frontmatter conventions, not section structure)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\entsoe\actual_generation.md (existing sample per-dataset brief for ENTSO-E — for voice continuity within the vendor)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 88-115 — the existing REAL_VENDORS["entsoe"]["vendor_meta"] block — lift verbatim where possible)
- All vault files: `/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/*.md` (49 files)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/endpoints.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/parsers.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py`
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/` (for transformer count + class names)
- Vendor docs: WebFetch `https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html` (or the equivalent EN-TSO-E API guide).
</read_first>

<action>
Produce `content-briefs/entsoe/_landing.md` following the recipe. Vendor-specific anchors:

- **H1**: `ENTSO-E <span class="italic">Transparency.</span>` (already in `REAL_VENDORS["entsoe"]["vendor_meta"]`; lift verbatim).
- **lede**: lift verbatim from `REAL_VENDORS["entsoe"]["vendor_meta"]["lede"]` (already polished, editorial-voice).
- **Vendor metadata 6 cells**: lift `base_url=web-api.tp.entsoe.eu`, `auth=API key · query param securityToken`, `rate_limit=~1 req/s · polite default`, `format=XML · GL_MarketDocument`, `earliest=2014-12-05`, `timezone=UTC · PT15M / PT30M / PT60M` from `REAL_VENDORS["entsoe"]["vendor_meta"]`. Verify each against `connectors/entsoe/endpoints.py` and `client.py`; if anything has drifted, surface in `discrepancies_found`.
- **Stats strip slots 3-4**: lift `B25 · PSR types · production codes` and `EU · Bidding zones` (already in REAL_VENDORS). Slot 1 = `49 Datasets`; Slot 2 = `6 Categories` (or however many groups you settle on).
- **Groups (6 default per CONTEXT D-05; verify from vault)**: `Generation` / `Load` / `Transmission & Cross-Border` / `Outages & Unavailabilities` / `Capacity & Auctions` / `Prices & Balancing`. Refine the group names + assignments from the actual vault dataset clustering. The brief's 49 listed dataset rows must equal the vault file count.
- **Cheatsheet**: PSR codes (B01-B25) from `parsers.py` if encoded; time resolutions; bidding zones list (read vault for the canonical list, often ~50 zones).
- **Discrepancies to look for**: Phase 7 ENTSO-E entitlement note (33 datasets with HTTP 401 deferred per Phase 7 D-06 — surface this in a caveat and in `discrepancies_found` if the entitlement-blocked datasets are still listed in the vault but not currently reachable via the connector). Vendor-doc fetchability of the official ENTSO-E web-api guide.

Run the 10 structural checks per the recipe. On success, commit:

```
docs(08D): landing-page brief for entsoe · 49 vault datasets, 6 groups, triangulated

<one-paragraph summary including>:
- 49 datasets clustered into 6 groups
- K Pydantic classes / J silver transformers cited
- P discrepancies surfaced (notably: Phase 7 entitlement-deferred 33 datasets if surfaced)
- Vendor docs <fetched | unfetchable: reason>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f content-briefs/entsoe/_landing.md` succeeds.
- `python -c "import yaml; yaml.safe_load(open('content-briefs/entsoe/_landing.md').read().split('---')[1])"` exits 0.
- `grep -c '^slug: _landing' content-briefs/entsoe/_landing.md` returns 1.
- `grep -c '^vendor: entsoe' content-briefs/entsoe/_landing.md` returns 1.
- `grep -c '^brief_type: landing' content-briefs/entsoe/_landing.md` returns 1.
- `grep -c '^vault_dataset_count: 49' content-briefs/entsoe/_landing.md` returns 1.
- `grep -c '^## Group:' content-briefs/entsoe/_landing.md` returns ≥2 (and matches the stats-strip Slot 2 value).
- Per-dataset row count in Groups equals 49: `awk '/^## Group:/{flag=1; next} /^# /{flag=0} flag' content-briefs/entsoe/_landing.md | grep -cE '^\| `[a-z_]+` \|'` returns 49.
- All 6 vendor-metadata cells present: `for cell in "BASE URL" "AUTH" "RATE LIMIT" "FORMAT" "EARLIEST" "TIMEZONE"; do grep -qF "| $cell |" content-briefs/entsoe/_landing.md || echo MISS:$cell; done` produces no MISS output.
- All 8 required `# <Section>` headings present (Editorial layer, Vendor metadata, Stats strip, About section, Groups, Source map, Cross-vendor links, Caveats).
- ≥3 caveats numbered (`grep -cE '^## 0[1-9]' content-briefs/entsoe/_landing.md` returns ≥3).
- Commit committed: `git log -1 --format=%s content-briefs/entsoe/_landing.md` contains `docs(08D): landing-page brief for entsoe`.
</acceptance_criteria>

---

### Task 04 — content-briefs/entsog/_landing.md (33 datasets, 4-5 groups)

<wave>2</wave>
<depends_on>[Task 01, Task 02]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\entsog\aggregated_physical_flows.md (existing sample per-dataset brief)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 118-132 — the COMING_SOON_VENDORS["entsog"] stub block; expand into a full vendor_meta in the brief)
- All vault files: `/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/*.md` (33 files)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsog/endpoints.py` (note: `DEFAULT_POINT_DIRECTIONS` lists key UK/IE interconnection points around L24-34; `KEY_POINT_KEYS` around L37; these feed the cheatsheet)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsog/client.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsog.py`
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsog/`
- Vendor docs: WebFetch `https://transparency.entsog.eu/api/v1` (ENTSO-G OpenAPI swagger / definitions page).
</read_first>

<action>
Produce `content-briefs/entsog/_landing.md` following the recipe. Vendor-specific anchors:

- **H1**: `ENTSO-G <span class="italic">Transparency.</span>` (parallel construction to ENTSO-E).
- **lede**: draft fresh — ~2-4 sentences, ≤60 words, editorial voice. Cover what ENTSO-G is (European gas-network transparency platform), what they publish (operational data at interconnection points: physical flows, nominations, capacities), and why it matters for trading (gas-burn vs power generation; cross-border gas flow dynamics).
- **Vendor metadata 6 cells**: derive from `connectors/entsog/endpoints.py` and `client.py`. Likely: `base_url=transparency.entsog.eu/api/v1` (verify), `auth=Public · OperatorKey query param (or no key)` (verify against `client.py`), `rate_limit=`-derive from the client, `format=JSON · ISO-8601 · timeZone:UCT` (note the `ENTSOG_TIMEZONE = "UCT"` in `endpoints.py` is a known vendor quirk — UCT not UTC), `earliest=`-derive from vault, `timezone=UCT · day periods`.
- **Stats strip slots 3-4**: candidates — `9 · UK/IE interconnection points` (from `DEFAULT_POINT_DIRECTIONS` in endpoints.py) and `33 · Indicator endpoints` (or `5 · CMP procedures` if CMP is a natural top-line stat).
- **Groups (per CONTEXT D-05; refine from vault)**: `Physical Flow` / `Nominations & Renominations` / `Capacities` / `CMP (Congestion Management)` / `Auctions & Allocations`. Some vault datasets may not fit cleanly — surface in `discrepancies_found` as `gridflow_taxonomy_gap` if needed. **Q-B resolved: one brief, multiple internal groups** — do NOT split into separate transmission/CMP hubs.
- **Cheatsheet**: operator-point keys table (lift from `DEFAULT_POINT_DIRECTIONS` in `endpoints.py`).
- **Discrepancies to look for**: `UCT` vs `UTC` editorial choice (the vendor uses `UCT`; gridflow normalises but worth surfacing); CMP-procedure dataset coverage; entry-vs-exit point disambiguation if vault and connector disagree on key shape.

Run the 10 structural checks. Commit:

```
docs(08D): landing-page brief for entsog · 33 vault datasets, N groups, triangulated

<summary>:
- 33 datasets clustered into N groups (incl. Physical Flow, Nominations, Capacities, CMP)
- K Pydantic classes / J silver transformers cited
- P discrepancies surfaced
- Vendor docs <fetched | unfetchable: reason>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f content-briefs/entsog/_landing.md` succeeds.
- `python -c "import yaml; yaml.safe_load(open('content-briefs/entsog/_landing.md').read().split('---')[1])"` exits 0.
- `grep -c '^slug: _landing' content-briefs/entsog/_landing.md` returns 1.
- `grep -c '^vendor: entsog' content-briefs/entsog/_landing.md` returns 1.
- `grep -c '^vault_dataset_count: 33' content-briefs/entsog/_landing.md` returns 1.
- `grep -c '^## Group:' content-briefs/entsog/_landing.md` returns ≥2 (CONTEXT D-05 suggests 4-5).
- Per-dataset row count in Groups equals 33: `awk '/^## Group:/{flag=1; next} /^# /{flag=0} flag' content-briefs/entsog/_landing.md | grep -cE '^\| `[a-z_]+` \|'` returns 33.
- All 6 vendor-metadata cells present.
- All 8 required `# <Section>` headings present.
- ≥3 caveats numbered.
- Commit committed: `git log -1 --format=%s content-briefs/entsog/_landing.md` contains `docs(08D): landing-page brief for entsog`.
</acceptance_criteria>

---

### Task 05 — content-briefs/gie/_landing.md (8 datasets, 2 groups: AGSI + ALSI)

<wave>2</wave>
<depends_on>[Task 01, Task 02]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\gie\storage.md (existing sample per-dataset brief)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 133-160 — the TWO COMING_SOON_VENDORS entries: `gie_agsi` and `gie_alsi`; the brief unifies them under a single `gie` vendor_id for the hub)
- All vault files: `/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/gie/datasets/*.md` (8 files)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/gie/endpoints.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/gie/client.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/gie.py`
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/gie/`
- Vendor docs: WebFetch `https://agsi.gie.eu/about` AND `https://alsi.gie.eu/about` (both — one brief covers both surfaces per Q-C resolved in CONTEXT and the recipe).
</read_first>

<action>
Produce `content-briefs/gie/_landing.md` following the recipe. Vendor-specific anchors:

- **H1**: choose `GIE <span class="italic">Storage.</span>` (covers both AGSI + ALSI under the storage/LNG inventory framing — verify against vault's own framing first). Alternative: `Gas Infrastructure Europe <span class="italic">AGSI + ALSI.</span>` if vault prefers the spelled-out form.
- **lede**: draft fresh — Gas Infrastructure Europe (GIE) operates AGSI (gas storage transparency) and ALSI (LNG terminal transparency). One brief covers both. Editorial voice; 2-4 sentences.
- **Vendor metadata 6 cells**: derive from `connectors/gie/endpoints.py`. AGSI and ALSI share base host `agsi.gie.eu` / `alsi.gie.eu`; record both if the connector hits both. Auth: likely `Public · no key required` post-2020 (verify against `client.py`).
- **Stats strip slots 3-4**: candidates — `~140 · Storage facilities (AGSI)` and `~25 · LNG terminals (ALSI)` (verify counts from vault).
- **Groups (2 — per Q-C resolved here)**: `Storage (AGSI)` covers the underground-gas-storage datasets (5-6 of the 8); `LNG (ALSI)` covers the LNG-terminal datasets (2-3 of the 8). Verify the exact 5+3 or 6+2 split from the vault file shapes. Per-dataset row count must equal 8.
- **Discrepancies to look for**: build.py has TWO COMING_SOON entries (`gie_agsi` and `gie_alsi`) but the Phase 8D brief unifies them under one `gie` hub — surface this in `discrepancies_found` as `build_config_drift: gie_agsi + gie_alsi → unified gie hub in 8D brief; reconciliation in Phase 10`. AGSI vs ALSI date-coverage differences.

Run the 10 structural checks. Commit:

```
docs(08D): landing-page brief for gie · 8 vault datasets (5 AGSI + 3 ALSI), 2 groups, triangulated

<summary>:
- 8 datasets clustered into 2 groups: Storage (AGSI) and LNG (ALSI)
- One brief covers both sub-products per Q-C resolved in 08D-CONTEXT
- K Pydantic classes / J silver transformers cited
- P discrepancies surfaced (notably: gie_agsi/gie_alsi unification in 8D vs build.py split)
- Vendor docs <fetched | unfetchable: reason>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f content-briefs/gie/_landing.md` succeeds.
- `python -c "import yaml; yaml.safe_load(open('content-briefs/gie/_landing.md').read().split('---')[1])"` exits 0.
- `grep -c '^slug: _landing' content-briefs/gie/_landing.md` returns 1.
- `grep -c '^vendor: gie' content-briefs/gie/_landing.md` returns 1.
- `grep -c '^vault_dataset_count: 8' content-briefs/gie/_landing.md` returns 1.
- `grep -c '^## Group:' content-briefs/gie/_landing.md` returns exactly 2 (AGSI + ALSI per Q-C).
- Per-dataset row count in Groups equals 8.
- All 6 vendor-metadata cells present.
- All 8 required `# <Section>` headings present.
- ≥3 caveats numbered (one should cover the AGSI/ALSI unification + build.py drift).
- Commit committed: `git log -1 --format=%s content-briefs/gie/_landing.md` contains `docs(08D): landing-page brief for gie`.
</acceptance_criteria>

---

### Task 06 — content-briefs/neso/_landing.md (34 datasets, 3-4 groups)

<wave>2</wave>
<depends_on>[Task 01, Task 02]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\neso\carbon_intensity.md (existing sample per-dataset brief — high quality reference)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 175-188 — the COMING_SOON_VENDORS["neso"] stub block. Note: stub `vendor_label` is "NESO Carbon Intensity" but the vault has 34 datasets covering more than just carbon intensity — surface this in `discrepancies_found`.)
- All vault files: `/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/neso/datasets/*.md` (34 files)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/neso/endpoints.py` (the ENDPOINTS registry — note the carbon-intensity vs intensity-current distinction)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/neso/carbon_intensity.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/neso.py` (`_TimestampedNesoBase` is the shared parent class; ~5-7 subclasses)
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/neso/`
- Vendor docs: WebFetch `https://carbon-intensity.github.io/api-definitions/` (known to render server-side; reliable source).
</read_first>

<action>
Produce `content-briefs/neso/_landing.md` following the recipe. Vendor-specific anchors:

- **H1**: `NESO <span class="italic">Carbon.</span>` (matches the "NESO Carbon Intensity" branding in REAL_VENDORS COMING_SOON stub; the API surface IS principally the carbon-intensity feed) — or refine to `National Energy System Operator <span class="italic">Carbon.</span>` if vault prefers spelling out. Verify from vault framing.
- **lede**: draft fresh — National Energy System Operator (NESO; rebranded from National Grid ESO 2024). Publishes the GB grid carbon-intensity time-series (forecast + actuals) and a wider statistics surface covering generation mix, regional carbon, and reference data. The canonical input for carbon-aware load shifting and MEF modelling.
- **Vendor metadata 6 cells**: derive from `connectors/neso/endpoints.py`. Likely: `base_url=api.carbonintensity.org.uk` (per the sample brief), `auth=Public · no key required`, `rate_limit=`-derive (NESO carbon API is generous; "polite default" probably 1-2 req/s), `format=JSON · ISO-8601 · UTC`, `earliest=`-derive from vault (carbon-intensity API earliest is ~2018), `timezone=UTC · 30-min settlement`.
- **Stats strip slots 3-4**: candidates — `48 / day · GB settlement periods` and `gCO2/kWh · Reporting unit` (matches the sample carbon_intensity brief slots).
- **Groups (default 3-4)**: `Carbon Intensity` (the per-SP forecast/actual feed + factor-by-fuel breakdown) / `Regional Carbon Intensity` (DNO/GSP-level) / `Generation Mix` (per-fuel share % time-series) / `Statistics & Reference` (max/min, percentiles, geo-reference). 34 datasets across 4 groups → ~8-9 per group. **Verify from vault** — NESO's surface may cluster differently (e.g. the connector hits the Carbon Intensity API and also broader NESO data portal endpoints; surface in `discrepancies_found` if the vault dataset shape doesn't match the 4-group taxonomy).
- **Cheatsheet**: intensity-index labels (`very low` / `low` / `moderate` / `high` / `very high`) lifted from the carbon-intensity sample brief.
- **Discrepancies to look for**: vendor_label "NESO Carbon Intensity" in build.py is narrower than the actual 34-dataset surface (`build_config_label_drift: vendor_label scope underspecifies actual surface`); ESO-vs-NESO rebrand (June 2024) — naming conventions may differ across vault/code/docs; carbon_intensity vs intensity_current endpoint disambiguation (documented in the sample carbon_intensity brief Caveats #02).

Run the 10 structural checks. Commit:

```
docs(08D): landing-page brief for neso · 34 vault datasets, N groups, triangulated

<summary>:
- 34 datasets clustered into N groups (carbon-intensity, regional, generation mix, statistics)
- K Pydantic classes / J silver transformers cited (note: most subclass _TimestampedNesoBase in schemas/neso.py)
- P discrepancies surfaced (notably: vendor_label scope drift in build.py; ESO→NESO rebrand)
- Vendor docs fetched at carbon-intensity.github.io

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f content-briefs/neso/_landing.md` succeeds.
- `python -c "import yaml; yaml.safe_load(open('content-briefs/neso/_landing.md').read().split('---')[1])"` exits 0.
- `grep -c '^slug: _landing' content-briefs/neso/_landing.md` returns 1.
- `grep -c '^vendor: neso' content-briefs/neso/_landing.md` returns 1.
- `grep -c '^vault_dataset_count: 34' content-briefs/neso/_landing.md` returns 1.
- `grep -c '^## Group:' content-briefs/neso/_landing.md` returns ≥2.
- Per-dataset row count in Groups equals 34.
- All 6 vendor-metadata cells present.
- All 8 required `# <Section>` headings present.
- ≥3 caveats numbered.
- Commit committed: `git log -1 --format=%s content-briefs/neso/_landing.md` contains `docs(08D): landing-page brief for neso`.
</acceptance_criteria>

---

### Task 07 — content-briefs/openmeteo/_landing.md (6 datasets, 2-3 groups)

<wave>2</wave>
<depends_on>[Task 01, Task 02]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md (especially the "Naming asymmetry" note about open-meteo/openmeteo)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\elexon\system_prices.md
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\content-briefs\openmeteo\forecast_solar.md (existing sample per-dataset brief)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\src\gridflow_front_end\build.py (lines 162-174 — COMING_SOON_VENDORS["openmeteo"] stub)
- All vault files: `/c/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/open-meteo/datasets/*.md` (6 files — note the HYPHEN in `open-meteo`)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/openmeteo/endpoints.py` (note: NO hyphen here)
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/openmeteo/client.py`
- `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/weather.py` (schema entry-point is `weather.py`, NOT `openmeteo.py` — pin this)
- `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/openmeteo/`
- Vendor docs: WebFetch `https://open-meteo.com/en/docs` (most accessible API documentation in the set; renders cleanly).
</read_first>

<action>
Produce `content-briefs/openmeteo/_landing.md` following the recipe. Vendor-specific anchors:

- **H1**: `Open-Meteo <span class="italic">Weather.</span>` (or `Forecast.` if vault prefers; default to `Weather.` for the broadest umbrella).
- **lede**: draft fresh — Open-Meteo is the open weather-API provider (sponsored by Zürich-based Open-Meteo). Publishes temperature, wind, solar irradiance, and precipitation as both forecast and historical (ERA5 reanalysis from 1940). The canonical weather input for wind/solar nowcasting against UK demand and generation.
- **Vendor metadata 6 cells**: derive from `connectors/openmeteo/endpoints.py` and `client.py`. Likely: `base_url=api.open-meteo.com/v1` (verify; the hyphen IS in the host name), `auth=Public · no key required` (free tier; verify rate-limit handling in `client.py`), `rate_limit=~10 req/s · free-tier polite default` (verify — Open-Meteo's free tier is unusually generous), `format=JSON · ISO-8601 · UTC`, `earliest=1940-01-01` (ERA5 reanalysis depth — verify), `timezone=UTC · hourly / 15-min`.
- **Stats strip slots 3-4**: candidates — `1940– · ERA5 reanalysis depth` and `Global · Coverage` (or `~80 / Variables` — number of weather variables exposed by the unified API).
- **Groups (2 — default; verify)**: `Forecast` (the 3 forecast_* vault datasets: forecast_solar, forecast_wind, forecast_demand) and `Historical` (the 3 historical_* vault datasets: historical_solar, historical_wind, historical_demand). Six datasets total; per-dataset row count = 6.
- **Cheatsheet**: variable groups — Temperature (air, soil, dewpoint), Wind (speed, direction, gusts at 10m / 100m / 250m), Solar (GHI / DNI / DHI, plus shortwave radiation), Precipitation, Pressure. Lift the exact variable list from `connectors/openmeteo/endpoints.py` or the API docs.
- **Discrepancies to look for**: vault directory uses hyphen (`open-meteo/`); gridflow connector module uses no-hyphen (`openmeteo/`); brief slug uses no-hyphen (`content-briefs/openmeteo/`); the `BASE URL` cell records the hyphen-form because the live API host is `api.open-meteo.com`. **Pin this in a caveat** under hub-scope naming/path conventions. Schema file is `schemas/weather.py` not `schemas/openmeteo.py` — surface in `discrepancies_found` as `gridflow_schema_naming: schema/weather.py is the entry-point for openmeteo (not schemas/openmeteo.py)`.

Run the 10 structural checks. Commit:

```
docs(08D): landing-page brief for openmeteo · 6 vault datasets, 2 groups (Forecast + Historical), triangulated

<summary>:
- 6 datasets clustered into 2 groups: Forecast and Historical
- K Pydantic classes / J silver transformers cited (schema entry-point: schemas/weather.py)
- P discrepancies surfaced (notably: open-meteo vs openmeteo naming asymmetry; schemas/weather.py vs schemas/openmeteo.py)
- Vendor docs fetched at open-meteo.com/en/docs

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f content-briefs/openmeteo/_landing.md` succeeds.
- `python -c "import yaml; yaml.safe_load(open('content-briefs/openmeteo/_landing.md').read().split('---')[1])"` exits 0.
- `grep -c '^slug: _landing' content-briefs/openmeteo/_landing.md` returns 1.
- `grep -c '^vendor: openmeteo' content-briefs/openmeteo/_landing.md` returns 1.
- `grep -c '^vault_dataset_count: 6' content-briefs/openmeteo/_landing.md` returns 1.
- `grep -c '^## Group:' content-briefs/openmeteo/_landing.md` returns ≥2.
- Per-dataset row count in Groups equals 6.
- All 6 vendor-metadata cells present.
- All 8 required `# <Section>` headings present.
- ≥3 caveats numbered (one should cover the hyphen/no-hyphen naming asymmetry).
- Commit committed: `git log -1 --format=%s content-briefs/openmeteo/_landing.md` contains `docs(08D): landing-page brief for openmeteo`.
</acceptance_criteria>

---

## Task 08 — Phase 8D SUMMARY + ROADMAP update

<wave>3</wave>
<depends_on>[Task 03, Task 04, Task 05, Task 06, Task 07]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08C-elexon-content-briefs\08C-01-SUMMARY.md (model for the per-vendor table + aggregate sections)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\ROADMAP.md (Phase 8D row at line ~125 in the progress table)
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\BRIEF-LOG.md (any failures recorded during Wave 2)
- All five committed briefs: `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/_landing.md`
</read_first>

<action>
Produce `.planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` following the Phase 8C model. Required sections:

1. **Outcome**: `Success` if 5/5 briefs committed; `Partial` if 3-4 of 5; `Failed` if &lt;3.
2. **Executed**: date + execution model (foreground sequential, opus-4.7).
3. **Commits**: count + branch + total brief size (sum of `wc -l` and `du -sh` across the 5 brief files + the build.py edit commit).
4. **Per-vendor table** (one row per vendor):

   | vendor | status | brief size (KB) | vault dataset count | groups | discrepancy count | commit hash |
   |---|---|---|---|---|---|---|
   | entsoe | ... | ... | 49 | ... | ... | ... |
   | entsog | ... | ... | 33 | ... | ... | ... |
   | gie | ... | ... | 8 | 2 | ... | ... |
   | neso | ... | ... | 34 | ... | ... | ... |
   | openmeteo | ... | ... | 6 | 2 | ... | ... |

5. **Per-source coverage stats**:
   - Vault: cited by all N briefs (X%).
   - Gridflow Pydantic schemas: cited by N briefs (note that openmeteo uses `schemas/weather.py`).
   - Gridflow connectors: cited by all N briefs.
   - Gridflow silver: cited by all N briefs.
   - Live vendor docs: fetched cleanly for X of 5; unfetchable for Y of 5 (note JS-rendered or 404 reasons).

6. **Aggregate discrepancy report**: roll up all `discrepancies_found:` items across the 5 briefs. Dominant types (per Phase 8C convention):
   - Build-config drift (e.g. gie_agsi/gie_alsi split, neso vendor_label scope)
   - Naming asymmetries (e.g. open-meteo/openmeteo, schemas/weather.py)
   - Vault-vs-vendor-docs drift
   - Schema-source-of-truth gaps for COMING_SOON vendors
   - Phase 7 entitlement-deferred datasets (entsoe specifically)

7. **Required deliverables** — checklist matching the handover acceptance criteria:
   - [ ] 5 briefs committed
   - [ ] Build-script override extension committed
   - [ ] Each brief passes 10 structural checks
   - [ ] `08D-01-SUMMARY.md` written
   - [ ] `08D-LANDING-RECIPE.md` written (this happened in plan-phase; this is a verification, not a new write)
   - [ ] ROADMAP.md Phase 8D row updated
   - [ ] BRIEF-LOG.md contains no entries (or, if any, surfaced here)

8. **Out of scope** (defer to later phases):
   - Per-dataset briefs for the 5 vendors (Phase 9 + Phase 10)
   - Claude-Designing the 5 vendor hub HTML pages (user-side work post-8D)
   - Updating `site/hifi/data/<vendor>.json` manifests with full dataset lists (Phase 9 + Phase 10 work)
   - Promoting `gie_agsi` / `gie_alsi` / `openmeteo` / `neso` / `entsog` from COMING_SOON to REAL_VENDORS in build.py (Phase 10)
   - Reconciling the build.py `gie_agsi` + `gie_alsi` split against the unified `gie` hub brief (Phase 10)

9. **Unexpected issues**: any observations worth recording (e.g. NESO surface broader than the "carbon-intensity" branding suggests; open-meteo schema entry-point under `weather.py`; ENTSO-E entitlement still a long shadow).

Then update `.planning/ROADMAP.md` Phase 8D row to:
- Change checkbox from `[ ]` to `[x]`.
- Update the progress table row: `| 8D. Vendor landing-page briefs (5 hubs) | 1/1 | Complete YYYY-MM-DD | — |` (or `5/5` if you count per brief).

Commit (combined):

```
docs(08D): close Phase 8D — 5 vendor landing-page briefs ready for Claude Design

5 of 5 vendor hub briefs committed under content-briefs/<vendor>/_landing.md
(entsoe, entsog, gie, neso, openmeteo). Build-script override extended in
build.py so authored-pages/<vendor>/_landing.html overrides the templated hub
when present (mirrors Phase 8B's per-dataset override).

Per-vendor: entsoe (49 datasets, N groups), entsog (33, N groups),
gie (8, 2 groups — AGSI + ALSI unified per Q-C), neso (34, N groups),
openmeteo (6, 2 groups — Forecast + Historical).

P total discrepancies surfaced across the 5 briefs; full breakdown in
08D-01-SUMMARY.md. Phase 9 (ENTSO-E per-dataset briefs) and Phase 10
(four-vendor per-dataset briefs) can now proceed against the established
hub-layer template.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```
</action>

<acceptance_criteria>
- `test -f .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` succeeds.
- `grep -c '^## Per-vendor table' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c 'entsoe' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c 'entsog' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c 'gie' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c 'neso' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c 'openmeteo' .planning/phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md` ≥1.
- `grep -c '\[x\] \*\*Phase 8D' .planning/ROADMAP.md` returns 1 (Phase 8D checkbox flipped to done).
- `grep -E '^\| 8D\. Vendor landing-page briefs' .planning/ROADMAP.md` shows progress (e.g. `1/1` or `5/5`) and a non-`Ready to plan` status.
- `git log -1 --format=%s` contains `docs(08D): close Phase 8D`.
</acceptance_criteria>

If the SUMMARY/ROADMAP commit fails pre-commit hooks: fix the issue (do NOT use `--no-verify`) and re-stage. Continue to Task 09.

---

## Task 09 — Final structural-checks rerun (verification)

<wave>3</wave>
<depends_on>[Task 08]</depends_on>
<autonomous>true</autonomous>

<read_first>
- C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\.planning\phases\08D-vendor-landing-page-briefs\08D-LANDING-RECIPE.md (Structural checks section)
- All 5 brief files at `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/_landing.md`
- `.planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md`
</read_first>

<action>
Run the 10 structural checks from `08D-LANDING-RECIPE.md` against all 5 briefs in a final sweep, ignoring any "expected pass" cache state. Confirm:

1. All five `content-briefs/<vendor>/_landing.md` files exist.
2. Each parses as valid YAML frontmatter.
3. Each has all required frontmatter keys (`slug`, `vendor`, `vendor_label`, `brief_type`, `vault_dataset_count`, `last_verified`, `sources_consulted`, `discrepancies_found`, `ready_for_claude_design`, `checked_at`).
4. Each `sources_consulted` has ≥3 entries.
5. Each contains all 8 required section headings (Editorial layer, Vendor metadata, Stats strip, About section, Groups, Source map, Cross-vendor links, Caveats).
6. Each has ≥2 groups defined.
7. Each per-dataset row count equals the corresponding vault dataset count (49, 33, 8, 34, 6).
8. Each has all 6 vendor-metadata cells (BASE URL, AUTH, RATE LIMIT, FORMAT, EARLIEST, TIMEZONE).
9. Each has all 4 stats-strip slots.
10. Each has ≥3 caveats.

Also verify:
- `BRIEF-LOG.md` is either empty or every entry has a recorded resolution.
- The build script still runs cleanly: `PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()"` exits 0.
- The Elexon hub still uses the templated path (no `authored-pages/elexon/_landing.html` exists, so the templated hub remains the canonical output for the visual reference page).

If any check fails: log the failure to `BRIEF-LOG.md` with timestamp + reason; do NOT re-commit; surface to the next agent or user via the SUMMARY's "Unexpected issues" section. Do NOT silently re-pass.

No new commit at this step (the SUMMARY/ROADMAP commit in Task 08 was the close-out commit). This task is verification only.
</action>

<acceptance_criteria>
- All 10 structural checks pass for all 5 brief files (verifiable by running the recipe's check block per-vendor and observing zero `FAIL:` lines).
- `wc -l .planning/phases/08D-vendor-landing-page-briefs/BRIEF-LOG.md` returns 0 (or matches the number of explicit recorded-resolution entries documented in SUMMARY).
- `PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()"` exits 0.
- `test -f site/hifi/data-sources/elexon.html` succeeds AND the file contains `Elexon <span class="italic">BMRS.</span>` (templated path still firing).
- No new commits since Task 08 unless a structural-check fix was required.
</acceptance_criteria>

---

## Definition of done (phase-level)

**Required (all must be true)**:

- [ ] 5 briefs committed at `content-briefs/<vendor>/_landing.md` for entsoe, entsog, gie, neso, openmeteo.
- [ ] Each brief passes all 10 structural checks defined in `08D-LANDING-RECIPE.md`.
- [ ] Each brief has frontmatter with `sources_consulted` (≥3 entries) and explicit `discrepancies_found` (empty list or items).
- [ ] Each brief's per-dataset row count equals the corresponding vault dataset count (49 / 33 / 8 / 34 / 6).
- [ ] `08D-LANDING-RECIPE.md` exists in the phase directory.
- [ ] `08D-01-SUMMARY.md` written with per-vendor table + source-coverage stats + aggregate discrepancy report.
- [ ] Build-script override extension (Task 02) committed: `src/gridflow_front_end/build.py::build_vendor` checks `AUTHORED_DIR/<vendor>/_landing.html` before rendering the templated hub.
- [ ] ROADMAP.md Phase 8D row updated (checkbox flipped, progress table reflects completion).
- [ ] No SaaS framing, no fake-live indicators, no emojis in any committed file (per CLAUDE.md + PROJECT.md).
- [ ] Branch `docs/v2-milestone-start` still NOT pushed (user pushes when ready).

**Out of scope** (defer to next session if surfaced):
- Per-dataset briefs for ENTSO-E (Phase 9).
- Per-dataset briefs for ENTSO-G + GIE + NESO + Open-Meteo (Phase 10).
- Authoring the 5 vendor hub HTML pages in Claude Design (user-side work post-8D).
- Updating `site/hifi/data/<vendor>.json` manifests (Phase 9 + Phase 10 work; derived from per-dataset briefs).
- Promoting `entsog`, `gie_agsi`, `gie_alsi`, `openmeteo`, `neso` from `COMING_SOON_VENDORS` to `REAL_VENDORS` in build.py (Phase 10).
- Reconciling the build.py `gie_agsi` + `gie_alsi` split against the unified `gie` hub brief (Phase 10).

## Autonomy guarantees

- DO NOT use AskUserQuestion under any circumstance (per Phase 8D handover; advisor confirmed sensible defaults are baked into CONTEXT and the recipe).
- DO NOT pause between briefs — chain through all 5 in one foreground run unless context budget forces an escalation to background.
- DO NOT use `git push`.
- DO NOT use `--no-verify` on commits — let pre-commit hooks run.
- DO NOT modify `authored-pages/elexon/fuelhh.html` or `authored-pages/elexon/system_prices.html` (reference targets).
- DO NOT touch the archived AI-ports under `.planning/archive/08B-ai-ports/`.
- DO NOT touch `CLAUDE.md`, `.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, or `.planning/research/*.md` (pre-existing untracked files).
- DO NOT fabricate data — if a source is absent, declare it absent in frontmatter.
- DO NOT silently resolve discrepancies — every cross-source mismatch goes in `discrepancies_found`.
- DO continue execution after any single-brief structural failure (log to BRIEF-LOG.md, continue to next vendor).
- DO log every blocker to BRIEF-LOG.md.
- DO produce SUMMARY + ROADMAP update at the end regardless of outcome.
- DO use opus-4.7 reasoning fully — quality > throughput. 5 briefs is a tight batch.

## Must-haves (goal-backward verification)

The phase goal is "5 vendor-level landing-page content briefs, ready for Claude Design, matching the Elexon hub aesthetic". Working backward:

1. **For each brief to be ready for Claude Design**, it must contain everything Claude Design needs without further research:
   - vendor identity (H1 italic-accent pattern + lede)
   - 6-cell access metadata (BASE URL / AUTH / RATE LIMIT / FORMAT / EARLIEST / TIMEZONE)
   - 4-cell stats strip (vendor-specific Slot 3 + 4)
   - About-section context (vendor framing)
   - Group definitions with blurbs (drive the manifest.groups[] structure)
   - Per-dataset listing rows (drive the manifest.groups[].datasets[] structure; row count == vault count)
   - Source map + cross-vendor links (for editorial polish)
   - Caveats (for accuracy nuance — entitlement, naming, drift)

2. **For each brief to match the Elexon hub aesthetic**, it must use the same editorial register as the Elexon hub and Phase 8C dataset briefs (no SaaS framing, no live indicators, brand-aligned tone, mono-chip technical identifiers).

3. **For the build script to serve authored hubs**, the override path must check `authored-pages/<vendor>/_landing.html` before rendering the templated hub. This is Task 02; ~5 LoC.

4. **For Phase 9 + Phase 10 to proceed**, the hub layer must be decoupled from the per-dataset layer. Phase 8D delivering 5 vendor hubs gives Phase 9 + Phase 10 a stable hub surface to build per-dataset pages against.

If any of these is missing at phase end, the phase is not done.

## Truths (cross-cutting)

- Brief slug naming: `_landing` for vendor hubs (underscore-prefix); per-dataset briefs continue to use the dataset slug (Phase 8C convention). The `.md` brief and the eventual `.html` authored output share the `_landing` stem.
- Vendor key (`entsoe`, `entsog`, `gie`, `neso`, `openmeteo`) is the canonical key everywhere except the Open-Meteo vault directory (`open-meteo/` — hyphen). The build override convention uses the vendor key, NOT the vault-dir key.
- All five vendors are currently in `COMING_SOON_VENDORS` except `entsoe` (which is in `REAL_VENDORS`). For ENTSO-E the brief lifts the existing `vendor_meta` block; for the other four the brief defines what the eventual `vendor_meta` block will become when Phase 10 promotes them.
- Discrepancies are surfaced in frontmatter; never silently resolved (Phase 8C discipline, restated here for emphasis).
- Conventional commits, branch invariant, never push without explicit user direction.
