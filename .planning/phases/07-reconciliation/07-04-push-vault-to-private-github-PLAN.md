---
id: 07-04-push-vault-to-private-github
phase: 07-reconciliation
plan: 04
type: execute
wave: 2
depends_on:
  - 07-03-fix-open-bucket-and-revendor
files_modified:
  # Upstream Vault (the new repo's initial commit set):
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md"
  # In-repo update (vendoring-workflow documentation):
  - ".planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md"  # docs the new pull/vendor cadence
requirements:
  - RECON-04
autonomous: false   # `gh repo create` and `git push` require GitHub auth — the create step is checkpointed
must_haves:
  truths:
    - "A new private GitHub repository exists at `EBentham/quant-vault` (verified by `gh repo view EBentham/quant-vault --json visibility` reporting `\"visibility\": \"PRIVATE\"`)"
    - "No GitHub App auth is configured for the repo (no `.github/auth/` directory; no installed GitHub App in the repo settings) — per ADR-0002 / D-09"
    - "The reconciled upstream Vault is pushed as the initial commit set (the 5+ fix commits from 07-03 plus the verifier rename + pyproject changes from 07-01 are all in the new repo's history; `git log --oneline | wc -l` >= 6)"
    - "The vendored snapshot in `gridflow-front-end/vault/<vendor>/` continues to be the source of truth for CI (vendoring pattern preserved per ADR-0002)"
    - "The upstream Vault contains no secrets (`.env`, credentials, API keys); secret-scan acceptance check passes before push"
    - "The new repo has a `LICENSE` file (planner decision: MIT, matching `gridflow-front-end` per inertia) and a `README.md` documenting the pull/vendor cadence"
  artifacts:
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore"
      provides: "Excludes `.env`, `*.env`, `**/credentials*`, `**/*secret*`, `**/*key.json` to prevent secret leakage"
      contains: ".env"
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE"
      provides: "MIT license matching gridflow-front-end (planner picks MIT for inertia per <license_decision>)"
      contains: "MIT License"
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md"
      provides: "Documents that this is the upstream Vault; vendored snapshot in `gridflow-front-end/vault/<vendor>/` is the consumer; ADR-0002 link"
      contains: "vendored snapshot"
    - path: ".planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md"
      provides: "In-repo docs of the new pull/vendor cadence: edit upstream → cp to vendored → commit"
      contains: "EBentham/quant-vault"
  key_links:
    - from: "Upstream Vault at `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/`"
      to: "GitHub repo `EBentham/quant-vault` (private)"
      via: "`gh repo create EBentham/quant-vault --private --source=. --remote=origin --push`"
      pattern: "gh repo view EBentham/quant-vault --json visibility"
    - from: "Future Vault edits"
      to: "Vendored snapshot in `gridflow-front-end/vault/<vendor>/`"
      via: "`cp` per-file (vendoring pattern preserved per ADR-0002; v1 used manual copy)"
      pattern: "07-04-VAULT-WORKFLOW.md"
---

<objective>
Create a new private GitHub repository at `EBentham/quant-vault` (D-09 — no GitHub App auth) and push the reconciled upstream Vault as the initial commit set. Add a `LICENSE` file (planner decision: MIT) and a `README.md` documenting the Vault's role and the vendoring workflow. Document the cross-repo workflow in this repo's `.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md`. Confirm the vendoring pattern is preserved (gridflow-front-end CI continues to consume `vault/<vendor>/` snapshots, not the upstream directly — per ADR-0002).

Purpose: deliver the version-controlled upstream Vault that future Phase 9 / Phase 10 / future Reconciliation work depends on; close the v2 milestone's "Vault has version control" prerequisite. RECON-04 from REQUIREMENTS.md is the single acceptance gate.

