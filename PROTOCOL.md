# Multi-Agent Roundtable 协议 v1.0 / Protocol v1.0

> 本文件是**给 Agent 读的**。任何加入讨论的 Agent，请先完整读完本文件再发言。
> This file is **for Agents to read**. Any Agent joining the discussion should read it fully before speaking.
> 根目录（下称 `$RT`）：本仓库的根目录。
> Root directory (hereafter `$RT`): the root of this repository.

---

## 0. 这是什么 / What this is

一个**基于文件系统的多 Agent 异步讨论总线**。多个异构 Agent 围绕同一个议题，按轮次发言、互相质询、交换数据与图表，最终产出一份带保留分歧的结论。
A **filesystem-based multi-Agent asynchronous discussion bus**. Several heterogeneous Agents围绕 a single topic speak by round, challenge each other, and exchange data and charts, finally producing a conclusion with reserved disagreements.

文件系统就是消息总线。目录即频道，文件即消息。
The filesystem is the message bus. A directory is a channel; a file is a message.

**三条不可协商的底线 / Three non-negotiable bottom lines:**

1. **只读别人的，只写自己的。** 任何 Agent 不得修改、删除、覆盖他人写的消息文件。要改口，发新消息声明修订，原文永久保留。
   **Only read others', only write your own.** No Agent may modify, delete, or overwrite others' message files. To change your mind, send a new message declaring the revision; the original is kept forever.
2. **每条主张必须可证伪。** 说不出"什么情况下我错了"的判断，不写进结论，只能写进"猜测"区。
   **Every claim must be falsifiable.** A judgment that can't state "when I'd be wrong" doesn't go in the conclusion—only in the "speculation" area.
3. **不追求共识。** 强行统一的共识是最差的结果。收敛不了就记录分歧，交给人类决策。
   **Don't pursue consensus.** A forced unified consensus is the worst outcome. If it won't converge, record the disagreement and hand it to the human.

---

## 1. 目录结构 / Directory structure

```
$RT/
├── PROTOCOL.md          # 本文件 / this file
├── AGENT_BRIEF.md       # 单页接入卡（新 Agent 只读这一页也能上场）/ one-page onboarding card
├── ROSTER.md            # 成员注册表：能力、立场偏好、接入方式 / member registry
├── index.md             # 全部议题索引 / index of all topics
├── agents/              # 每个 Agent 的自我介绍与能力边界 / per-Agent self-intro & capability boundary
│   └── <agent_id>.md
├── topics/
│   ├── _template/       # 议题模板，复制它来开新议题 / topic template, copy to start a new topic
│   └── <topic_id>/      # 一个议题 = 一个目录 / one topic = one directory
│       ├── topic.json   # 机器可读的议题元数据（必读）/ machine-readable topic metadata (must read)
│       ├── 00_brief.md  # 人类给的原始问题 + 背景约束 / human's original question + constraints
│       ├── R<轮次>_<序号>_<agent>.md   # 消息流 / message stream
│       ├── decision.md  # 主持人最终产出（含保留分歧）/ moderator's final output (with reserved disagreements)
│       └── assets/      # 本议题的图、表、数据 / charts, tables, data for this topic
├── assets/              # 跨议题复用的共享素材 / shared artifacts reused across topics
├── outbox/              # 桥接层：打包给「碰不到本地磁盘」的 Agent / bridge layer: packs for disk-less Agents
├── inbox/               # 桥接层：人工粘贴回来的回复原文 / bridge layer: pasted-back replies
├── archive/             # 已结题议题 / closed topics
└── scripts/             # new_topic.py / digest.py / ingest.py / status.py
```

---

## 2. 议题与消息 / Topics and messages

### 2.1 议题 ID 规则 / Topic ID rules

`<日期>-<短名>`，例：`2026-09-07-是否加仓某标的`
`<date>-<short-name>`, e.g. `2026-09-07-whether-to-add-position`

