# Multi-Agent Roundtable（多智能体圆桌）/ Multi-Agent Roundtable

> 用**文件系统当消息总线**，让多个异构 AI Agent（Claude、豆包、GPT、扣子、本地 CLI Agent 等）围绕同一个议题异步讨论、互相质询、交换证据，最终产出一份**带保留分歧**的结论——而不是几个模型各说一遍好听的。
> Use the **filesystem as a message bus** to let several heterogeneous AI Agents (Claude, Doubao, GPT, Coze, local CLI Agents, etc.) asynchronously discuss one topic, challenge each other, and exchange evidence—finally producing a conclusion **with reserved disagreements**, rather than several models each saying pleasant things.

---

## 一句话说清它解决什么问题 / What problem it solves in one sentence

你问单个 AI 一个问题，它给你一个"看起来全面"的答案，把分歧熨平、把错误藏起来、把不确定说成确定。
You ask one AI a question and it gives you a "looks-comprehensive" answer that smooths over disagreements, hides errors, and presents uncertainty as certainty.

圆桌的做法相反：**让几个立场不同、能力互补的 Agent 独立成稿 → 交叉质询 → 红队反向攻击 → 收敛或保留分歧**。错误被揪出来、分歧被摆上台面、结论被压力测试过。
The roundtable does the opposite: **several Agents with different stances and complementary skills draft independently → cross-challenge → the red team attacks in reverse → converge or keep disagreements**. Errors get caught, disagreements surface, conclusions get stress-tested.

**核心机制：目录即频道，文件即消息，一个议题 = 一个文件夹。**
**Core mechanism: a directory is a channel, a file is a message, one topic = one folder.**

---

## 30 秒看懂它怎么工作 / See how it works in 30 seconds

```
你（人类）提出问题
      │
      ▼
主持人建一个议题文件夹  topics/2026-09-12-是否加仓某标的/
      │
      ▼
┌─ R1 独立成稿（并行，禁止互相偷看）───────────┐
│  Claude 写  R01_001_claude.md               │
│  豆包  写   R01_002_doubao.md               │
│  GPT   写   R01_003_gpt.md                  │
└────────────────────────────────────────────┘
      │
      ▼
┌─ R2 交叉质询（可以互相读了）───────────────┐
│  每方必须质疑至少 1 条对方的 claim          │
│  红队负责构造最强反对论证                   │
└────────────────────────────────────────────┘
      │
      ▼
┌─ R3 收敛 ─────────────────────────────────┐
│  每方投票 + 触发条件                        │
│  主持人写 decision.md（含保留分歧 + 推翻条件）│
└────────────────────────────────────────────┘
```

English: You raise a question → the moderator creates a topic folder → **R1** each Agent drafts in parallel, forbidden to peek at others → **R2** cross-challenge, each must challenge ≥1 opposing claim, the red team builds the strongest counter-case → **R3** vote with trigger conditions, the moderator writes `decision.md` (with reserved disagreements + overturn conditions).

---

## 推荐用法：让主持人 Agent 直接接管（零人工操作）/ Recommended use: let the moderator Agent take over (zero manual work)

> 这套框架**生来就是给 Agent 用的**，不是给人一步步点的。最省事、也最不容易出错的用法，是直接把它交给你的主持人 Agent 自己跑。
> This framework **was built for Agents, not for humans to click through step by step**. The most effortless and error-resistant use is to hand the whole thing to your moderator Agent to run itself.

**一句话启动**：把你主持人 Agent（WorkBuddy / Claude Code / 任意能读写本地文件的 agent）指向**整个仓库根目录**，然后对它说：
**One-line launch:** point your moderator Agent (WorkBuddy / Claude Code / any agent that can read/write local files) at **the whole repo root**, then tell it:

> *"读 `PROTOCOL.md`、`AGENT_BRIEF.md` 和 `scripts/`，以后任何议题都按这套协议自己开圆桌、自己调度成员、自己写 `decision.md`。除非遇到标记为『保留分歧 / 待用户拍板』的结论，否则不用问我。"*
> *"Read `PROTOCOL.md`, `AGENT_BRIEF.md`, and `scripts/`. For any future topic, run the roundtable yourself per this protocol, dispatch members yourself, and write `decision.md` yourself. Unless you hit a conclusion marked 'reserved disagreement / awaiting user decision', don't ask me."*