Output: A new private GitHub repo at `EBentham/quant-vault` with the reconciled Vault as initial commits; LICENSE + README + .gitignore in the upstream Vault; an in-repo workflow document; no GitHub Actions workflows added (cross-repo automated drift CI is explicitly deferred per ADR-0002).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/07-reconciliation/07-CONTEXT.md
@.planning/phases/07-reconciliation/07-01-SUMMARY.md
@.planning/phases/07-reconciliation/07-02-SUMMARY.md
@.planning/phases/07-reconciliation/07-03-SUMMARY.md
@docs/adr/0002-vault-hosted-private-github-repo.md

<license_decision>
**Planner decision: MIT.** Rationale:
- Matches `gridflow-front-end/LICENSE` (also MIT per v1 HON-04) — inertia.
- The Vault contains derivative documentation of public data sources (Elexon, ENTSO-E, etc.); restrictive licenses (CC-BY-NC, GPL) add cost without adding clarity for a docs-heavy private repo.
- The repo is private (D-09); the license matters less for discovery than for any future open-source pivot. Picking MIT now preserves an easy public flip if `EBentham/quant-vault` is ever opened up.

Counter-considered: CC-BY-4.0 (docs-heavy, well-known for documentation projects). Rejected because the Vault is .md files used by a Python build script, not purely human-readable documentation — MIT covers both code-y and docs-y artefacts identically and matches the rest of the ecosystem.
</license_decision>

<gitignore_specification>
The Vault directory may currently have ZERO `.gitignore`. If it does, scan it for the patterns below and ADD only what's missing. If no `.gitignore` exists, create one with:

```gitignore
# Secrets — never commit
.env
*.env
**/credentials*
**/*secret*
**/*key.json
*.pem
*.key

# Obsidian workspace files (per-user state, not content)
.obsidian/workspace.json
.obsidian/workspaces.json
.obsidian/hotkeys.json
.trash/

# Editor / OS noise
.DS_Store
Thumbs.db
*.swp
*~

# Python (the verifier script is here)
__pycache__/
*.py[cod]
.venv/
.python-version

# Drift-check temporary outputs (the verifier writes vault-curl-schema-validation.{md,json}
# in-place; Q-DD-17 default lean keeps them committed as historical record — DO NOT
# add them to .gitignore)
```

Note the comment block at the bottom: per Q-DD-17 default lean from drift research, the verifier reports STAY committed in the Vault as historical record. Do not add them to `.gitignore`.
</gitignore_specification>

<readme_specification>
The upstream Vault's `README.md` should explain WHAT it is (Obsidian knowledge base, Canonical-derivative), WHO consumes it (the `gridflow-front-end` repo via the vendored snapshot at `vault/<vendor>/`), and HOW the workflow operates (edit upstream → cp to vendored → both commit). It links to ADR-0002 for the rationale.

Template:
```markdown
# quant-vault

Private Obsidian knowledge base for the gridflow ecosystem. Per-vendor documentation of data sources, schemas, sample responses, and provenance.

## What this repo is

A **derivative documentation layer** authored from canonical inputs (the `gridflow` Pydantic schemas + live vendor APIs). See:
- [`30-vendors/<vendor>/datasets/<slug>.md`](./30-vendors/) — one file per dataset, ~163 across 6 Vendors (Elexon · ENTSO-E · ENTSO-G · GIE · NESO · Open-Meteo).
- [`30-vendors/scripts/gridflow_drift_check.py`](./30-vendors/scripts/gridflow_drift_check.py) — the verifier that runs against this Vault and produces `vault-curl-schema-validation.{md,json}`.

This Vault **never** overrides the canonical (`gridflow` Pydantic schemas + live API responses); when they disagree, the Vault is wrong. See the project's vocabulary glossary at `gridflow-front-end/CONTEXT.md`.

## Who consumes it

The `gridflow-front-end` static-site generator at `https://github.com/EBentham/gridflow-front-end` consumes a **vendored snapshot** of this Vault. Snapshot path: `gridflow-front-end/vault/<vendor>/`. The vendoring pattern was preserved in v2 per ADR-0002 (in `gridflow-front-end/docs/adr/0002-vault-hosted-private-github-repo.md`) — content phases in the front-end repo read from the snapshot, not from this upstream repo directly.

## Workflow

Editing a Vault dataset is a two-step process:

