#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""status.py - 查看全部议题进度

用法: python status.py
"""
import sys, json, re
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
TOPICS = RT / "topics"


def load(d):
    p = d / "topic.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    dirs = [d for d in sorted(TOPICS.iterdir())
            if d.is_dir() and d.name != "_template"]
    if not dirs:
        print("还没有议题。用 python scripts/new_topic.py \"短名\" 开题。")
        return 0

    print("=" * 72)
    print(f"{'议题':<34}{'轮次':<8}{'消息':<7}{'红队':<12}状态")
    print("=" * 72)
    for d in dirs:
        tj = load(d)
        msgs = sorted(d.glob("R*_*.md"))
        rounds = set()
        for f in msgs:
            m = re.match(r"^R(\d\d)_", f.name)
            if m:
                rounds.add(int(m.group(1)))
        cur = tj.get("current_round", "?")
        mx = max(rounds) if rounds else 0
        status = "已结题" if (d / "decision.md").exists() else "进行中"
        name = d.name if len(d.name) <= 32 else d.name[:29] + "..."
        print(f"{name:<34}{f'{cur}/{tj.get('rounds','?')}':<8}{len(msgs):<7}{tj.get('red_team','-'):<12}{status}")
        if msgs:
            last = max(msgs, key=lambda p: p.stat().st_mtime)
            t = datetime.fromtimestamp(last.stat().st_mtime).strftime("%m-%d %H:%M")
            print(f"{'':<34}最新: {last.name}  ({t})")
        if mx and cur != "?" and isinstance(cur, int) and mx > cur:
            print(f"{'':<34}[提醒] 已有 R{mx} 消息，但 topic.json 的 current_round 仍是 {cur}，请更新")

    print("=" * 72)
    inbox = list((RT / "inbox").glob("*.md"))
    outbox = list((RT / "outbox").glob("*.md"))
    print(f"inbox 待处理: {len(inbox)}     outbox 简报: {len(outbox)}")
    if inbox:
        for f in inbox:
            print(f"  - {f.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