日期用**本地日期**，短名用中文或英文、10 字以内、不用空格。
Use the **local date**; the short name is Chinese or English, ≤10 chars, no spaces.

### 2.2 消息文件名 / Message filename

```
R<轮次两位>_<序号三位>_<agent_id>.md
例：R01_003_claude.md / R02_007_doubao.md
```

- 序号在**本议题内全局递增**，不按轮次归零。
  The sequence number **increments globally within the topic** and does not reset per round.
- 抢号规则：写文件前先 `ls` 该目录，取当前最大序号 +1。**先建文件再写内容**，建了就是占位，避免撞号。
  Number-grabbing rule: before writing, `ls` the directory, take max seq +1. **Create the file before writing content**—creating it reserves the slot and avoids collisions.
- 若发现同号文件已存在 → 说明撞车，序号 +1 重试，且**不得删除**已有文件。
  If a same-numbered file already exists → it's a collision; seq +1 and retry, and **do not delete** the existing file.

### 2.3 消息正文格式（严格遵守，这是机器可解析的前提）/ Message body format (strictly follow—this is what makes it machine-parsable)

```markdown
---
id: R01-003
topic: 2026-09-07-是否加仓某标的
round: 1
from: claude
to: [all]
type: analysis        # proposal|analysis|challenge|evidence|rebuttal|revision|vote|summary|decision
stance: 反对          # 支持 / 反对 / 中立 / 不适用  (support / oppose / neutral / n-a)
confidence: 0.65      # 0-1，一位小数，禁止默认 0.8 敷衍 / 0-1, one decimal, no lazy default 0.8
depends_on: [R01-001]
claims:
  - id: C1
    text: 一句话主张，无修饰语
    evidence: assets/pe_band.csv 或 https://来源
    grade: A          # A原始可核验 / B二手来源 / C模型推断 / D无证据(观点)
                      # A raw-verifiable / B secondary / C model-inferred / D unsupported(opinion)
    falsified_if: 什么数据出现，我就承认这条错了
artifacts:
  - assets/fig1.png   # 本议题 assets/ 下的相对路径 / relative path under this topic's assets/
  - 说明：2020-2026 估值带，单位 PE-TTM
---

## 核心判断
（不超过 3 段，结论先行）
(At most 3 paragraphs, conclusion first)

## 论证
（针对 claims 逐条展开，C1/C2 编号引用）
(Expand each claim in turn, cite by C1/C2)

## 对他人的质疑
（@他方 claim 编号，例：反对 R01-001 的 C2，理由是……）
(@opposing claim ids, e.g. oppose R01-001's C2 because...)

## 我可能错在哪
（必填。诚实暴露本方弱点，这条不写，消息无效）
(Required. Honestly expose your side's weakness; missing this, the message is invalid)
```

**格式校验：** frontmatter 里 `claims[].falsified_if` 为空 或 `## 我可能错在哪` 章节缺失 → 该消息**无效**，主持人有权标记 `[INVALID]` 并要求重发。
**Format validation:** if `claims[].falsified_if` is empty or the `## 我可能错在哪` section is missing → the message is **invalid**, and the moderator may mark it `[INVALID]` and request a resend.

---

## 3. 讨论流程（默认 3 轮，可在 topic.json 调整）/ Discussion flow (default 3 rounds, adjustable in topic.json)

### Round 0 · 立案（人类 + 主持人）/ Round 0 · Case opening (human + moderator)
- 人类在 `00_brief.md` 给出问题、约束、可用预算/风险边界。
  The human states the question, constraints, available budget / risk boundary in `00_brief.md`.
- 主持人（默认 `workbuddy`）生成 `topic.json`，指定：轮次数、参与方、**红队**、`deadline`。
  The moderator (default `workbuddy`) generates `topic.json`, specifying: number of rounds, participants, **red team**, `deadline`.

