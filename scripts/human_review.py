#!/usr/bin/env python3
"""
PinchBench Human Review Tool
讀取 benchmark 結果，產生人工評分表，合併自動+人工分數。

用法:
  # 產生人工評分表（從最新結果）
  python3 human_review.py generate results/0007_*.json

  # 填完後，合併檢視
  python3 human_review.py compare results/0007_*.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_review(result_file: str):
    """從 benchmark 結果產生人工評分表"""
    with open(result_file) as f:
        data = json.load(f)

    model = data["model"]
    run_id = data["run_id"]

    review = {
        "model": model,
        "run_id": run_id,
        "reviewed_at": None,
        "reviewer": "",
        "tasks": []
    }

    for task in data["tasks"]:
        auto_breakdown = task["grading"]["runs"][0]["breakdown"]
        review_task = {
            "task_id": task["task_id"],
            "name": task["frontmatter"]["name"],
            "auto_score": task["grading"]["mean"],
            "auto_breakdown": auto_breakdown,
            "human_score": None,        # ← 填 0.0 ~ 1.0
            "human_notes": "",          # ← 填你的觀察
            "human_breakdown": {        # ← 各項人工評分
                "correctness": None,    # 結果正確嗎？
                "completeness": None,   # 有沒有做完全部要求？
                "readability": None     # 輸出好讀嗎？
            }
        }
        review_task["_hint"] = (
            "填 human_score (0.0-1.0), human_notes, "
            "和 human_breakdown 各項 (0.0-1.0)"
        )
        review["tasks"].append(review_task)

    # Save review file
    review_file = result_file.replace(".json", "_human_review.json")
    with open(review_file, "w") as f:
        json.dump(review, f, indent=2, ensure_ascii=False)

    print(f"已產生人工評分表: {review_file}")
    print(f"共 {len(review['tasks'])} 題待評分")
    print()
    print("請用編輯器打開，填寫以下欄位：")
    print("  human_score:  整體人工分數 (0.0 ~ 1.0)")
    print("  human_notes:  你的觀察和備註")
    print("  human_breakdown:")
    print("    correctness:   結果正確嗎？")
    print("    completeness:  有沒有做完全部要求？")
    print("    readability:   輸出好讀嗎？")
    print()
    print(f"填完後執行: python3 human_review.py compare {result_file}")


def compare_review(result_file: str):
    """比較自動評分和人工評分"""
    review_file = result_file.replace(".json", "_human_review.json")

    if not Path(review_file).exists():
        print(f"找不到人工評分表: {review_file}")
        print(f"先執行: python3 human_review.py generate {result_file}")
        return

    with open(result_file) as f:
        auto_data = json.load(f)
    with open(review_file) as f:
        review_data = json.load(f)

    print(f"模型: {auto_data['model']}")
    print(f"Run: {auto_data['run_id']}")
    print(f"評審: {review_data.get('reviewer', '(未填)')}")
    print("=" * 70)
    print(f"{'題目':<25} {'自動':>6} {'人工':>6} {'差異':>6}  備註")
    print("-" * 70)

    auto_total = 0
    human_total = 0
    reviewed = 0

    for task in review_data["tasks"]:
        auto = task["auto_score"]
        human = task.get("human_score")
        notes = task.get("human_notes", "")[:30]

        auto_total += auto

        if human is not None:
            human_total += human
            reviewed += 1
            diff = human - auto
            diff_str = f"{diff:+.0%}"
            if diff < 0:
                diff_str = f"\033[91m{diff_str}\033[0m"  # red
            elif diff > 0:
                diff_str = f"\033[92m{diff_str}\033[0m"  # green
            else:
                diff_str = f"  ={diff_str[1:]}"
        else:
            human_total += auto  # fallback
            diff_str = "  --"
            notes = "(未評分)"

        print(f"{task['task_id']:<25} {auto:>5.0%} {(human if human is not None else auto):>5.0%} {diff_str:>6}  {notes}")

    total_tasks = len(review_data["tasks"])
    print("-" * 70)
    print(f"{'平均':<25} {auto_total/total_tasks:>5.0%} {human_total/total_tasks:>5.0%}")
    print()

    if reviewed < total_tasks:
        print(f"⚠️  還有 {total_tasks - reviewed} 題未人工評分")

    # Show breakdown for reviewed tasks
    print()
    for task in review_data["tasks"]:
        if task.get("human_score") is None:
            continue
        hb = task.get("human_breakdown", {})
        if not any(v is not None for v in hb.values()):
            continue
        print(f"📋 {task['task_id']} — 人工細項:")
        for k, v in hb.items():
            if v is not None:
                icon = "✅" if v >= 0.8 else "⚠️" if v >= 0.5 else "❌"
                print(f"   {icon} {k}: {v:.0%}")
        if task.get("human_notes"):
            print(f"   💬 {task['human_notes']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 human_review.py generate <result.json>")
        print("  python3 human_review.py compare <result.json>")
        sys.exit(1)

    cmd = sys.argv[1]
    result_file = sys.argv[2]

    if cmd == "generate":
        generate_review(result_file)
    elif cmd == "compare":
        compare_review(result_file)
    else:
        print(f"未知指令: {cmd}")
