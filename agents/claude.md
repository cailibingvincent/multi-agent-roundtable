# agents/claude.md

- **id**: claude
- **access**: bridge（网页版无文件系统工具；可挂 Filesystem MCP 升 native）
  <bridge (web version has no filesystem tools; can be upgraded to native via Filesystem MCP)>
- **红队适配**: 强
  <red-team fit: strong>

## 能力 / Capabilities
- 长链条推理与结构化拆解
  Long-chain reasoning and structured decomposition
- 识别论证漏洞、隐含假设、幸存者偏差
  Identifying argument flaws, hidden assumptions, survivorship bias
- 构造反例与压力测试
  Constructing counterexamples and stress tests

## 已知偏差（其他人据此重点核查）/ Known biases (others scrutinize accordingly)
- 倾向"平衡、周全"，结论偏保守
  Tends toward "balanced, comprehensive" answers that are overly conservative
- 数据不足时易以"需要更多信息"回避判断 → **必须被要求给出临时结论 + 置信度 + 触发条件**
  When data is thin, tends to dodge judgment with "need more info" → **must be required to give a provisional conclusion + confidence + trigger condition**
- 长推理链中可能混入看似合理但不可核验的中间步骤 → 要求逐条标 A/B/C/D 证据等级
  Long reasoning chains may smuggle in plausible-but-unverifiable steps → require per-claim A/B/C/D evidence grading

## 使用建议 / Usage advice
派去：找逻辑漏洞、做红队、写推翻条件。
Assign to: find logic holes, act as red team, write overturn conditions.
别派去：需要实时行情或本地中文语境的活。
Do not assign to: tasks needing real-time quotes or local Chinese-language context.
