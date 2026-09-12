#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ingest.py - 把 inbox/ 里粘贴回来的 Agent 回复，落位到议题消息流

用法:
  python ingest.py                     # 处理 inbox/ 下所有 .md
  python ingest.py --topic <议题id>    # 未写 topic 字段时指定归属
  python ingest.py --dry-run           # 只检查不写入

规则:
  - 必须有 YAML frontmatter（以 --- 开头）
  - 必须含 "## 我可能错在哪"，否则拒绝
  - 作者标记为 <agent>@bridge，序号自动分配
  - 成功后原文件移入 inbox/_done/
"""
import sys, re, argparse, shutil
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RT = Path(__file__).resolve().parent.parent
TOPICS = RT / "topics"
INBOX = RT / "inbox"
REQUIRED_SECTION = "## 我可能错在哪"
# 必须行首匹配：防止 Agent 在正文里引用协议文字（如「需包含 ## 我可能错在哪」）蒙混过关
REQUIRED_RE = re.compile(r"^##\s*我可能错在哪\s*$", re.M)


def parse_frontmatter(text):
    """极简 YAML frontmatter 解析：只取顶层 key: value"""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    block = text[3:end]
    data = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line.strip())
        if m and not line.startswith((" ", "\t", "-")):
            data[m.group(1)] = m.group(2).strip().strip('"\'')
    return data, text[end + 4:].lstrip("\n")


def resolve(topic_id):
    if (TOPICS / topic_id).exists():
        return TOPICS / topic_id
    cands = [d for d in TOPICS.iterdir() if d.is_dir() and topic_id in d.name]
    if len(cands) == 1:
        return cands[0]
    return None


def next_seq(topic_dir):
    mx = 0
    for f in topic_dir.glob("R*_*.md"):
        m = re.match(r"^R\d\d_(\d\d\d)_", f.name)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    INBOX.mkdir(exist_ok=True)
    files = [f for f in sorted(INBOX.glob("*.md")) if f.is_file()]
    if not files:
        print("[i] inbox/ 为空，没有待处理回复。")
        print("    把网页版 Agent 的回复原文存成 .md 放进 inbox/ 再运行。")
        return 0

    done = INBOX / "_done"
    ok, bad = 0, 0

    for f in files:
        text = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        if meta is None:
            print(f"[SKIP] {f.name} — 缺少 YAML frontmatter（必须以 --- 开头）")
            bad += 1
            continue
        if not REQUIRED_RE.search(text):
            print(f"[SKIP] {f.name} — 缺少独立的「## 我可能错在哪」章节（须独占一行），按协议该消息无效，请让 Agent 重发")
            bad += 1
            continue

        topic_id = meta.get("topic") or args.topic
        if not topic_id:
            print(f"[SKIP] {f.name} — frontmatter 无 topic 字段，请用 --topic 指定")
            bad += 1
            continue
        topic_dir = resolve(topic_id)
        if not topic_dir:
            print(f"[SKIP] {f.name} — 找不到议题 {topic_id}")
            bad += 1
            continue

        agent = (meta.get("from") or "unknown").strip()
        try:
            rnd = int(str(meta.get("round", "1")).strip())
        except ValueError:
            rnd = 1
        seq = next_seq(topic_dir)
        target = topic_dir / f"R{rnd:02d}_{seq:03d}_{agent}@bridge.md"

        print(f"[OK] {f.name} -> {topic_dir.name}/{target.name}")
        if not args.dry_run:
            tmp = target.with_suffix(".md.tmp")
            tmp.write_text(text.rstrip() + "\n", encoding="utf-8")
            tmp.replace(target)
            done.mkdir(exist_ok=True)
            shutil.move(str(f), str(done / f.name))
        ok += 1

    print("")
    print(f"完成: 成功 {ok} · 拒绝 {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
