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

*Procedures will be added here as experience accumulates from audit runs. Each procedure will include:*
- *Step-by-step execution instructions*
- *Framework-specific variations*
- *Known false-positive patterns to exclude*
- *Thresholds and heuristics*

---

## Known False-Positive Patterns

*Will be populated as patterns emerge from real audits. Expected categories:*
- *Generated code flagged as orphan (Alembic stubs, OpenAPI clients)*
- *Test utilities flagged as undocumented features*
- *Framework boilerplate flagged as convention violations*
- *Re-exported types flagged as drift*