主持人 Agent 会**自动完成**整条链路，人类全程不碰命令行：
The moderator Agent will **automatically complete** the whole chain; the human never touches the command line:

1. 跑 `scripts/new_topic.py` 开议题、写 `00_brief.md`；
   Run `scripts/new_topic.py` to open a topic and write `00_brief.md`;
2. 把 `AGENT_BRIEF.md` 整段派给每个成员 Agent（原生 Agent 直接读盘，网页版走打包简报）；
   Dispatch `AGENT_BRIEF.md` wholesale to each member Agent (native Agents read disk directly; web Agents go through the packed brief);
3. 汇总发言、交叉质询、收敛分歧、落盘 `decision.md`；
   Aggregate messages, cross-challenge, converge disagreements, and write `decision.md`;
4. 用 `status.py` 跟踪进度，结题后归档到 `archive/`。
   Track progress with `status.py`, and archive to `archive/` after closure.

**人类只在两种情况下介入 / The human intervenes only in two cases:**

- **喂私密口径**：账户资金、风险偏好、真实持仓等不便外泄的信息，你只写进 `00_brief.md` 一次，后续 Agent 自动带入，不用到处粘贴；
  **Feed private context:** account size, risk appetite, real positions—anything not for leakage—you write into `00_brief.md` once; later Agents bring it in automatically, no scattered pasting;
- **拍板未决分歧**：`decision.md` 里标为「保留分歧 / 待用户拍板」的条目，Agent 会把正反证据摆给你，你定。
  **Decide open disagreements:** items in `decision.md` marked "reserved disagreement / awaiting user decision"—the Agent lays out the pros and cons for you to decide.

> ⚠️ **关于手动流程**：下面「快速开始」里的 `digest.py` / `inbox/` / `ingest.py` 复制粘贴动作，是**专门为「网页版 Agent 看不到你磁盘」这种受限场景准备的兜底**。
> ⚠️ **About the manual flow:** the `digest.py` / `inbox/` / `ingest.py` copy-paste steps in "Quick start" below are **fallbacks prepared specifically for the constrained scenario where "web Agents can't see your disk."**
> 只要主持人本身是能读写文件的 Agent，**整条链路零人工**，那些手动步骤你永远用不到——直接把包交给它就对了。
> As long as the moderator itself is an Agent that can read/write files, **the whole chain is zero-manual**; you'll never need those manual steps—just hand it the package.

---

## 目录结构 / Directory structure

```
multi-agent-roundtable/
├── README.md            # 本文件（给人看）/ this file (for humans)
├── 00_START_HERE.md     # 三分钟上手（给人看）/ 3-minute onboarding (for humans)
├── PROTOCOL.md          # 完整协议（给 Agent 看）/ full protocol (for Agents)
├── AGENT_BRIEF.md       # 单页接入卡（拉新 Agent 时整段贴给它）/ one-page onboarding card
├── ROSTER.md            # 成员注册表（示例版，照抄改成你的）/ member registry (example)
├── agents/              # 每个 Agent 的能力档案 / per-Agent capability profile
│   ├── _template.md     # 新成员档案模板 / new-member profile template
│   ├── workbuddy.md     # 主持人示例 / moderator example
│   └── claude.md        # 成员示例 / member example
├── topics/
│   ├── _template/       # 议题模板（复制它开新议题）/ topic template
│   │   ├── 00_brief.md  # 人类填的原始问题 + 约束 / human's raw question + constraints
│   │   └── topic.json   # 机器可读的议题元数据 / machine-readable topic metadata
│   └── <议题id>/        # 一个议题 = 一个目录 / one topic = one directory
├── scripts/             # 全部命令行工具（见下）/ all CLI tools (see below)
├── assets/              # 跨议题共享素材 / shared artifacts across topics
├── inbox/               # 桥接层：人工粘贴回来的回复 / bridge: pasted-back replies
├── outbox/              # 桥接层：打包给网页版 Agent 的简报 / bridge: briefs for web Agents
└── archive/             # 已结题议题 / closed topics
```

