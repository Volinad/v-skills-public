---
name: evolve
description: "Post-development change journal — turns every change to already-built functionality into a permanent lesson. Use after ANY such change (bug fix, config tweak, integration fix, UX/performance/security change): record an EVO-NNN entry in the project's evolution log, commit as evo(EVO-NNN), push to claim the number. Trigger on '/evolve', 'document this change', 'задокументируй изменение', or when the project's CLAUDE.md mandates evolve after changes. ACTIVE only in projects that keep an evolution log (docs/EVOLUTION-LOG.md exists) or whose CLAUDE.md mandates it; in other projects act only on explicit request — offer first-time setup instead."
---

# Evolution Log

Document every post-development change to build institutional memory for the project's next version.

## Where this applies (the gate)

This skill is active when EITHER:

- `docs/EVOLUTION-LOG.md` exists in the project, or
- the project's CLAUDE.md mandates running evolve after changes.

In any other project, do NOT volunteer this workflow after ordinary code changes — most
projects don't keep an evolution log, and nagging them to start one is noise. Apply it only
when the user explicitly asks; if they ask in a project with no log yet, run First-time setup.

"Post-development" is the other half of the gate: this journal is for changes to
already-BUILT functionality (the product runs — real data, real users). A project still in
its initial build doesn't evolve yet — its record is the spec, the commits, and the handoffs.

## Why this exists

Once a product runs against real data and real users, every change is a verdict on the
original spec: what it missed, which assumption was wrong, what breaks in production. These
are the most valuable learnings the project produces — and the git diff alone doesn't
preserve the WHY. If they aren't captured, the next version repeats the same mistakes. This
skill turns every fix into a permanent lesson.

## First-time setup (once per project)

When the user asks for an evolution log in a project that has none:

1. **Confirm the intent.** This is a standing discipline — every post-dev change gets an
   entry, no "too small" exceptions. It earns its keep on projects that will live for months
   or be rebuilt as a next version.
2. **Create `docs/EVOLUTION-LOG.md`:**

   ```markdown
   # Evolution Log

   Append-only journal of post-development changes: what broke, why, how it was fixed,
   and the lesson the next version must absorb. Entries are numbered EVO-001, EVO-002, …
   — see the evolve skill for the entry format and the numbering protocol.

   ---
   ```

3. **Register the mandate in the project's CLAUDE.md** — root `CLAUDE.md` first, then
   `.claude/CLAUDE.md`; append to whichever exists (create root `CLAUDE.md` if neither):

   ```markdown

   ## Evolution log

   Run /evolve after ANY post-development change — entry in `docs/EVOLUTION-LOG.md`, commit `evo(EVO-NNN)`, push immediately (the push claims the number against parallel sessions).
   ```

   If the repo has no remote, drop the push clause.
4. **If the project uses handoffs**, note the pairing: handoff "What was done" sections
   should reference EVO numbers instead of restating the changes.

## When to use

ALWAYS, after ANY change to already-implemented functionality:

- Bug fixes found during real-world use
- Configuration fixes (wrong paths, missing env vars, CORS)
- Integration issues (data formats, auth, timezones)
- UI/UX improvements driven by actual usage
- Performance fixes
- Security patches
- Any change that wasn't in the original plan

## Workflow

### Step 1: Identify what changed

List every modified file and categorize the change (default taxonomy — extend it if the
project needs more):

| Category | Examples |
|----------|---------|
| `bugfix` | wrong calculation, null pointer, encoding issue |
| `config` | .env path, CORS setup, API URL |
| `integration` | external API connection, data format mismatch |
| `ux` | timezone display, loading states, error messages |
| `performance` | query optimization, caching, lazy loading |
| `security` | auth bypass, token exposure, input validation |

### Step 2: Write the evolution entry

Append to `docs/EVOLUTION-LOG.md` using this exact format:

```markdown
## EVO-NNN: Short title (YYYY-MM-DD)

**Category:** bugfix | config | integration | ux | performance | security
**Refs:** [optional — whatever the project anchors work to: feature IDs, issue numbers, handoff-NNN, lane name]
**Files changed:**
- `path/to/file.py` — what was changed
- `path/to/other.tsx` — what was changed

**Problem:**
What went wrong or was missing. Be specific — error messages, wrong behavior,
the user's report. One paragraph max.

**Root cause:**
Why the original implementation had this issue. What assumption was wrong or
what the spec didn't account for. This is the most important field — it's what
prevents the same mistake in the next version.

**Fix:**
What was done to resolve it. Technical details, approach chosen.

**Lesson:**
One-line takeaway for the next version's spec.
Format: "SPEC MUST [requirement]" or "ALWAYS [practice]" or "NEVER [antipattern]"

**Tests:** Passed / Added test_xxx / No tests needed (explain why)
```

