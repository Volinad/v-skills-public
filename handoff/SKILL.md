---
name: handoff
description: >
  Create structured handoff documents that capture session context for the next session
  or a parallel session. Trigger on: "handoff", "pass context", "передай контекст",
  "сделай хэндофф", "wrap up", "let's stop here", "split this off", "start a new session",
  "записать что сделали", "record what we did", "продолжу завтра", "I'll continue tomorrow",
  "capture context for a parallel session", "save progress", "that's all for today", "pick this up later".
  PROACTIVELY suggest this skill when ANY of these conditions are true: (1) context window
  is getting long and you have accumulated unrecorded decisions or TODOs, (2) user says
  "давай закончим", "на сегодня всё", "в следующий раз", "let's wrap up", "done for today",
  "next time", "let's call it a day", (3) a complex
  multi-session project is being discussed, (4) you are about to lose important context
  that the next session will need, (5) scope is changing to a different topic, (6) a
  side-task emerged that deserves a parallel session. If you are ending a session that
  involved significant work and have NOT suggested a handoff — this is a bug in your
  behavior. Handoffs are not optional for non-trivial sessions.
---

# Handoff

You create handoff documents — structured context packages that let the next session
(or a parallel session) pick up work without losing important context.

## When to create a handoff

There are two distinct situations:

**Session handoff** — the current session is ending (or should end). You're passing the
baton to the next session that will continue the same line of work.

**Branch handoff** — you've discovered a side-task during the current work that deserves
its own session. You write a handoff with everything the parallel session needs to know,
and then continue your current work. The user will launch the branch session separately.

Use context to infer the type: if the user says "ending", "stopping", "tomorrow", "next session",
or similar — it's a **session** handoff. If they say "split off", "parallel", "side task", "meanwhile",
or similar — it's a **branch** handoff. If neither signal is present, ask the user which type they want.

Beyond creating, there's a third motion: **updating** a handoff this session already wrote or
picked up, to fold in newer work ("update the handoff with what we just did"). That's an
in-place edit of the same file, not a new handoff — see "Updating a handoff in place" below.

## Where handoffs live

All handoffs go in `.handoffs/` at the project root. Create this directory if it doesn't exist.

Project root is the directory containing `.git` (for git repos) or the current working directory
(for non-git projects).

File naming: `handoff-NNN.md` where NNN is zero-padded to 3 digits (001, 002, 003...).
The number is the highest existing number in `.handoffs/` plus 1 (start at 001 if the
directory is empty) — but **don't pick it now.** Claim it atomically as the very last step,
after the body is written (see "Claiming the number" below). Choosing it up front is exactly
what makes parallel sessions collide: writing a handoff takes minutes, and a second session
that grabs the same number meanwhile will silently overwrite your file — this skill doesn't
commit, so there's no git safety net, and the same filename means a lost handoff.

## Handoff document structure

Use this template:

