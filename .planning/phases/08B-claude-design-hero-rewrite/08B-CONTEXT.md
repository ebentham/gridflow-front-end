# Phase 8B: Claude-Design hero rewrite (hybrid authored/templated) - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning
**Supersedes:** Phase 8 (`08-bug-fix-dataset-formatting`) — see `08-01-SUMMARY.md` for the failed-Phase-8 retrospective

<domain>
## Phase Boundary

Replace Phase 8's failed locked-scope CSS patch with a **hybrid rendering model**: hand-authored HTML pages take precedence over the Jinja2 template on a per-page basis. The motivating learning from Phase 8 is that no rendering-layer patch can fix an editorial-content gap in the source-of-truth layer (the vault has no short H1 tagline field, no accent-styled fragments, no inline `<code>` chips embedded in prose) — so the template has a quality ceiling that cannot meet recruiter-portfolio expectations for showcase datasets.

**The fix is architectural**, not visual: introduce an `authored-pages/<vendor>/<slug>.html` override path. The build script (`src/gridflow_front_end/build.py`) checks `authored-pages/<vendor>/<slug>.html` first; if present, copy it to `site/hifi/data-sources/<vendor>/<slug>.html`; if absent, fall through to the existing Jinja2 template render. The vault-driven long-tail path is preserved unchanged; only the override path is new.