### Step 3: Update related docs if the project tracks status

If the project tracks feature/task status (feature JSONs, roadmap, backlog): do NOT flip a
completed status back — completed items stay completed, and the evolution log IS the record
of post-done changes. Anchor the entry to the affected items via **Refs** instead.

### Step 4: Stage, commit

```bash
# 0. Finalize the number NOW: recompute the next free EVO-NNN from the current log
#    (a parallel session may have appended) and set it in the entry header + commit label.

# 1. Stage the evolution log and the changed files
git add docs/EVOLUTION-LOG.md [changed files]

# 2. Commit with the evo prefix
git commit -m "evo(EVO-NNN): short description

[one-line summary of root cause and fix]

Co-Authored-By: [the model you are running as] <noreply@anthropic.com>"
```

The commit prefix is `evo(EVO-NNN)` — NOT `feat` or `fix`. It makes evolution entries
instantly findable:

```bash
git log --oneline --grep="^evo("
```

### Step 5: Push immediately to claim the number (when a remote exists)

Push right after committing — don't wait and don't ask first. The push is what claims your
EVO number against parallel sessions:

```bash
git push || {
  # Rejected → another session pushed first and may have taken your number.
  git pull --rebase
  # ...renumber EVO-NNN -> next free, in BOTH the log-entry header and the
  #    commit label (git commit --amend), then push again:
  git push
}
```

If the repo has no remote, skip this step — the log in the working tree is the only
registry, and recomputing the number at commit time (step 4.0) is what protects against
parallel local sessions.

### Step 6: Report to the user

After committing (and pushing), give the user a clear summary. This is mandatory — the user
must always know what documentation was created and what went into git:

```
✅ Evolution documented:

📝 EVOLUTION-LOG.md:
- Added EVO-NNN: "Short title"
- Category: bugfix/config/integration/ux/performance/security
- Refs: [if any]
- Root cause: one-line summary
- Lesson: the "SPEC MUST…" takeaway

📁 Files changed: N files
- path/to/file1.py
- path/to/file2.tsx

🔀 Git commit:
- `evo(EVO-NNN): short description` (hash: abc1234)
- Pushed: Yes/No
```

Never skip this step — even if the change seems trivial.

## Entry numbering

EVO numbers are sequential (EVO-001, EVO-002, …) — the next one is the last entry in
`docs/EVOLUTION-LOG.md` plus 1 (start at EVO-001 if the log is empty). Multiple related
changes in one session are ONE entry, not separate.

**Finalize the number at commit time, not when you start writing.** Sessions often run in
parallel, and the log is one shared, append-only file — bake the number in up front and two
sessions pick the same EVO-NNN, forcing the loser to redo it. So treat the number as
tentative until the very end:

1. While drafting, leave the number tentative. Recompute it from the current log the moment
   before you commit — another session may have appended in the meantime.
2. Commit, then **push immediately** (when a remote exists) — the push is what actually
   claims the number. Whoever pushes first owns it.
3. If the push is rejected (someone else took the number), `git pull --rebase`, bump yours
   to the next free number in BOTH places it lives — the log-entry header and the commit
   label (`git commit --amend`) — and push again. The number lives in only those two spots
   by design, so renumbering is a two-line fix.

There's no separate "next number" registry to keep in sync: the log plus git ARE the source
of truth, and git's push ordering is the mutex that serializes parallel sessions.

## Pairing with handoffs and lanes

- In projects that use the **handoff** skill: a handoff's "What was done" references EVO
  numbers instead of restating the changes — one source of truth per change.
- In **lane mode** (`.handoffs/LANES.md` exists): put your lane's name in **Refs** — it
  gives the Oversight role a per-lane view of change activity for free.
- A lane **close-out** distills lessons FROM this log's Lesson lines into permanent homes;
  the log itself is one of those permanent homes.

## Principles

- **Every change gets documented** — no "it's too small" exceptions
- **Root cause is mandatory** — "it was broken" is not enough. WHY was it broken?
- **Lesson must be actionable** — "SPEC MUST require CORS preflight testing", not "CORS is tricky"
- **Group related changes** — several fixes in one session's batch = one EVO entry
- **Never edit old entries** — the evolution log is append-only