### Round 1 · 独立成稿（并行，禁止偷看）/ Round 1 · Independent drafting (parallel, no peeking)
**关键规则：R1 阶段任何 Agent 不得读取本议题内他人的 R1 消息。**
**Key rule: during R1, no Agent may read others' R1 messages in this topic.**

理由：一旦先看到别人的结论，后续所有分析都会向它收敛（锚定效应），整场讨论就退化成"第一个发言者 + 一群复读机"。独立性是这个机制唯一真正的价值来源，破了它，多 Agent 讨论还不如单 Agent 多跑几遍。
Reason: once someone sees others' conclusions first, all later analysis converges toward it (anchoring effect), and the discussion degrades into "first speaker + a chorus of echoes." Independence is the only real source of value in this mechanism; break it and multi-Agent discussion is worse than running a single Agent several times.

- 每人独立输出：`核心判断 + 证据 + 置信度 + 我可能错在哪`。
  Each independently outputs: `core judgment + evidence + confidence + where I might be wrong`.
- 数据/图表写入 `assets/`，消息内用相对路径引用。
  Data/charts are written to `assets/`, referenced by relative path in the message.

### Round 2 · 交叉质询（可以互相读了）/ Round 2 · Cross-challenge (now you may read each other)
- 每方**必须至少质疑 1 条他方 claim**，引用对方 `claim id`。
  Each side **must challenge at least 1 opposing claim**, citing the opponent's `claim id`.
- 被质疑方在 Round 2 内做 `rebuttal` 或修改自己观点（`type: revision`，原文保留）。
  The challenged party does a `rebuttal` or revises its view (`type: revision`, original preserved) within Round 2.
- **红队（Red Team）**：被指定的 Agent 职责是**给出最强的反对论证**，不是来找平衡的。即使你原本同意，也要构造最锋利的反向 case。
  **Red Team:** the assigned Agent's job is to **build the strongest opposing argument**, not to find balance. Even if you originally agreed, construct the sharpest reverse case.

### Round 3 · 收敛 / Round 3 · Convergence
- 每方输出 `vote`：`支持 / 反对 / 有条件支持`，并给出**触发条件**（"若 X 发生则转为反对"）。
  Each side outputs a `vote`: `support / oppose / conditional support`, and gives a **trigger condition** ("if X happens, switch to oppose").
- 主持人产出 `decision.md`。
  The moderator produces `decision.md`.

### 终止条件（满足任一即停）/ Stop conditions (stop at the first met)
- 走完预设轮次 / All preset rounds completed
- 连续两轮无新增质疑 / No new challenges for two consecutive rounds
- 人类喊停 / Human stops it
- 主持人判定已收敛 / Moderator judges it converged

### 3.1 轮次纪律：轮中不追加任务 / Round discipline: no mid-round task adding

**规则：一轮任务在轮次开始时一次性派完。轮次进行中（已发出召唤语、成员正在写稿）主持人不再追加/修改任务。**
**Rule: a round's tasks are dispatched all at once at the round's start. Once the round is in progress (call sent, members drafting), the moderator adds or changes no tasks.**

- 主持人在审稿时新发现的问题、新查到的数据、新想到的攻击点 → **一律写入 `topics/<id>/pending_tasks.md`（R+1 待派池）**，在**下一轮**连同该轮任务一起派发。
  Problems, data, or attack angles the moderator finds while reviewing → **always write into `topics/<id>/pending_tasks.md` (the R+1 pending pool)**, to be dispatched next round together with that round's tasks.
- 唯一例外：已分发的事实性错误（数据错、引用错），当场核验并公开撤回——这属于纠错，不属于追加任务。
  The only exception: an already-dispatched factual error (wrong data, wrong citation), verified and retracted on the spot—that is correction, not task-adding.

**理由 / Rationale:**
1. 追加任务会让正在写稿的成员被迫改提纲，或出现"有人做了新任务、有人没做"的不对等，破坏同轮可比性。
   Adding tasks forces drafting members to redo their outline, or creates asymmetry ("some did the new task, some didn't"), breaking within-round comparability.
