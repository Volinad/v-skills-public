#!/usr/bin/env python3
"""Autoresearch Report Generator — produces markdown report from journal.

Reads journal.jsonl and generates AUTORESEARCH-REPORT-YYYY-MM-DD-HHMM.md.

Usage:
    python report_generator.py <journal_path> [--output path] [--top-n 5]
"""

import json
import sys
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_journal(path: str) -> list[dict]:
    """Load journal entries from JSONL file."""
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def format_duration(seconds: float) -> str:
    """Format seconds as Xh Ym."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def get_top_n(entries: list[dict], n: int = 5) -> list[dict]:
    """Get top N experiments by primary metric."""
    valid = [e for e in entries if e.get("is_valid") and e.get("metric_value") is not None]
    if not valid:
        return []

    direction = entries[0].get("metric_direction", "maximize")
    reverse = direction == "maximize"
    return sorted(valid, key=lambda e: e["metric_value"], reverse=reverse)[:n]


def compute_sensitivity(entries: list[dict]) -> dict[str, list[dict]]:
    """Parameter sensitivity analysis."""
    param_metrics = defaultdict(lambda: defaultdict(list))

    for entry in entries:
        if entry.get("error") or entry.get("metric_value") is None:
            continue
        params = entry.get("params")
        if not params:
            continue
        for key, value in params.items():
            param_metrics[key][str(value)].append(entry["metric_value"])

    result = {}
    for param_name, value_groups in param_metrics.items():
        if len(value_groups) < 2:
            continue
        rows = []
        for value, metrics in sorted(value_groups.items()):
            n = len(metrics)
            mean = sum(metrics) / n
            std = (sum((m - mean) ** 2 for m in metrics) / (n - 1)) ** 0.5 if n > 1 else 0.0
            rows.append({"value": value, "mean": round(mean, 3), "std": round(std, 3), "count": n})
        result[param_name] = rows

    return result


def generate_report(entries: list[dict], top_n: int = 5) -> str:
    """Generate markdown report from journal entries."""
    if not entries:
        return "# Autoresearch Report\n\nNo experiments recorded.\n"

    # Session info
    session_id = entries[0].get("session_id", "unknown")
    mode = entries[0].get("metric_direction", "maximize")
    metric_name = entries[0].get("metric_name", "metric")
    metric_direction = entries[0].get("metric_direction", "maximize")
    baseline = entries[0].get("baseline_value")

    # Compute stats
    total = len(entries)
    valid = [e for e in entries if e.get("is_valid")]
    errors = [e for e in entries if e.get("error")]
    improvements = [e for e in entries if e.get("is_improvement")]

    # Best experiment
    top = get_top_n(entries, top_n)
    best = top[0] if top else None
    best_value = best["metric_value"] if best else None

    # Improvement percentage
    if baseline and best_value and baseline != 0:
        if metric_direction == "maximize":
            improvement_pct = ((best_value - baseline) / baseline) * 100
        else:
            improvement_pct = ((baseline - best_value) / baseline) * 100
    else:
        improvement_pct = 0

    # Runtime
    total_experiment_sec = sum(
        e.get("timing", {}).get("experiment_sec", 0) for e in entries
    )

    # Detect mode from entries
    has_params = any(e.get("params") for e in entries)
    has_changes = any(e.get("changes_summary") for e in entries)
    report_mode = "code" if has_changes and not has_params else "parameter"

    # Stopping reason
    last = entries[-1]
    if last.get("error"):
        stop_reason = "eval failures"
    elif total >= 50:
        stop_reason = "budget exhausted"
    else:
        stop_reason = "completed"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build report
    lines = []

    # Frontmatter
    lines.append("---")
    lines.append("type: autoresearch-report")
    lines.append(f"session: {session_id}")
    lines.append(f"mode: {report_mode}")
    lines.append(f"metric: {metric_name}")
    lines.append(f"direction: {metric_direction}")
    if baseline is not None:
        lines.append(f"baseline: {baseline}")
    if best_value is not None:
        lines.append(f"best: {round(best_value, 4)}")
    lines.append(f"improvement: {round(improvement_pct, 1)}%")
    lines.append(f"experiments: {total}")
    lines.append(f"valid: {len(valid)}")
    lines.append(f"runtime: {format_duration(total_experiment_sec)}")
    lines.append(f"created: {now}")
    lines.append("---")
    lines.append("")

    # Title
    desc = session_id.split("-", 4)[-1] if "-" in session_id else session_id
    lines.append(f"# Autoresearch Report: {desc}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- Experiments: {total} total, {len(valid)} valid, {len(improvements)} improvements over baseline")
    if best_value is not None:
        lines.append(f"- Best result: {metric_name}={round(best_value, 4)} (+{round(improvement_pct, 1)}% over baseline)")
    lines.append(f"- Runtime: {format_duration(total_experiment_sec)}")
    lines.append(f"- Stopping reason: {stop_reason}")
    if errors:
        lines.append(f"- Errors: {len(errors)} experiments failed")
    lines.append("")

    # Top-N configurations
    lines.append(f"## Top-{top_n} Configurations")
    lines.append("")
    if top:
        lines.append(f"| Rank | Experiment | {metric_name} | Secondary Metrics | Key Params/Changes | Notes |")
        lines.append("|------|-----------|" + "-" * (len(metric_name) + 2) + "|-------------------|-------------------|-------|")
        for i, exp in enumerate(top, 1):
            exp_id = exp["experiment_id"]
            metric_val = round(exp["metric_value"], 4)

            # Secondary metrics
            all_m = exp.get("all_metrics", {})
            secondary = ", ".join(
                f"{k}={round(v, 2) if isinstance(v, float) else v}"
                for k, v in all_m.items()
                if k != metric_name
            )[:50]

            # Key params or changes
            if exp.get("params"):
                key_params = ", ".join(
                    f"{k}={v}" for k, v in list(exp["params"].items())[:3]
                )[:50]
            elif exp.get("changes_summary"):
                key_params = exp["changes_summary"][:50]
            else:
                key_params = "-"

            tags = ", ".join(exp.get("tags", []))[:30]
            lines.append(f"| {i} | {exp_id} | {metric_val} | {secondary} | {key_params} | {tags} |")
        lines.append("")
    else:
        lines.append("No valid experiments found.")
        lines.append("")

    # Parameter sensitivity (parameter mode only)
    if has_params:
        sensitivity = compute_sensitivity(entries)
        if sensitivity:
            lines.append("## Parameter Sensitivity")
            lines.append("")
            for param_name, rows in sensitivity.items():
                lines.append(f"### {param_name}")
                lines.append(f"| Value | Mean {metric_name} | Std | Count |")
                lines.append("|-------|" + "-" * (len(metric_name) + 7) + "|------|-------|")
                for row in rows:
                    lines.append(f"| {row['value']} | {row['mean']} | {row['std']} | {row['count']} |")
                lines.append("")

    # Change log (code mode only)
    if has_changes:
        committed = [e for e in entries if e.get("git_commit_hash")]
        if committed:
            lines.append("## Change Log")
            lines.append("")
            lines.append("| Experiment | Commit | Change | Metric Delta |")
            lines.append("|-----------|--------|--------|-------------|")
            prev_best = baseline
            for exp in committed:
                delta = round(exp["metric_value"] - (prev_best or 0), 4)
                sign = "+" if delta > 0 else ""
                lines.append(
                    f"| {exp['experiment_id']} | {exp['git_commit_hash'][:7]} "
                    f"| {exp.get('changes_summary', '-')[:60]} | {sign}{delta} |"
                )
                prev_best = exp["metric_value"]
            lines.append("")

    # Researcher insights
    lines.append("## Researcher Insights")
    lines.append("")

    # Extract key insights from hypotheses and analyses
    successful = [e for e in entries if e.get("is_improvement") and e.get("analysis")]
    failed = [e for e in entries if not e.get("is_improvement") and not e.get("error") and e.get("analysis")]

    if successful:
        lines.append("### What Worked")
        for exp in successful[:5]:
            lines.append(f"- **{exp['experiment_id']}**: {exp.get('analysis', '')[:120]}")
        lines.append("")

    if failed:
        lines.append("### What Didn't Work")
        for exp in failed[:5]:
            lines.append(f"- **{exp['experiment_id']}**: {exp.get('analysis', '')[:120]}")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    if entries:
        last_entry = entries[-1]
        if last_entry.get("next_direction"):
            lines.append(f"- Next direction (from last experiment): {last_entry['next_direction']}")
    if best:
        lines.append(f"- Best configuration ({best['experiment_id']}) should be validated on additional data periods")
        if has_params and best.get("params"):
            lines.append(f"- Consider testing interactions between top parameters")
    lines.append("")

    # Experiment log (abbreviated)
    lines.append("## Experiment Log (abbreviated)")
    lines.append("")

    show_entries = entries[:5] + entries[-5:] if len(entries) > 10 else entries
    shown_ids = set()

    lines.append("| # | Experiment | Metric | Hypothesis (short) | Result |")
    lines.append("|---|-----------|--------|-------------------|--------|")
    for i, exp in enumerate(show_entries):
        if exp["experiment_id"] in shown_ids:
            continue
        shown_ids.add(exp["experiment_id"])
        metric_val = round(exp["metric_value"], 4) if exp.get("metric_value") is not None else "ERROR"
        hyp = exp.get("hypothesis", "")[:60]
        if exp.get("error"):
            result = "error"
        elif exp.get("is_improvement"):
            result = "improved"
        elif exp.get("is_valid"):
            result = "valid"
        else:
            result = "invalid"

        idx = int(exp["experiment_id"].split("-")[1]) if "-" in exp["experiment_id"] else i
        lines.append(f"| {idx} | {exp['experiment_id']} | {metric_val} | {hyp} | {result} |")

        if i == 4 and len(entries) > 10:
            lines.append(f"| ... | ... ({len(entries) - 10} more) | ... | ... | ... |")

    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Autoresearch report generator")
    parser.add_argument("journal_path", help="Path to journal.jsonl file")
    parser.add_argument("--output", help="Output file path (default: auto-generated in session dir)")
    parser.add_argument("--top-n", type=int, default=5, help="Number of top configs to show (default: 5)")
    args = parser.parse_args()

    journal_path = Path(args.journal_path)
    if not journal_path.exists():
        print(f"Error: Journal file not found: {args.journal_path}", file=sys.stderr)
        sys.exit(1)

    entries = load_journal(str(journal_path))
    report = generate_report(entries, args.top_n)

    if args.output:
        output_path = Path(args.output)
    else:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
        output_path = journal_path.parent / f"AUTORESEARCH-REPORT-{now}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
