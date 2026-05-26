# Vault workflow after Phase 7

**Locked:** 2026-05-19 per ADR-0002 + Phase 7 D-09.

## What changed

Before Phase 7, the upstream Vault at `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/` was a local-only Obsidian directory; the only version-controlled view was the vendored snapshot at `gridflow-front-end/vault/<vendor>/`.

After Phase 7, the upstream Vault is committed to a new **private** GitHub repository: [`EBentham/quant-vault`](https://github.com/EBentham/quant-vault). The vendored snapshot remains the source of truth for `gridflow-build` and `gridflow-front-end` CI (vendoring pattern preserved per `docs/adr/0002-vault-hosted-private-github-repo.md`).

## Editing a Vault file (cross-repo discipline)

For any Vault edit affecting a dataset that's rendered on the site:

1. **Edit upstream first.** Open `C:/Users/.../quant-vault/30-vendors/<vendor>/datasets/<slug>.md`; make the change; commit.
   ```bash
   git -C "C:/Users/.../quant-vault" add 30-vendors/<vendor>/datasets/<slug>.md
   git -C "C:/Users/.../quant-vault" commit -m "fix: <concise description>"
   git -C "C:/Users/.../quant-vault" push origin master
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

These are revisit triggers per `docs/adr/0002-vault-hosted-private-github-repo.md`. Until a trigger fires, drift verification is manual via the steps above.
