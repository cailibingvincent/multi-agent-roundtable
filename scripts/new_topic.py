#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""new_topic.py - 开一个新议题

用法:
  python new_topic.py "是否加仓某标的"
  python new_topic.py "是否加仓某标的" --participants workbuddy,claude,doubao --red-team claude --rounds 3
"""
import sys, json, shutil, argparse
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
TOPICS = RT / "topics"
TEMPLATE = TOPICS / "_template"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("short", help="议题短名，10 字以内，例：是否加仓某标的")
    ap.add_argument("--participants", default="workbuddy,claude,doubao")
    ap.add_argument("--red-team", default="claude")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--deadline", default="")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print("[ERR] 找不到模板目录 topics/_template")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    base = f"{today}-{args.short.strip()}"
    target = TOPICS / base
    n = 2
    while target.exists():
        target = TOPICS / f"{base}-{n}"
        n += 1

    target.mkdir(parents=True)
    (target / "assets").mkdir()

    # topic.json
    tj = json.loads((TEMPLATE / "topic.json").read_text(encoding="utf-8"))
    tj.update({
        "id": target.name,
        "title": args.short.strip(),
        "created": today,
        "rounds": args.rounds,
        "current_round": 1,
        "participants": [p.strip() for p in args.participants.split(",") if p.strip()],
        "red_team": args.red_team.strip(),
        "deadline": args.deadline,
    })
    (target / "topic.json").write_text(
        json.dumps(tj, ensure_ascii=False, indent=2), encoding="utf-8")

    # 00_brief.md
    shutil.copy(TEMPLATE / "00_brief.md", target / "00_brief.md")

    print(f"[OK] 议题已创建: {target}")
    print("")
    print("下一步:")
    print(f"  1. 填写背景与约束: {target / '00_brief.md'}")
    print(f"  2. 确认参与方/红队: {target / 'topic.json'}")
    print("  3. 把 AGENT_BRIEF.md 贴给每个 Agent")
    print("")
    print("R1 独立成稿（不给任何 Agent 看他人稿）:")
    print(f"     python scripts/digest.py {target.name} --brief-only")
    print("R2 起打包全部上下文:")
    print(f"     python scripts/digest.py {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