```markdown
# Handoff NNN — [short title describing the task/context]

**Session name:** [session name + handoff number]
**Type:** session | branch
**Created:** YYYY-MM-DD HH:MM (local time)
<!-- Add **Updated:** YYYY-MM-DD HH:MM (local time) when you refresh this handoff in place (see "Updating a handoff in place"). Omit on first creation. -->
**Branch:** [current git branch, if in a git repo]
**Picked up:** no
**Status:** [one-line summary of where things stand]

## What was done
<!-- For branch handoffs: this section is optional — omit if the branch task is entirely new. -->

[Concrete list of completed work. Reference specific files, commits, functions changed.
Be precise — the next session can't see this conversation.]

## Current state
<!-- For branch handoffs: optional — include only if there's relevant state the parallel session needs. -->

[What's working, what's broken, what's half-finished. Include any running processes,
temporary files, or state that the next session should know about.]

## Next steps

[Ordered list of what needs to happen next. Be specific enough that someone with no
prior context can start working immediately.]

## Key decisions & context

[Important decisions made during this session and WHY they were made. Include rejected
alternatives if the reasoning matters. This section prevents the next session from
relitigating settled questions.]

## Key files

[List the files that matter most for continuing this work. The next session will read
these first to rebuild context. Group by role if helpful.]

- `src/auth/session.ts` — new session management (created this session)
- `src/auth/middleware.ts` — modified: JWT → session validation
- `db/migrations/003_sessions.sql` — not yet applied
- `tests/auth.test.ts` — needs updating

## Errors & workarounds

[Errors encountered during this session and how they were resolved (or not).
This prevents the next session from hitting the same walls.]

- `ECONNREFUSED on port 5432` — PostgreSQL wasn't running in Docker; fixed with `docker compose up -d`
- `TypeError: session.validate is not a function` — was importing from wrong module; switched to `session-store.ts`
- UNRESOLVED: `jest --coverage` hangs on auth tests — possibly related to open DB connections

## Learnings

[Patterns, insights, or project-specific knowledge discovered during this session
that aren't obvious from the code alone.]

- The project uses a custom ORM wrapper in `src/lib/db.ts`, not raw Knex — always use `db.query()` not `knex()`
- CI runs on Node 18 but local dev is Node 20 — watch for API differences
- The team prefers explicit error types over generic `throw new Error()`

## Open questions

[Anything unresolved that the next session needs to figure out or ask the user about.]

## Backlog

[Carried forward from previous handoffs. These are tasks that were not completed in
prior sessions and are still relevant. Review the previous handoff's "Next steps" and
"Backlog" — carry forward anything not done, drop anything no longer relevant.]

- [ ] (from handoff-002) Set up Redis session store — still needed, blocked on infra decision
- [ ] (from handoff-001) Add rate limiting to /api/auth endpoints
- ~(from handoff-001) Migrate user avatars to S3~ — no longer needed, switched to Cloudflare Images
```

For **branch handoffs**, the emphasis shifts: "What was done" becomes shorter (or absent —
the branch task may be entirely new), while "Next steps" and "Key decisions & context"
become the core. "Key files", "Errors & workarounds", and "Learnings" include only what's
relevant to the branch task. Include everything the parallel session needs to understand
the problem without access to this conversation.

Sections can be omitted if empty — don't add "Errors & workarounds: none". But err on the
side of including more context rather than less. The sections "Key files", "Errors &
workarounds", and "Learnings" mirror what Claude Code accumulates in session memory,
so including them gives the next session a head start instead of rediscovering everything.

## Backlog propagation

Tasks get lost between sessions when plans change mid-session. The Backlog section
prevents this by carrying unfinished work forward.

**When creating a handoff**, read the previous handoff (if one exists) and:

1. Compare its "Next steps" with what was actually done this session
2. For each undone task, decide: still relevant? → add to Backlog. Obsolete? → add
   with strikethrough and a short reason why it's dropped
3. Carry forward any existing Backlog items from the previous handoff that are still open
4. If a backlog item is large enough for its own session, suggest a branch handoff for it

Format backlog items with origin: `(from handoff-NNN)` so the user can trace where
a task originated. Use checkboxes: `- [ ]` for open, `- [x]` for done, `~strikethrough~`
for dropped.

**When picking up a handoff**, present the backlog to the user at session start:
"We're continuing with [Next steps]. There are also N open items in the backlog from
previous sessions — want to review them or focus on the main task?"

This way the user always knows what's accumulating and can decide to address it,
delegate it to a parallel session, or explicitly drop it.

## Session naming convention

Every handoff records a "Session name" field. This is informational — there's no way
to rename a session programmatically. The user may use it to rename manually if they want.

**How to construct the session name:**
1. Take the current session's base name (strip any trailing number):
   "Agent Composer 002" → base name is "Agent Composer"
2. Append the handoff number: creating handoff-003.md → "Agent Composer 003"
3. If this is the first handoff (001) and the session has no name — use the project
   directory name (shortened if long) as the base: e.g., "Agent Composer 001"

