"""圆桌决议 → 微信友好 PDF（通用版）

用法:
    python scripts/make_pdf_decision.py --topic "2026-09-08-当升科技底部买入"
    python scripts/make_pdf_decision.py --topic <议题目录名> --out <自定义输出路径>
    python scripts/make_pdf_decision.py --src a.md --dst a.pdf --title "标题"

自动从 topic.json 或 decision.md 头部推断标题与日期。
"""
import re
import os
import sys
import json
import argparse
from pathlib import Path

import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.pdfbase.pdfmetrics import registerFontFamily

RT = Path(__file__).resolve().parent.parent
OUTBOX = RT / "outbox"

# 中文字体路径：Windows 默认在 C:\Windows\Fonts；macOS/Linux 需自备字体并改此路径
FONT_DIR = os.environ.get("RT_FONT_DIR", r"C:\Windows\Fonts")
_msyh = Path(FONT_DIR) / "msyh.ttc"
_msyhbd = Path(FONT_DIR) / "msyhbd.ttc"
if _msyh.exists() and _msyhbd.exists():
    pdfmetrics.registerFont(TTFont("CN", str(_msyh)))
    pdfmetrics.registerFont(TTFont("CN-B", str(_msyhbd)))
    registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")
else:
    # 无微软雅黑时回退到 Helvetica（会丢失中文，仅用于无中文字体的环境）
    print("[WARN] 未找到微软雅黑字体，中文可能显示为方块。可用环境变量 RT_FONT_DIR 指定字体目录。")
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
USABLE_W = PAGE_W - 2 * MARGIN

BRAND = "#c8102e"  # 中国红

styles = {
    "h1": ParagraphStyle("h1", fontName="CN-B", fontSize=20, leading=26, spaceBefore=8, spaceAfter=12, textColor=colors.HexColor("#1a1a1a")),
    "h2": ParagraphStyle("h2", fontName="CN-B", fontSize=15, leading=20, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor(BRAND)),
    "h3": ParagraphStyle("h3", fontName="CN-B", fontSize=12.5, leading=17, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor("#333333")),
    "p":  ParagraphStyle("p",  fontName="CN",   fontSize=10.5, leading=15, spaceAfter=4, textColor=colors.HexColor("#1a1a1a")),
    "quote": ParagraphStyle("quote", fontName="CN", fontSize=10.5, leading=15, leftIndent=14, spaceAfter=4, textColor=colors.HexColor("#555")),
    "li": ParagraphStyle("li", fontName="CN", fontSize=10.5, leading=15, leftIndent=14, bulletIndent=2, spaceAfter=2),
}


def md_to_blocks(md_text: str):
    blocks = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        # 表格
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1].lstrip()):
            tbl = [line]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i].rstrip())
                i += 1
            blocks.append(("table", tbl))
            continue

        # 分隔线
        if re.match(r"^-{3,}$", line.strip()):
            blocks.append(("hr", ""))
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            blocks.append((f"h{len(m.group(1))}", m.group(2).strip()))
            i += 1
            continue

        if line.lstrip().startswith(">"):
            qt = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                qt.append(lines[i].lstrip()[1:].strip())
                i += 1
            blocks.append(("quote", " ".join(qt)))
            continue

        if re.match(r"^[\-\*]\s+", line.lstrip()):
            li_items = []
            while i < len(lines) and re.match(r"^[\-\*]\s+", lines[i].lstrip()):
                li_items.append(re.sub(r"^[\-\*]\s+", "", lines[i].lstrip()))
                i += 1
            blocks.append(("ul", li_items))
            continue

        if re.match(r"^\s*-\s+\[[ xX]\]\s+", line):
            checked = re.search(r"\[[ xX]\]", line).group(0).lower() == "[x]"
            txt = re.sub(r"^\s*-\s+\[[ xX]\]\s+", "", line)
            blocks.append(("checkbox", (txt, checked)))
            i += 1
            continue

        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() \
                and not re.match(r"^#{1,6}\s+", lines[i]) \
                and not lines[i].lstrip().startswith("|") \
                and not lines[i].lstrip().startswith(">") \
                and not re.match(r"^[\-\*]\s+", lines[i].lstrip()) \
                and not re.match(r"^\s*-\s+\[[ xX]\]\s+", lines[i]) \
                and not re.match(r"^-{3,}$", lines[i].strip()):
            para.append(lines[i].rstrip())
            i += 1
        blocks.append(("p", " ".join(para)))

    return blocks