**In scope:**
- Build-script change: `_resolve_page_source(vendor_id, slug)` (or equivalent) that returns `("authored", path)` or `("template", doc)` based on `authored-pages/<vendor>/<slug>.html` existence
- Un-gitignore `authored-pages/**` (currently nothing in this path is gitignored; the constraint is just that it doesn't exist yet)
- Commit `authored-pages/elexon/fuelhh.html` (the Claude-Design output user-verified 2026-05-19) as the first showcase page
- Port (or Claude-Design) one additional showcase page — initial target `system_prices` — as the verification probe for the AI-hand-port path
- User visual verification on the second page → decides long-tail strategy (see success criterion 4 in ROADMAP entry)
- v1 CI gates remain green (`gridflow-build --check`, `htmlhint`, `lychee --offline --include-fragments`)

**Out of scope:**
- Re-running Phase 8's CSS patches (already attempted ×2; closed)
- Reverting the Iteration 2 template changes from Phase 8 (`align-items: stretch`, `grid-template-rows: repeat(3, 1fr)`, `silver.{slug}` short-form) — these are the best-effort layout for the long-tail templated branch and stay in place
- Adding new vault frontmatter fields for editorial content (short_title, editorial_lede, accent_phrase) — explicitly rejected during Phase 8 retrospective because the hybrid override is a cleaner separation of concerns: vault stays terse and machine-parseable; authored pages live where editorial polish belongs
- Visual-regression infrastructure (snapshot testing) — v2 still explicitly skips per PROJECT.md scope
- Porting more than 2 pages before user verification — D-02 below
- Per-dataset related-card blurbs, fuel-pill grid restoration, Pydantic schema drift closure — all explicit v3 candidates per PROJECT.md

</domain>

<decisions>
## Implementation Decisions

### Architecture choice

- **D-01:** **Hybrid model (Option B).** Authored pages override the template per-slug; long tail stays templated. User picked this 2026-05-19 in conversation after Option A (template-only) and Option C (all-authored) were laid out, with Option C as the explicit fallback if Option B doesn't scale.
  - **Why:** Best of both — showcase quality where it matters (recruiter spot-checks fuelhh, system_prices, actual_generation), template economics for the long tail (150+ pages where vault-driven is "good enough"). Option A failed the quality bar (Phase 8 outcome); Option C front-loads 163× external work and erases vault → site automation.
  - **How to apply:** Build script gets a single resolver function. Authored pages and templated pages produce **byte-identical site/hifi/** output structure (same paths, same asset links, same anchor IDs) — they're indistinguishable to lychee, htmlhint, the dev server, and the GitHub Pages deploy.

### Second-page port strategy

- **D-02:** **One probe page before scaling.** The user's plan step 2 explicitly says "Do one first, and I will verify" — port exactly one additional page (initial target: `system_prices`) and stop for user verification before doing the other 32 Elexon + 1 ENTSO-E pages. The verification outcome decides between three long-tail strategies (success criterion 4 of the ROADMAP entry).
  - **Why:** Hand-porting (or Claude-Design generating) each page is bespoke work; the second-page outcome is high-signal about whether AI-hand-port can match Claude-Design quality. Front-loading 33 ports before verification risks burning effort on the wrong path. The user's plan structures this as a checkpoint.
  - **How to apply:** Port `system_prices` to `authored-pages/elexon/system_prices.html` using `vault/elexon/system_prices.md` as content source and `authored-pages/elexon/fuelhh.html` as design reference. Stop for verification before any third page.

### Build-pipeline integration

- **D-03:** **Authored pages live OUTSIDE `site/hifi/data-sources/`.** Source at `authored-pages/<vendor>/<slug>.html` (top-level repo dir, NOT under `.planning/` and NOT under `site/`). The build copies (not symlinks) authored pages into `site/hifi/data-sources/<vendor>/<slug>.html`. `site/hifi/data-sources/<vendor>/*.html` stays gitignored (generated).
  - **Why:** Keeps the "site/ is the published artefact" invariant; `gridflow-build --check` idempotence still works (copy is byte-stable); preserves the GitHub Pages deploy contract (site/hifi/ is the upload root). Source-vs-output separation matches `vault/ → site/` direction already established in v1.
  - **How to apply:** Build script `OUTPUT_DIR = site/hifi/`; add `AUTHORED_DIR = authored-pages/`. New resolver function checks `AUTHORED_DIR / vendor / f"{slug}.html"` first.

### Viewport meta tag in authored pages

- **D-04:** **Authored pages MUST use mobile-friendly viewport** (`<meta name="viewport" content="width=device-width, initial-scale=1">`), NOT the desktop-fixed `width=1280` that Claude Design defaulted to in the verified fuelhh output. The build can either (a) accept this as a hand-author responsibility and CI-gate it via grep, or (b) post-process authored HTML to normalise the viewport meta. Option (a) is simpler; option (b) is more defensive.
  - **Why:** Mobile viewport was the single highest-leverage fix in v1 Phase 1 (per Pitfall 10). Regressing to `width=1280` on showcase pages would undo a v1 milestone-success criterion.
  - **How to apply:** Initial implementation = (a) hand-author responsibility + grep gate. Add to CI: `grep -L "width=device-width" authored-pages/**/*.html` must return zero files. If a future authored page violates, the gate fails loudly.

</decisions>

<specifics>
## Provisional Implementation Notes

### Resolver function shape (build.py)

```python
def _resolve_page_source(vendor_id: str, slug: str) -> tuple[Literal["authored", "template"], Path | None]:
    """Return ('authored', source_path) if an authored override exists; else ('template', None) for vault-driven render."""
    authored = AUTHORED_DIR / vendor_id / f"{slug}.html"
    if authored.exists():
        return ("authored", authored)
    return ("template", None)
```

Build loop integration: in the per-dataset write step, branch on the resolver's return:
- `("authored", path)` → `shutil.copy(path, output_path)`
- `("template", None)` → existing Jinja2 render path

### Idempotence

`gridflow-build --check` already compares old vs new output. Authored pages are byte-stable (copy is deterministic). Templated pages are byte-stable (Jinja2 + sorted dict iteration). Both branches preserve `--check` behaviour without modification.

### CI gates

- `htmlhint` — runs on `site/hifi/**/*.html` (already in place); authored pages produce HTML in that path, so they're auto-gated
- `lychee --offline --include-fragments` — same surface, auto-gated
- New: viewport meta grep gate on `authored-pages/**/*.html` (D-04)

### Cross-link anchors

Authored pages MUST include the standard sidebar anchors (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) so `lychee --include-fragments` doesn't flag cross-page anchor refs from the vendor hub. The verified fuelhh.html (from Claude Design) does include these — confirmed during D-04 review. Future authored pages must too. This is a hand-author responsibility; not currently a CI gate (could add one).
</specifics>

<questions_answered>
## Questions Resolved Before Planning

- **Q-1:** Which page is the second-page port target? → `system_prices` (different schema, no fuel-pill section, well-known Elexon dataset, simple test of design generalisation)
- **Q-2:** Who produces the second page — orchestrator AI-hand-port, or external Claude Design? → AI-hand-port (cheap probe; user verification decides whether to escalate to Claude Design for the rest)
- **Q-3:** What happens to the Iteration 2 template changes from Phase 8? → Kept (best-effort layout for templated long tail)
- **Q-4:** Where do authored pages live? → `authored-pages/<vendor>/<slug>.html` at repo root (D-03)
- **Q-5:** Do authored pages need vault frontmatter? → No. The vault → site invariant is preserved for templated pages; authored pages are pure HTML deliverables.

## Questions Still Open (Planner Decides)

- **Q-A:** Is the build-script change one plan or two (override-path implementation vs. second-page port)? Likely two waves: (1) build-script + commit fuelhh authored; (2) port system_prices + verify.
- **Q-B:** Should the long-tail strategy decision (success criterion 4) be a third plan, or just a SUMMARY.md note? Likely SUMMARY.md note — the decision is a single sentence ("AI-port the rest" / "Claude-Design the rest" / "leave templated") with no implementation work in this phase.
- **Q-C:** Does the override path need to be CONFIG-driven (so a future per-vendor opt-in is easy), or is the directory existence check sufficient? Likely existence check is sufficient — KISS, and a future config layer can be added if needed without breaking the API.
</questions_answered>

<deferred>
## Deferred to v3 (per PROJECT.md Out of Scope)

- Editorial content fields in vault frontmatter (short_title, editorial_lede, accent_phrase) — would let template approach Claude-Design quality but explicitly out of v2 scope
- Visual regression snapshot testing — v2 skips
- Fuel-pill grid restoration on fuelhh — already a v3 candidate
- Per-dataset related-card blurbs — already a v3 candidate
- Build-script config layer for per-vendor override defaults — only needed if hybrid evolves beyond "directory existence check"
</deferred>
