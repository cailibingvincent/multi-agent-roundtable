#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""onboard.py - 生成「新人入场包」，整段贴给一个新 Agent 即可让它上场

用法:
  python onboard.py qclaw                      # 通用入场包（只登记，不发议题）
  python onboard.py qclaw --topic 是否加仓某标的  # 入场包 + 附该议题背景（R1 独立成稿用）

生成的包会让新 Agent 自己回答：能否读写本地文件、比别人强在哪、系统性偏差是什么。
省得人类去猜，也避免注册表里出现「待填写」的水货条目。
"""
import sys, json, argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
OUTBOX = RT / "outbox"
TOPICS = RT / "topics"


def resolve_topic(t):
    if not t:
        return None
    if (TOPICS / t).exists():
        return TOPICS / t
    cands = [d for d in TOPICS.iterdir() if d.is_dir() and t in d.name]
    if len(cands) == 1:
        return cands[0]
    print(f"[WARN] 议题匹配异常（{len(cands)} 个），本次不附带议题背景")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id", help="新 Agent 的 id，全小写英文，例：qclaw / kimi / yuanbao")
    ap.add_argument("--topic", default=None, help="可选，附带的议题 ID（只含背景，不含他人消息）")
    ap.add_argument("--access", choices=["native", "bridge", "ask"], default="ask",
                    help="native=能直接读写本地目录 / bridge=无文件权限需人工搬运 / ask=让它自己回答（默认）")
    ap.add_argument("--team", dest="team", action="store_true", default=None,
                    help="附带 ROSTER.md 与自己档案的原文（bridge 模式默认开启，因为它自己读不到）")
    ap.add_argument("--no-team", dest="team", action="store_false",
                    help="不附带队友信息（native 模式默认，它能自己读）")
    args = ap.parse_args()

    aid = args.agent_id.strip().lower()
    brief_path = RT / "AGENT_BRIEF.md"
    if not brief_path.exists():
        print("[ERR] 找不到 AGENT_BRIEF.md")
        return 1
    Brief = brief_path.read_text(encoding="utf-8")

    topic_dir = resolve_topic(args.topic)
    tj = {}
    topic_brief = ""
    if topic_dir:
        p = topic_dir / "topic.json"
        if p.exists():
            tj = json.loads(p.read_text(encoding="utf-8"))
        b = topic_dir / "00_brief.md"
        if b.exists():
            topic_brief = b.read_text(encoding="utf-8")

    L = []
    L.append(f"# 入场包 · 致 `{aid}`")
    L.append("")
    L.append("> 本文件由 onboard.py 生成。人类把整段内容贴给你，代表正式邀请你加入 **AgentRoundtable（圆桌）**。")
    L.append("")
    L.append("## 你要做的三件事")
    L.append("")
    L.append("1. 读完本文的《接入规则》")
    L.append("2. 填好文末的《成员登记表》并输出（这是我的档案，决定以后派什么活给我）")
    L.append("3. 等人类发第一个议题，然后按规则发言")
    L.append("")
    L.append("**登记表是必填项，不填视为放弃入场。**")
    L.append("填的时候别客气也别吹牛：写不出独特优势，说明这个议题不该叫你，")
    L.append("人类会换人——这比让你硬凑一场讨论对所有人都好。")
    L.append("")

    acc = args.access
    if acc == "bridge":
        L.append("## 你的接入方式：桥接（bridge）")
        L.append("")
        L.append("**你没有本地磁盘读写权限**，所有内容由人类搬运。流程是：")
        L.append("")
        L.append("1. 我把议题简报（附件或粘贴）发给你")
        L.append("2. 你按格式输出**完整消息原文**（必须含 YAML frontmatter）")
        L.append("3. 我把你的回复存回圆桌目录，它从此和其他成员的消息并列，参与后续轮次")
        L.append("4. 下一轮我把别人的发言一起打包发给你，你做交叉质询")
        L.append("")
        L.append("### 你怎么交素材（你没有落盘能力，这条必须照做）")
        L.append("")
        L.append("- **数据**：用 ` ```csv ` 代码块内联输出完整数据，我存成 .csv")
        L.append("- **表格**：直接写 markdown 表格，留在消息里")
        L.append("- **图**：你生成图片后由我手动保存；你在 artifacts 里写 `assets/xxx.png  # 待人工落位`")
        L.append("- **任何素材都必须附说明行**：这是什么、单位、时间区间")
        L.append("")
        L.append("  **没说明的素材视为无效素材，等于白做。**")
        L.append("")
        L.append("对你只有一个额外要求：**输出可直接存档的成品消息**，")
        L.append("不要写「你可以这样写…」这类教学式回答。")
        L.append("")
    elif acc == "native":
        L.append("## 你的接入方式：原生（native）")
        L.append("")
        L.append(f"你可以直接读写 `{RT}`：")
        L.append("")
        L.append("1. 读 `PROTOCOL.md`（完整规则）")
        L.append("2. 读 `topics/<议题>/topic.json` 与 `00_brief.md`")
        L.append("3. 按命名规则直接往该目录写你的消息文件")
        L.append("")
        L.append("注意：**只写你自己的文件**，绝不改动、删除他人文件。")
        L.append("")
    else:
        L.append("## 你的接入方式：待确认（请先回答这一条）")
        L.append("")
        L.append(f"你能否直接读写 `{RT}` 这个目录？")
        L.append("")
        L.append("- **能** → 你是 native，直接读写文件，效率最高")
        L.append("- **不能** → 你是 bridge，所有内容由人类搬运")
        L.append("  （每轮我把简报发给你，你把回复原文给我，我帮你存进圆桌）")
        L.append("")
        L.append("**别为了显得能干而回答「能」。** 答错的代价远大于答「不能」——")
        L.append("你会试图去读一个在你世界里根本不存在的路径，然后开始编造内容。")
        L.append("")

    if topic_dir:
        L.append("## 你的第一个议题（先看，但**现在还不要发言**）")
        L.append("")
        L.append(f"- 议题 ID：`{topic_dir.name}`")
        L.append(f"- 参与方：{', '.join(tj.get('participants', []))}")
        L.append(f"- 红队：`{tj.get('red_team', '未指定')}`")
        L.append(f"- 轮次安排：共 {tj.get('rounds', 3)} 轮，当前第 {tj.get('current_round', 1)} 轮")
        L.append("")
        L.append("> 注意：Round 1 是**独立成稿**阶段，你看不到其他成员的观点（这是刻意的）。")
        L.append("> 现在只填登记表，收到「开始第一轮」的指令后再发言。")
        L.append("")
        if topic_brief:
            L.append("### 议题背景（人类填写）")
            L.append("")
            L.append(topic_brief)
            L.append("")
    else:
        L.append("> 当前还没有绑定议题。填完登记表后等人类开题即可。")
        L.append("")

    L.append("---")
    L.append("")
    L.append("## 接入规则（AGENT_BRIEF 全文）")
    L.append("")
    if acc == "bridge":
        L.append("> 下面嵌入的是 AGENT_BRIEF 原文。其中让你「读 `PROTOCOL.md` / `topic.json`」这类路径你读不到——")
        L.append("> **忽略所有文件路径，只遵守规则本身**。上下文会由人类以简报形式发给你。")
        L.append("")
    L.append(Brief.rstrip())
    L.append("")

    include_team = args.team if args.team is not None else (acc == "bridge")
    if include_team:
        roster = RT / "ROSTER.md"
        me = RT / "agents" / f"{aid}.md"
        L.append("---")
        L.append("")
        L.append("## 你的队友与你自己")
        L.append("")
        L.append("> 你读不到这些文件，所以原文贴在下面。据此判断自己该在哪些议题上说话、在哪些议题上闭嘴。")
        L.append("")
        if me.exists():
            L.append(f"### `agents/{aid}.md` · 你的档案")
            L.append("")
            L.append(me.read_text(encoding="utf-8").rstrip())
            L.append("")
        if roster.exists():
            L.append("### `ROSTER.md` · 在册成员")
            L.append("")
            L.append(roster.read_text(encoding="utf-8").rstrip())
            L.append("")
        L.append("---")
        L.append("")

    L.append("## 成员登记表（请完整输出，字段一个都别漏）")
    L.append("")
    L.append("````markdown")
    L.append("---")
    L.append(f"id: {aid}")
    if acc == "bridge":
        L.append("access: bridge   # 已确认：你无本地文件权限，内容由人类搬运")
    elif acc == "native":
        L.append("access: native   # 已确认：你可直接读写本目录")
    else:
        L.append("access: native 或 bridge   # 你能否直接读写本圆桌目录？能=native，不能=bridge")
    L.append("red_team_ok: 强 或 中 或 否   # 你能否胜任「构造最强反对论证」的红队角色")
    L.append("---")
    L.append("")
    L.append("## 我的独特优势（比在册其他成员强在哪一项）")
    L.append("一句话。写不出来就直说「没有明显优势」，别编。")
    L.append("")
    L.append("## 我的系统性偏差（我在哪类问题上会稳定地答错）")
    L.append("诚实列出来。其他成员会据此重点核查你，这对你自己是保护。")
    L.append("")
    L.append("## 派我去做 / 别派我去")
    L.append("- 派我去：")
    L.append("- 别派我去：")
    L.append("")
    L.append("## 确认")
    L.append("我已读完接入规则，理解并接受以下三条：")
    L.append("1. Round 1 独立成稿，不读他人消息")
    L.append("2. 每条主张写 falsified_if，每条消息写「## 我可能错在哪」")
    L.append("3. 不删改他人文件，不编造来源，收敛不了就保留分歧")
    L.append("````")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 附加说明（人类可删）")
    L.append("")
    L.append(f"- 本包生成时间：本地日期可用 `date` 确认")
    L.append(f"- 根目录：`{RT}`")
    L.append("- 若该 Agent 回答 `access: native`，人类应把 `PROTOCOL.md` 路径直接给它，后续它可自行读写；")
    L.append("  若回答 `bridge`，后续每轮用 `python scripts/digest.py <议题>` 打包、回复存 `inbox/` 再 `python scripts/ingest.py`。")
    L.append("")

    OUTBOX.mkdir(exist_ok=True)
    out = OUTBOX / f"onboard_{aid}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"[OK] 入场包已生成: {out}")
    print("")
    print("把整段内容复制粘贴给该 Agent 即可。")
    print("")
    print("建议的最简召唤语（贴在前面）:")
    print(f"  你要加入一个多 Agent 圆桌讨论机制，成员包括 WorkBuddy、Claude、豆包和你（{aid}）。")
    print("  请完整读完下面这份《入场包》，然后输出文末的《成员登记表》。现在还不要对任何议题发言。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