---

## 快速开始（3 步）/ Quick start (3 steps)

> 下面三步描述的是**主持人 Agent 在后台自动执行的流程**——你不必亲手敲这些命令。把包交给 Agent 后，它读一遍本段就知道怎么干了。仅当你想用「网页版 Agent 看不到磁盘」的受限模式时，才需要你手动跑它们。
> The three steps below describe the flow the **moderator Agent executes in the background**—you don't have to type these commands yourself. Once you hand the package to the Agent, it reads this section once and knows what to do. You only run them manually if you want the constrained "web Agent can't see disk" mode.

### 前置条件 / Prerequisites

- Python 3.8+（脚本只用标准库，无需安装依赖，除 PDF 导出外）
  Python 3.8+ (scripts use only the standard library; no dependencies except for PDF export)
- 至少两个能对话的 AI Agent（一个原生能读写文件，其他可以是网页版）
  At least two chat-capable AI Agents (one native that reads/writes files; others can be web-only)

### 第 1 步：开一个新议题 / Step 1: Open a new topic

```bash
python scripts/new_topic.py "是否加仓某标的"
# 或指定参与方与红队： / or specify participants and red team:
python scripts/new_topic.py "是否加仓某标的" \
  --participants workbuddy,claude,doubao \
  --red-team claude \
  --rounds 3
```

生成 `topics/2026-09-12-是否加仓某标的/`，然后：
This generates `topics/2026-09-12-whether-to-add-position/`, then:

1. 打开 `00_brief.md`，写下你的问题、约束（预算上限、可承受损失、时间窗口）
   Open `00_brief.md` and write your question and constraints (budget cap, tolerable loss, time window)
2. 打开 `topic.json`，确认参与方、轮次、红队
   Open `topic.json` and confirm participants, rounds, and red team

### 第 2 步：拉 Agent 入场 / Step 2: Bring Agents in

**原生 Agent（能读写本地文件的）**：直接告诉它根目录路径，让它读 `PROTOCOL.md` 和议题文件。
**Native Agent (can read/write local files):** just tell it the root path and let it read `PROTOCOL.md` and the topic files.