1. **Edit the file here** (`30-vendors/<vendor>/datasets/<slug>.md`). Commit using Conventional Commits, one concern per commit.
2. **Re-vendor the file** into `gridflow-front-end/vault/<vendor>/<slug>.md` via `cp`. Commit on the front-end side with a separate Conventional Commit.

This split is deliberate per ADR-0002: it keeps the upstream Vault as the source-of-truth-by-version-control while preserving the v1 vendoring pattern that the front-end build pipeline already expects.

## Drift verification

Run `gridflow-drift-check` (installed via `gridflow-front-end`'s `[drift]` extras — `uv pip install -e ".[drift]"` from a checkout of `gridflow-front-end`) from inside this repo's `30-vendors/` directory. The script compares:
- Vault schema tables ↔ canonical Pydantic classes in `gridflow/src/gridflow/schemas/`
- Vault curl examples ↔ live vendor API responses

Outputs `vault-curl-schema-validation.{md,json}` to the same directory. These reports are kept committed (per Q-DD-17 default lean in `gridflow-front-end/.planning/research/post-v1/drift-detection/`).

## License

MIT — see [LICENSE](./LICENSE). Matches `gridflow-front-end` for ecosystem consistency.

## Privacy

Currently a private repository (per ADR-0002). The privacy choice is preserves modelling work-in-progress off the recruiter-visible surface. Re-visit triggers in ADR-0002.
```

This README is committed AS-IS during 07-04 Task 2. Do not add a "How to contribute" section, do not add badges, do not link to GitHub Actions (none exist — ADR-0002 defers cross-repo drift CI).
</readme_specification>

<vault_workflow_doc>
`.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` lives in `gridflow-front-end` (this repo). It's the in-repo audit trail of the new workflow, sibling to other Phase 7 artefacts. Required content:

```markdown
# Vault workflow after Phase 7

**Locked:** 2026-05-19 per ADR-0002 + Phase 7 D-09.

## What changed

Before Phase 7, the upstream Vault at `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/` was a local-only Obsidian directory; the only version-controlled view was the vendored snapshot at `gridflow-front-end/vault/<vendor>/`.

After Phase 7, the upstream Vault is committed to a new **private** GitHub repository: [`EBentham/quant-vault`](https://github.com/EBentham/quant-vault). The vendored snapshot remains the source of truth for `gridflow-build` and `gridflow-front-end` CI (vendoring pattern preserved per ADR-0002).

## Editing a Vault file (cross-repo discipline)

For any Vault edit affecting a dataset that's rendered on the site:

1. **Edit upstream first.** Open `C:/Users/.../quant-vault/30-vendors/<vendor>/datasets/<slug>.md`; make the change; commit.
   ```bash
   git -C "C:/Users/.../quant-vault" add 30-vendors/<vendor>/datasets/<slug>.md
   git -C "C:/Users/.../quant-vault" commit -m "fix: <concise description>"
   git -C "C:/Users/.../quant-vault" push origin main
   ```

2. **Re-vendor into the front-end.** Copy the file into `gridflow-front-end/vault/<vendor>/<slug>.md`; commit and PR on the front-end side.
   ```bash
   cp "C:/Users/.../quant-vault/30-vendors/<vendor>/datasets/<slug>.md" \
      "C:/Users/.../gridflow-front-end/vault/<vendor>/<slug>.md"
   git -C "C:/Users/.../gridflow-front-end" add vault/<vendor>/<slug>.md
   git -C "C:/Users/.../gridflow-front-end" commit -m "feat: re-vendor <slug> after upstream fix"
   ```

3. **Verify byte-equivalence** before pushing the front-end commit:
   ```bash
   diff -q "vault/<vendor>/<slug>.md" \
           "C:/Users/.../quant-vault/30-vendors/<vendor>/datasets/<slug>.md"
   # Expected: silent (byte-equivalent)
   ```

## Verifying drift

From a `gridflow-front-end` checkout with `[drift]` extras installed:

```bash
uv pip install -e ".[drift]"
GRIDFLOW_DRIFT_CHECK_SCRIPT="C:/Users/.../quant-vault/30-vendors/scripts/gridflow_drift_check.py" \
  gridflow-drift-check
```

The verifier writes `vault-curl-schema-validation.{md,json}` to the upstream Vault directory. Commit those alongside the dataset edit if they materially differ from the previous run.

## What's NOT in scope

Per ADR-0002, the following are explicitly NOT v2 deliverables:

- GitHub App auth for cross-repo access
- Automated drift-check CI runs from `gridflow-front-end` against `EBentham/quant-vault`
- A GitHub Actions workflow inside `EBentham/quant-vault` that schedules drift-checks

These are revisit triggers per ADR-0002's "Future revisit triggers" section. Until a trigger fires, drift verification is manual via the steps above.
```
</vault_workflow_doc>

<secret_scan_specification>
Before pushing the upstream Vault to GitHub, scan for committed secrets. The Vault is currently local-only, so it may contain a stray `.env`, a `notes.md` with a pasted API key, etc.

Required checks:

```bash
# Find any .env files:
find "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" -name '.env' -o -name '*.env' -o -name '*credentials*' -o -name '*secret*' -o -name '*key.json' 2>/dev/null | grep -v node_modules
# Expected: empty

# Find any pasted-key shapes inside .md / .txt files:
grep -rnE '[A-Z_]+_API_KEY\\s*=\\s*[A-Za-z0-9-]{20,}|securityToken=[A-Za-z0-9-]{20,}' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" --include='*.md' --include='*.txt' --include='*.yaml' --include='*.yml'
# Expected: empty

# Find any obvious PAT shapes (ghp_, gho_, ghu_, ghs_, ghr_):
grep -rnE 'gh[opusr]_[A-Za-z0-9]{36}' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault"
# Expected: empty
```

If ANY of these return hits: STOP, surface the finding, scrub the secret (re-encrypt or move to a `.env` outside the repo + add to `.gitignore`), and re-scan before proceeding. Do NOT push secrets to GitHub even if the repo is private — GitHub's secret-scanning may surface them via partner alerts; rotation cost > the time to clean up before push.
</secret_scan_specification>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Prepare the upstream Vault for first push — `.gitignore`, `LICENSE`, `README.md`; run secret-scan</name>
  <files>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md
  </files>
  <read_first>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/ (full directory listing — what's already at the root? An existing README? A workspace file?)
    - test -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.git/HEAD (is the upstream Vault already a git repo? — 07-03 may have `git init`'d it for the 5 fix commits)
    - LICENSE (gridflow-front-end repo's MIT license — copy the text exactly, just change the year/holder if needed)
    - docs/adr/0002-vault-hosted-private-github-repo.md (the rationale this README/.gitignore implements)
  </read_first>
  <action>
    **Step 1 — Confirm git state of the upstream Vault.**
    ```bash
    cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault"
    test -d .git && git status || git init
    # 07-03 may have already initialised git for the 5 fix commits; if not, init now.
    # If git init was just run, also configure git user (use the same identity as gridflow-front-end):
    git config user.name "EBentham"
    git config user.email "$(git -C 'C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end' config user.email)"
    ```

    **Step 2 — Write `.gitignore`.** Use the content from `<gitignore_specification>` in the context block above. If a `.gitignore` already exists (e.g. an Obsidian-default), merge: don't remove existing entries; add the secret-exclusion block at the top with a `# Secrets — never commit` header.

    **Step 3 — Write `LICENSE`.** Copy the existing `gridflow-front-end/LICENSE` text exactly to `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE`. The MIT license text is short and standard; do not modify beyond updating the copyright year to `2026` if the source LICENSE has an older year.

    Confirm via `head -5 C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE` returns:
    ```
    MIT License

    Copyright (c) 2026 EBentham

    Permission is hereby granted...
    ```

    **Step 4 — Write `README.md`.** Use the content from `<readme_specification>` in the context block. This is the new repo's first impression to the user when they revisit and to GitHub's preview pane. Do NOT add badges, do NOT link to GitHub Actions (none exist), do NOT add hyperlinks to URLs that don't yet exist.

    **Step 5 — Run the secret scan.** Use the three commands from `<secret_scan_specification>` in the context block. If ANY of them surface a match: STOP, write a blocker note, scrub the secret, re-run. Do not skip this step.

    The scan covers the entire Vault root, not just files this plan modifies. The Vault has been local-only for some time; the cost of one extra grep pass before first push is trivial vs the cost of leaked credentials.

    **Step 6 — Commit.**
    Conventional Commits in the upstream Vault repo:
    - `chore: add .gitignore covering secrets and editor noise`
    - `chore: add MIT LICENSE matching gridflow-front-end`
    - `docs: add README documenting Vault role and vendoring workflow`

    Three separate commits; one concern per commit per CLAUDE.md.
  </action>
  <verify>
    <automated>cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" && test -f .gitignore && test -f LICENSE && test -f README.md && head -1 LICENSE | grep -c 'MIT License' && grep -c 'EBentham/quant-vault' README.md && grep -c '.env' .gitignore && find . -name '.env' -not -path './.git/*' | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - `test -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore` succeeds.
    - `test -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE` succeeds; `head -1` returns `MIT License`; `grep -c 'EBentham' LICENSE` returns >= 1.
    - `test -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md` succeeds; `grep -c 'EBentham/quant-vault' README.md` returns >= 1; `grep -c 'vendored snapshot' README.md` returns >= 1; `grep -c 'ADR-0002' README.md` returns >= 1.
    - `grep -c '\\.env' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore` returns >= 1.
    - `find "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" -name '.env' -not -path '*/.git/*' -not -path '*/.venv/*' 2>/dev/null | wc -l` returns 0 (no committable .env in the tree) OR every match appears in `.gitignore`.
    - `grep -rnE 'gh[opusr]_[A-Za-z0-9]{36}' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" 2>/dev/null` returns zero hits.
    - `grep -rnE '[A-Z_]+_API_KEY\\s*=\\s*[A-Za-z0-9-]{20,}' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" --include='*.md' --include='*.txt' --include='*.yaml' --include='*.yml' 2>/dev/null` returns zero hits (or every hit is inside a `.gitignore`d directory like `.venv/`).
    - `git -C "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" log --oneline | wc -l` returns >= 8 (5 from 07-03 + 3 new ones for .gitignore + LICENSE + README).
  </acceptance_criteria>
  <done>
    `.gitignore`, `LICENSE`, and `README.md` exist in the upstream Vault root with the correct content; secret-scan passes (no `.env` outside `.gitignore`, no PAT shapes, no API_KEY assignments). The Vault is ready for `gh repo create`.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2 (CHECKPOINT — `gh auth status` required): Create the private GitHub repo `EBentham/quant-vault` and push</name>
  <what-built>
    Tasks 1 prepared the upstream Vault with `.gitignore` + `LICENSE` + `README.md` and ran the secret-scan. Now the repo needs to be created on GitHub via `gh repo create` and the local commits pushed. This step requires the user to be authenticated with the GitHub CLI; if not, Claude will see auth errors and the user provides credentials.
  </what-built>
  <how-to-verify>
    **Step 1 — Confirm GitHub CLI is authenticated:**
    ```bash
    gh auth status
    ```
    Expected: shows `Logged in to github.com as EBentham`. If shown as a different identity, or if not logged in, run `gh auth login` interactively and select GitHub.com → HTTPS → paste a token (or browser-based auth) before proceeding.

    **Step 2 — Create the private repo and push:**
    ```bash
    cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault"
    gh repo create EBentham/quant-vault --private --source=. --remote=origin --push
    ```

    Key flags:
    - `--private` — REQUIRED per D-09 / ADR-0002. Do NOT use `--public`. Do NOT use `--internal` (organisation feature; doesn't apply here).
    - `--source=.` — uses the current directory as the source.
    - `--remote=origin` — names the new remote `origin`.
    - `--push` — pushes after creation.
    - NO `--app-id` / no GitHub App configuration. ADR-0002 explicitly rejects this; D-09 confirms.

    **Step 3 — Verify privacy:**
    ```bash
    gh repo view EBentham/quant-vault --json visibility,isPrivate,hasIssuesEnabled
    ```
    Expected JSON output: `"visibility": "PRIVATE"`, `"isPrivate": true`. `hasIssuesEnabled` is whatever GitHub defaults to (probably `true`); D-08 says we don't use GitHub Issues, but the toggle being `true` doesn't violate anything — it's just unused.

    **Step 4 — Confirm push succeeded:**
    ```bash
    gh repo view EBentham/quant-vault --json defaultBranchRef
    git -C "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" log origin/main --oneline | head -10
    ```
    Expected: `defaultBranchRef.name` is `main` (gh repo create's default); the commits from 07-03 + Task 1 of this plan are visible.

    **Step 5 — Sanity-check the GitHub web view (browser):**
    Open `https://github.com/EBentham/quant-vault` in a browser. Confirm:
    - The repo shows the "🔒 Private" badge in the top-left.
    - The README renders (the file from Task 1).
    - The commit history shows the 8+ commits in order.
    - The `30-vendors/` directory is browsable.
    - There is NO `.github/workflows/` directory (no CI YAML; per D-09 / ADR-0002 cross-repo automated drift CI is out of scope).

    **Sign off with:**
    - "approved" — repo is private, push succeeded, browser sanity-check confirms no leaked content.
    - "blocked: <description>" — describe the issue. The most likely blockers: `gh auth status` shows wrong identity (resolve: `gh auth switch` or `gh auth login`); push fails on a large `.obsidian/workspace.json` (resolve: add to `.gitignore`, recommit, push again); `gh repo create` errors because the repo already exists (resolve: skip create, just `git remote add origin git@github.com:EBentham/quant-vault.git && git push -u origin main`).
  </how-to-verify>
  <resume-signal>Type "approved" or describe the blocker.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: Document the new cross-repo workflow in `gridflow-front-end/.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md`</name>
  <files>
    - .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md
  </files>
  <read_first>
    - docs/adr/0002-vault-hosted-private-github-repo.md (the rationale this workflow doc implements)
    - .planning/phases/07-reconciliation/07-03-fix-open-bucket-and-revendor-PLAN.md (the re-vendor mechanism description — preserves the same pattern)
  </read_first>
  <action>
    Write `.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` using the template in `<vault_workflow_doc>` in the context block above. This is a self-contained reference doc in the front-end repo's planning state; it sits alongside the other Phase 7 artefacts.

    Do not duplicate ADR-0002's content (that ADR exists at `docs/adr/0002-vault-hosted-private-github-repo.md`); link to it. The workflow doc is the operational how-to; ADR-0002 is the why.

    The doc must contain these literal substrings (acceptance grep targets them):
    - `EBentham/quant-vault`
    - `vendored snapshot`
    - `ADR-0002`
    - `diff -q`
    - `gridflow-drift-check`

    Conventional Commit message: `docs(07-04): document upstream-Vault-to-vendored-snapshot workflow`
  </action>
  <verify>
    <automated>test -f .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && grep -c 'EBentham/quant-vault' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && grep -c 'vendored snapshot' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && grep -c 'ADR-0002' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && grep -c 'diff -q' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && grep -c 'gridflow-drift-check' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md && echo "OK all-substrings-present"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` exits 0
    - `grep -c 'EBentham/quant-vault' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - `grep -c 'vendored snapshot' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - `grep -c 'ADR-0002' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - `grep -c 'diff -q' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - `grep -c 'gridflow-drift-check' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - The file does NOT duplicate ADR-0002's content — it links to it via a relative-path reference (`docs/adr/0002-vault-hosted-private-github-repo.md`) rather than restating the decision rationale; `grep -c 'docs/adr/0002-vault-hosted-private-github-repo.md\|/docs/adr/0002-' .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` returns >= 1
    - `markdownlint --disable MD013 .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` exits 0 (or — if markdownlint is not installed locally — the file parses cleanly under `python -c "import pathlib; pathlib.Path('.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md').read_text(encoding='utf-8')"`)
  </acceptance_criteria>
  <done>
    Task 3 is done when: the workflow doc exists at the specified path, all 6 required literal substrings are present (each `grep -c` returns >= 1), the doc links to ADR-0002 rather than restating it, and the file parses cleanly. The doc is the operational how-to that future Phase 7-style work (when re-running drift-check, when re-vendoring) will read; ADR-0002 stays the canonical "why".
  </done>
</task>

</tasks>

<threat_model>

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Local working tree → GitHub remote (`origin`) | `git push` crosses this boundary; everything in the push set becomes part of the new private repo's history |
| Upstream Vault filesystem → secret-scan find | The scan must catch `.env`, credentials, API keys, `*key.json` files BEFORE push (post-push remediation requires `git filter-repo` which is expensive) |
| GitHub repo settings → user identity | `gh repo create --private` is scoped to the authenticated `gh` user; an accidentally-authenticated wrong identity creates the repo under the wrong account |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-07-04-01 | I (Information disclosure) | `git push` of upstream Vault | mitigate | Task 1 includes a secret-scan acceptance check (`find` for `.env*`, `*credentials*`, `*secret*`, `*key.json`; any matches must be in `.gitignore` before push). Task 2 includes a browser sanity-check confirming no leaked content. |
| T-07-04-02 | I (Information disclosure) | Accidental public-repo creation | mitigate | `gh repo create --private` flag is explicit (not derived from default). Acceptance check (`gh repo view EBentham/quant-vault --json visibility`) must report `"visibility": "PRIVATE"` post-create. Browser sanity-check at Task 2 visually confirms the 🔒 Private badge. |
| T-07-04-03 | E (Elevation of privilege) | `gh auth status` wrong identity | mitigate | Task 2 is a `checkpoint:human-action` (autonomous: false) — the user actively confirms `gh auth status` identity before push. The plan's `autonomous: false` frontmatter flag also surfaces this as a manual-intervention point in `/gsd-execute-phase`. |
| T-07-04-04 | T (Tampering) | Vendored snapshot drifts from upstream | accept (covered by 07-03) | The vendored snapshot in `gridflow-front-end/vault/<vendor>/` is the consumer; the upstream Vault is the source. 07-03 already verified byte-equivalence via `diff -q`. 07-04 does not modify the snapshot; only documents the cadence in the new workflow doc. Drift detection between upstream and vendored is a v2.1+ concern per ADR-0002. |
| T-07-04-05 | R (Repudiation) | Vault commit authorship | accept | Vault commits use the local `git config user.email` — same as `gridflow-front-end`. Repudiation isn't load-bearing for a docs repo on a personal-portfolio scale. |

</threat_model>

<verification>

Plan-level acceptance — re-run after all 3 tasks land:

```bash
# 1. Repo exists, is private, has no GitHub App installed:
gh repo view EBentham/quant-vault --json visibility,name | grep -E '"visibility":\s*"PRIVATE"'
# Expect: 1 match

gh api /repos/EBentham/quant-vault/installations 2>/dev/null | grep -c '"total_count": 0'
# Expect: 1 (no GitHub App installed — ADR-0002 / D-09)

# 2. The 3 vault meta-files (.gitignore, LICENSE, README.md) exist upstream and are committed:
test -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore"
test -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE"
test -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md"

# 3. .gitignore contains the secret-leak guard entries:
grep -E '^\.env$|^\*\.env$|credentials|secret|key\.json' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.gitignore" | wc -l
# Expect: >= 3

# 4. LICENSE present (MIT default per planner decision — inertia from gridflow-front-end):
grep -c 'MIT License\|Apache License\|Creative Commons' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/LICENSE"
# Expect: 1

# 5. README.md documents the upstream-vs-vendored relationship:
grep -c 'gridflow-front-end\|vendored\|snapshot' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/README.md"
# Expect: >= 1

# 6. Push succeeded — initial commit set on `main` includes the 07-01 + 07-03 changes:
cd C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault && git log --oneline | wc -l
# Expect: >= 6 (renamed verifier from 07-01 + Vault edits from 07-03 + the 3 meta files from this plan = at least 6 commits)

# 7. Secret-scan passes pre-push (re-run as a smoke check):
find C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault -type f \( -name '.env' -o -name '*.env' -o -name '*credentials*' -o -name '*secret*' -o -name '*key.json' \) -not -path '*/.git/*' -not -path '*/node_modules/*' | tee /tmp/secret-scan-hits.txt
# Expect: all listed files are matched by .gitignore patterns (cross-check with `git check-ignore`)
xargs -a /tmp/secret-scan-hits.txt -I {} git -C C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault check-ignore {} 2>/dev/null | wc -l
# Expect: equal to `wc -l < /tmp/secret-scan-hits.txt` (every hit is gitignored)

# 8. NO drift-check workflow added (cross-repo automated CI explicitly deferred per ADR-0002):
test ! -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/.github/workflows/drift-check.yml"

# 9. The workflow doc exists with all 6 required literal substrings:
test -f .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md
for needle in 'EBentham/quant-vault' 'vendored snapshot' 'ADR-0002' 'diff -q' 'gridflow-drift-check' 'docs/adr/0002'; do
  grep -c "$needle" .planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md
done
# Expect: each grep returns >= 1

# 10. Vendoring pattern preserved — the gridflow-front-end/vault/<vendor>/ snapshot still exists and matches upstream byte-equivalently (smoke-check on one file):
diff -q C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md \
        C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end/vault/elexon/fuelhh.md
# Expect: no output (files identical)
```

</verification>

<success_criteria>

RECON-04 from REQUIREMENTS.md is satisfied:
- New private GitHub repository `EBentham/quant-vault` exists (verified by `gh repo view --json visibility` → `"PRIVATE"`)
- No GitHub App auth configured (verified by `gh api /repos/EBentham/quant-vault/installations` → `"total_count": 0`)
- The reconciled upstream Vault is pushed as the initial commit set (renamed verifier from 07-01 + Vault edits from 07-03 + meta-files from this plan, all present in `git log`)
- The vendoring pattern is preserved — `gridflow-front-end/vault/<vendor>/` remains the snapshot the build consumes, byte-equivalent to upstream after 07-03's re-vendor
- The upstream Vault contains no secrets — `.env`/credentials/key files are either absent or gitignored before push
- `LICENSE` (MIT) and `README.md` exist; the README documents the upstream-vs-vendored relationship
- A new operational workflow doc lives at `.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md` with the 6 required literal substrings, linking (not restating) ADR-0002

</success_criteria>

<output>

After all 3 tasks complete, create `.planning/phases/07-reconciliation/07-04-SUMMARY.md` per the standard summary template. Capture:

- **Repo identity** — final URL of the new repo (`https://github.com/EBentham/quant-vault`); the SHA of the initial commit on `main`; the SHA of the final push commit; the count of commits in the initial push set.
- **License choice** — confirm MIT was selected (or note the deviation and why); paste the LICENSE header.
- **`.gitignore` final content** — paste the file (it should be short — ~10 lines of secret-leak guards plus any `.obsidian/`-style Obsidian-internal files the planner decided to ignore).
- **README.md final content** — paste the file (or a high-level summary if long).
- **Secret-scan result** — paste `find` output and `git check-ignore` cross-check output; confirm zero unguarded secrets crossed the push boundary.
- **Browser sanity-check result** — confirm Task 2's "approved" sign-off was received; note any blockers encountered and how they were resolved.
- **Workflow-doc commit hash** — the Conventional Commit hash for the `docs(07-04): document upstream-Vault-to-vendored-snapshot workflow` commit.
- **What stays manual** — call out that the drift-check itself remains a manual cadence (run `gridflow-drift-check` from a local shell; copy report files into `quant-vault/30-vendors/`; re-vendor as needed). Cross-repo automated drift CI is explicitly v2.1+ per ADR-0002.

</output>