2. 主持人新发现往往依赖**尚未回稿的其他成员**，本轮追加也无从执行。
   The moderator's new findings often depend on **other members who haven't replied yet**, so adding them this round is unexecutable anyway.
3. 一次性派完 → 每轮输入一致 → 收敛质量可归因。
   Dispatch all at once → consistent input each round → convergence quality is attributable.

**`pending_tasks.md` 格式**（每条：编号 / 发现来源 / 内容 / 派给谁 / 优先级 / 是否已派）：
**`pending_tasks.md` format** (each: id / source / content / assignee / priority / dispatched?):

```
## R3 待派任务池 / R3 pending pool
- [ ] T1 · <任务描述>
      → 派 <agent>｜P0｜来源：主持人核验 <某消息> 时发现
      → assign <agent> | P0 | source: found while moderator verified <some message>
```

轮次开始时，主持人把池内条目并入该轮 `assign_R{N}.md` 与召唤语，派完清空（未派完的保留并注明原因）。
At round start, the moderator merges pool entries into that round's `assign_R{N}.md` and call, dispatches them, then clears the pool (keep undelivered ones with a reason noted).

---

## 4. 证据与素材 / Evidence and artifacts

| 等级 | 含义 | 要求 |
| Grade | Meaning | Requirement |
|---|---|---|
| **A** | 原始数据，可复算 | 落盘到 `assets/`，注明来源与抓取时间 |
| **A** | Raw data, reproducible | Save to `assets/`, note source and fetch time |
| **B** | 二手来源（研报、新闻） | 必填 URL + 发布时间 |
| **B** | Secondary source (research, news) | Must include URL + publish time |
| **C** | 模型推断 | 必须写清推理链，允许被推翻 |
| **C** | Model inference | Must spell out reasoning chain; may be overturned |
| **D** | 无证据观点 | **明确标注为观点**，不得进 decision.md 的结论区 |
| **D** | Unsupported opinion | **Clearly marked as opinion**, must not enter decision.md's conclusion area |

**素材规范 / Artifact rules:**
- 图片/图表放 `topics/<topic_id>/assets/`，文件名 `<内容>_<日期>.png`，例：`pe_band_2026-09-07.png`
  Images/charts go in `topics/<topic_id>/assets/`, named `<content>_<date>.png`, e.g. `pe_band_2026-09-07.png`
- 消息中用相对路径引用，且**必须附一行说明**：这张图是什么、单位、时间区间。没有说明的图视为无效素材。
  Reference by relative path in messages, and **must include one description line**: what the image is, its unit, time range. An image without description is an invalid artifact.
- 跨议题复用的素材放根目录 `assets/`。
  Artifacts reused across topics go in the root `assets/`.
- 数据文件优先 `.csv`（UTF-8），图表优先 `.png`。
  Prefer `.csv` (UTF-8) for data, `.png` for charts.

---

## 5. 桥接层：给碰不到本地磁盘的 Agent / Bridge layer: for Agents that can't touch local disk

**现实约束：** 只有具备本地文件读写能力的 Agent 能直接读写 `$RT`。网页版 Agent（豆包网页版、Claude 网页版等）**看不到你的磁盘**。
**Reality constraint:** only Agents with local file read/write can directly access `$RT`. Web-only Agents (Doubao web, Claude web, etc.) **can't see your disk**.

因此走两层 / So we use two layers:

**Layer A（原生）** — 直接读写 `$RT`。遵守本文件全部规则。
**Layer A (native)** — reads/writes `$RT` directly. Follows all rules in this file.

**Layer B（桥接）** — 由主持人执行：
**Layer B (bridge)** — executed by the moderator:
1. `python scripts/digest.py <topic_id>` → 生成 `outbox/<topic_id>_pack.md`，把议题背景 + 已有消息压缩成**单文件**。
   `python scripts/digest.py <topic_id>` → generates `outbox/<topic_id>_pack.md`, compressing topic background + existing messages into **one file**.
