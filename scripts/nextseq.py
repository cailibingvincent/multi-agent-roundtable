#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""nextseq.py - 查询议题的下一个可用消息序号（防撞号）

起因：主持人（workbuddy）在 R1 连撞两次号（003 撞 qclaw、004 撞 doubao），
原因是没先 ls 目录就写文件。协议写了规则，但人肉执行会偷懒——所以做成工具。

用法:
  python nextseq.py <议题id> [--round 1]        # 打印下一个可用序号和完整文件名
  python nextseq.py <议题id> --agent workbuddy  # 带作者名，直接给可复制的文件名
"""
import sys, re, json, argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
TOPICS = RT / "topics"


def resolve(t):
    if (TOPICS / t).exists():
        return TOPICS / t
    cands = [d for d in TOPICS.iterdir() if d.is_dir() and t in d.name]
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        print("[ERR] 匹配到多个议题：")
        for c in cands:
            print("   ", c.name)
        return None
    print(f"[ERR] 找不到议题: {t}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--round", type=int, default=None, help="轮次；不传则自动读 topic.json 的 current_round")
    ap.add_argument("--agent", default=None, help="你的 agent_id，给出完整文件名")
    args = ap.parse_args()

    d = resolve(args.topic)
    if not d:
        return 1

    # 轮次自动推断：优先读 topic.json 的 current_round，避免手写 R01_010 这类错前缀
    if args.round is None:
        try:
            tj = json.loads((d / "topic.json").read_text(encoding="utf-8"))
            args.round = int(tj.get("current_round", 1))
        except Exception:
            args.round = 1

    used = []
    for f in d.glob("R*_*.md"):
        m = re.match(r"^R(\d\d)_(\d\d\d)_", f.name)
        if m:
            used.append((int(m.group(2)), f.name))
    used.sort()

    nxt = (used[-1][0] + 1) if used else 1
    print(f"议题: {d.name}")
    print(f"已占用序号: {[u[0] for u in used]}")
    print(f"下一个可用序号: {nxt:03d}")
    print("")
    if args.agent:
        print(f"文件名: R{args.round:02d}_{nxt:03d}_{args.agent}.md")
        print(f"frontmatter id: R{args.round:02d}-{nxt:03d}")
    else:
        print(f"文件名前缀: R{args.round:02d}_{nxt:03d}_<agent>.md")
    print("")
    print("提醒：先创建文件占位，再写内容。写完再有人抢号，你就是先到者。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
