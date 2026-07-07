---
name: autoresearch
description: "Universal AI-driven research engine (Karpathy autoresearch pattern). Use this skill whenever the user or an agent wants to optimize anything with a measurable metric — trading strategy parameters, code performance, ML hyperparameters, prompts, configs. Triggers on: 'optimize', 'tune', 'autoresearch', 'find best parameters', 'improve performance', 'run experiments overnight'. Two modes: parameter (tune numbers via eval command) and code (modify files + git commit/reset). Can run autonomously for hours."
---

# Autoresearch

Universal optimization engine. Hypothesis → experiment → analysis → repeat. Optimizes anything with a measurable metric.

## Attribution

Adapted from the [autoresearch](https://github.com/karpathy/autoresearch) pattern by [Andrej Karpathy](https://github.com/karpathy). The original implements autonomous AI-driven research for single-GPU LLM training. This skill generalizes the pattern into a reusable Claude Code skill for optimizing any measurable metric — parameters, code, prompts, or configurations.

## How It Works

You are the Researcher. You formulate hypotheses about what parameter values or code changes will improve a metric, run experiments to test them, analyze results, and decide what to try next. The loop runs autonomously until a stopping condition is met.

Two modes:
- **Parameter mode:** You generate JSON parameters → eval command runs → you parse the metric → repeat
- **Code mode (Karpathy-style):** You edit target file(s) → eval command runs → you parse the metric → git commit if better, git revert if not → repeat

Read the SPEC for full details: `~/.claude/skills/autoresearch/SPEC-v1.md`

## Prerequisites

- Python 3.10+ (for analyzer and report scripts)
- Git repository (required for code mode; recommended for parameter mode)
- An eval command that outputs metrics to stdout

## Phase 1: Setup

### If invoked interactively (`/autoresearch` without args):

1. Check if `.autoresearch/` exists in project root. If not, create it:
   ```
   .autoresearch/
     config.json     # {"project_name": "<detected>", "default_mode": "parameter", ...}
     sessions/
   ```

2. Ask the user:
   - "What do you want to optimize?" → detect mode (parameter vs code)
   - Eval command (what runs the experiment and outputs the metric)
   - Metric name, direction (maximize/minimize), current baseline value
   - Budget (max experiments, max hours)
   - Parameter mode: parameter space (ranges, types) or path to param_space.json
   - Code mode: target file(s), create/review program.md

3. **Validate before starting:** Run the eval command once with default/baseline params. Confirm:
   - Exit code is 0
   - Metric is parseable from stdout (see Eval Command Protocol below)
   - If validation fails → show error, ask user to fix

4. Confirm all settings and begin.

### If invoked with args:

Parse arguments. Required:
- `--mode parameter|code`
- `--eval-command "command with {params_file} placeholder"` (parameter mode) or `--eval-command "command"` (code mode)
- `--metric <name>` `--direction maximize|minimize` `--baseline <value>`

Optional:
- `--max-experiments N` (default: 50)
- `--max-hours H` (default: 8)
- `--plateau-window N` (default: 10)
- `--report-to <path>`
- `--param-space <path>` (parameter mode)
- `--target "file1,file2"` (code mode)
- `--program <path>` (code mode)
- `--resume [session-id]` (resume interrupted session)

Run baseline validation, then begin.

## Eval Command Protocol

The eval command MUST output metrics to stdout in one of these formats:

**Format 1 — Single metric:**
```
METRIC: 2.34
```

**Format 2 — Named metrics (recommended):**
```
METRIC accuracy: 0.934
METRIC f1_score: 0.891
METRIC latency_ms: 42
```

**Format 3 — JSON:**
```
AUTORESEARCH_RESULT: {"accuracy": 0.934, "f1_score": 0.891}
```

The `--metric` name specifies which metric is primary for optimization. All others are recorded as secondary metrics in the journal.

Exit code 0 = success. Non-zero = failure (recorded in journal, counts toward consecutive failure limit).

**The eval command is the contract — never game it.** Do not modify the eval script, weaken
or skip its tests/filters, narrow the dataset, or special-case inputs so the metric improves:
that is reward hacking — optimizing the measurement instead of the system — and it invalidates
the entire session's results. In code mode the eval command and everything it depends on are
READ-ONLY. If the eval itself looks wrong or unfair, STOP and report to the user — changing
the eval is the owner's decision, and doing so resets all baselines.

### Parameter Passing (parameter mode)

For each experiment, you write the params dict to:
`.autoresearch/sessions/<session-id>/current_params.json`

Then substitute `{params_file}` in the eval command with the absolute path to this file. The eval script reads params from this JSON file.

### Token tracking

At session start, create `.token-log/autoresearch-<session-id>.jsonl`.

After each experiment completes, append a JSONL entry:
`{"agent": "experiment-<N>", "model": "<model>", "total_tokens": N, "duration_ms": N, "timestamp": "<ISO>", "phase": "research-loop"}`

Also log setup, report generation, and learn phases. At session end (before
`=== Autoresearch: SESSION COMPLETE ===`), read the log and print a token usage
summary table with per-phase breakdown and estimated cost.
Blended rates (per 1K tokens): opus=$0.033, sonnet=$0.0066, haiku=$0.0006.

## Phase 2: Initialize Session

1. Generate session ID: `YYYY-MM-DD-HHMM-<mode>-<description>`
2. Create session directory: `.autoresearch/sessions/<session-id>/`
   **Token tracking**: create `.token-log/autoresearch-<session-id>.jsonl`
3. Load prior session journals from this project (read-only context)
4. Read holdout files:
   - `~/.claude/skills/autoresearch/holdout/research-procedures.md`
   - `~/.claude/skills/autoresearch/holdout/antipatterns.md`
5. Read `~/.claude/skills/autoresearch/LEARNINGS.md`
6. Save initial checkpoint:
   ```json
   {
     "session_id": "<id>",
     "mode": "parameter|code",
     "status": "running",
     "completed_experiments": 0,
     "max_experiments": 50,
     "best_experiment_id": null,
     "best_metric_value": null,
     "started_at": "<ISO-8601>",
     "last_checkpoint_at": "<ISO-8601>",
     "eval_command": "<command>",
     "metric_name": "<name>",
     "metric_direction": "maximize|minimize",
     "baseline_value": <value>,
     "param_space_path": "<path|null>",
     "target_files": "<files|null>",
     "program_md_path": "<path|null>",
     "git_stash_ref": "<ref|null>"
   }
   ```
7. Code mode: if working tree is dirty, `git stash` and save ref to checkpoint

## Phase 3: Research Loop

This is the core autonomous loop. Run without user input until stopping.

```
=== Autoresearch: Research Loop START [timestamp] ===
```

### For each experiment:

**Step 1 — Hypothesize**

Review the journal (all prior experiments this session) and analyzer output. Then formulate:

Parameter mode — output:
- `hypothesis`: WHY these specific values (reference prior experiment IDs)
- `params`: JSON dict matching parameter space schema
- `tags`: categorization (e.g., "threshold_sweep", "explore", "exploit")

Code mode — output:
- `hypothesis`: what change and why
- `changes_plan`: one sentence per file describing the planned edit
- Then make the actual edits using Edit tool. ONE conceptual change per experiment.

**Decision framework:**
- First 5 experiments: broad exploration (cover different regions)
- After finding a promising region: 3-5 experiments to refine
- After 3 refinements without improvement: switch to exploration
- After analyzer flags diminishing returns: try a completely new dimension
- NEVER repeat exact same params — check journal first
- ALWAYS reference prior experiments: "Based on EXP-003 showing X, I think..."

**Step 2 — Execute**

Parameter mode:
```bash
# Write params to file
echo '<params_json>' > .autoresearch/sessions/<session-id>/current_params.json
# Run eval with substituted path
<eval_command with {params_file} replaced>
```

Code mode:
```bash
# Files already edited in Step 1
<eval_command>
```

Timeout: 30 minutes per experiment. If exceeded, kill and record timeout error.

**Step 3 — Parse & Record**

Parse metric from stdout per Eval Command Protocol. Create journal entry:

```json
{
  "experiment_id": "EXP-NNNN",
  "session_id": "<session-id>",
  "timestamp": "<ISO-8601 UTC>",
  "hypothesis": "<your hypothesis>",
  "params": {"key": "value"},
  "changes_summary": null,
  "git_commit_hash": null,
  "metric_name": "<name>",
  "metric_value": <value>,
  "metric_direction": "maximize|minimize",
  "baseline_value": <baseline>,
  "all_metrics": {"metric1": val1, "metric2": val2},
  "is_improvement": <bool>,
  "is_valid": <bool>,
  "analysis": "<your analysis of the result>",
  "next_direction": "<what this suggests trying next>",
  "tags": ["tag1", "tag2"],
  "timing": {"experiment_sec": <N>, "researcher_sec": <N>},
  "error": null
}
```

Append to `journal.jsonl`. This is append-only — never modify past entries.

**Step 4 — Checkpoint**

Update checkpoint.json: increment completed_experiments, update best if new best, update timestamp.

**Step 5 — Analyze**

Run the analyzer script:
```bash
python ~/.claude/skills/autoresearch/scripts/analyzer.py \
  .autoresearch/sessions/<session-id>/journal.jsonl \
  --window <plateau_window>
```

Read the JSON output. Key signals:
- `is_plateau: true` → stopping condition
- `diminishing_returns: true` → consider stopping or changing approach
- Sensitivity data → informs next hypothesis

If analyzer script fails, continue without analyzer data.

**Step 6 — Git (code mode only)**

If metric improved over current best:
```bash
git add <target_files>
git commit -m "autoresearch(EXP-NNNN): <hypothesis_short>"
```

If metric regressed or stayed same:
```bash
git checkout -- <target_files>
```

**Step 7 — Status & Decision**

Print status line:
```
[EXP-NNNN] metric=X.XX (best=Y.YY) | hypothesis: <short> | improved/no change/regression
```

Every 10 experiments, print summary:
```
=== Progress: N/M experiments | best=Y.YY (+Z% over baseline) | plateau: no ===
```

Check stopping conditions:
- Budget exhausted (max experiments or max hours)
- Plateau detected (N experiments without improvement)
- 3 consecutive eval failures
- Analyzer recommends stop (diminishing returns)

If any triggered → Phase 4. Otherwise → next experiment.

## Phase 4: Report Generation

```
=== Autoresearch: Report Generation START [timestamp] ===
```

Run the report generator:
```bash
python ~/.claude/skills/autoresearch/scripts/report_generator.py \
  .autoresearch/sessions/<session-id>/journal.jsonl \
  --output <report_destination> \
  --top-n 5
```

If report generator fails, write a minimal summary directly:
- Session ID, total experiments, best experiment ID
- Best metric value and improvement over baseline
- Top-3 configurations

Update checkpoint status to "completed".

Print to user:
```
=== Autoresearch: RESULTS ===
Best: <metric>=<value> (+X% over baseline)
Experiments: N total, M valid, K improvements
Runtime: Xh Ym
Report: <path>
=== Autoresearch: Report Generation DONE [timestamp] ===
```

## Phase 5: Learn

1. Reflect on the session:
   - Did any hypothesis pattern consistently work or fail?
   - Was there an unexpected finding?
   - Did any antipattern occur despite warnings?

2. If a new insight is worth preserving, read `~/.claude/skills/autoresearch/LEARNINGS.md`, find the last L-number, and append a new entry:
   ```markdown
   ### L-NNN: <title>
   **Status:** NOTED
   **Source:** <session-id>
   **Finding:** <what was discovered>
   **Impact:** <how this affects future sessions>
   **Action:** <what to do about it>
   ```

3. If a pattern appeared in 2+ sessions → add to holdout files and mark learning as MATERIALIZED.

4. Commit skill updates:
   ```bash
   cd ~/.claude/skills && git add autoresearch/ && git commit -m "autoresearch: update learnings (L-NNN)" && git push
   ```

5. Code mode: restore stashed changes if applicable:
   ```bash
   git stash pop  # in project directory
   ```
   If conflicts, warn user and leave stash intact.

6. **Token cost summary**: include estimated cost in the final summary line.
   Calculate: total_tokens × blended_rate (opus=$0.033/1K, sonnet=$0.0066/1K, haiku=$0.0006/1K).
   Example: "~168k tokens (~$5.54), ~2 minutes". The cost goes in every experiment result too.
7. Print: `=== Autoresearch: SESSION COMPLETE ===`

## Parameter Space Definition

For parameter mode, provide a JSON file or define interactively:

```json
{
  "parameters": {
    "learning_rate": {"type": "float", "min": 0.0001, "max": 0.1, "default": 0.001},
    "batch_size": {"type": "int", "min": 8, "max": 256, "default": 32},
    "dropout": {"type": "float", "min": 0.0, "max": 0.5, "default": 0.1},
    "optimizer": {"type": "enum", "values": ["adam", "sgd", "adamw"], "default": "adam"}
  },
  "constraints": [
    "learning_rate should be tested at log scale first, then refined"
  ],
  "validity_gates": {
    "min_samples": 100,
    "max_metric": 1.0,
    "min_accuracy": 0.60
  }
}
```

If no param-space file is provided, ask the user to define parameters interactively during setup.

## Resume Protocol

`/autoresearch --resume [session-id]`

1. Find session: if session-id provided, load that checkpoint. Otherwise, find most recent session with `status: "running"`.
2. Load checkpoint.json and full journal.jsonl
3. Verify eval command still works (run baseline)
4. Continue research loop from `completed_experiments + 1`
5. Code mode: verify git state matches expectation (no uncommitted changes to target files)

## Error Handling Summary

| Error | Action |
|-------|--------|
| Eval command returns non-zero | Record error in journal, increment failure counter |
| Eval command timeout (>30 min) | Kill process, record timeout, increment failure counter |
| 3 consecutive eval failures | Pause, ask user if eval command is correct |
| Metric parsing fails | Record parsing error, increment failure counter |
| Analyzer script fails | Log warning, continue without analyzer data |
| Report generator fails | Write minimal summary directly |
| Git stash pop conflicts | Warn user, leave stash intact |
| 10 experiments with 0 valid results | Pause, ask user to verify eval command and validity gates |
| Code doesn't compile after edit | Revert files, record error, try different approach |