**网页版 Agent（豆包/GPT 网页等，看不到你磁盘的）**：
**Web Agent (Doubao/GPT web, etc., can't see your disk):**

```bash
python scripts/digest.py <议题id> --brief-only   # R1 独立成稿，只打包背景 / R1 independent drafting, pack background only
```

生成 `outbox/<议题>_pack.md`，把它 + `AGENT_BRIEF.md` 一起贴给网页 Agent。
This generates `outbox/<topic>_pack.md`; paste it together with `AGENT_BRIEF.md` to the web Agent.

它回复后，把**原文**存进 `inbox/`，然后：
After it replies, save the **verbatim text** into `inbox/`, then:

```bash
python scripts/ingest.py    # 自动编号、落位到议题消息流 / auto-number and place into the topic's message stream
```

### 第 3 步：看进度 / 结题 / Step 3: Check progress / close

```bash
python scripts/status.py    # 列出所有议题的轮次、发言数、收敛状态 / list rounds, message counts, convergence per topic
```

结题由主持人写 `decision.md`，然后目录移入 `archive/`。
Closure is done by the moderator writing `decision.md`, then moving the directory into `archive/`.

---

## 核心设计（为什么这么设计）/ Core design (why it's designed this way)

### 1. R1 禁止互相偷看 / 1. R1 forbids peeking at each other

一旦谁先看到别人的结论，后续所有分析都会向它收敛（锚定效应），整场讨论退化成"第一个发言者 + 一群复读机"。**独立性是这套机制唯一真正的价值来源。**
Once someone sees others' conclusions first, all later analysis converges toward it (anchoring effect), and the discussion degrades into "first speaker + a chorus of echoes." **Independence is the only real source of value in this mechanism.**

### 2. 每条主张必须可证伪 / 2. Every claim must be falsifiable

说不出"什么情况下我错了"的判断，不写进结论。强制每条 claim 带 `falsified_if` 字段、每条消息以 `## 我可能错在哪` 结尾。这是区分"有意义的讨论"和"几个模型互相吹捧"的分水岭。
A judgment that can't state "when I'd be wrong" doesn't go in the conclusion. Every claim is forced to carry a `falsified_if` field, and every message ends with `## 我可能错在哪`. This is the watershed between "a meaningful discussion" and "several models flattering each other."

### 3. 不追求共识 / 3. Don't pursue consensus

几个 Agent 吵不出结果，本身就是重要信息：说明这个问题在现有信息下没有高置信度答案。`decision.md` 会原样保留分歧给人类拍板，而不是用"综合来看"抹平。
Several Agents failing to reach a result is itself important information: it means the question has no high-confidence answer under current information. `decision.md` preserves disagreements verbatim for the human to decide, rather than smoothing them over with "on balance."

### 4. 证据分级（A/B/C/D）/ 4. Evidence grading (A/B/C/D)

- **A** 原始数据可复算，落盘 `assets/`
  **A** raw data, reproducible, saved to `assets/`
- **B** 二手来源，必填 URL + 发布时间
  **B** secondary source, must include URL + publish time
- **C** 模型推断，写清推理链
  **C** model inference, spell out the reasoning chain
- **D** 无证据观点，不得进结论区
  **D** unsupported opinion, must not enter the conclusion area

### 5. 红队机制 / 5. Red-team mechanism

每个议题指定一个 Agent 当**红队**，职责是构造最强反对论证，不是找平衡。红队轮换，不连任两期。
Each topic assigns one Agent as the **red team**, whose job is to build the strongest opposing argument, not to find balance. The red team rotates and never serves two consecutive terms.

---

## 命令行工具一览 / Command-line tools

| 脚本 | 用途 | | Script | Purpose |
|---|---|---|---|---|
| `new_topic.py` | 开新议题，生成目录 + 模板 | | `new_topic.py` | Open a new topic, generate dir + template |
| `nextseq.py` | 查下一个可用消息序号（防撞号） | | `nextseq.py` | Get the next available message seq (prevent collisions) |
| `digest.py` | 把议题打包成单文件简报（桥接网页版 Agent） | | `digest.py` | Pack a topic into a single-file brief (bridge web Agents) |
| `ingest.py` | 把 inbox 里粘贴回来的回复落位到议题 | | `ingest.py` | Place pasted-back replies from inbox into the topic |
| `status.py` | 查看全部议题进度 | | `status.py` | View progress of all topics |
| `onboard.py` | 生成"新人入场包"，拉新 Agent 时整段贴给它 | | `onboard.py` | Generate an "onboarding pack" to paste wholesale for new Agents |
| `make_pdf_decision.py` | 把 decision.md 转成 PDF（需 `markdown` + `reportlab`） | | `make_pdf_decision.py` | Convert decision.md to PDF (needs `markdown` + `reportlab`) |

### PDF 导出（可选）/ PDF export (optional)

```bash
pip install markdown reportlab
python scripts/make_pdf_decision.py --topic "2026-09-12-是否加仓某标的"
```

---

## 协议版本 / Protocol version

当前 `PROTOCOL.md` 为 **v1.0**。规则变更记录在 `index.md`。
Current `PROTOCOL.md` is **v1.0**. Rule changes are logged in `index.md`.

---

## 许可 / License

[MIT License](LICENSE)

---

## 致谢与说明 / Acknowledgements

本项目源于一个真实的多 Agent 协作实践。通过反复迭代，沉淀出了一套可复用的协议与工具。这里开源的**只有框架与工具**，不含任何具体议题内容或成员档案的原始数据（已用示例替代）。
This project grew out of a real multi-Agent collaboration practice. Through repeated iteration, a reusable protocol and toolset crystallized. What's open-sourced here is **only the framework and tools**—no specific topic content or raw member-profile data (replaced by examples).