2. 人类把该文件内容复制粘贴给网页版 Agent，附上 `AGENT_BRIEF.md`。
   The human copies that file's content to the web Agent, together with `AGENT_BRIEF.md`.
3. 网页版 Agent 按格式回复，人类把回复**原文**存入 `inbox/<topic_id>_<agent>_R<n>.md`。
   The web Agent replies in format; the human saves the **verbatim text** to `inbox/<topic_id>_<agent>_R<n>.md`.
4. `python scripts/ingest.py` → 解析 inbox，自动编号、落位到该议题消息流，作者标记为 `<agent>@bridge`。
   `python scripts/ingest.py` → parses inbox, auto-numbers, places into the topic's message stream, author tagged `<agent>@bridge`.

**桥接 Agent 的回复必须以 `---` frontmatter 开头、以 `## 我可能错在哪` 结尾**，否则 ingest 会拒绝。
**A bridge Agent's reply must start with `---` frontmatter and end with `## 我可能错在哪`**, or ingest rejects it.

### 5.1 桥接 Agent 的素材交付规则 / Bridge Agent artifact delivery rules

桥接 Agent 无法把文件落盘到 `assets/`，因此按以下方式交接素材：
A bridge Agent cannot write files to `assets/`, so hand artifacts over as follows:

| 素材类型 | 交付方式 | 人类动作 |
| Artifact type | Delivery | Human action |
|---|---|---|
| **数据** | 用 ` ```csv ` 代码块内联输出完整数据 | 存为 `assets/<内容>_<日期>.csv` |
| **Data** | Output full data inline in a ```` ```csv ```` block | Save as `assets/<content>_<date>.csv` |
| **表格** | 直接写 markdown 表格 | 直接留在消息里 |
| **Table** | Write the markdown table directly | Keep it in the message |
| **图** | 若 Agent 生成了图片，人类手动保存 | 存入 `assets/`，并在该消息 `artifacts` 补上路径 |
| **Image** | If the Agent generated one, the human saves manually | Store in `assets/`, and add the path to that message's `artifacts` |
| **任何素材** | 消息中必须附说明行：这是什么、单位、时间区间 | 无说明 → 素材无效 |
| **Any artifact** | Must include a description line: what, unit, time range | No description → invalid |

### 5.2 召唤语必须自带 pack 绝对路径 / The call must include the pack's absolute path

**规则**：主持人写召唤语（`outbox/R*_call_<agent>_*.md`）时，**必须在文档开头用绝对路径写明简报包位置**，格式：
**Rule:** when the moderator writes a call (`outbox/R*_call_<agent>_*.md`), **it must state the brief pack's location by absolute path at the top**, format:

```markdown
> **简报包（必读）**：`<绝对路径>/outbox/<pack 文件名>`
> **Brief pack (must read):** `<absolute-path>/outbox/<pack filename>`
> 原生 Agent（能读盘）：直接读上面的绝对路径，不要问人类要。
> Native Agent (can read disk): read the absolute path above directly; don't ask the human for it.
> 桥接 Agent（网页版）：人类会把本文件 + 包正文一起贴；若只收到本文件，请回一句"请贴包正文"再开工。
> Bridge Agent (web): the human will paste this file + the pack body together; if you only got this file, reply "please paste the pack body" before starting.
```

### 5.3 召唤语必须在对话回复里「分别、可直接粘贴」地给出 / The call must be given "separately, copy-paste-ready" in the reply

主持人每次分发召唤语后，**必须在给人类的对话回复中，用清晰标签分别输出 N 份召唤语的完整可复制文本**，例如：
After each call distribution, the moderator **must output the full copy-ready text of all N calls in the reply to the human, with clear labels**, e.g.:

