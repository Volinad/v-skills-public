# Claude Code Skills Collection

by [Denis Danilov](https://github.com/volinad) ([X/Twitter](https://x.com/volinad))

A curated set of reusable skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — the CLI-based AI coding assistant by Anthropic. Each skill extends Claude's capabilities with specialized workflows, validation engines, and automation patterns.

## Quick Reference

| Skill | Category | What it does |
|-------|----------|-------------|
| [spec-compiler](#spec-compiler) | Documentation | Validates any documentation set through 18 methods, fixes issues autonomously |
| [doc-compiler](#doc-compiler) | Documentation | Quality engine for non-technical writing with interactive setup |
| [impl-auditor](#impl-auditor) | Documentation | Validates that code matches documentation, reports discrepancies |
| [autoresearch](#autoresearch) | Optimization | Autonomous hypothesis-experiment-analysis loop for any measurable metric |
| [agent-audit](#agent-audit) | Architecture | Audits agent systems against 12 production infrastructure primitives |
| [handoff](#handoff) | Session | Captures session context for seamless continuation or parallel work |
| [youtube-transcript](#youtube-transcript) | Media | Extracts transcripts from YouTube videos in any language |

## Installation

Copy the skill directory you want into your Claude Code skills folder:

```bash
cp -r spec-compiler ~/.claude/skills/
```

The skill is automatically detected and available in your Claude Code sessions. It triggers based on context — for example, saying "validate my docs" activates spec-compiler, and "optimize these parameters" activates autoresearch.

---

## Skills by Category

### Documentation & Quality

Skills that validate, audit, and improve documents and specifications.

#### spec-compiler

Universal documentation validation engine. Takes any set of documents, validates them through 18 methods organized in 5 groups, fixes issues autonomously, and stops when quality converges.

- **18 validation methods** — numbers & cross-validation, consistency & freshness, structure & completeness, execution & traceability, adversarial checks
- **Writer/Auditor separation** — two independent agents: one fixes, one validates. Auditor never sees Writer's process
- **Autonomous multi-pass loop** — continues until 2 consecutive clean Auditor rounds
- **Multi-model rotation** — alternates between models for diverse validation perspectives
- **Works on any docs** — specs, architecture, guides, configs, API docs, agent instructions

**Prerequisites:** Git repository initialized, at least one document to validate.

**A note on cost:** A full compilation (5-7 validation rounds until 2 consecutive clean passes) takes 5-15 minutes and consumes 300k-800k tokens total. That may seem expensive, but this skill is built for spec-driven development — catching inconsistencies and errors in documentation before they become bugs during implementation saves significantly more time and tokens downstream.

#### doc-compiler

Document quality engine for non-technical writing — plans, ideas, proposals, reports, narratives. Same core architecture as spec-compiler but tailored for human-facing documents.

- **14 validation methods** — facts & consistency, structure & completeness, clarity & flow, adversarial checks
- **Interactive setup** — choose edit permissions (editable/read-only per document) and autonomy level (full auto, ask on important, approve everything)
- **Preserves author's voice** — fixes problems without rewriting style
- **Mixed document sets** — some editable, some read-only in the same run

**Prerequisites:** At least one document. Git recommended but not required.

#### impl-auditor

Validates that code matches documentation — bridges the gap between passing tests and spec-compliant implementation. Unlike spec-compiler and doc-compiler, impl-auditor only reports discrepancies without fixing them, because when code and docs disagree it requires human judgment to determine which is correct.

- **17 audit methods** — structural mapping, API contract verification, schema drift detection, ADR compliance, invariant verification, and more
- **Dual-source analysis** — compares documentation against code, not docs against docs
- **Reports only, no auto-fix** — delivers a prioritized report for human decision
- **Framework-aware** — built-in detection patterns for FastAPI, Express, Next.js, SQLAlchemy, React, Prisma, and more

**Prerequisites:** Run after spec-compiler (docs must be clean first) and after tests pass.

---

### Research & Optimization

Skills that automate experimental workflows and iterative improvement.

#### autoresearch

Universal AI-driven research engine. Implements the autonomous hypothesis-experiment-analysis loop for optimizing anything with a measurable metric.

- **Two modes:**
  - **Parameter mode** — generates JSON parameters, runs eval command, parses metric, repeats
  - **Code mode** — edits target files, runs eval, git commits improvements / reverts failures
- **Hypothesis-driven** — every experiment must reference prior evidence, not random exploration
- **Autonomous operation** — runs for hours with configurable stopping conditions (max experiments, max hours, plateau detection)
- **Built-in analysis** — plateau detection, diminishing returns warnings, cross-session learning

**Prerequisites:** Python 3.10+, Git (required for code mode), eval command that outputs metrics to stdout.

**Attribution:** Adapted from [autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy.

---

### Architecture & Infrastructure

Skills for evaluating and planning agent systems and infrastructure.

#### agent-audit

Structured interview that audits agentic AI systems against 12 production infrastructure primitives. Delivers a prioritized gap analysis with tiered verdicts and concrete next steps.

- **12 primitives in 2 tiers:**
  - **Day One (primitives 1-8)** — tool registry, permission model, session persistence, workflow state, token budgeting, streaming, structured logging, verification harness
  - **Week One (primitives 9-12)** — tool pools, context compaction, audit trails, health checks
- **Adaptive depth** — calibrates for solo hobbyist, startup team, or enterprise
- **Actionable output** — top 3 priorities with specific acceptance criteria and scope signals
- **Works at any stage** — from "I'm planning to build" to "we have 500 users in production"

**Attribution:** Based on [Agent Infrastructure Audit](https://promptkit.natebjones.com/20260331_6yc_promptkit_1) by Nate B Jones.

---

### Session Management

Skills for managing context across sessions and parallel work streams.

#### handoff

Creates structured handoff documents that capture session context for the next session or a parallel session. Prevents loss of critical context across long-running projects.

- **Proactive triggering** — suggests itself when context window is getting long, scope is changing, or a side-task emerges
- **Two handoff types:**
  - **Session handoff** — wrap up current work for continuation tomorrow
  - **Branch handoff** — spin off a parallel session for a separate task
- **Auto-pickup** — next session automatically detects unpicked handoffs and continues
- **Structured format** — captures decisions, progress, blockers, next steps, and key files

---

### Media & Content

Skills for extracting and processing media content.

#### youtube-transcript

Extracts subtitles and transcripts from YouTube videos by URL. Works with manual and auto-generated captions in any language. No API keys or subscriptions required.

- **Any language** — supports manual and auto-generated captions
- **Multiple output formats** — plain text, timestamps, SRT, JSON
- **Multiple extraction paths** — bundled Python script (fastest), browser-based extraction, or manual paste fallback
- **Content analysis** — enables summarization, search, and Q&A on video content without watching

## License

[MIT](./LICENSE)
