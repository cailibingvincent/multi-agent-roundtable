# ROSTER · 成员注册表（示例版）/ Member Registry (example)

> **这是示例版。照抄改成你自己的成员。** 新增成员：复制下方模板追加，并在 `agents/<id>.md` 建同名文件写能力说明。
> **This is an example. Copy and adapt it to your own members.** To add a member: copy the template below and append, and create a same-named file `agents/<id>.md` describing its capabilities.

## 字段说明 / Field reference

| 字段 | 含义 | | Field | Meaning |
|---|---|---|---|---|
| `id` | 全小写英文，用于文件名，一旦启用**不可更改** | | `id` | Lowercase English, used in filenames; **immutable** once activated |
| `access` | `native` 可直接读写本地文件 / `bridge` 需人工粘贴桥接 | | `access` | `native` = direct local file read/write / `bridge` = needs human paste bridging |
| `edge` | 它的独特优势，别派它干别人更擅长的活 | | `edge` | Its unique strength; don't assign it work others do better |
| `bias` | 已知系统性偏差，其他成员质询时可据此重点核查 | | `bias` | Known systematic bias; others use it to focus scrutiny |
| `red_team_ok` | 是否适合当红队（能否构造强反对论证） | | `red_team_ok` | Whether suited to red team (can it build strong opposing arguments) |

---

## 在册成员 / Registered members

### workbuddy（主持人示例）/ workbuddy (moderator example)
- **access**: `native`
- **角色**: 主持人 / 归档者（默认）
  <role: moderator / archivist (default)>
- **edge**: 唯一默认拥有本地文件系统与脚本执行能力；负责建题、编号、格式校验、产出 decision.md、执行归档
  <unique default capability of local filesystem + script execution; handles topic creation, numbering, format validation, decision.md, archiving>
- **bias**: 作为主持人与用户长期协作，容易倾向于附和用户既有偏好 → **其他成员应对其结论提高质询强度**
  <as moderator collaborating long-term with the user, tends to echo existing user preferences → **others should scrutinize its conclusions more strongly**>
- **red_team_ok**: 否（主持人不兼任红队，避免既当裁判又当球员）
  <no (moderator doesn't double as red team, to avoid judge-and-player conflict)>

### claude（成员示例）/ claude (member example)
- **access**: `bridge`（网页版无文件系统工具；可挂 Filesystem MCP 升 `native`）
  <bridge (web version lacks filesystem tools; can upgrade to native via Filesystem MCP)>
- **edge**: 长链条推理、结构化分析、识别论证漏洞、构造反例
  <long-chain reasoning, structured analysis, spotting argument flaws, building counterexamples>
- **bias**: 倾向给出平衡、周全但偏保守的结论；容易在缺乏数据时用"需要更多信息"回避判断 → **应被要求给出临时结论和置信度**
  <tends toward balanced, comprehensive but conservative conclusions; dodges judgment with "need more info" when data is thin → **must be required to give a provisional conclusion and confidence**>
- **red_team_ok**: 强
  <strong>

### doubao（成员示例）/ doubao (member example)
- **access**: `native` 或 `bridge`（取决于接入的版本）
  <native or bridge (depends on the version connected)>
- **edge**: 中文语境与本地信息（政策、产业、舆情）检索；快速给出市场共识视角；能直接生成图表
  <Chinese-context and local information retrieval (policy, industry, sentiment); quick market-consensus view; can generate charts directly>
- **bias**: 倾向贴近主流观点与官方口径，对反共识信号不敏感 → **其结论应被要求单独标注"这与市场共识一致/不一致"**
  <leans toward mainstream and official lines, insensitive to contrarian signals → **its conclusions should be required to flag "consistent / inconsistent with market consensus"**>
- **red_team_ok**: 中（需明确指令要求其做反对论证，否则默认给平衡答案）
  <medium (needs explicit instruction to argue against; otherwise defaults to balanced answers)>

---

## 已退场成员 / Retired members

（记录退场成员及原因，供后人避坑。例：某 Agent 无文件系统工具 + edge 与已有成员重叠，退出。）
(Record retired members and reasons, to help others avoid pitfalls. Example: an Agent with no filesystem tools + edge overlapping existing members → retired.)

## 模板 / Template

```markdown
### <agent_id>
- **access**: native | bridge
- **edge**: 独特优势一句话
  <one-line unique strength>
- **bias**: 已知系统性偏差，供他人质询时重点核查
  <known systematic bias for others to scrutinize>
- **red_team_ok**: 强 | 中 | 否
  <strong | medium | no>
```

---

## 出场规则 / Participation rules

1. 每个议题在 `topic.json` 的 `participants` 中显式列出成员，**未列入者不发言**。
   Each topic must explicitly list members in `topic.json`'s `participants`; **those not listed do not speak.**
2. 红队每议题轮换，不连任两期。
   Red team rotates per topic; no two consecutive terms.
3. 同一 `edge` 重复的两个 Agent 不同时入场（冗余发言，只增加噪声）。
   Two Agents with the same `edge` don't enter together (redundant speech, only adds noise).
4. 成员长期给出无信息量发言（连续 2 个议题被标记 `[NO_DELTA]`）→ 从注册表移出。
   A member giving consistently low-information replies (marked `[NO_DELTA]` in 2 consecutive topics) → removed from the registry.
