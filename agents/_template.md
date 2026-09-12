# agents/_template.md

复制本文件为 `<agent_id>.md`，填完再让它入场。
Copy this file to `<agent_id>.md`, fill it in, then onboard the agent.

---

# agents/<agent_id>.md

- **id**: <全小写英文，与文件名一致，启用后不可改>
  <lowercase English, matching the filename; immutable once activated>
- **access**: native | bridge
- **红队适配**: 强 | 中 | 否
  <red-team fit: strong | medium | no>

## 能力 / Capabilities
它比别人强在哪一项。写不出独特优势的成员，就不要拉进来。
What it does better than others. Don't onboard a member that cannot state a unique edge.

## 已知偏差 / Known biases
它在哪一类问题上会系统性地给错答案。留空 = 没想清楚 = 别人不知道该重点核查什么。
What class of problems it will systematically get wrong. Blank = not thought through = others won't know what to scrutinize.

## 使用建议 / Usage advice
派去：……
Assign to: …
别派去：……
Do not assign to: …

## 首次入场检查清单 / First-onboarding checklist
- [ ] 把 `AGENT_BRIEF.md` 贴给它，确认能遵守 frontmatter 格式
      Paste `AGENT_BRIEF.md` to it; confirm it follows the frontmatter format
- [ ] 小议题试跑一轮
      Dry-run one round on a small topic
- [ ] 确认它会写 `falsified_if` 和 `## 我可能错在哪`
      Confirm it writes `falsified_if` and `## 我可能错在哪`
- [ ] 在 `ROSTER.md` 登记
      Register it in `ROSTER.md`
