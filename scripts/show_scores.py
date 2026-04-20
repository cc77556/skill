#!/usr/bin/env python3
"""Quick score viewer for PinchBench results."""
import json, sys

if len(sys.argv) < 2:
    print("Usage: python3 show_scores.py results/xxxx.json")
    sys.exit(1)

d = json.load(open(sys.argv[1]))
print(f"Model: {d['model']}")
print(f"Run ID: {d['run_id']}")
print()

for t in d["tasks"]:
    score = t["grading"]["mean"] * 100
    icon = "+++" if score >= 100 else "+-" if score > 0 else "---"
    print(f"{icon} {t['task_id']}: {score:.0f}%")
    if "runs" in t["grading"]:
        for k, v in t["grading"]["runs"][0]["breakdown"].items():
            sub = "[v]" if v >= 1.0 else "[~]" if v > 0 else "[x]"
            print(f"    {sub} {k}: {v}")
