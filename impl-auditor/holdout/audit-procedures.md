# Audit Procedures — Holdout File

This file is accessible to the Auditor agent. It contains concrete execution procedures for each of the 17 audit methods. Procedures are developed incrementally as experience accumulates from real audit runs.

## Principle

These procedures are analogous to spec-compiler's validation-scenarios.md. They provide the Auditor with specific, tested steps for each method — going beyond the summary-level descriptions in SKILL.md.

---

## Framework-Specific Lookup Tables

### FastAPI + SQLAlchemy
- **Routes:** grep for `@router.get`, `@router.post`, `@router.put`, `@router.delete`, `@router.patch` in `routers/` directory and any file containing `@app.`
- **Models:** grep for `class.*Base.*:` or `class.*Model.*:` in `models/` directory
- **Migrations:** check `alembic/versions/` for migration files; read `op.create_table`, `op.add_column`, etc.
- **Env vars:** grep for `os.environ`, `os.getenv`, `settings.` in all Python files
- **Tests:** check `tests/` directory, match `test_*.py` files

### Next.js + React
- **Routes:** scan `pages/` or `app/` directory structure
- **API routes:** check `pages/api/` or `app/api/` directories
- **Components:** scan `components/` directory
- **Env vars:** grep for `process.env.` in all JS/TS files
- **Tests:** check for `*.test.ts`, `*.test.tsx`, `*.spec.ts` files

### Express
- **Routes:** grep for `router.get`, `router.post`, `app.get`, `app.post` patterns
- **Middleware:** grep for `app.use(` patterns
- **Env vars:** grep for `process.env.` in all JS files

---

## Method Procedures

### IA-17 — Invariant verification by live execution at the DIVERGENT input

**When to apply.** Any behavior-critical invariant where a static read cannot prove the runtime truth: exemptions, deadlines enforced across retries, state-machine guards, statistical aggregation / normalize math, and rounding / binning / quantization conventions. The tell: the code reads correct, but a *subtly-wrong* variant (round instead of floor, `<` instead of `<=`, mean-before-normalize instead of normalize-before-mean) would read equally correct.

**Steps.**
1. **State the invariant as two rival implementations** — the documented one and the most plausible wrong one (floor vs round; deadline admits 1 retry vs 3; NaN skipped vs propagated).
2. **Find the DIVERGENT input** — the value(s) at which the two rivals produce DIFFERENT outputs. This is the crux: an input where floor and round disagree distinguishes them; one where they agree proves nothing.
3. **Drive the actual code path** with that input via a small in-process snippet (import the real function — do NOT re-implement the logic in the snippet, that only tests your copy).
4. **Assert the observed output equals the documented rival, not the wrong one.** Record the concrete input→output pair in the report.
5. If the code can't run in isolation, fall back to a static read but DOWNGRADE confidence and say so; note the un-exercised divergent input as a residual risk.

**Pitfall guards.**
- Testing at a non-divergent input and declaring the invariant "verified by execution" is a *false* confirmation — worse than a static read because it looks rigorous. Always pick the divergent input.
- Re-implementing the math inside the snippet instead of importing the code tests the snippet, not the code.

**Provenance bonus.** If the invariant traces to an upstream spec/contract correction (a "Re: …" clause, possibly implemented in a different session), treat it as a first-class hypothesis and prefer the divergent-input probe there — a cross-session hand-off is exactly where a correction is most likely to have mis-landed.

---

## Known False-Positive Patterns

### FP-1 — Base-vs-wrapper function-name mismatch (doc names the base fn, code calls a wrapper of it)
- **Symptom:** The doc names a base function/symbol, but the code calls a thin wrapper of it (or vice versa) — common when the code and doc were co-authored in one pass, where the residual drift is almost always prose-vs-symbol naming, not a contract divergence.
- **Guard:** Verify the wrapper genuinely delegates to the named base before flagging. If it does, this is at most a minor doc-precision nit (recommend aligning the name), NOT a drift/conformance finding.

### FP-2 — "Poll-tail has no dedicated test" is an observation, not a blocker (when cross-checked)
- **Symptom:** A "fetch-full-once + poll-tail" (or windowed-incremental) feature has tests for the full path but none for the incremental live-edge tail.
- **Guard:** The missing tail test is a recurring **observation** (recommend a `tail == full at settled columns` regression test), not a critical/major finding — **provided** the audit confirmed the tail behaves via an in-process cross-check (run the tail, compare to the full series at settled columns). Escalate only if no live cross-check was possible AND the tail logic is non-trivial (stateful / cumsum-seeded), leaving the harder code wholly unverified.

### FP-3 — "The other half of a split feature is missing" is an expected observation, not a critical
- **Symptom:** The audited diff is one track of a deliberately-split feature (backend-DATA vs frontend-RENDER, producer vs consumer, library vs caller), and the audit notices the other track doesn't exist / isn't wired.
- **Guard:** Before flagging "feature missing" as **critical**, confirm whether the absent half is **this commit's job** or a **separate, deliberately-deferred track**. If the spec/handoff splits the work, audit the present half against ITS contract (the interface the other half will consume) and classify the absent half as an **observation**. Auditing the present half against the WHOLE feature's ACs manufactures a false critical.
- **Escalate only if:** the split is NOT by design (no doc defers the other half) and the feature is claimed complete, OR the present half's contract is itself incompatible with what the other half needs.