def render_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="CN" color="' + BRAND + r'">\1</font>', text)
    return text


def build_table(rows_str):
    def split_row(s):
        s = s.strip().strip("|")
        return [c.strip() for c in s.split("|")]
    rows = [split_row(s) for s in rows_str]
    n_cols = max(len(r) for r in rows)
    col_w = USABLE_W / n_cols
    style = TableStyle([
        ("FONT", (0, 0), (-1, -1), "CN", 9),
        ("FONT", (0, 0), (-1, 0), "CN-B", 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fafafa"), colors.HexColor("#ffffff")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    data = [[Paragraph(render_inline(c), styles["p"]) for c in r] for r in rows]
    for r in data:
        while len(r) < n_cols:
            r.append("")
    return Table(data, colWidths=[col_w] * n_cols, style=style, repeatRows=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", help="议题目录名，如 2026-09-08-当升科技底部买入")
    ap.add_argument("--src", help="源 markdown（与 --topic 二选一）")
    ap.add_argument("--dst", help="输出 PDF 路径")
    ap.add_argument("--out", help="仅指定输出文件名，落在 outbox/")
    ap.add_argument("--title", help="PDF 标题与页脚文字")
    args = ap.parse_args()

    # 解析源与目标
    if args.topic:
        tdir = RT / "topics" / args.topic
        if not tdir.exists():
            print(f"[ERR] 找不到议题: {tdir}")
            return 1
        src = tdir / "decision.md"
        # 标题：优先 --title，其次 decision.md 首个 # 标题
        title = args.title
        if not title:
            first = next((l for l in src.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), None)
            title = first.lstrip("# ").strip() if first else args.topic
        # 日期：从目录名取
        m = re.match(r"(\d{4}-\d{2}-\d{2})", args.topic)
        date = m.group(1) if m else ""
        safe = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", args.topic)
        if args.out:
            dst = OUTBOX / args.out
        elif args.dst:
            dst = Path(args.dst)
        else:
            dst = OUTBOX / f"{safe}决议_{date}.pdf"
    elif args.src:
        src = Path(args.src)
        dst = Path(args.dst) if args.dst else src.with_suffix(".pdf")
        title = args.title or src.stem
        date = ""
    else:
        print("[ERR] 需要 --topic 或 --src")
        return 1

    if not src.exists():
        print(f"[ERR] 找不到源文件: {src}")
        return 1

    blocks = md_to_blocks(src.read_text(encoding="utf-8"))
    story = []
    for kind, content in blocks:
        if kind.startswith("h") and kind in styles:
            story.append(Paragraph(render_inline(content), styles[kind]))
        elif kind == "p":
            story.append(Paragraph(render_inline(content), styles["p"]))
        elif kind == "quote":
            story.append(Paragraph("│ " + render_inline(content), styles["quote"]))
        elif kind == "ul":
            for it in content:
                story.append(Paragraph("• " + render_inline(it), styles["li"]))
            story.append(Spacer(1, 4))
        elif kind == "checkbox":
            txt, checked = content
            story.append(Paragraph(("☑ " if checked else "☐ ") + render_inline(txt), styles["li"]))
        elif kind == "hr":
            story.append(Spacer(1, 6))
        elif kind == "table":
            try:
                story.append(build_table(content))
                story.append(Spacer(1, 6))
            except Exception as e:
                print(f"[WARN] 表格渲染失败: {e}")
                story.append(Paragraph(render_inline(" | ".join(content[0].split("|"))), styles["p"]))

    footer = f"第 {{page}} 页 · {title}" + (f" · {date}" if date else "")

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("CN", 8)
        canvas.setFillColor(colors.HexColor("#888"))
        canvas.drawCentredString(PAGE_W / 2, MARGIN / 2, footer.format(page=doc.page))
        canvas.restoreState()

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(dst), pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title=title, author="workbuddy")
    frame = Frame(MARGIN, MARGIN, USABLE_W, PAGE_H - 2 * MARGIN, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="default", frames=[frame], onPage=add_page_number)])
    doc.build(story)

    print(f"[OK] 已生成: {dst}")
    print(f"     {dst.stat().st_size / 1024:.1f} KB · 标题「{title}」")
    return 0


if __name__ == "__main__":
    sys.exit(main())
