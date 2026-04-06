#!/usr/bin/env python3
"""Autoresearch Analyzer — quantitative analysis of experiment journals.

Reads a journal.jsonl file and outputs analysis as JSON to stdout.
No LLM calls — pure Python computation.

Usage:
    python analyzer.py <journal_path> [--window 10] [--pareto metric1,metric2]
"""

import json
import sys
import argparse
from collections import defaultdict
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


def analyze_sensitivity(entries: list[dict]) -> dict:
    """Parameter sensitivity: mean/std of metric per parameter value.

    For each parameter that varies across experiments, compute the
    mean and standard deviation of the primary metric for each value.
    """
    if not entries:
        return {}

    # Collect metric values per (param_name, param_value)
    param_metrics = defaultdict(lambda: defaultdict(list))

    for entry in entries:
        if entry.get("error") or entry.get("metric_value") is None:
            continue
        params = entry.get("params")
        if not params:
            continue
        metric = entry["metric_value"]
        for key, value in params.items():
            # Convert value to string for grouping
            param_metrics[key][str(value)].append(metric)

    # Compute stats
    result = {}
    for param_name, value_groups in param_metrics.items():
        if len(value_groups) < 2:
            continue  # Skip params that don't vary
        param_result = []
        for value, metrics in sorted(value_groups.items()):
            n = len(metrics)
            mean = sum(metrics) / n
            if n > 1:
                variance = sum((m - mean) ** 2 for m in metrics) / (n - 1)
                std = variance ** 0.5
            else:
                std = 0.0
            param_result.append({
                "value": value,
                "mean_metric": round(mean, 4),
                "std_metric": round(std, 4),
                "count": n,
            })
        result[param_name] = param_result

    return result


def detect_plateau(entries: list[dict], window: int = 10) -> dict:
    """Check if the best metric has improved in the last N experiments.

    Returns plateau status and experiments since last improvement.
    """
    if not entries:
        return {"is_plateau": False, "best_metric": None, "experiments_since_improvement": 0}

    direction = entries[0].get("metric_direction", "maximize")
    is_maximize = direction == "maximize"

    valid_entries = [e for e in entries if e.get("metric_value") is not None and not e.get("error")]
    if not valid_entries:
        return {"is_plateau": False, "best_metric": None, "experiments_since_improvement": 0}

    best_metric = None
    best_idx = 0

    for i, entry in enumerate(valid_entries):
        metric = entry["metric_value"]
        if best_metric is None:
            best_metric = metric
            best_idx = i
        elif (is_maximize and metric > best_metric) or (not is_maximize and metric < best_metric):
            best_metric = metric
            best_idx = i

    experiments_since = len(valid_entries) - 1 - best_idx

    return {
        "is_plateau": experiments_since >= window,
        "best_metric": round(best_metric, 4) if best_metric is not None else None,
        "best_experiment_id": valid_entries[best_idx]["experiment_id"] if valid_entries else None,
        "experiments_since_improvement": experiments_since,
        "total_valid_experiments": len(valid_entries),
    }


def compute_pareto(entries: list[dict], metric1: str, metric2: str) -> list[dict]:
    """Find Pareto-optimal configurations for two metrics.

    A configuration is Pareto-optimal if no other configuration is
    strictly better on both metrics simultaneously.
    Both metrics are assumed to be maximized.
    """
    points = []
    for entry in entries:
        if entry.get("error") or not entry.get("all_metrics"):
            continue
        m = entry["all_metrics"]
        if metric1 in m and metric2 in m:
            points.append({
                "experiment_id": entry["experiment_id"],
                metric1: m[metric1],
                metric2: m[metric2],
                "params": entry.get("params"),
            })

    if not points:
        return []

    # Find Pareto front
    pareto = []
    for p in points:
        dominated = False
        for q in points:
            if q is p:
                continue
            if q[metric1] >= p[metric1] and q[metric2] >= p[metric2] and \
               (q[metric1] > p[metric1] or q[metric2] > p[metric2]):
                dominated = True
                break
        if not dominated:
            pareto.append(p)

    return sorted(pareto, key=lambda x: x[metric1], reverse=True)


def detect_diminishing_returns(entries: list[dict], window_size: int = 5) -> dict:
    """Detect if the rate of improvement is declining.

    Computes improvement rate over sliding windows. If the rate
    drops below 1% for 3 consecutive windows, flags diminishing returns.
    """
    valid = [e for e in entries if e.get("metric_value") is not None and not e.get("error")]
    if len(valid) < window_size * 2:
        return {"diminishing_returns": False, "windows_analyzed": 0}

    direction = entries[0].get("metric_direction", "maximize")
    is_maximize = direction == "maximize"

    # Track cumulative best over time
    bests = []
    current_best = None
    for entry in valid:
        m = entry["metric_value"]
        if current_best is None:
            current_best = m
        elif (is_maximize and m > current_best) or (not is_maximize and m < current_best):
            current_best = m
        bests.append(current_best)

    # Compute improvement rate per window
    rates = []
    for i in range(window_size, len(bests)):
        prev_best = bests[i - window_size]
        curr_best = bests[i]
        if prev_best != 0:
            rate = abs(curr_best - prev_best) / abs(prev_best)
        else:
            rate = 0.0
        rates.append(round(rate, 6))

    # Check for 3 consecutive windows below 1%
    consecutive_low = 0
    for rate in rates:
        if rate < 0.01:
            consecutive_low += 1
            if consecutive_low >= 3:
                return {
                    "diminishing_returns": True,
                    "windows_analyzed": len(rates),
                    "improvement_rates": rates[-5:],
                }
        else:
            consecutive_low = 0

    return {
        "diminishing_returns": False,
        "windows_analyzed": len(rates),
        "improvement_rates": rates[-5:] if rates else [],
    }


def compute_summary(entries: list[dict]) -> dict:
    """Compute session summary statistics."""
    total = len(entries)
    valid = sum(1 for e in entries if e.get("is_valid"))
    errors = sum(1 for e in entries if e.get("error"))
    improvements = sum(1 for e in entries if e.get("is_improvement"))

    metrics = [e["metric_value"] for e in entries if e.get("metric_value") is not None]

    return {
        "total_experiments": total,
        "valid_experiments": valid,
        "error_experiments": errors,
        "improvements": improvements,
        "metric_range": [round(min(metrics), 4), round(max(metrics), 4)] if metrics else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Autoresearch journal analyzer")
    parser.add_argument("journal_path", help="Path to journal.jsonl file")
    parser.add_argument("--window", type=int, default=10, help="Plateau detection window (default: 10)")
    parser.add_argument("--pareto", help="Two comma-separated metric names for Pareto analysis")
    args = parser.parse_args()

    if not Path(args.journal_path).exists():
        print(json.dumps({"error": f"Journal file not found: {args.journal_path}"}))
        sys.exit(1)

    entries = load_journal(args.journal_path)

    if not entries:
        print(json.dumps({"error": "Journal is empty"}))
        sys.exit(0)

    result = {
        "summary": compute_summary(entries),
        "plateau": detect_plateau(entries, args.window),
        "diminishing_returns": detect_diminishing_returns(entries),
        "sensitivity": analyze_sensitivity(entries),
    }

    if args.pareto:
        metrics = args.pareto.split(",")
        if len(metrics) == 2:
            result["pareto"] = compute_pareto(entries, metrics[0].strip(), metrics[1].strip())

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
