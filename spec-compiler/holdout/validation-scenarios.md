# Holdout Validation Scenarios

This file is accessible ONLY to Auditor Agent. Writer Agent MUST NOT see it.

## Principle

Holdout scenarios are analogous to holdout sets in ML — with one clarification: nothing here protects model parameters (an LLM Writer has none to overfit). What is protected is the measurement. If the fixing agent knew which specific checks run and how they detect, a "clean" round would only prove that the published detectors pass (Goodhart's law), and effort would flow to the probed paths only (coverage gaming). Writing conventions themselves are NOT secret — Writer receives them openly in SKILL.md. What stays hidden is this probe set: which scenarios run, their procedures, and the trap catalog. See SKILL.md "Why Holdout".

---

## Scenario 1: Number Integrity

For every number in documentation (feature count, tables, endpoints, tests, env vars):
1. Find all places where this number is mentioned
2. Recount from source of truth (JSON files, source code, configs)
3. Do all occurrences match?

**Typical traps:**
- Summary says "23 features" but counting JSON entries yields 24
- Architecture section "Inventory: 7 tables" — actually 6
- "12 modules" — 12 of what? Sections? Routers? Files?

After Writer adds/removes items — recount independently (don't trust Writer's numbers).

## Scenario 2: Password/Secret Consistency

Collect all mentions of passwords, keys, credentials:
- .env / .env.example
- docker-compose.yml
- init.sh / setup scripts
- CI yaml
- Test fixtures / conftest
- CLAUDE.md or equivalent

All values identical? Crypto keys valid format (not stubs)?

Also check generated config files (alembic.ini, settings.py, etc.) with hardcoded secrets — are they in .gitignore?

## Scenario 3: Shell Script Execution

For every script (init.sh, CI yaml, Makefiles):
1. Mentally execute line by line
2. Track: cwd, env vars, running processes
3. `cd dir1 && ... && cd dir2` — dir2 is relative to dir1, not root!
4. Brace expansion `{a,b,c}` in heredoc = literal string
5. Conditional guards that assume file exists (e.g., .gitignore guard only runs if file already present — breaks on fresh repos)

## Scenario 4: Vague Acceptance Criteria

For every feature check AC for:
- "works correctly" — WHAT specifically?
- "configurable" — default value specified?
- "similar to X" — X = specific reference?
- "standard" — standard for whom?

## Scenario 5: Dependency Completeness

For every feature:
1. Search steps for references to other features (F-xxx or equivalent IDs)
2. Search for usage of tables/endpoints from other features
3. All found references present in depends_on?

## Scenario 6: API Contract Mismatch

1. Collect all endpoints from features/requirements
2. Collect all endpoints from architecture/design docs
3. Diff: present in one but missing in the other?

## Scenario 7: Status Enum Drift

For every entity with status/state:
1. Collect all possible values from feature definitions
2. Collect from architecture docs
3. Do they match? Is there a state machine with transitions?

## Scenario 8: CI Pipeline Reality Check

1. Will CI yaml run? Do all images exist?
2. Do env vars in CI match test config defaults?
3. Do test commands match actual file structure?

## Scenario 9: Domain-Specific Edge Cases

Identify the project's domain and check for domain-critical edge cases:

**Finance/Trading:** Atomicity of multi-step operations, race conditions, time-window constraints, partial operation handling, immutability requirements (append-only logs), currency precision and rounding.

**Medical/Health:** Data retention policies, consent tracking, audit trail completeness, anonymization requirements, regulatory compliance references.

**Legal/Compliance:** Version control of documents, approval workflows, access control requirements, retention periods, jurisdiction-specific rules.

**E-commerce:** Inventory consistency, payment failure handling, refund flows, tax calculation edge cases, concurrent purchase conflicts.

If domain is not obvious — skip this scenario.

## Scenario 10: Orphan Writes

For every table/file that a feature CREATES:
- Who READS this data?
- Is there a consumer? Or is it an orphan write?

## Scenario 11: Summary Count Verification

For every summary table (overview lines like "Domain: N tables"):
- Recount N from detailed sections
- Does summary match details?

## Scenario 12: depends_on Cross-Reference Scan

For every feature:
1. Search steps and description for references to other features
2. Search for usage of tables/endpoints/data from other features
3. All found references present in `depends_on`?
4. No circular dependencies? (A depends on B depends on A)

## Scenario 13: Cycle and Cross-Phase Dependency Detection

After any modification to dependency declarations:
1. Build dependency graph from all features
2. Check for cycles (A depends on B depends on C depends on A)
3. Check for cross-phase violations: feature in Phase 0 depends on feature in Phase 1 — unimplementable!
4. Every dependency target must exist and be in the same or earlier phase

## Scenario 14: Ground-truth Graph Integrity

When documentation describes code structure (component registry, API catalog, dependency manifest):

1. Collect ground truth from source files in a single pass (grep imports, scan exports, read configs)
2. Build a ground-truth map keyed by entity name
3. Cross-reference EVERY claim in the document against the map
4. Check bidirectionality: if A.field contains B, verify B.reverseField contains A
5. Check completeness: are there source entities missing from the document?

**Typical traps:**
- Registry lists component X as used by [A, B] but source shows A, B, C use it
- Document says "5 endpoints" but scanning route files reveals 7
- Import graph in docs missing recently added modules
- Non-obvious exports missed entirely: context providers, config exports, composite hooks — cross-check the full export surface (index.ts), not just component directories

## Scenario 15: Terminology Drift

Across all documents in scope:

1. Build a glossary of key concepts from context
2. Search for synonyms and near-synonyms used for the same concept
3. For each inconsistency: is there a defined canonical term?

**Typical traps:**
- "agent" / "bot" / "worker" / "assistant" used interchangeably
- "endpoint" / "route" / "API" / "path" mixed without consistency
- "module" / "skill" / "plugin" / "extension" drift across documents
- Abbreviations used inconsistently (sometimes "DB", sometimes "database")

## Scenario 16: Dead Reference Detection

For every internal reference in documentation (file paths, links, feature IDs, section refs):

1. Does the target exist?
2. Has it been renamed or moved?
3. Is the content at the target still relevant to the reference context?

**Typical traps:**
- "See docs/GUIDE.md" but file was archived/deleted
- File path referenced but file renamed
- Link to `#section-name` but heading was reworded
- Feature ID referenced in text but removed from features list

## Scenario 17: Temporal Consistency

For all dates, versions, timelines, and sequences across documents:

1. Are dates internally consistent? (created before modified, v1 before v2)
2. Do version numbers follow a coherent progression?
3. Do "current" / "latest" / "now" references match actual state?
4. Are deprecated items marked as such?

**Typical traps:**
- "Updated: 2025-01-15" but references features added in February
- "v2.0" in one doc, "v1.3" in another for the same release
- "Currently using X" but architecture says "migrating to X"
- Roadmap dates in the past with status still "planned"

**Ground-truth note for snapshot/status docs:** when a document self-certifies VCS/filesystem state (a fixed-state snapshot, status report, release log), verify every release/version date against `git log` / tag timestamps — NOT against the prose narrative. Authors copy dates from the session narrative they were reading, and that date can be wrong. Trap: doc dates a release at several sites two days off from the release commit's own timestamp. Mark narrative-sourced dates explicitly (e.g. "(per narrative)"); precise release dates must be git-sourced.

## Scenario 18: Scope Creep & Coverage Gaps

For each document that declares its scope (intro, purpose statement, table of contents):

1. Does the document actually cover everything it claims?
2. Does it contain material outside its declared scope?
3. Are there sections that promise detail but deliver only stubs?

**Typical traps:**
- "This document covers X, Y, and Z" but Z section is empty
- Architecture doc includes deployment instructions that belong in ops guide
- "See below for API reference" but API section has only "TODO"
- Document title says "Complete Guide" but covers only 3 of 7 subsystems

## Scenario 19: Source Attribution Verification

When documentation attributes a value, boundary, behavior, or schema to a NAMED source ("aligned with `session_config`", "matches the `gateway` window", "per `RECORD_DTYPE`", "same boundary as function X"):

1. Locate and read that EXACT named symbol's definition in the source — do not trust the doc's attribution.
2. Confirm the named symbol actually exists (not renamed/removed).
3. Confirm the quoted value/boundary actually appears in THAT symbol — not in a sibling function with a similar role.
4. Treat code comments that repeat the doc's claim as NON-independent — if the doc is wrong, the comment is usually wrong too (they were written together).

**Typical traps:**
- "Aligned with `session_config` (08:00–20:00)" — but `session_config`'s actual boundary is 06:00; 08:00 belongs to a *different* function (`gateway.is_active_window`). Real value, wrong source.
- "Matches the upstream session window" — but two different windows exist (ingestion vs. serving) and the doc cites the wrong one.
- A doc and its mirrored code comment make the SAME false attribution — cross-checking them confirms nothing; only the cited source definition is ground truth.

This is distinct from Scenario 15 (terminology drift) and the "same as X" identity trap (Antipattern #2): here the value may be real but is bound to the WRONG named entity, and the named entity is itself checkable.

## Scenario 20: Paired / Bilingual Document Precision Asymmetry

When the document set is a paired or bilingual representation of the SAME state (e.g. a precise technical snapshot + a plain-language or translated overview of it):

1. Identify the higher-precision variant — the one carrying exact dates, counts, version strings, named-source attributions.
2. Weight ITS claim-by-claim (M8) and ground-truth (M14) audit harder: the precise variant carries the higher factual risk. A vague variant ("mid-March", "a couple of modules") rarely carries precise-fact errors because it makes no precise claim to be wrong.
3. Cross-check the precise variant's exact facts against BOTH ground truth AND the vaguer sibling. Where they disagree and the precise one is wrong, the vaguer sibling is often the accurate-wording reference — fix the precise doc toward truth, do NOT force precision into the vague doc.
4. Do not down-rank the precise doc's risk just because the pair "mostly agrees" — agreement on vague phrasing proves little.

**Typical traps:**
- A precise snapshot dates a release to an exact (wrong) day; its plain-language sibling says "mid-March" (vague, therefore correct) — audit the precise one harder, use the vague one as wording reference.
- A precise variant attributes a step to a specific named source while the vaguer variant describes it generically and correctly.

## Scenario 21: Wire-Unit Consistency Across a Client↔Server Boundary

When a plan/doc adds, renames, or threads a PARAMETER that crosses a client↔server (or producer↔consumer, frontend↔backend) boundary:

1. For EACH such param, locate BOTH ends in source: the emit site (where the value is read from state/UI and put on the wire) and the consume site (where it is parsed and used in a computation).
2. Establish the unit/scale at each end independently from code: percent (30), fraction (0.30), basis points, %/second, seconds, milliseconds, a count? Read the actual arithmetic that consumes it.
3. Confirm the plan's conversion (or absence of one) makes the two ends agree. A missing `/100` turns a 30% threshold into a 30× band that filters nothing; a spurious `/100` shrinks it 100×.
4. Do this PER PARAM — never assume sibling params share a rule. Adjacent params on the same wire commonly have OPPOSITE conversion rules (one converts client-side, the next is consumed raw because the server converts internally).
5. Verify default/identity behavior: at the default value, does the round-trip reproduce the pre-change behavior exactly?

**Typical traps:**
- One threshold param is held client-side as a percent but the server expects a fraction (needs `/100`); its neighbor is `%/s` and the server divides internally (must NOT be converted). Same wire, two params, opposite rules.
- A duration emitted in seconds but consumed as milliseconds.

**In-formula sibling:** a related unit-scale defect needs no wire and no second site — a bps/percent CONSTANT used inside a single formula without its scale factor (`RATE_BPS · price` missing `· 1e-4`; `*_PCT · x` missing `· 0.01`). Its signature is silent degeneracy against an adjacent clamp: `clamp(RATE_BPS · price, …, 0.30)` with `RATE_BPS = 8` yields `8 · 330 = 2640` → pinned to the 0.30 cap for all prices, so the knob is inert and the output still looks plausible. Check every bps/% constant applies its factor before it multiplies a price/quantity, and whether a downstream clamp would mask a missing factor; confirm by executing over a value sweep.

This is distinct from Scenario 1 (recount occurrences of a literal) and Antipattern #31 (claimed arithmetic equality between two stated numbers): here the defect is a unit/scale mismatch between two code sites, found only by reading both ends.

## Scenario 22: Enumerate Every Cache of a Derived Value Before Keying It

When a plan adds a discriminator/variant key to a DERIVED value, the value is typically held in MORE THAN ONE cache, and patching them one at a time leaves a symmetric gap that re-surfaces every round:

1. Up front, in a SINGLE pass, grep for EVERY container that can hold the derived value: in-memory dicts, LRU/TTL caches, byte/serialized caches, per-request memos, disk/Redis caches. List them all.
2. Also enumerate EVERY PRODUCER of the value (every site that computes-and-stores it), including the live/hot branch AND the cold/reload branch — producers and caches are different lists; both must be covered.
3. For EACH cache: does its key now include the new discriminator? For tuple/prefix keys, is the new component at the correct position (e.g. an eviction prefix `key[:5]` → `key[:6]`)?
4. Confirm completeness by counting: "caches touched" must equal the grep'd cache count.
5. Re-audit after the Writer fixes one cache: a piecemeal fix that keys cache A but not symmetric cache B is the dominant recurrence here.

**Typical traps:**
- A derived result lives in several caches (a non-live dict, a live byte-cache, serialized-byte caches, and an eviction-key structure whose key ORDER also matters); rounds each surface one more because none was enumerated up front.
- A single-flight LOCK guarding cache population is keyed by a DIFFERENT (param-independent) key, so concurrent requests for different param values collide.

**Doc-literal sibling (Antipattern #39):** the same "fix one occurrence, leave the symmetric twin stale" mechanism recurs on documents — a duplicated literal across two structurally-parallel blocks. After any correction, diff every parallel occurrence character-for-character.

This is distinct from Scenario 10 (orphan writes) and Scenario 14 (registry counts): here every consumer is known; the trap is that the write/cache surface of one value is wider than it first appears and must be enumerated comprehensively, not incrementally.

## Scenario 23: Enumeration Completeness & Ownership in a Single Pass (fix-boundary)

When a Writer fix INTRODUCES an explicit enumeration — a dependency array (memo/effect deps), an "affected/known sites" list, or a multi-field signature / merge layer — that enumeration must be made provably EXHAUSTIVE and have its OWNERSHIP stated in the SAME pass. A partial enumeration self-replenishes: each subsequent round peels off one more missing element, costing one round per omission.

After EVERY Writer round, for each enumeration the fix added or touched:

1. **Recount against ground truth.** For a dependency array: grep every variable the derived expression actually reads (including ones the same fix introduced) and confirm each appears — a dep used in the body but absent is a stale-recompute bug. For an "affected sites" list: grep ALL occurrences of the pattern; the list's count must equal the grep count. For a merge/signature: confirm every field the consumers read is present.
2. **Confirm single ownership** of any merge/derivation: exactly ONE component must own the operation, and the doc must name it. Two plausible owners (a pure helper AND a memo both merging the same inputs) is a double-application risk — flag it even if each site is individually correct.
3. **Treat "to be completed next round" as a defect, not progress** — a partial list will generate a new finding every round until exhaustively closed.

**Typical traps:**
- A dependency array completed incrementally across rounds (missing one variable, then another) — several rounds to converge.
- A "known sites" list with 4 of 6 sites enumerated; the 2 missing surface a round later.
- A merge left ambiguous between a helper and a memo (both could concatenate the same inputs) → double-merge risk until one owner is named.

Distinct from Antipattern #30's other shapes (a wrong claim, an inverted AC): those are a single CLAIM with wrong content. This is an added LIST/SIGNATURE with wrong COMPLETENESS. Cross-linked from Antipattern #30.

## Scenario 24: Design Spec for a Not-Yet-Built Feature That References Existing Code

When the target is a DESIGN/SPEC for a feature NOT yet implemented but citing EXISTING code (functions, endpoints, files, keys it will extend or call), the document mixes two symbol classes with opposite verification rules. Conflating them floods the run with false positives — every PROPOSED symbol reads as a "missing reference" — or lets a genuine stale reference hide among the proposed ones.

Before auditing, establish an explicit EXISTING-vs-PROPOSED symbol split, derived FROM SOURCE, not from the spec's own labelling:

1. **Partition every code symbol the spec names** into EXISTING vs PROPOSED by grepping source — do NOT trust the spec's prose (it may assume a symbol exists that does not).
2. **EXISTING → ground-truth verification (M14, M17, M8).** Grep-verify each against source: it exists, has the cited signature, the cited file:line/value is current. A claimed-existing symbol absent from source is a REAL stale reference (critical), not a false positive.
3. **PROPOSED → internal-consistency + implementability ONLY (M13, M7, M12).** Do NOT flag a proposed symbol as missing — there is nothing to ground it against yet. Dry-run it: is every name it uses defined? Do its signature, return contract, and call sites agree across all mentions? Is it implementable without guessing?
4. **Skip mutation testing (M11)** — no code for the unbuilt feature to mutate; record the skip.
5. **The boundary is itself a high-value check:** a symbol the spec treats as proposed but that ALREADY exists (collision), or treats as existing but that does NOT (stale ref), are both real defects. The EXISTING-side staleness check — mechanically grep-resolving every claimed-existing `file:line`/symbol against current source — is the one most easily under-weighted: a non-existent symbol cited inside a dense, plausible (e.g. safety) paragraph can pass several reading rounds. Require at least one round that re-resolves EVERY existing-side symbol against source before trusting a clean on the ground-truth layer.
6. **M13 BY EXECUTION on the proposed algorithm — don't just read it.** When the proposed half contains a self-contained algorithm (a compute function with a worked example, bin/grid math, an iterative expansion), TRANSCRIBE it into a scratch runtime and RUN it — the algorithm is executable on its own worked vector even though the feature is unbuilt. This reproduces the asserted numbers end-to-end and quantifies robustness a read-through cannot (e.g. confirming a reconstructed bin index matches the source across a value sweep, vs being wrong in N cases for a naive variant). For a piecewise/state-machine output chosen by a cascade of branches, EXECUTE the branch predicate over a sweep of the input domain (a grid for two drivers, a range for one) and assert EXACTLY ONE branch fires at every node — proving the function is TOTAL and MUTUALLY EXCLUSIVE and pinning any gap/overlap. A passing aggregate or a single worked point is NOT evidence the partition is total + disjoint. The fix must make the branches ordered and state both the tie/overlap rule and the none-match default.

**Typical traps:**
- A spec names new compute functions, endpoints, and cache keys (all PROPOSED) alongside existing loader/normalizer/view symbols (all EXISTING). Without the split, M14/M17 flag the proposed ones as stale — all false positives.
- A proposed function binds `x = normalize(...)` as if it returns a value, but the EXISTING function mutates in place and returns `None` — an implementability bug found by M13 dry-run.
- A symbol the spec assumes exists (`load_data`) is actually named `load_data_v2` in source — a REAL stale reference on the existing side of the split.
- A proposed compute function ships a worked example whose defining extremum is a TIE, so its position outputs are non-reproducible while the example's aggregate (sum) assertion still passes and masks it (Antipattern #36).

Distinct from Scenario 14 (counts of EXISTING structure) and Scenario 16 (every ref must resolve): here a large fraction of named symbols INTENTIONALLY do not resolve yet. Method weighting on this class: M13 > M7 > M14(existing-only).

**Phasing-axis corollary (Scenario 27):** such a spec frequently also carries a release-phasing axis (v1/v1.1, Tier 1/2); the EXISTING-vs-PROPOSED split (which symbols resolve) is orthogonal to the phase axis (which features ship when). After the split, run Scenario 27 over the acceptance criteria.

## Scenario 25: Findings Doc Paired with a Script-Generated Source of Truth

When the target is a numbers-heavy research/analysis FINDINGS doc whose tables and statistics are PASTED from a script-generated source of truth (`results.json` / `tables.md` / `*.csv` from a generator script), and whose recommendation section proposes a mechanism for FUTURE code, it has two layers with different rules and one trap unique to generated artifacts.

1. **Factual layer → M2, every cell, both gate models.** Recompute EVERY pasted number directly from the generated source, not from the prose. This is the load-bearing method and the convergence axis; do NOT down-sample to "spot-check a few."
2. **An M2 mismatch has TWO root causes — disambiguate by reading the generator.** A cell disagreeing with the artifact is EITHER a stale paste (fix the doc) OR a generator bug (fix the generator, regenerate, re-paste). Open the generator to tell which; do NOT hand-edit a cell to "look right" when the generator is wrong — that desyncs the doc from its source of truth and masks a code bug (Antipattern #9). Buggy-generator branch (Lead-owned): fix → re-run → re-paste; confirm the UNAFFECTED tables reproduce byte-exactly (proves the fix was localized and the generator deterministic).
3. **Recommendation layer → M13 (dry-run against the EXISTING code it will plug into).** Is the proposed sign/weight/threshold buildable without contradiction? This is where the implementation-blocking issues live (a sign double-negation if a signed weight and a legacy invert flag both apply; an unspecified ramp shape).
4. **Fix-boundary is NUMERIC on this class (Scenario 1 + Antipattern #30).** A fix that rewords an interpretive sentence tends to leave an ADJACENT number stale — a range endpoint un-harmonized across sibling sections, a ratio bound off by a point. After each round, M2-recompute every number sharing a paragraph/row with edited prose.
5. **Generator-prose-vs-generator-code.** The generator's own docstring/comments can be stale relative to its code even when the doc and numbers are correct. Audit the generator's prose against its implementation; a stale header describing a superseded method is a propagation risk (an absolute claim in it may have been copied into the doc).
6. **Skip and record:** M9 (no cross-doc interface), M11 (the doc is findings, not executable code; the generator is verified by re-run determinism, not mutation), M4/M6 (no credentials/attack surface).

**Method weighting:** M2 (every cell, both models) ≈ M13 (recommendation dry-run) > M12 (fix-boundary contradiction) > M7/M18 > M15/M17.

Distinct from Scenario 1 (the ground truth is an EXTERNAL generated artifact and the generator itself can be the bug) and Scenario 24 (here the factual layer is fully checkable against shipped artifacts; only the recommendation is forward-looking).

## Scenario 26: Spec That Documents Already-Shipped Code

When the target is a spec / algorithm doc / API reference written AFTER the code merged, it is the MIRROR of Scenario 24: there almost every symbol is PROPOSED; here almost every symbol is EXISTING and grep-verifiable against source. Auditing it like a design spec (weighting M13 implementability) wastes budget on code that already exists; auditing it like a generated-findings doc is wrong (the ground truth is the shipped SOURCE, not an artifact).

1. **Verify the EXISTING majority against source (M14 + M2).** Grep-confirm every symbol/constant/endpoint/signature; recount every number. The load-bearing pair and convergence axis.
2. **Verify load-bearing claims by EXECUTING the shipped code (M8 + M13-by-execution).** A numeric/behavioral claim ("invert is cosmetic — residual & R² identical") is stronger checked by RUNNING the code and diffing (e.g. max-abs-diff 0.0) than by argument. For a multi-branch piecewise claim, execute the predicate over a sweep and assert exactly-one-fires (totality + mutual exclusivity).
3. **The residual risk is PROSE ACCURACY, not implementation gaps.** Point M8/M12 at universal quantifiers and at every number's aggregation provenance — a value can be correct against one source column but wrong against the column the prose names.
4. **Skip M11 and record it** (no proposed-code surface to mutate); on a pure math+API doc also skip M4/M5/M6.
5. **Watch the small PROPOSED remainder** (deferred/future work). Apply Scenario 24's rule to just that remainder. A symbol the doc treats as shipped but absent from source is a REAL stale reference, not future work.
6. **Staleness on a RE-RUN of a now-built doc — sweep by READING every built section, NOT by phrase-grep.** When the doc earlier passed the gate as a *spec* and the feature has since shipped, the dominant defect is PRE-BUILD LANGUAGE: future/imperative phrasing for now-shipped work. Every reference still resolves and every number is correct — it is correct content in the wrong TENSE/MOOD. READ every built-feature sentence and classify shipped-fact vs pre-build intent; a fixed phrase-grep misses novel forms. Rewrite imperative/future constructions over shipped work to past-tense fact; re-title any "Implementation plan (next session)" heading over completed work; re-derive any "existing N keys" count a now-shipped addition has incremented. See Antipattern #38.

**Method weighting:** M14 ≈ M2 > M8/M13-by-execution > M7/M12 (pointed at prose universals + aggregation provenance) > M15/M16/M18. Skip M11 (record); skip M4/M5/M6 on a math+API doc. On a RE-RUN of a now-built doc, READ-based M17 staleness becomes co-primary with M14/M2.

Distinct from Scenario 24 (PROPOSED symbols don't resolve yet) and Scenario 25 (ground truth is a generated artifact and the generator can be the bug).

## Scenario 27: Release-Phasing AC Coherence (acceptance criteria vs. a version/tier axis)

When a spec introduces a RELEASE-PHASING AXIS — a per-feature phase/tier/version tag (v1 / v1.1, Tier 1 / Tier 2, MVP / later, P0 / P1) — acceptance criteria silently drift out of phase: an AC with a GENERIC QUANTIFIER over the full feature catalogue ("each module in §3.2–3.7", "every feature ships with its UI", "all exporters expose a format option") sweeps in not-yet-built later-phase items, so it asserts buildable-now behavior for features that will not exist until a later release. The AC is precise and individually testable — but not YET, and the mismatch hides because it reads as rigorous.

1. **Build the phase→feature map from the doc's OWN tags.** Record the phase/tier/version tag on every feature/section the spec defines; this map is the ground truth for which items each phase ships.
2. **For EVERY acceptance criterion, resolve its generic quantifiers to the concrete feature SET it tests** — do not accept the AC's own tag at face value; compute the set from what it actually exercises.
3. **Intersect that set against the phase map.** An AC whose set lies entirely within ONE phase is coherent. An AC whose set SPANS two phases is a blocking coherence defect even though each clause is individually testable — it tests something the current phase does not ship. Fix by tagging the AC to the narrowest phase it tests and splitting per-phase, or stating explicitly which phase each clause belongs to.
4. **Check the reverse coverage gap:** a later-phase feature with NO acceptance criterion is an untested deferred item — add a phase-tagged AC for it.
5. **The boundary is itself a check:** an AC mistagged to a phase that doesn't include the feature it tests, and a feature whose only AC lives in the wrong phase, are both real defects surfaced only by maintaining the phase→AC intersection rigorously.

**Typical traps:**
- An AC labeled `[v1]` tests a feature that is a `[v1.1]` item → split into a `[v1]` AC and a `[v1.1]` AC.
- An AC quantified as "each feature ships with its UI" ranges across later-phase items → add a parenthetical scoping each to its phase, or split.
- A later-phase feature sits in a generic untagged AC block → tag it; a deferred feature with no functional AC → add one.

Distinct from Scenario 4 / Antipattern #8 (VAGUE AC — no specific metric) and Antipattern #37 (a named metric has no DEFINITION): here the AC is precise and every metric defined; the defect is that its IMPLICIT scope ranges across the doc's EXPLICIT phase tags. Distinct from Scenario 18 / Antipattern #27 (a promised section is empty): here the content is complete and the mismatch is AC-scope vs phase-tag.