The base name always comes from the current session, not the project. If the user
renamed their session to something custom, that name sticks for all future handoffs.

**When picking up a handoff:** use the session name from the handoff as context
for continuity, but do not ask the user to rename anything.

## How to write a good handoff

The next session starts with zero context from this conversation. Write as if briefing
a colleague who is skilled but knows nothing about what just happened. Every file path,
every decision rationale, every "we tried X and it didn't work because Y" matters.

Avoid vague language like "continue the work" or "fix the remaining issues". Instead:
"The migration script at `db/migrate_v3.py` fails on line 47 when the `users` table
has NULL values in the `email` column. The fix is probably a COALESCE but needs testing."

## Claiming the number (do this last)

**The numbered file `handoff-NNN.md` comes into existence ONLY through the atomic claim
below — never created with the Write tool, and never at the start.** Your instinct will be
to pick a number and immediately write `handoff-101.md`; that instinct is the collision bug —
two parallel sessions both pick 101 and the second's write silently clobbers the first. So
keep the body out of any numbered file until the very end.

Write the entire handoff body first (in your reply, or a uniquely-named non-numbered draft),
using a placeholder like `NNN` wherever the handoff's own number appears (the title line, the
"Session name" field). Only once the body is ready, claim a number — at the last possible
moment, with an atomic create so two sessions can never land on the same file:

```bash
cd "<project-root>/.handoffs"
n=$(( $(ls handoff-[0-9]*.md 2>/dev/null | sed -E 's/.*handoff-0*([0-9]+)\.md/\1/' | sort -n | tail -1) + 1 ))
# `set -C` (noclobber) makes `>` fail if the file already exists, so this create is atomic.
# If a parallel session claimed this number a moment ago, the create fails and we bump.
until ( set -C; : > "$(printf 'handoff-%03d.md' "$n")" ) 2>/dev/null; do n=$((n+1)); done
printf 'Claimed handoff-%03d.md\n' "$n"
```

The empty file now reserves your number — no concurrent session can take it, because their
atomic create on the same name fails. Then write the body into that exact file, substituting
the real number for the `NNN` placeholder. (The file already exists as the empty reservation,
so Read it once — it'll be empty — then Write the full content; don't delete and recreate it,
or you reopen the race.)

Why atomic, and not just "pick the number later"? Late alone isn't enough — two sessions
finishing within the same few seconds would still collide on a plain "highest + 1". The
atomic create is a real mutex. And note what's doing the work: the `.handoffs/` directory
itself is the registry, so the number is always derived from what actually exists (it can't
drift) and the filesystem guarantees uniqueness — no separate "next number" file to maintain
or leak a number when a session is abandoned.

## Updating a handoff in place (no new number)

Handoffs are often kept alive within one session: you write one, the user keeps working
("keep going, finish X"), then asks you to fold that progress in — "update the handoff with
what we just did", "refresh the handoff before we stop". This is an UPDATE of the existing
file, not a new handoff: overwrite the SAME `handoff-NNN.md` and do NOT claim a new number.

Claiming a fresh number here is wrong on two counts: it leaves the older snapshot behind as a
stale `Picked up: no` file that resurfaces as an unpicked handoff in the next session, and it
fragments one evolving snapshot across several files. One live handoff you keep current is what
the user wants.

**How to update:**
1. **Target the handoff this session owns** — the one you created or picked up earlier in this
   conversation (you already know its number). Do NOT re-derive "highest + 1" and do NOT open a
   different handoff.
2. **Read it, then Write the refreshed body back to the same path.** Fold the new work into
   `Status`, `What was done`, `Current state`, and `Next steps`; append to `Errors & workarounds`
   / `Learnings` / `Backlog` as needed. Keep the original `Created:` line and set/refresh an
   `**Updated:** YYYY-MM-DD HH:MM (local time)` line beneath it.
