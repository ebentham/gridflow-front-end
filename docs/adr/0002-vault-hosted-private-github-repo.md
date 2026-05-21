# ADR-0002: Vault hosted as private GitHub repo, no GitHub App auth

Status: accepted (2026-05-19)
Related: ADR-0001 (Phase 7 Reconciliation work requires the Vault to have version control)
Affects: v1 Decision "Vault vendored in-repo at `vault/<vendor>/`, not cross-repo checkout" (the underlying constraint changes but the vendoring pattern is preserved)

## Context

The Vault (Obsidian knowledge base at `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`) has historically been local-only. v1's decision to vendor a snapshot into `gridflow-front-end/vault/<vendor>/` was driven by the fact that CI could not clone the upstream Vault.

ADR-0001's Phase 7 Reconciliation needs the Vault to be version-controlled — every Drift fix produces edits we want to diff, revert, and audit. Three options were considered:

1. **Public GitHub repo** — gives CI direct access; adds a recruiter-visibility surface. Risk: exposes half-finished notes, research directions, and modelling work-in-progress for an energy-trading career move.
2. **Private GitHub repo + GitHub App auth** — gives front-end CI access to the Vault repo via a scoped App; nothing public. Cost: one-time GitHub App setup + secret management in CI workflows.
3. **Private GitHub repo, no App auth** — version control only; cross-repo CI integration not enabled.

## Decision

Adopt **option 3**: create a new private GitHub repo for the Vault (name TBD — default lean `EBentham/quant-vault` matching the local directory name) and push the Vault to it. **No GitHub App auth is configured.**

## Considered Options

- Option 1 (public) — rejected for privacy on a portfolio aimed at energy-trading recruiters; the Site is the credibility surface, the Vault is the working layer.
- Option 2 (private + App auth) — rejected by user preference: *"do we need anything so fancy, let's just make a private repo."* Cross-repo automated drift CI is judged not yet load-bearing for v2.

## Consequences

- The vendoring pattern (`gridflow-front-end/vault/<vendor>/` as a snapshot) is **preserved**. Content phases continue to consume the vendored snapshot, not the upstream Vault directly. The locked v1 vendoring decision is therefore not actually reversed — only its motivating constraint (the Vault not being on GitHub at all) changes.
- Front-end CI **cannot** automatically fetch a fresh drift report from the Vault repo without auth. Drift Verification runs manually (or via a workflow scheduled inside the Vault repo itself, which has access to its own secrets).
- The "Day-7-caught vs Day-21-caught" benefit catalogued in the drift-detection research's worst-case scenario (DRIFT-SURFACES.md § 5) is *not* realized by this ADR — it requires cross-repo CI, which requires App auth.
- Version history of the Vault is now durable and remote-backed. Branching, PR review, and rollback become available for Vault edits.

## Future revisit triggers

Re-open this decision if any of the following becomes true:

- A collaborator joins the project and needs to triage Vault Drift findings from outside the local machine
- Vendor APIs change frequently enough that the manual Verification cadence becomes a burden
- Recruiter visibility of the Vault is judged worth the privacy cost (would flip to public, not to App auth)
- A v2.1+ phase explicitly requires automated cross-repo drift CI as a deliverable
