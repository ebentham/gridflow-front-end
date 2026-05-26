# Phase 8D — Brief Check Log

Records structural check failures and known false positives encountered during brief production.

---

## neso — Check 7 false positive: regex pattern excludes numeric slugs

**Vendor:** neso
**Check:** 7 (per-dataset row count == vault dataset count)
**Result:** FAIL (expected=34, listed=20)
**Cause 1:** `expected` uses `ls *.md | wc -l` = 34, which includes README.md. True dataset count is 33.
**Cause 2:** The RECIPE Check 7 regex `^\| `[a-z_]+` \|` uses `[a-z_]+` which excludes slugs containing digits (e.g. `intensity_fw24h`, `intensity_fw48h`, `intensity_pt24h`, `generation_pt24h`, `regional_intensity_fw24h`, etc.). Manual inspection confirms all 33 dataset rows are present.
**Resolution:** Both causes are known false positives. `vault_dataset_count: 33` (true count). All 33 dataset rows manually verified present. The RECIPE Check 7 regex should use `[a-z0-9_]+` to handle numeric suffixes.
**Status:** Logged — no fix required to brief content.

