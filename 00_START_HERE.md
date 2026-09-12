# 00_START_HERE · 三分钟上手（给人看）/ 3-Minute Onboarding (for humans)

这是圆桌文件夹的使用说明。**给 Agent 看的是 `AGENT_BRIEF.md`，不是这份。**
This is the usage guide for the roundtable folder. **The file for Agents is `AGENT_BRIEF.md`, not this one.**

---

## 这套东西解决什么问题 / What problem this solves

你问一个问题，让多个 Agent 一起讨论，互相挑错、共享图表和数据，最后给出一份**带分歧记录**的结论——而不是几个 Agent 各说一遍好听的。
You ask a question, let several Agents discuss it together—challenging each other, sharing charts and data—and end up with a conclusion that **records the disagreements**, rather than several Agents each saying pleasant things.

核心机制：**文件系统当消息总线**。一个议题 = 一个文件夹，一次发言 = 一个 markdown 文件，图表数据放 `assets/`。
Core mechanism: **the filesystem is the message bus**. One topic = one folder, one message = one markdown file, charts/data go in `assets/`.

---

## 日常三种用法 / Three everyday uses

### 用法一：开一个新议题 / Usage 1: Open a new topic

```bash
python scripts/new_topic.py "是否加仓某标的"
```

会生成 `topics/<日期>-是否加仓某标的/`，然后：
This generates `topics/<date>-whether-to-add-position/`, then:

1. 打开里面的 `00_brief.md`，写下你的问题、约束（预算上限、可承受损失、时间窗口）
   Open the `00_brief.md` inside and write your question and constraints (budget cap, tolerable loss, time window)
2. 打开 `topic.json`，确认参与方、轮次数、指定谁当**红队**
   Open `topic.json` and confirm participants, number of rounds, and who is the **red team**
3. 把 `AGENT_BRIEF.md` 的内容贴给每个要参与的 Agent
   Paste the contents of `AGENT_BRIEF.md` to each Agent you want to involve

### 用法二：拉网页版 Agent 进讨论 / Usage 2: Bring a web-only Agent into the discussion

它们看不到你的磁盘，所以：
They can't see your disk, so:

```bash
python scripts/digest.py <议题id>
```

生成 `outbox/<议题>_pack.md`（把整个议题压缩成一个文件）。
This generates `outbox/<topic>_pack.md` (compresses the whole topic into a single file).

把它 + `AGENT_BRIEF.md` 一起贴给网页 Agent → 它回复后，把**原文**存进 `inbox/` →
Paste it together with `AGENT_BRIEF.md` to the web Agent → after it replies, save the **verbatim text** into `inbox/` →

```bash
python scripts/ingest.py
```

自动编号、落位到议题消息流。
Auto-numbers and places it into the topic's message stream.

### 用法三：看进度 / 结题 / Usage 3: Check progress / close a topic

```bash
python scripts/status.py
```

列出所有议题的轮次、发言数、是否收敛。
Lists every topic's rounds, message counts, and whether it has converged.

结题由主持人写 `decision.md`，然后整个目录移入 `archive/`。
Closure is done by the moderator writing `decision.md`, then moving the whole directory into `archive/`.

---

## 文件速查 / File quick-reference

| 文件                 | 给谁看       | 什么时候用              |
| File                | For         | When to use              |
| ------------------ | --------- | ------------------ |
| `AGENT_BRIEF.md`   | **Agent** | 拉新 Agent 入场时，整段贴给它 |
| `AGENT_BRIEF.md`   | **Agent** | Paste wholesale when onboarding a new Agent |
| `PROTOCOL.md`      | Agent     | 完整规则，接入卡不够时查       |
| `PROTOCOL.md`      | Agent     | Full rules; consult when the briefing card isn't enough |
| `ROSTER.md`        | Agent + 你 | 谁参加、各自什么能力和立场      |
| `ROSTER.md`        | Agent + you | Who participates, each one's capability and stance |
| `00_START_HERE.md` | **你**     | 本文件                |
| `00_START_HERE.md` | **you**   | This file                |
| `index.md`         | 你         | 全部议题索引             |
| `index.md`         | you       | Index of all topics             |

---

## 三条设计上的判断，先说清楚 / Three design judgments, stated up front

**1. 为什么 R1 禁止 Agent 互相看稿。**
**1. Why R1 forbids Agents from reading each other's drafts.**

一旦谁先看到别人的结论，后面的分析都会向它收敛（锚定效应），讨论就退化成"第一个发言者 + 一群复读机"。独立性是这套机制唯一真正的价值来源。所以第一轮必须并行独立成稿。
Once someone sees others' conclusions first, all later analysis converges toward it (anchoring effect), and the discussion degrades into "first speaker + a chorus of echoes." Independence is the only real source of value in this mechanism. So Round 1 must be parallel and independent.

**2. 为什么强制写"我可能错在哪"。**
**2. Why we force "where I might be wrong".**

不写可证伪条件的判断，本质上是在耍赖——它永远不错，也就永远没用。这是区分"有意义的讨论"和"几个模型互相吹捧"的分水岭。
A judgment without a falsifiable condition is essentially cheating—it can never be wrong, and therefore is never useful. This is the watershed between "a meaningful discussion" and "several models flattering each other."

**3. 为什么不追求共识。**
**3. Why we don't pursue consensus.**

几个 Agent 吵不出结果，本身就是重要信息：说明这个问题在现有信息下没有高置信度答案。`decision.md` 会原样保留分歧给你拍板，而不是用"综合来看"抹平。
Several Agents failing to reach a result is itself important information: it means the question has no high-confidence answer under current information. `decision.md` preserves the disagreements verbatim for you to decide, rather than smoothing them over with "on balance."

---

## 你需要付出的成本 / The cost you pay

- 每轮要给每个 Agent 贴一次上下文（网页版），原生 Agent 可以自己读文件
  Each round you paste context to each Agent (web version); native Agents can read files themselves
- 一次讨论约 3 轮 × N 个 Agent，token 消耗不小
  One discussion is roughly 3 rounds × N Agents, which costs a fair amount of tokens
- **建议只在真正重要的决策上用**（大额资金、方向选择、不可逆判断）。日常小问题单问一个 Agent 更快。
  **Recommended only for genuinely important decisions** (large sums, direction choices, irreversible judgments). For daily small questions, asking one Agent is faster.

---

## 维护 / Maintenance

- 新 Agent 入场：在 `ROSTER.md` 登记 + 在 `agents/` 下建 `<id>.md`
  New Agent: register in `ROSTER.md` + create `<id>.md` under `agents/`
- 议题做多了就归档：把 `topics/<id>/` 整个移到 `archive/`
  When you accumulate many topics, archive them: move `topics/<id>/` entirely into `archive/`
- 规则要改：改 `PROTOCOL.md`，版本号 +1，并在 `index.md` 记录变更
  To change rules: edit `PROTOCOL.md`, bump the version, and log the change in `index.md`

版本 v1.0 / Version v1.0
