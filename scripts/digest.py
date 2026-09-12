#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""digest.py - 把议题打包成单文件简报，用于桥接网页版 Agent

用法:
  python digest.py <议题id>                 # 打包全部上下文
  python digest.py <议题id> --brief-only    # 只打包背景（R1 独立成稿用）
  python digest.py <议题id> --round 2       # 只含第 2 轮及以前的消息
  python digest.py <议题id> --hide claude   # 排除某人的消息（防锚定）
"""
import sys, json, argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
TOPICS = RT / "topics"
OUTBOX = RT / "outbox"


def resolve(topic_id):
    if (TOPICS / topic_id).exists():
        return TOPICS / topic_id
    cands = [d for d in TOPICS.iterdir() if d.is_dir() and topic_id in d.name]
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        print("[ERR] 匹配到多个议题，请用完整 ID:")
        for c in cands:
            print("   ", c.name)
        return None
    print(f"[ERR] 找不到议题: {topic_id}")
    return None


def pick_messages(topic_dir, max_round=None, hide=None):
    out = []
    for f in sorted(topic_dir.glob("R*_*.md")):
        try:
            rnd = int(f.name[1:3])
        except ValueError:
            continue
        if max_round and rnd > max_round:
            continue
        if hide and f.name[:-3].split("_")[-1] == hide:
            continue
        out.append(f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--brief-only", action="store_true", help="只打包背景，不含任何消息")
    ap.add_argument("--round", type=int, default=None)
    ap.add_argument("--hide", default=None, help="排除某 agent 的消息")
    ap.add_argument("--assign", default=None,
                    help="本轮分工文件路径；省略则自动找 topics/<id>/assign_R<n>.md")
    ap.add_argument("--pick", default=None,
                    help="只打包指定消息文件（逗号分隔文件名）。桥接 Agent 用：包太大发不出去")
    ap.add_argument("--out", default=None, help="输出文件名（默认 <议题>_pack.md）")
    ap.add_argument("--no-brief", action="store_true", help="不打包 00_brief（配合 --pick 做瘦身包）")
    args = ap.parse_args()

    topic_dir = resolve(args.topic)
    if not topic_dir:
        return 1

    OUTBOX.mkdir(exist_ok=True)
    brief = (topic_dir / "00_brief.md").read_text(encoding="utf-8") \
        if (topic_dir / "00_brief.md").exists() else "（无 00_brief.md）"
    tj = json.loads((topic_dir / "topic.json").read_text(encoding="utf-8")) \
        if (topic_dir / "topic.json").exists() else {}

    if args.pick:
        want = [w.strip() for w in args.pick.split(",") if w.strip()]
        msgs = []
        for w in want:
            f = topic_dir / w
            if f.exists():
                msgs.append(f)
            else:
                print(f"[WARN] 找不到消息文件: {w}")
        msgs.sort()
        # 瘦身包：明确告知接收方这是节选，避免它误以为看到了全部
        if msgs:
            brief += "\n\n> **注意：本简报为节选包（--pick），只包含主持人指定的关键消息。"
            brief += "\n> 你未看到全部历史消息——引用时只能引用本包内出现的内容，"
            brief += "\n> 不要假设包外的消息说了什么。**\n"
    else:
        msgs = [] if args.brief_only else pick_messages(topic_dir, args.round, args.hide)

    assets = sorted([p.name for p in (topic_dir / "assets").iterdir()]) \
        if (topic_dir / "assets").exists() else []

    lines = []
    lines.append(f"# 议题简报 · {topic_dir.name}")
    lines.append("")
    lines.append("> 本文件由 digest.py 自动生成。你是被邀请参与讨论的 Agent 之一。")
    lines.append("> 完整规则见下方《接入规则》，严格执行。")
    lines.append("")
    lines.append("## 你的任务")
    lines.append("")
    if args.brief_only:
        lines.append("**当前处于 Round 1（独立成稿阶段）。**")
        lines.append("你没有看到任何其他 Agent 的观点——这是刻意的。请先独立给出你自己的判断，")
        lines.append("不要猜测别人会怎么说，也不要为了周全而回避结论。")
    else:
        lines.append(f"**当前处于 Round {tj.get('current_round', '?')}（交叉质询/收敛阶段）。**")
        lines.append("你必须至少质疑 1 条他方 claim（引用其 id），并回应指向你的质疑。")
    lines.append("")
    lines.append(f"- 你的 agent_id：**（由人类在下方 `from` 字段替你填写，或你自行声明）**")
    lines.append(f"- 本轮次：R{tj.get('current_round', 1)}")
    if tj.get("red_team"):
        lines.append(f"- 本议题红队：`{tj['red_team']}`")
        lines.append("  - 若你就是红队：你的职责是给出**最强的反对论证**，不是找平衡。")
    lines.append("")

    # 本轮分工（主持人指定）：显式 --assign，或自动 topics/<id>/assign_R<n>.md
    rnd = tj.get("current_round", 1)
    assign_path = None
    if args.assign:
        p = Path(args.assign)
        assign_path = p if p.exists() else (RT / args.assign)
        if not assign_path.exists():
            print(f"[WARN] 找不到分工文件: {args.assign}")
            assign_path = None
    else:
        for name in (f"assign_R{rnd}.md", f"assign_R{rnd:02d}.md"):
            p = topic_dir / name
            if p.exists():
                assign_path = p
                break
    if assign_path and assign_path.exists():
        lines.append("## 本轮分工（主持人指定，优先级最高）")
        lines.append("")
        lines.append(assign_path.read_text(encoding="utf-8").rstrip())
        lines.append("")
    lines.append("")
    lines.append("## 输出要求（严格遵守）")
    lines.append("")
    lines.append("输出一个完整的 markdown 消息，含 YAML frontmatter，结尾必须有 `## 我可能错在哪`。")
    lines.append("每条 claim 必须写 `falsified_if`（什么数据出现，你就承认错了）。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 接入规则（AGENT_BRIEF 摘要）")
    lines.append("")
    lines.append("1. 证据分级：A 原始数据可复算 / B 二手来源带 URL+时间 / C 模型推断写清推理链 / D 无证据观点（不得进结论区）")
    lines.append("2. 素材引用必须附说明行：这张图是什么、单位、时间区间")
    lines.append("3. 禁止和稀泥（\"双方都有道理\"视为弃权）")
    lines.append("4. 禁止编造 URL 与数据（发现一次，来源永久拉黑）")
    lines.append("5. 收敛不了就记录分歧，别硬凑共识")
    lines.append("6. 你没有本地文件权限：直接输出消息原文，人类会帮你落位")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 议题元数据")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(tj, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    if args.no_brief:
        lines.append("## 00_brief（人类给的背景）")
        lines.append("")
        lines.append("（本瘦身包已省略完整背景；关键事实见下方消息与分工文件）")
    else:
        lines.append("## 00_brief（人类给的背景）")
        lines.append("")
        lines.append(brief)
    lines.append("")
    lines.append("---")
    lines.append("")
    if msgs:
        lines.append(f"## 已有消息（{len(msgs)} 条，按时间序）")
        lines.append("")
        for f in msgs:
            lines.append(f"### 来源文件：`{f.name}`")
            lines.append("")
            lines.append(f.read_text(encoding="utf-8").rstrip())
            lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.append("## 已有消息")
        lines.append("")
        lines.append("（暂无——你是首批发言者之一，请独立成稿）")
        lines.append("")
    lines.append("## 本议题已有素材")
    lines.append("")
    if assets:
        for a in assets:
            lines.append(f"- `{a}`")
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 现在请输出你的消息")
    lines.append("")

    out = OUTBOX / (args.out or f"{topic_dir.name}_pack.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] 简报已生成: {out}")
    print(f"     消息数 {len(msgs)} · 素材 {len(assets)} 个")
    print("")
    # [协议 §5.2] 召唤语必须自带 pack 绝对路径，避免人类为同一件事发两次消息
    print("=" * 60)
    print("[协议 §5.2] 写召唤语时，把下面这段贴在文档开头（绝对路径，勿改）：")
    print("=" * 60)
    print("")
    print(f"> **简报包（必读）**：`{out}`")
    print("> 原生 Agent（能读盘）：直接读上面的绝对路径，不要问人类要。")
    print('> 桥接 Agent（网页版）：人类会把本文件 + 包正文一起贴；若只收到本文件，请回一句"请贴包正文"再开工。')
    print("")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
