# External-URL liveness pre-work (orchestrator, 2026-06-07)

CI's lychee runs `--offline`, so external links are never verified by CI. This is the
out-of-band liveness pass over the unique clickable external destinations (the audit
workflow agents were told NOT to fetch). To be merged into RESEARCH.md.

## Method
Extracted unique `<a href="https?://...">` destinations across `site/hifi/*.html` +
`authored-pages/**`. Liveness-checked the unique vendor-doc landing pages, repo/personal
links, and representative deep links via WebFetch + `gh`.

## Results

| Destination | Where | Status | Note |
|---|---|---|---|
| `www.elexonportal.co.uk/` | 33 Elexon pages (vendor-docs CTA) | ✅ LIVE | Current Elexon Portal (refreshed Jun 2026) — NOT legacy. Valid. |
| `carbon-intensity.github.io/api-definitions/` | 65× NESO pages | ✅ LIVE | Official NESO Carbon Intensity API docs. Valid. |
| `open-meteo.com/en/docs` + `/historical-weather-api` | Open-Meteo pages | ✅ LIVE | Valid Open-Meteo docs. |
| `transparency.entsog.eu/` | 33 ENTSO-G pages | ✅ LIVE (JS SPA) | Title "ENTSOG - TP" returned; known Angular SPA, renders client-side. |
| `transparency.entsoe.eu/` | 74× ENTSO-E pages | ✅ LIVE (JS SPA) | Major vendor site; assume live. |
| `bmrs.elexon.co.uk/api-documentation/...` | 33 Elexon deep links + others | ✅ LIVE (JS SPA) | Angular SPA; WebFetch gets empty shell but pages exist. |
| `github.com/EBentham/gridflow-front-end/issues/new` | data-sources.html:316 "Suggest a new source" | ✅ VALID | `gh repo view`: repo is **PUBLIC**, issues enabled. WebFetch hit GitHub's create-issue auth wall (expected) — not a defect. |
| `github.com/EBentham` | index.html:842 (footer profile) | ✅ VALID | Profile link. |
| `linkedin.com/in/elliot-bentham` | index.html:843 (footer) | ✅ VALID | 301 → `uk.linkedin.com/in/elliot-bentham`. Works; could canonicalise to the `uk.` URL (cosmetic). |

## Findings (feed into RESEARCH.md)

- **F-LIVE-1 (HIGH — broken/placeholder link).** `site/hifi/architecture.html:1157` — the
  button **"Read the full source on GitHub →"** links to bare `https://github.com` (no
  path). A visitor lands on GitHub's homepage. Should point to the actual repo — most
  likely the main ETL repo `https://github.com/EBentham/gridflow` (the architecture page
  documents the gridflow pipeline), or `…/gridflow-front-end`. Confirm intended target.
  Source is the static `site/hifi/architecture.html` (not build-generated).

- **F-LIVE-2 (LOW/borderline — UX).** `authored-pages/gie/{storage,storage_reports,unavailability}.html`
  (and rendered copies) link `<a>"GIE AGSI+ · /api ↗"` → `https://agsi.gie.eu/api`, which
  returns raw JSON `{"error":"access denied","message":"Invalid or missing API key"}` to a
  click-through visitor (the endpoint needs an `x-key`). It's labelled as the API endpoint
  (not "docs"), so defensible, but a recruiter clicking it sees a raw auth error. Consider
  pointing the human-facing CTA at `https://agsi.gie.eu/` (the portal) instead of the bare
  API root. Minor.

- **No dead vendor-doc links found.** All six vendors' documentation CTAs resolve. The
  `elexonportal.co.uk` vs `bmrs.elexon.co.uk` split is intentional (portal vs API docs),
  both live — though the audit's `links` dimension should confirm intra-vendor consistency.