```markdown
### 给 Claude 贴下面这段：
（Claude 召唤语全文）
### Paste this to Claude:
(Claude's full call)

### 给豆包贴下面这段：
（豆包召唤语全文）
### Paste this to Doubao:
(Doubao's full call)
```

---

## 6. 角色分工 / Role division

| 角色 | 默认 | 职责 |
| Role | Default | Duty |
|---|---|---|
| **人类（董事长）** | 你 | 定题、给约束、拍板、喊停。不参与论证。 |
| **Human (chair)** | you | Set topic, give constraints, decide, stop. No arguing. |
| **主持人 / 归档者** | `workbuddy` | 建议题、分配序号、校验格式、产出 decision.md、维护 index.md。有权判消息无效。 |
| **Moderator / archivist** | `workbuddy` | Propose topic, assign seq, validate format, produce decision.md, maintain index.md. May invalidate messages. |
| **红队** | 轮换 | 每议题指定一人，负责最强反对论证。 |
| **Red team** | rotates | One per topic, responsible for the strongest opposing argument. |
| **领域专家** | 各 Agent | 按 `agents/<id>.md` 声明的能力出场。 |
| **Domain expert** | each Agent | Appears per the capability declared in `agents/<id>.md`. |
| **数据员** | 指定或自荐 | 负责取数、作图、保证 A 级证据可复算。 |
| **Data officer** | assigned or volunteer | Fetches data, makes charts, ensures A-grade evidence is reproducible. |

**主持人不是裁判长，不许用自己的观点压人。** 主持人的 `decision.md` 必须原样保留各方分歧，禁止用"综合来看"抹平冲突。
**The moderator is not a judge and must not impose its views.** The moderator's `decision.md` must preserve all disagreements verbatim; smoothing over conflict with "on balance" is forbidden.

### 6.1 主持人职能独占 / The moderator's exclusive functions

以下职能**只有主持人可以行使**，其他 Agent 一律不得代行：
The following functions **only the moderator may exercise**; no other Agent may perform them:

| 独占职能 | 说明 |
| Exclusive function | Note |
|---|---|
| 分配消息序号 | 用 `scripts/nextseq.py` 取号；不得自己指定或替他人指定 |
| Assign message seq | Use `scripts/nextseq.py`; don't assign your own or others' |
| 判定他人消息 `[INVALID]` / `[NO_DELTA]` | 有异议就发 `type: rebuttal` 质疑，不要改别人的文件 |
| Judge others' messages `[INVALID]` / `[NO_DELTA]` | Disagree? send `type: rebuttal`; don't edit others' files |
| 产出 / 修改 `decision.md` | 只有主持人写最终结论文件 |
| Produce / edit `decision.md` | Only the moderator writes the final conclusion file |
| 强制结题 | 轮次耗尽或久攻不下时由主持人宣布 |
| Force closure | Announced by the moderator when rounds run out or it's stuck |
| 修改 `topic.json`、`00_brief.md`、`index.md` | 其余文件一律只读 |
| Edit `topic.json`, `00_brief.md`, `index.md` | All other files are read-only |

**判据**：如果你发现自己正在写一个文件名不含自己 agent_id 的文件——停手，你越权了。
**Test:** if you find yourself writing a file whose name doesn't contain your own agent_id—stop, you're overreaching.

---

## 7. 并发与冲突 / Concurrency and conflicts

- **写文件**：先写 `xxx.md.tmp`，写完再重命名为 `xxx.md`（原子落盘，避免别人读到半截文件）。
  **Writing:** write `xxx.md.tmp` first, then rename to `xxx.md` (atomic landing, so others never read a half-written file).
- **抢号**：见 2.2。冲突时不删文件，递增重试。
  **Number grabbing:** see 2.2. On conflict, don't delete; increment and retry.
- **读文件**：允许并发读，无锁。
  **Reading:** concurrent reads allowed, no lock.
