# Pitfalls Research

**Domain:** Editorial portfolio + technical data-source documentation site, audience = energy-trading-firm recruiters
**Researched:** 2026-05-17
**Confidence:** HIGH (anchored in this codebase's `CONCERNS.md`, the explicit anti-goals in `PROJECT.md`, and the specific shape of the recruiter audience; not generic web-dev advice)

## How to read this

`CONCERNS.md` catalogues what is broken in the current commit. **This file catalogues forward-looking traps the v1 cleanup is likely to fall into.** Every pitfall maps to a specific phase of the milestone in `PROJECT.md § Active` and, where relevant, extends the corresponding `CONCERNS.md` entry rather than duplicating it.

Phase names referenced (all from `PROJECT.md § Active`):
- **Main-page polish** — home, architecture, data-sources landing
- **Elexon dataset depth** — 22 pages to fuelhh fidelity + count reconciliation
- **Cross-vendor proof** — vendor stubs + 1 ENTSO-E dataset
- **Honesty sweep** — kill live framing, label snapshots
- **Bug & a11y fallout** — viewport, license, landmarks, etc.
- **Structural / CSS debt** — extract duplicated styles, consolidate scripts
- **Cross-repo sync** — Obsidian Vault alignment

### Phase ordering implied by these pitfalls

The pitfalls below imply a partial order on the cleanup phases. Not all phases are sequential — some can interleave — but several dependencies are hard:

1. **Pitfall 0 (uncommitted refactor) → everything else.** The 26 modified files must be split into the four logical commits and pushed before any new cleanup work. Otherwise every subsequent commit entangles the new work with the in-flight typography sweep, honesty edits, and pillar-status removal. Bisect dies; review becomes "one giant commit."
2. **Structural / CSS debt → Elexon dataset depth.** The templating decision (Pitfall 6) and the manifest-or-not decision (Pitfall 4) must precede the depth pass — otherwise depth either copy-pastes 16 stubs by hand (Pitfall 6's bad endpoint) or has nowhere to render counts from (Pitfall 4 unresolved).
3. **Structural / CSS debt → Bug & a11y fallout.** The mobile-CSS pass on dataset pages (Pitfall 10 step 2) only makes sense once the duplicated inline `<style>` blocks are in `theme.css` — otherwise the media queries have to be added to 22 inline blocks.
4. **Elexon dataset depth → Honesty sweep.** Run the sweep *after* depth so the newly-completed pages get cleaned in the same pass, but *scope and grep-list before* depth so depth doesn't reintroduce `chip live` and `LAST FETCH` chrome by copy-paste.
5. **Cross-repo sync policy decision → Vault port.** Pitfall 5: pick sync direction before touching vault files; redoing a wrong direction costs more than the initial port.
6. **Main-page polish, Bug & a11y fallout** can interleave with the above; they are leaf phases with few inter-dependencies (except mobile CSS in fallout depending on Structural debt).

---

## Critical Pitfalls

### Pitfall 0: Compounding cleanup on top of the uncommitted in-flight refactor

**What goes wrong:**
The current branch has 26 modified files with no commit since the initial `351c580`. The in-flight changes are already heterogeneous: a `fg-accent → italic` typography sweep, removal of the false `pillar-status: Shipping` badges, fuelhh-specific honesty edits, plus per-page tweaks. Starting v1 cleanup work *on top of* this state means every new commit is entangled with whatever subset of the in-flight refactor happens to be staged at the moment. Three concrete failure modes:

1. **Megacommit.** The "next commit" becomes 26 files of refactor + N files of v1 work + the new viewport fix. Reviewer cannot see incremental intent; bisect cannot isolate the cause of any regression introduced.
2. **Lost durable work.** Anyone running `git reset --hard`, `git stash drop`, or switching branches without stashing loses the partial honesty edits to `fuelhh.html`. None of that work is in any reflog beyond local Git GC.
3. **Re-clobbered partial work.** The honesty sweep (Pitfall 1) re-touches `fuelhh.html`. If the existing partial edits aren't committed first, the sweep either has to merge them manually or just re-applies the same changes — best case wastes time, worst case overwrites a more thoughtful edit with a mechanical one.

**Why it happens:**
The in-flight changes feel like "almost done" — typography is a coherent sweep, the pillar-status removal is one concept. The temptation is "I'll just finish them as part of the cleanup milestone, since they're the same direction." But the cleanup milestone is a *fresh* scope decision; rolling the old refactor into it loses the per-concern commit history.

A second cause: this is a Windows-edited Git working tree with no `.gitattributes`. Every modified file emits the `warning: LF will be replaced by CRLF` notice. The author has been ignoring those warnings, which discourages running `git diff` cleanly, which discourages committing incrementally.

**How to avoid:**
Phase 0 of the milestone, before any new cleanup commit, is to commit the in-flight refactor in the four chunks `CONCERNS.md § In-Flight Refactor` already enumerates:

1. The `fg-accent → italic` typography sweep across architecture, index, fuelhh, every elexon page.
2. Removal of the `<span class="pillar-status">Shipping</span>` blurbs on `index.html`.
3. The fuelhh honesty edits (`LAST FETCH` → `PRIMARY KEY`, `Live chart` → `Static snapshot`).
4. The remaining per-page tweaks.

Also: add `.gitattributes` with `*.html text eol=lf` (plus `.css`, `.js`, `.json`, `.py`) **in the first cleanup commit** to stop the LF/CRLF warning noise. Every Windows-edited commit going forward registers as the actual diff, not the line-ending churn.

Push to `main` after committing — GitHub Pages will catch up to working-tree state, and the deployed site stops being a different version from what the author is editing against.

**Warning signs:**
- `git status` showing more files modified than the cleanup task itself touched
- A commit message that has to use the word "and" three times to describe what it does
- An author reluctant to `git reset --hard` because they "have unsaved good work in the working tree"

**Phase to address:**
**Phase 0** — precedes every other phase. This is the gating prerequisite for the milestone, not a content phase. Extends `CONCERNS.md § In-Flight Refactor (Uncommitted)` and adds the `.gitattributes` fix from the same section.

---

### Pitfall 1: Partial honesty pivot — surface relabel without removing interactive affordances

**What goes wrong:**
The user already started the live → static pivot on `fuelhh.html` (changed `LAST FETCH / 42 s ago` to `PRIMARY KEY`, changed the chart caption to `Static snapshot · live wiring planned`). But the same page still ships `<span class="chip live" style="font-size:11px;">live · 30 min</span>` in the hero (line 131), and the snapshot chart still wears `24h / 7d / 30d` tab pills (lines 271–274) that don't switch anything. **A reader registers cognitive dissonance: the chrome says "this is live and you can change the window" but the prose admits it is a static snapshot.** That dissonance is worse than either of the unambiguous endpoints.

Identical pattern across the 22 dataset pages: hero `chip live`, hero `LAST FETCH · N min ago`, plus every Related-dataset card carries its own `<span class="chip live">live</span>` (see `boal.html` lines 54–56, 70 and the related cards on `fuelhh.html` lines 542, 578, 590, 602).

**Why it happens:**
"Honesty sweep" feels like a copy-edit job, but the false-liveness is encoded in:
1. Hero chips (`chip live`)
2. Hero LAST FETCH stat-card
3. Footer "last sync" string in `site.js`
4. Time-window tab pills on every snapshot chart
5. Live-status chips on every Related-dataset card (so even a *correctly* relabelled page still advertises its siblings as "live")
6. The `v0.4.2 · build 2026.04.30` footer string

Touching one surface at a time leaves the others to contradict it.

**How to avoid:**
Treat the honesty sweep as one atomic pass with a fixed grep checklist, not a per-page polish. Before declaring honesty sweep done, the repo must have **zero hits** for: `chip live`, `class="dot live"`, `LAST FETCH`, `last sync`, `last fetch`, ` min ago`, ` s ago`, `live · `, `Live chart`. The `24h / 7d / 30d` tab pills on snapshot charts must either be removed or relabelled as a static-period indicator (one of them outlined-active, the others gone — not three "buttons").

**Warning signs:**
- Any commit message that touches only one of the six surfaces above
- A reviewer/author who can find a `chip live` after they believed the sweep was done
- "Static snapshot" prose next to a "live" badge in the same hero block

**Phase to address:**
Honesty sweep (extends `CONCERNS.md § Hardcoded "live" timestamps that aren't live`). Should run **after** Elexon dataset depth in order of execution — otherwise every newly-completed stub will reintroduce the same liveness anti-pattern from copy-pasting the fuelhh chrome. But should be *scoped and grep-listed* before depth work starts, so depth work doesn't lay more landmines.

---

### Pitfall 2: Phantom coverage — sidebar advertises sections the page does not contain

**What goes wrong:**
Every dataset page's sidebar lists six on-page anchors: `#overview / #schema / #sample / #api / #caveats / #related`. On the 16 broken stubs only `#caveats` and `#related` actually exist (see `boal.html` lines 83–88 advertising six anchors vs lines 131–144 containing two). A recruiter clicking the "Schema" sidebar link finds the page does not scroll — phantom navigation. This is worse than missing a section, because **the sidebar is the visible promise of depth**; clicking it and finding nothing is the moment a spot-checking reader concludes "this is theatre."

This is not the same problem as the DOM brokenness CONCERNS catalogues. CONCERNS describes the missing `</nav>` and dangling section close tags. The pitfall here is the **shape of the advertised promise**: even if you fix the DOM but copy the sidebar verbatim from fuelhh, half the dataset pages will still over-promise.

**Why it happens:**
The sidebar template is the same on every page because consistency is the goal — but consistency-of-shape masquerading as consistency-of-content is the trap. When the author "fixes one stub" by hand, the sidebar shape is the most copy-pasteable thing, and the temptation is to leave the sidebar alone and just add sections.

**How to avoid:**
For each of the 22 dataset pages, the sidebar's on-page anchors must be a **subset** of the actual `<section id="">` elements on the page. Two enforceable rules:
1. A pre-commit grep: collect all `<section id="X">` ids on a page, and assert every `.sidebar a[href^="#"]` href in the sidebar resolves to one of them.
2. In the cleanup roadmap, finish a dataset page **end-to-end** before moving to the next — don't bulk-add sidebars and bulk-fill sections in separate passes.

The "snapshot chart" section (between Overview and Schema on `fuelhh.html`) is also part of the canonical shape — either make it standard across all 22 or remove the sidebar entry for it on pages that won't have one.

**Warning signs:**
- A sidebar anchor href in `git diff` that doesn't correspond to a new `<section id="...">` in the same diff
- A page where `Array.from(document.querySelectorAll('.sidebar a[href^="#"]')).filter(a => !document.querySelector(a.getAttribute('href')))` returns anything in the browser console

**Phase to address:**
Elexon dataset depth (extends `CONCERNS.md § 16 of 22 Elexon dataset pages are broken stubs` and `CONCERNS.md § Fragile Areas: "Schema/sample/api" sections only exist on 6 pages`). Add the grep as a deploy-workflow check, not a hope.

---

### Pitfall 3: Vendor-doc drift — schema/endpoint/path claims don't match what Elexon actually returns

**What goes wrong:**
The site invites the spot-check. Every dataset page lists an API path (`/datasets/FUELHH`), a param style (`publishDateTimeFrom / To`), a column list with types, primary-key declarations, and even URL example query strings (`fuelhh.html` line 453: `https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2026-05-01T00:00:00Z`). A recruiter who knows Elexon — and the audience is people who *might* know Elexon, since they work at energy trading firms — can copy that URL, hit the API, and confirm or deny.

**Drift is not a hypothetical.** The current code already demonstrates one drift event: `boal.html` caveat 01 explicitly says "Old BOAL endpoint decommissioned · /datasets/BOAL returns 404 · now sources from /datasets/BOALF". That happened. ENTSO-E went through its own SOAP → REST migration. Vendor docs change between when the page is authored and when a recruiter reads it.

If a recruiter spot-checks one schema field — say, `published_at` on `fuelhh` — and finds Elexon's response key is actually `publishTime`, the site's "domain depth" claim collapses for that recruiter.

**Why it happens:**
- Schema columns are hand-typed from memory or from a stale copy of the vendor docs
- API endpoint paths get copy-pasted page-to-page; if one was wrong, all 22 are wrong the same way
- Vendor docs themselves are versioned out from under the page over time; nothing in the site declares "verified against vendor docs of date X"
- Re-checking is invisible work, so it's the first thing to slip

**How to avoid:**
- Each dataset page carries a micro-line near the metadata block: `verified-against-vendor-docs: YYYY-MM-DD` and a link to the specific vendor doc page (Elexon's per-dataset Insights API page).
- For columns: the schema table notes name the source of truth (e.g. `fuelhh.html` line 286–287 already does this: "Defined in `gridflow/schemas/elexon.py · ElexonFuelHH`"). Extend this: also cite the Elexon Insights field name where it differs from the silver column. This makes the alignment explicit and reviewable.
- Pin example URLs to a known-historical date range, not "today minus 24h" framing. `fuelhh.html`'s example uses `2026-05-01` to `2026-05-02` — that is correct.
- Don't write claims about API behaviour you haven't observed. The hardest example: `fuelhh.html` caveat 05 says "median observed lag is 42 s from Gridflow's perspective". If that came from the actual gridflow pipeline metrics, keep it; if it was invented, it's a load-bearing fiction.

**Warning signs:**
- Author cannot say "I last verified this page against the Elexon docs on YYYY-MM-DD"
- Two dataset pages claim different things about the same shared concept (e.g. one says SP is 1–48, another implies 1–50 routinely)
- An example URL that returns 404 or returns shaped-differently JSON when run

**Phase to address:**
Elexon dataset depth (a NEW concern not in `CONCERNS.md`). Cross-vendor proof must apply the same discipline to the one ENTSO-E dataset — and the ENTSO-E migration history means *flag* the rate-of-change in the caveats.

---

### Pitfall 4: Manifest-as-fiction — JSON files that look like the source of truth but are never read

**What goes wrong:**
`site/hifi/data/vendors.json` and `site/hifi/data/elexon.json` look authoritative. `elexon.json` lists 25 dataset IDs; the catalogue UI claims 28; 22 pages exist on disk. They have never been `fetch()`ed. They are entirely an authoring artefact. During cleanup, the temptation is "I'll just update `elexon.json` to match" — making it a dual-write with the HTML, which is the dual-write problem at its most boring: two files claim authority, neither is.

**Why it happens:**
The JSON looks technical and ground-truthy. Spending effort on it *feels* like reconciling a count discrepancy. But touching the JSON does nothing for the page count discrepancy until something *reads* it.

**How to avoid:**
Pick one of two paths, write down the choice, and stick with it.

- **Path A (delete):** Remove `site/hifi/data/vendors.json` and `site/hifi/data/elexon.json`. HTML is the source of truth. The numbers in the catalogue UI ("7 vendors · 49 datasets", "28 datasets") get reconciled by hand to match the actual `.html` files on disk.
- **Path B (generate):** Wire `site/hifi/assets/site.js` (or a build-time script — see Pitfall 6) to render the catalogue cards from `elexon.json`. The JSON becomes the source of truth. Page counts are computed from JSON length, not typed. Existing card HTML is replaced by a `<template>` plus a `fetch('data/elexon.json')` pass on `data-sources.html` and `data-sources/elexon.html`.

Path A is correct for v1 because Path B introduces a runtime dependency and a build step that violates the "no build step" constraint unless it runs in the browser (which adds an empty-state flash). Path B is correct after v1 when the page-count is over ~30.

What to NOT do: keep both, "syncing" them by hand. That is the pitfall.

**Warning signs:**
- A commit that edits both an HTML count *and* the JSON
- A grep for `fetch(` still returns zero hits on JS files after the cleanup is "done"
- Discussion of "the JSON is the source of truth" without code that reads it

**Phase to address:**
Structural / CSS debt (extends `CONCERNS.md § Unused JSON manifests` and `CONCERNS.md § Hardcoded duplicated catalogue counts`). Decide before the count-reconciliation work in Elexon dataset depth, because the decision determines where the 22/25/28 numbers actually live.

---

### Pitfall 5: Obsidian Vault sync direction left ambiguous

**What goes wrong:**
The user says "sync the Obsidian Vault dataset pages so they match the new on-site content." Direction implied: on-site → vault. But the vault is the user's *working notebook* in the `gridflow` repo; in practice vault-side edits will happen — the author makes a note during pipeline work, captures a Caveat the API throws, etc. The hybrid case (some edits start on-site, some start in the vault) plus no automation = guaranteed drift within a month. The pitfall is **failing to pick one direction and one mechanism**, not the act of syncing.

A second flavour: the source-of-truth hierarchy in `PROJECT.md` is `vendor docs > on-site > vault`. That's a *read* hierarchy. The *write* direction is unstated. Read and write directions are different questions.

**Why it happens:**
"Sync once" feels achievable. "Maintain sync" is a recurring discipline that's invisible work between milestones. Authors underestimate vault-side edit pressure because the vault is also their reference.

**How to avoid:**
Pick one and commit in writing in `PROJECT.md`:

1. **Vault is a read-only mirror of on-site.** Vault pages get a header banner: "Auto-mirror from gridflow-front-end @ commit X · DO NOT EDIT HERE · edit on-site." Vault-side edits are explicitly out-of-policy. Sync is a manual port from on-site → vault at milestone boundaries.
2. **Vault is the working source; on-site is generated from vault.** On-site dataset pages are rendered from vault markdown by a script. Vault-side edits flow forward; on-site edits are forbidden.
3. **Vault and on-site are independently authored documents that share a subject.** No sync. Each lives its own life. Drift is acknowledged and accepted.

Pick #1 for v1. It matches the stated hierarchy. Add the banner. Add a `Last synced from on-site: YYYY-MM-DD @ commit-hash` footer on every vault page. Without the banner+timestamp pair, future-you will edit the vault and forget which side wins.

**Warning signs:**
- A vault page with no provenance timestamp
- A vault page edited after the last on-site sync (check git timestamps in the gridflow repo)
- The author saying "I'm not sure if this should go in the vault or the site"

**Phase to address:**
Cross-repo sync (a NEW concern not in `CONCERNS.md` — out of scope for the front-end repo's audit). This pitfall is the entire reason cross-repo sync is its own phase: if the sync mechanism is wrong, redoing it is more work than the initial sync. Get the policy right before the port.

---

### Pitfall 6: Hand-edit-22 vs SSG false dichotomy — over- or under-engineering the templating

**What goes wrong:**
There are two visible bad endpoints:

- **Hand-edit each of 22 dataset pages to fuelhh fidelity, copy-paste the chrome.** Looks fast for the first three pages. By page 12 the author has made small drift in section ordering, chip text, sidebar order — and any future visual change requires editing 22 files (plus, soon, 14 ENTSO-E pages). This is what produced the current state.
- **Adopt Astro / 11ty / Hugo, introduce a build step, npm/node toolchain.** Over-engineering for 22 → 50 pages, violates the explicit `PROJECT.md` constraint "Static site, no SSG today — must remain deployable as a plain GitHub Pages artefact from `site/hifi/`. If a build step is added, it must produce a deployable static directory and not break the existing deploy."

The pitfall is treating those as the only two options and picking one of them.

**Why it happens:**
"Static site generator" is a binary in most people's heads — you either have an SSG or you don't. The middle path (a 100–200 line Python script that templates HTML from JSON, run pre-commit or pre-deploy, output committed to the repo) is rarely the first thing reached for.

**How to avoid:**
Middle path: a small Python script (stdlib + Jinja2 if installable; the `gridflow-serve` package can host it) that:
1. Reads `site/hifi/data/elexon.json` (resolves the manifest-as-fiction problem from Pitfall 4).
2. Renders each dataset page from a single `dataset.html.j2` template + a per-dataset content fragment.
3. Writes the generated HTML to `site/hifi/data-sources/elexon/*.html` (still committed; deploy stays a static dir copy).

This satisfies the constraints: deployment artefact is unchanged, no node/npm, no build step in CI (the script runs locally pre-commit), and adding ENTSO-E is one more script invocation, not 14 more page authors. **Caveat: Jinja2 is a third-party dep, and `pyproject.toml` declares `dependencies = []`. Either gate the templating script behind an `[dev]` extra (the user's preferences mention `uv pip install -e ".[dev]"` already), or hand-roll templating with `string.Template` / f-strings on a single anchor file.**

The pitfall to NOT fall into: starting hand-edit, getting 6 pages done at fuelhh fidelity, and then refusing to switch to the script because "we've come this far." Decide on templating mechanism in the planning phase, before page 1 of the rewrite.

**Warning signs:**
- A commit that copies `fuelhh.html` to `system_prices.html` and edits in place — that is the moment the templating decision should have been made.
- Section ordering differs between two dataset pages without intent.
- The author considers, mid-stream, "should I just adopt 11ty?" — that's the symptom of the false dichotomy.

**Phase to address:**
Structural / CSS debt (extends `CONCERNS.md § Massive duplication of inline CSS across dataset pages` and `CONCERNS.md § Scaling Limits: Manual dataset-page authoring scales O(N×regions)`). The decision precedes Elexon dataset depth — the depth pass should consume the templating output, not produce the inputs.

---

### Pitfall 7: Made-up precision in domain numbers

**What goes wrong:**
`fuelhh.html` claims `~1.4M rows / month`, `11y history (from 2014)`, `48 Rows / SP`, `16 Fuel types`. `boal.html` claims `~1.1M rows / month`. These look authoritative. A recruiter who runs the actual API might find, say, that fuelhh returns 22 fuel types in 2026 (added new interconnectors), or that the 11-year backfill only goes to 2017 in practice because Elexon retired BMRS V1.

**Domain precision is more credibility-load-bearing than design polish.** A typo in body copy is forgivable; an incorrect dataset claim is the thing the recruiter remembers when they decide whether to look at the GitHub.

**Why it happens:**
Numbers feel like they need to be specific to look credible. "~1.4M rows / month" reads as more domain-grounded than "monthly ~10⁶ rows". The temptation is to round to a plausible-sounding precise number rather than admit "this is the order of magnitude I haven't measured exactly."

**How to avoid:**
Two rules:
1. **Provenance test:** for every quantitative claim on a dataset page, the author can say in one sentence where the number came from. "I queried the actual silver parquet partition on 2026-04-29 and counted." "I read Elexon's docs section X." "I estimated from a single day's sample × 30." If the answer is "it sounded right", the number doesn't ship.
2. **Honesty about precision:** if it's order-of-magnitude, write "~1M rows / month" or "low millions of rows per month". Reserve precise numbers (`48`, `16`, `2014-04-01`) for things that are structurally exact (a settlement day has 48 SPs).

The dataset hero metric strip on `fuelhh.html` (`48 Rows / SP · 16 Fuel types · 1.4M Rows / month · 11y History · 30min Resolution`) mixes structural facts (48, 30min) with measured estimates (1.4M, 16). Distinguish them in the prose if not in the layout.

**Warning signs:**
- A number on a dataset page that doesn't appear in the corresponding gridflow pipeline code, schema, or sample data
- Two dataset pages with suspiciously similar magnitudes (1.4M, 1.1M…) — suggests copy-paste rather than measurement
- The author cannot name the source of a number when challenged

**Phase to address:**
Honesty sweep + Elexon dataset depth. Treat this as an extension of the live-framing pivot: not just "kill live", but "kill made-up precision." This is a new concern; `CONCERNS.md` doesn't explicitly call it out.

---

### Pitfall 8: GitHub-repo cross-check failure — site claims diverge from sibling repo state

**What goes wrong:**
The site documents two external repos (`github.com/EBentham/gridflow`, `github.com/EBentham/gridflow-models`). The site asserts things about them: "Defined in `gridflow/schemas/elexon.py · ElexonFuelHH`" (`fuelhh.html` line 287), "silver path: silver.fuelhh", "12-step transform pipeline", etc.

A recruiter who clicks through to the gridflow repo is the **best-case audience**, the one who actually wants to read the code. They will find one of three things:
1. The schema file at the claimed path exists and matches the claim — credibility multiplied.
2. The path exists but the schema is different — credibility crater.
3. The path doesn't exist — credibility crater + suggestion that the site is fiction.

Outcomes 2 and 3 are far more probable than outcome 1 *as time passes* and the gridflow repo evolves. The site and the gridflow repo will drift unless someone re-checks.

**Why it happens:**
The site is the polished public artefact; the repos are working state. Authors update the repo without re-checking the site claims, and vice versa.

**How to avoid:**
- Treat the cross-repo claims as a small fixed set (every `gridflow/...` path mentioned, every `silver.*` table name, the architecture-page diagram boxes). Maintain them as a list, not as scattered prose.
- At the end of v1, do a pass: for each cross-repo claim, click through to the repo at HEAD and confirm. If it's wrong, fix the site or open an issue against gridflow.
- Pin the architecture-page diagram to a specific gridflow commit hash and footnote it: "Diagram reflects gridflow @ commit abc1234". Then drift is acknowledged, not hidden.

**Warning signs:**
- A `gridflow/...` path quoted on the site does not exist in the gridflow repo at HEAD
- The architecture page describes a pipeline step that's been renamed or removed in gridflow
- "When was the last time I checked the schemas in `fuelhh.html` matched the gridflow repo?" cannot be answered with a date

**Phase to address:**
Main-page polish (for architecture.html claims) + Elexon dataset depth (for per-dataset claims). A NEW concern not in `CONCERNS.md` — out of scope of a single-repo audit, but in scope of the cleanup milestone because the milestone is about credibility.

---

### Pitfall 9: "Coming soon" vendor stubs that read as half-done vendor pages

**What goes wrong:**
The cleanup will replace dead `<a href="#">` vendor placeholders with "clean coming soon landing pages" for ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO. The trap: if those stub pages reuse the vendor-page template (the same chrome as `data-sources/elexon.html`) with empty sections inside, they look exactly like the broken stubs the cleanup is removing. A recruiter cannot distinguish "page that isn't done yet" from "page that's intentionally minimal because we're being honest about coverage."

The signal collapses to the same one as the dataset stubs: "advertised coverage, no actual content."

**Why it happens:**
Template reuse is the obvious move. Empty sections feel like placeholders; the difference between "placeholder for content that's coming" and "intentional acknowledgement that there's nothing" is not visually encoded by default.

**How to avoid:**
The "coming soon" pages need a **visually distinct treatment** that says "I'm intentional, not unfinished." Concretely:
- Different layout: no sidebar, no stats strip, no chart container. A one-screen page.
- Explicit framing in the lede: "ENTSO-E datasets are documented in a later milestone. For now, this page covers what gridflow already ingests from this vendor and which datasets are next."
- Honest list of which gridflow modules already touch this vendor and which don't.
- A "see Elexon for the documentation pattern" cross-link, so recruiters who want depth know where to go.

The contrast between the one done ENTSO-E *dataset* page (the cross-vendor proof) and the intentional ENTSO-E *hub* stub becomes a feature: the dataset page shows "here is what depth looks like for ENTSO-E", the hub stub shows "here is what we explicitly haven't shipped." Both are honest.

**Warning signs:**
- A "coming soon" page that has the same chrome shell as `elexon.html`
- A reviewer cannot tell, from a quick scroll, whether a page is honestly stubbed or accidentally broken
- The "coming soon" pages include the same `chip live` chrome as the dataset pages

**Phase to address:**
Cross-vendor proof. This pitfall is specific to the v1 milestone scope and has no direct CONCERNS analogue (CONCERNS catalogues the dead-anchor problem; this pitfall is about *how to fix it without recreating it*).

---

### Pitfall 10: Mobile fix is a viewport find-and-replace; CSS underneath is desktop-only

**What goes wrong:**
The viewport meta-tag fix (`width=1280` → `width=device-width, initial-scale=1`) is a one-line find-and-replace per file — described as "trivial" in `CONCERNS.md § Non-responsive viewport`. But fixing the viewport is necessary, not sufficient. Once the viewport responds to actual device width, the underlying CSS has to handle ~360px screens. The dataset pages use:
- `grid-template-columns: 220px 1fr` for the sidebar layout (`boal.html` line 30, `fuelhh.html` line 76) — does this collapse on mobile?
- Inline `style="display:grid;grid-template-columns:1fr auto;gap:48px;"` for the hero (`boal.html` line 52)
- Inline 5-column stats strips (`grid-template-columns:repeat(5,1fr);` `boal.html` line 76)
- Hard-coded `min-width:340px` on the metric card (`boal.html` line 64)

The home and architecture pages already have correct viewports and *some* media queries (`theme.css` `@media (max-width: 720px)` at line 634, `@media (max-width: 480px)` at line 716). The dataset pages have **none** — they have never been rendered at mobile width, because their viewport was locked to 1280. Fixing the viewport will expose them to mobile for the first time.

**Why it happens:**
"Mobile fix" sounds like the viewport tag, because that's what `CONCERNS.md` highlights. But the CONCERNS framing is "23 of 27 pages have the wrong viewport tag" — it is correct as far as it goes, and stops short of "and the CSS for those pages was never written to respond." The fix scope is bigger than the warning.

**How to avoid:**
After the viewport tag is fixed on the 23 pages, open every dataset page at 375px width (iPhone SE) and 414px (larger phone) and fix the breakages. Specific expected problems:
- Sidebar `220px + 1fr` is 220 + 155 = too wide; sidebar should collapse to a top-of-page list or a disclosure widget below 720px.
- Hero `1fr auto · 48px gap` overflows; the metric card should stack below the title.
- 5-column stats strip becomes 2×3 or 1-column.
- The data sample table (with `white-space: nowrap`) and the schema table need horizontal scrolling treatment, which `fuelhh.html` line 371 already does with `style="overflow-x: auto;"` — port that to every page.

This is a single CSS pass on `theme.css` (after CSS debt extraction from Pitfall 6 / Structural debt phase), not 23 per-page fixes.

**Warning signs:**
- "Mobile is fixed" claimed without anyone having loaded a dataset page on an actual phone (or DevTools at 375px)
- Sidebar still visible at 375px width
- Horizontal scrollbar on a phone

**Phase to address:**
Bug & a11y fallout (extends `CONCERNS.md § Non-responsive viewport on 23 of 27 pages`). Specifically: the viewport find-and-replace is *step 1*; step 2 is the mobile-CSS pass on the dataset-page styles, which depends on the CSS extraction from Structural / CSS debt completing first.

---

## Technical Debt Patterns

Shortcuts that the cleanup will be tempted to take.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip committing the in-flight refactor; "I'll roll it into the cleanup commits" | Saves the four-commit sequencing work upfront | Every future cleanup commit is entangled with three concurrent refactors; bisect dies; partial honesty edits to fuelhh become un-reviewable | Never — Pitfall 0 makes this the gating Phase 0 task |
| Skip `.gitattributes` because "the line-ending warnings are noise" | Saves one trivial commit | Every Windows-edited commit registers as full-file diffs against any Linux PR/deploy; future merges have cosmetic conflicts | Never — single-line `.gitattributes` is cheaper than living with the warnings |
| Copy-paste fuelhh.html for each of the 16 broken stubs, edit in place | Each page reaches fuelhh fidelity in ~30 min | Re-introduces all duplication; next visual change re-edits 22 files | Never in v1 — adopt the templating path from Pitfall 6 instead |
| "I'll fix the inline `<style>` block extraction later, just fill the stubs first" | Unblocks Elexon dataset depth phase | The 22 stubs each acquire the ~30 line block as you fill them; CSS extraction becomes 22-file diff | Only if extraction is committed within the same milestone, not deferred |
| Hardcode "28 datasets" on the catalogue UI to match the 22 actual + 6 stubs that ship | Reconciles the count discrepancy by hand | Counts will drift the next time a dataset is added; the discrepancy is a symptom of the unwired manifest | Acceptable if Path A (delete JSON) is chosen and the count is honestly typed |
| Leave `chip live` on the 5 NESO Carbon-related references because "Carbon Intensity API really is live" | True statement defends the chip; one less file to touch | "Live" everywhere else means fake; reader can't tell which "live" is real | Never — find one word that's not "live" for the genuinely-live case (e.g. "real-time") to keep the contrast clean |
| Use `<!-- TODO: -->` HTML comments for known-incomplete sections, ship them | Author knows what's pending; reviewer can grep | Recruiters can View Source. A TODO in the source of a portfolio page is a credibility hit. | Never — convert TODOs to GitHub issues, remove from HTML |
| Skip the Obsidian Vault sync this milestone, "do it after v1 ships" | Reduces v1 scope by one phase | Vault drift gets a month of head start; future sync is harder, not easier | Acceptable only if vault is declared explicitly out-of-scope until milestone 2 — but the user picked it as v1 scope, so this is the wrong shortcut here |
| Wire `gridflow-serve` to live-reload during cleanup, ship the live-reload script in the deployed bundle | Faster cleanup feedback loop | Live-reload code on the deployed site is dead weight; reader inspects it and sees "this is dev tooling" | Acceptable only if the live-reload is dev-server-only, not in the static artefact |

---

## Integration Gotchas

The "integrations" here are not runtime API calls (the site is static) but **documentation integrations** — the site claims things about external systems whose behaviour it doesn't control.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Elexon BMRS Insights API | Documenting endpoints from memory or a stale cache | Hit each endpoint live during the dataset-depth pass; pin the example URL to a fixed date so it's reproducible |
| Elexon endpoint renames (BOAL → BOALF pattern) | Discovering the rename only when the recruiter reports the 404 | The cleanup adds a `verified` date to each page; future renames are caught by re-verification, not by user reports |
| ENTSO-E Transparency Platform | Documenting SOAP-era patterns because that's what the older blogs describe | Use the REST API docs for the one ENTSO-E dataset, since SOAP was sunset; flag in caveats that ENTSO-E has migrated |
| `gridflow` (sibling repo) — schema paths | Site claims `gridflow/schemas/elexon.py · ElexonFuelHH`; gridflow renames the module | Make cross-repo claims a maintained list (see Pitfall 8); re-verify at milestone boundaries |
| `gridflow-models` (sibling repo) | Site implies a model exists ("demand forecast", "SRMC") that's only sketched in the repo | Each model case study links to the specific module in gridflow-models; if the module is a stub, say so on the case study |
| Google Fonts CDN (Fraunces, Inter, JetBrains Mono) | Treating it as "free" but it cross-origin-leaks the visitor's IP to Google; also contradicts the `0 Cloud deps` claim on `index.html:384` | Either self-host the fonts under `site/hifi/assets/fonts/` and refine the cloud-deps claim, or remove the claim. Don't do both half-way. |
| GitHub Pages deploy | Assuming Pages caches your CSS forever — they don't, but they cache for a few minutes after redeploy | Don't add cache-busting query strings unless a real cache problem appears; if it does, append `?v=` to the asset link from a single point of edit (e.g. inject in `site.js`) |
| Obsidian Vault | Treating the vault folder structure as identical to the site's (`vault/elexon/datasets/fuelhh.md` ↔ `site/.../elexon/fuelhh.html`) and assuming a 1:1 file map | The vault has folders the site doesn't (`10-personal/`, `20-projects/`) and may have an Index-of-vendors page the site renders differently; specify the mapping explicitly in the sync policy |

---

## "Looks Done But Isn't" Checklist

The dataset-page-by-dataset-page completion checklist. A page is **not** done until every box is checked.

- [ ] **Viewport:** `<meta name="viewport" content="width=device-width, initial-scale=1" />` (not `width=1280`)
- [ ] **DOM structure:** opens with `<body data-page="dataset" data-root="../../" data-screen-label="NN Dataset · slug">`, contains `<nav class="sidebar" aria-label="On this page">`, contains `<main>` wrapping the main content, closes nav and main properly
- [ ] **Sidebar promises match reality:** every `<a href="#X">` in the sidebar has a corresponding `<section id="X">` on the page
- [ ] **Live-framing zero hits:** no `chip live`, no `dot live`, no `last fetch`, no `min ago`, no `last sync`, no `Live chart` (run grep — list of forbidden strings is fixed)
- [ ] **Snapshot caption present:** the chart container ends in `<div class="snapshot-note">Static snapshot · …</div>` (or equivalent honest framing)
- [ ] **Inline `<style>` block removed:** the dataset-page CSS is in `theme.css`, not the head of every page
- [ ] **Inline `style="color:var(--ink-faint);"` removed from sidebar links:** uses `class="muted"` (or similar) so hover affordance works
- [ ] **Vendor verification micro-line:** the metric block or hero footer carries `verified-against-vendor-docs: YYYY-MM-DD` and an explicit Elexon doc URL
- [ ] **Numbers have provenance:** the author can name where every quantitative claim (rows/month, history depth, etc.) came from
- [ ] **Cross-repo claim verified:** if the page mentions `gridflow/schemas/...` or `silver.X`, that path/table actually exists in the gridflow repo at HEAD
- [ ] **API example URL works:** copy the example URL, paste it, get a response that matches the documented schema
- [ ] **Schema columns match vendor:** the column names in the schema table match what the Elexon endpoint actually returns (allow renamed silver columns, but say so in the note column)
- [ ] **Mobile rendering:** open the page at 375px width and confirm sidebar collapses, hero stacks, stats strip wraps, sample table scrolls horizontally
- [ ] **A11y minimums:** decorative `<span class="arrow">→</span>` carries `aria-hidden="true"`; sidebar `<nav>` has `aria-label`; current sidebar item has `aria-current="location"`
- [ ] **Tabs use shared mechanism:** dataset-page tabs use `[data-tabs]` (read by `site.js`), not the per-page global `setTab()` function (which must be removed)
- [ ] **Scroll-spy uses shared mechanism:** no per-page `IntersectionObserver` snippet; the helper lives in `site.js` and is gated by `data-page="dataset"`
- [ ] **Related-card statuses honest:** Related dataset cards don't carry `chip live` (or the chip word matches the target page's honest framing)
- [ ] **No TODO comments:** `git grep TODO site/hifi/<file>` returns nothing

---

## UX Pitfalls

Recruiter-facing UX issues specific to a 30-90 second skim audience.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Hero on the home page leads with a chart, not a sentence | Recruiter has to decode visuals to understand what this *is* before deciding to scroll | Lead with a one-sentence framing: "Documentation of the gridflow ETL pipeline and the models built on it, for energy-trading recruiters." Then the chart. |
| "Live" badges everywhere set the wrong expectation | Recruiter expects an interactive product; sees static page; concludes "broken" rather than "honest doc site" | After honesty sweep, the absence of liveness chips makes the documentation framing clearer |
| Dataset page hero buries the dataset name in body copy | Recruiter skimming the sidebar / browser tab sees the slug, not the human name | The hero already does this right on `fuelhh.html` (slug in mono + the human title as a display line) — replicate the pattern on all 22 |
| Caveats section reads as theoretical rather than from-real-experience | Recruiter discounts "things to know before using this" as boilerplate | Each caveat starts with the observable phenomenon, not the abstraction. "If you sum fuel types for an SP and get more than total demand, you've forgotten WIND is metered-only" beats "Some Elexon datasets exclude embedded generation." |
| Sidebar siblings list isn't browseable — clicking lands on a *similar* page that's missing its own anchors | After clicking 2-3 sibling links, recruiter loses trust in navigation | Until all 22 are at fidelity, the sidebar's sibling list should only list complete pages. (Or, less drastically, mark stubs as `(planned)` and link to the elexon hub instead of the stub.) |
| Same chrome for "this is a stub" and "this is a depth page" | Recruiter can't tell from page chrome whether they're on an authored page or a placeholder | See Pitfall 9: distinct layout for intentional placeholders |
| Three-place dataset count (22 / 25 / 28) — at least one is visible to a recruiter on each visit | Recruiter notices the inconsistency before the author does; concludes "they don't QA their own site" | Compute or fix once after the manifest-or-not decision (Pitfall 4) |
| Long-form sections (architecture.html at 1178 lines, fuelhh.html at 648 lines) have no anchor TOC at the top | Recruiter skimming has no map to jump into the section that interests them | Architecture page already has a sidebar pattern; dataset pages have a sidebar already; the home and architecture-introduction sections do not. Add an inline "in this article" anchor block for those. |

---

## "Recruiter-Bounce" Signals

Specific things that close the tab in the first 30 seconds. Higher priority than abstract polish.

1. **Mobile broken**: 23/27 pages render at 1280px on a phone. Single highest-leverage fix.
2. **A typo in a domain term**: "Settlmenet Period" or "BOALF" misspelled = doubt cast on all other domain claims. Spell-check pass against a domain glossary.
3. **A `<a href="#">` link**: looks interactive, does nothing. 10+ instances per `CONCERNS.md`. Replace with non-link spans or actual links.
4. **A "Last sync 2026-04-30" date older than today by more than a week**: the lie of "this is current". Already happening — `site.js:73` hardcodes 2026-04-30, today is 2026-05-17.
5. **A 404 from a footer link** (e.g. the "Catalogue · Carbon" link in `site.js:62` that lands on a card mid-page, not a section).
6. **A counter that disagrees with itself between pages** (22 datasets on the elexon hub, 28 on the catalogue, 25 in the JSON).
7. **An obvious template artefact** (the `<!-- TODO: replace 'E. Bentham' with your full legal name -->` in `index.html:808`, visible in View Source).
8. **Default favicon**: the browser tab shows the generic globe icon. Reads as "personal project I didn't finish".
9. **A code block that's clearly fake** (e.g. a SQL query that references a table the rest of the site says doesn't exist).
10. **A model case study that hand-waves the model**: "we use a tree-based regressor on demand features" with no follow-through is worse than "we don't have this case study yet".

---

## Vendor-Doc-Drift: Typical Pattern and Detection

The pattern of drift for documentation sites tracking an external API:

1. **Initial authoring** captures vendor docs at a point in time. ~95% accurate.
2. **Vendor introduces a parameter alias** (`from` accepted alongside `publishDateTimeFrom`). Site says only the old one. Recruiter who knows the alias is mildly surprised.
3. **Vendor renames a field** (`publishTime` → `publishedAt`). Site uses the old name. A recruiter who runs the API in parallel sees mismatch.
4. **Vendor renames an endpoint** (`/BOAL` → `/BOALF`). Old URL returns 404. Site is broken for anyone who copy-pastes.
5. **Vendor changes payload shape** (singular → array; nested object lifted to top level). Site's schema description is structurally wrong.
6. **Vendor deprecates and replaces** (V1 BMRS → V2 Insights API). Site is now describing a non-existent system.

The site is currently somewhere between stages 3 and 4 for several Elexon datasets (BOAL → BOALF is captured; whether SP 49–50 handling for DST has been updated is unknown).

**Detection mechanism:** a re-verification pass per dataset every N months, where N is a function of vendor rate of change. For Elexon (~quarterly platform updates), every 3-6 months. For ENTSO-E (~yearly major releases), yearly. The cleanup milestone adds the *machinery* for this: per-page `verified` date, vendor URL, list of cross-repo claims. The recurring discipline is out of scope for v1 but the machinery is in scope.

---

## Pitfall-to-Phase Mapping

How v1 cleanup phases address each pitfall. Phase names are from `PROJECT.md § Active`. The `Depends on` column captures the partial-order constraints from the phase-ordering section above.

| Pitfall | Prevention Phase | Depends on | Verification |
|---------|------------------|------------|--------------|
| 0. Uncommitted in-flight refactor | **Phase 0** (precedes everything) | none — this is the gate | `git log` shows the four logical commits from `CONCERNS § In-Flight Refactor`; `.gitattributes` is committed; `git push` succeeds; Pages catches up |
| 1. Partial honesty pivot | Honesty sweep (run *after* Elexon dataset depth; scope *before*) | Phase 0 + Elexon dataset depth | `git grep -E '(chip live\|last fetch\| min ago\|last sync\|Live chart)' site/` returns zero hits |
| 2. Phantom coverage (sidebar over-promises) | Elexon dataset depth + Cross-vendor proof | Phase 0 + Structural / CSS debt | Per-page assertion: every `.sidebar a[href^="#"]` href resolves to a `<section id>` on the same page |
| 3. Vendor-doc drift | Elexon dataset depth | Phase 0 | Each dataset page carries a `verified: YYYY-MM-DD` micro-line; example URLs return live 200s with shape-matching JSON |
| 4. Manifest-as-fiction | Structural / CSS debt (decide path A vs B before counts work in dataset depth) | Phase 0 | Either `data/*.json` files are deleted, or there is at least one `fetch()` call against them in `site.js` |
| 5. Obsidian Vault sync direction ambiguous | Cross-repo sync (policy before port) | Phase 0 + all on-site work that the vault must mirror (so port happens once) | `PROJECT.md § Key Decisions` carries an explicit sync-direction decision; vault pages have a provenance banner |
| 6. Hand-edit-22 vs SSG false dichotomy | Structural / CSS debt (decision precedes Elexon dataset depth) | Phase 0 | A templating mechanism is committed to the repo before page 1 of the rewrite; or, if hand-edit, explicit acknowledgement and a single anchor file |
| 7. Made-up precision | Honesty sweep + Elexon dataset depth | Phase 0 | Author can cite source for every quantitative claim on a dataset page |
| 8. GitHub-repo cross-check failure | Main-page polish (architecture claims) + Elexon dataset depth (per-dataset claims) | Phase 0 | At milestone close, all cross-repo paths quoted on the site resolve in the corresponding repo at HEAD |
| 9. "Coming soon" stubs look half-done | Cross-vendor proof | Phase 0 + Elexon dataset depth (so the contrast is meaningful) | The 5 vendor stubs use a distinct layout (no sidebar, no chart container, single-screen) from the real vendor pages |
| 10. Mobile fix is viewport-only | Bug & a11y fallout (after Structural / CSS debt extracts dataset CSS) | Phase 0 + Structural / CSS debt | Every dataset page renders correctly at 375px width — sidebar collapses, hero stacks, stats wrap, tables scroll |

---

## Recovery Strategies

If a pitfall slips through and reaches the deployed site.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| 0. Cleanup commits entangled with in-flight refactor | HIGH | Interactive rebase to split commits is expensive and error-prone; in practice, take the loss on review-ability for v1 and pin the discipline ("commit per concern") for v2 |
| 1. Partial honesty pivot — `chip live` left on a few pages | LOW | Re-run the grep checklist; commit + redeploy in one pass |
| 2. Phantom coverage — sidebar links to non-existent sections | LOW | Per-page lint check; remove orphan sidebar entries or add stub sections |
| 3. Vendor-doc drift — recruiter reports a 404 on an example URL | MEDIUM | Re-verify the affected dataset; update endpoint, params, schema; refresh `verified:` date; redeploy. If the dataset has wide changes, add a caveat noting the migration. |
| 4. Manifest-as-fiction left ambiguous — JSON edited but never wired | LOW | Pick path A (delete JSON) or path B (wire fetch); both are short interventions |
| 5. Vault sync direction wrong — vault edits clobber on-site updates | HIGH | If discovered late, manual diff of every vault page vs on-site page; restore the canonical-direction copy; pin policy in PROJECT.md to prevent recurrence |
| 6. Hand-edit creep — 6 pages diverged by hand before templating decision | MEDIUM | Adopt templating retroactively; pick the most-correct page as the anchor; regenerate other 5 from it; verify against caveats and schema lists per page |
| 7. Made-up precision — recruiter calls out a wrong rows/month number | MEDIUM | Audit every quantitative claim; replace with measured numbers or "~order-of-magnitude" framing |
| 8. Cross-repo divergence — site says `silver.X`, repo has no such table | MEDIUM | Fix on the more authoritative side (usually: site catches up to repo); add the alignment to the v2 checklist |
| 9. Coming-soon stubs read as broken | LOW | Restyle the 5 stubs to a one-screen layout with explicit "next-milestone" framing |
| 10. Mobile broken at 375px after viewport fix | MEDIUM | One CSS pass in `theme.css` with `@media (max-width: 720px)` and `@media (max-width: 480px)` blocks for dataset-page selectors; redeploy |

---

## Note on Out-of-Scope Trap Categories

**Performance scaling pitfalls (`breaks at 10K users`, etc.):** intentionally not surfaced. This is a 27-page static site behind GitHub Pages CDN; the audience is recruiters, not concurrent users. Treat performance as "page loads under 2 seconds on 3G" — already mostly met per the cold-load analysis in `CONCERNS.md § Performance Bottlenecks`. The font CDN trip cost is the one real performance lever; addressed in Integration Gotchas above (self-host vs refine cloud-deps claim).

**Generic security pitfalls (XSS in user inputs, CSRF, auth):** intentionally not surfaced. The site has no user inputs, no auth, no forms, no backend. The two security-adjacent items in `CONCERNS.md` (`target="_blank"` missing `rel="noopener"`, the `gridflow-serve` LAN binding) are bug-class, not pitfall-class, and are addressed in Bug & a11y fallout.

**Generic SEO pitfalls (meta-description, OpenGraph):** not surfaced as critical. A recruiter who reaches this site reached it from a CV link or a GitHub link, not from search. Adding OG cards is a nice-to-have, not a credibility lever.

---

## Sources

- `.planning/PROJECT.md` — anti-goals, audience, scope decisions, source-of-truth hierarchy (HIGH; primary source of intent)
- `.planning/codebase/CONCERNS.md` — exhaustive catalogue of current bugs; this file extends, not duplicates (HIGH; primary source of current state)
- `.planning/codebase/ARCHITECTURE.md` — body-data-attribute contract, chrome-injection model, anti-patterns already named (HIGH)
- `.planning/codebase/STACK.md` — no-build-step constraint, stdlib-only Python, no third-party browser deps (HIGH)
- `site/hifi/data-sources/elexon/fuelhh.html` — canonical reference template; structural fidelity target (HIGH; reference implementation)
- `site/hifi/data-sources/elexon/boal.html` — example of the broken-stub shape (HIGH; counterexample)
- Elexon BMRS endpoint rename evidence (BOAL → BOALF) is documented inside the site itself, in `boal.html` caveat 01 (MEDIUM; single source, in-house)
- The forward-looking pitfalls in this file are not from external research — they are derived by reasoning over the codebase concerns, the project's anti-goals, and the recruiter-audience constraint. External validation (industry post-mortems on documentation-site drift, energy-data portfolio reviews) would strengthen specific pitfalls but the codebase + intent docs are the load-bearing evidence here.

---

*Pitfalls research for: editorial portfolio + technical data-source documentation, energy-trading recruiter audience*
*Researched: 2026-05-17*