3. **Leave `Picked up:` unchanged.** You're keeping the handoff current for the next session, not
   consuming it.
4. **No atomic claim, no number bump.** The "create the numbered file only via the atomic claim"
   rule guards two sessions racing for the *same new number* — it does not apply here, because you
   already own this file and take no new number. A plain Read + Write is correct and safe.

After updating, tell the user the path and carry on — an in-place refresh is not itself a reason
to end the session.

**Update in place vs. claim a new number — how to decide:**
- **Update in place** when this session already owns a handoff and the user asks to refresh it
  with what you've since done. This is the common case, and the default whenever a current
  handoff exists.
- **Claim a new number** when: this session has no handoff of its own yet; the user explicitly
  asks for a fresh handoff / a milestone snapshot; or the topic has shifted enough that it's
  logically a different handoff (a scope *change* — see "Proactive handoff suggestions").
- **When it's genuinely ambiguous** (you've done a lot since, and it's unclear whether the user
  wants the old one refreshed or a new snapshot), ask — one short question beats guessing.

If context was compacted and you no longer remember which handoff is yours, don't guess a number:
check `.handoffs/` for the most recent one matching this line of work and confirm with the user
before overwriting it.

## After writing the handoff

Once the handoff file is saved, tell the user the full file path.

- **Session handoff:** suggest ending the session so the user can start a fresh one with the handoff.
- **Branch handoff:** resume your current work immediately — the user will launch the branch
  session separately when ready.

## Picking up a handoff

At session start, scan all files in `.handoffs/` for `Picked up: no`. If there are
unpicked handoffs:

- **One unpicked**: pick it up immediately — no questions asked. Change `Picked up: no`
  to `Picked up: yes` and present:
  ```
  **Agent Composer 003** — continue API versioning
  Next steps: set up OpenRouter, run 4 models, compare profiles
  ```
  The session name goes first in bold so the user can easily copy it for renaming.
  Then start working on the first next step right away.

- **Multiple unpicked**: list them, let the user choose:
  ```
  Unpicked handoffs:
  1. **Agent Composer 003** (session) — Continue API versioning
  2. **Agent Composer 004** (branch) — Fix broken logging infrastructure
  3. **Agent Composer 005** (branch) — Migrate user avatars to S3
  Which one?
  ```
  After the user picks one, mark it `Picked up: yes` and proceed.

If the user says "continue" or "let's go" without specifying — show the list if there
are multiple, or auto-pick if there's only one.

## Auto-register in project CLAUDE.md

The first time you create a handoff in a project, check if the project's CLAUDE.md
(at `.claude/CLAUDE.md`) contains a handoff instruction. If it doesn't, append this block:

```markdown

## Handoffs

At session start: scan `.handoffs/` for files where `Picked up: no`, list them to the user, and follow directives of the one they choose.
```

Create `.claude/CLAUDE.md` if it doesn't exist. If it already exists, append at the end.
This ensures future sessions automatically pick up handoff context without the user having
to remind the agent.

## Proactive handoff suggestions

There's an important distinction between scope expanding and scope changing:

- **Scope expands** (more work on the same topic) — keep working in the current session.
  Example: "fix the CSS" turns into "refactor the whole component" — it's bigger, but
  it's the same theme. No handoff needed.
- **Scope changes** (switching to a different topic) — suggest a session handoff.
  Example: "fix the CSS" turns into "we need to redesign the data model" — that's a
  different problem entirely.

Suggest a handoff when you notice:

- The scope is **changing** — the user is asking about something substantially different
  from what you've been working on (not just more of the same)
- Context is getting long and you're starting to lose track of earlier details
- A side-task emerged that would benefit from dedicated focus in parallel
- You've hit a blocker that requires a fresh perspective

Do NOT suggest a handoff just because the task got bigger. More work on the same topic
is normal — that's what sessions are for.

Frame it naturally: "This looks like a different problem from what we've been doing —
want me to write a handoff so you can start a fresh session for it?"