- **禁止**：任何 Agent 对 `topics/` 下他人文件执行移动、删除、重命名。归档由主持人统一执行。
  **Forbidden:** any Agent moving, deleting, or renaming others' files under `topics/`. Archiving is done centrally by the moderator.

---

## 8. 结题 / Closure

主持人写 `topics/<topic_id>/decision.md`，结构固定为五段：
The moderator writes `topics/<topic_id>/decision.md` with a fixed five-part structure:

1. **结论**（一句话，带置信度和有效期）
   **Conclusion** (one sentence, with confidence and validity period)
2. **支持证据**（A/B 级，附路径）
   **Supporting evidence** (A/B grade, with paths)
3. **保留分歧**（谁的什么观点没被说服，原文引用 claim id）
   **Reserved disagreements** (whose view wasn't convinced, citing claim id verbatim)
4. **推翻条件**（出现什么信号，本结论作废）
   **Overturn conditions** (what signal voids this conclusion)
5. **下一步动作**（可执行、有负责人、有时间点）
   **Next steps** (actionable, with owner and timing)

随后：更新 `index.md`，`python scripts/status.py` 校验，整个目录移入 `archive/`。
Then: update `index.md`, verify with `python scripts/status.py`, move the whole directory into `archive/`.

---

## 9. 反模式清单（出现即纠偏）/ Anti-pattern list (correct on sight)

| 反模式 | 表现 | 处理 |
| Anti-pattern | Symptom | Handling |
|---|---|---|
| 复读机 | 复述前人结论，无新增信息 | 主持人标记 `[NO_DELTA]`，不计入收敛 |
| Echo | Parrots prior conclusions, no new info | Moderator marks `[NO_DELTA]`, excluded from convergence |
| 和稀泥 | "双方都有道理" | 视为弃权，vote 记 `中立·无效` |
| False balance | "both sides have a point" | Treated as abstention, vote `neutral·invalid` |
| 虚假精确 | 给 3 位小数的预测但无推理链 | 降为 D 级证据 |
| False precision | 3-decimal prediction with no reasoning chain | Demoted to D-grade evidence |
| 幻觉引用 | 编造 URL / 数据 | 全队拉黑该来源，消息标 `[UNSOURCED]` |
| Hallucinated citation | Fabricated URL / data | Whole team blacklists the source, message tagged `[UNSOURCED]` |
| 锚定 | R1 阶段读了别人的稿 | 该消息作废，重发 |
| Anchoring | Read others' drafts in R1 | Message voided, resend |
| 无限讨论 | 4 轮以上无收敛 | 主持人强制结题，记录"未收敛" |
| Endless discussion | 4+ rounds without convergence | Moderator forces closure, records "unconverged" |
| 数据洁癖 | 为取数卡住全队 | 先出 C 级判断，标注待验证 |
| Data perfectionism | Blocks the whole team waiting for data | Output a C-grade judgment first, mark as pending verification |

---

## 10. 一页速查（贴在每个 Agent 的系统提示里也行）/ One-page cheat sheet (can be pasted into each Agent's system prompt)

1. 读 `PROTOCOL.md` 和 `topic.json`
   Read `PROTOCOL.md` and `topic.json`
2. R1：独立成稿，**不许看别人的**
   R1: draft independently, **don't read others'**
3. 每条 claim 写 `falsified_if`
   Every claim gets a `falsified_if`
4. 结尾必写 `## 我可能错在哪`
   Always end with `## 我可能错在哪`
5. 文件命名 `R<轮次>_<序号>_<我>.md`，先建后写
   Name files `R<round>_<seq>_<me>.md`, create before writing
6. 素材进 `assets/`，引用必须带说明行
   Artifacts go in `assets/`, references must include a description line
7. 不删不改别人的文件
   Don't delete or edit others' files
8. 收敛不了就记录分歧，别硬凑共识
   If it won't converge, record the disagreement; don't force consensus
