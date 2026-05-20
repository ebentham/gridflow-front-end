# Phase 8C-01 — BRIEF-LOG.md

Append-only failure log. One entry per brief that fails structural checks.

Format per entry:

```
## <slug> · <timestamp UTC>

Failed checks:
- check N: <reason>
- check M: <reason>

One-line reason: <summary>
```

---
