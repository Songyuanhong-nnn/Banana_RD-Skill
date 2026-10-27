#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a Markdown report into a styled Word (.docx) document.

Why this exists: the skill's reports are written in Markdown because that is what
a model edits reliably, but they are *delivered* as Word because that is what a
reader opens. This script is the bridge, so the Word document is generated from
the same single source rather than retyped (retyping is how reports drift).

Usage
-----
    # one file
    python scripts/build_docx.py report.md -o report.docx --title "标题"

    # many files as chapters, driven by a config
    python scripts/build_docx.py --config docx_config.json

Config (JSON) fields, all optional except `files`:
    title, subtitle, date, meta[[label, value]], toc(bool), header, footer_note,
    accent("1F3864"), font_body("宋体"), font_head("微软雅黑"),
    files: [{"path": "a.md", "pagebreak": true, "title": "可选章节名"}]

Supported Markdown subset: #/##/### headings, paragraphs, **bold**, `code`,
[text](url) links, -/* bullets, 1. numbered lists, > blockquotes (rendered as
callout boxes), fenced code blocks, pipe tables, --- rules, ![alt](img) images.

Exit codes: 0 ok, 2 bad input.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DEFAULTS = {
    "title": "调研报告",
    "subtitle": "",
    "date": "",
    "meta": [],
    "toc": True,
    "header": "",
    "footer_note": "",
    "accent": "1F3864",
    "accent2": "2E74B5",
    "font_body": "宋体",
    "font_head": "微软雅黑",
    "font_mono": "Consolas",
}

INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|https?://[^\s)\]）】,，。]+)")


# --------------------------------------------------------------------------- #
# low-level helpers
# --------------------------------------------------------------------------- #
def _set_run_font(run, name=None, size=None, bold=None, color=None, italic=None):
    if name:
        run.font.name = name
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:eastAsia"), name)
        rfonts.set(qn("w:ascii"), name)
        rfonts.set(qn("w:hAnsi"), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


PPR_AFTER_PBDR = (
    "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
    "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
    "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
    "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
    "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
)
TCPR_AFTER_SHD = (
    "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign",
    "w:hideMark", "w:headers", "w:cellIns", "w:cellDel", "w:cellMerge",
    "w:tcPrChange",
)


def _shade(element, fill):
    """Apply background shading, inserted at a schema-valid position."""
    is_cell = element.tag.endswith("}tc")
    pr = element.get_or_add_tcPr() if is_cell else element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    successors = TCPR_AFTER_SHD if is_cell else PPR_AFTER_PBDR[1:]
    try:
        pr.insert_element_before(shd, *successors)
    except (AttributeError, ValueError):
        pr.append(shd)


def _para_border(paragraph, side="left", color="2E74B5", size=18):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = ppr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        try:
            ppr.insert_element_before(pbdr, *PPR_AFTER_PBDR)
        except (AttributeError, ValueError):
            ppr.append(pbdr)
    el = OxmlElement("w:" + side)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), "6")
    el.set(qn("w:color"), color)
    pbdr.append(el)


def _add_hyperlink(paragraph, url, text, color="1155CC"):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rpr.append(c)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


def _add_field(paragraph, instr, placeholder=""):
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), instr)
    run = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = placeholder
    run.append(t)
    fld.append(run)
    paragraph._p.append(fld)


def _enable_update_fields(doc):
    """Ask Word to refresh the TOC/page fields when the file is opened."""
    settings = doc.settings.element
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings.append(uf)


# --------------------------------------------------------------------------- #
# inline markdown -> runs
# --------------------------------------------------------------------------- #
def add_inline(paragraph, text, cfg, base_size=10.5, bold=False, font=None):
    body_font = font or cfg["font_body"]
    text = text.replace("\\|", "|")
    for token in INLINE_RE.split(text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            run = paragraph.add_run(token[2:-2])
            _set_run_font(run, body_font, base_size, bold=True)
        elif token.startswith("`") and token.endswith("`") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            _set_run_font(run, cfg["font_mono"], base_size - 0.5)
        elif token.startswith("[") and "](" in token:
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token)
            if m:
                _add_hyperlink(paragraph, m.group(2), m.group(1))
        elif token.startswith("http"):
            _add_hyperlink(paragraph, token, token)
            run = paragraph.add_run("")
            _set_run_font(run, body_font, base_size)
        else:
            run = paragraph.add_run(token)
            _set_run_font(run, body_font, base_size, bold=bold)


# --------------------------------------------------------------------------- #
# block renderers
# --------------------------------------------------------------------------- #
def add_heading(doc, text, level, cfg):
    sizes = {1: 19, 2: 15, 3: 12.5, 4: 11.5}
    p = doc.add_paragraph(style="Heading %d" % min(level, 4))
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    add_inline(p, text, cfg, base_size=sizes.get(level, 11), bold=True, font=cfg["font_head"])
    color = cfg["accent"] if level == 1 else cfg["accent2"]
    for run in p.runs:
        run.font.color.rgb = RGBColor.from_string(color)
        run.font.bold = True
    if level == 1:
        _para_border(p, "bottom", cfg["accent"], 12)
    return p


def add_paragraph(doc, text, cfg, indent=0.0, size=10.5, after=4):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.55
    pf.space_after = Pt(after)
    if indent:
        pf.left_indent = Cm(indent)
    add_inline(p, text, cfg, base_size=size)
    return p


def add_bullet(doc, text, cfg, ordered=False, level=0):
    style = "List Number" if ordered else "List Bullet"
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.45
    if level:
        p.paragraph_format.left_indent = Cm(0.75 + 0.6 * level)
    add_inline(p, text, cfg)
    return p


def add_callout(doc, lines, cfg):
    """Blockquote -> shaded box with left rule. Used for banners and caveats."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    _shade(cell._tc, "F2F5FA")
    cell.paragraphs[0].text = ""
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.35
        _para_border(p, "left", cfg["accent2"], 12)
        add_inline(p, line, cfg, base_size=9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_code_block(doc, lines, cfg):
    table = doc.add_table(rows=1, cols=1)
    cell = table.rows[0].cells[0]
    _shade(cell._tc, "F5F5F5")
    cell.paragraphs[0].text = ""
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line if line else " ")
        _set_run_font(run, cfg["font_mono"], 8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def add_table(doc, rows, cfg):
    header, body = rows[0], rows[1:]
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    size = 8.5 if ncols >= 6 else 9.0

    for r, cells in enumerate(rows):
        for c in range(ncols):
            cell = table.cell(r, c)
            cell.paragraphs[0].text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.2
            txt = cells[c] if c < len(cells) else ""
            if r == 0:
                _shade(cell._tc, cfg["accent"])
                for tok in [txt]:
                    run = p.add_run(tok)
                    _set_run_font(run, cfg["font_head"], size, bold=True, color="FFFFFF")
            else:
                if r % 2 == 0:
                    _shade(cell._tc, "F7F9FC")
                add_inline(p, txt, cfg, base_size=size)

    # repeat header row on page breaks
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_image(doc, path, cfg, width_cm=15.5):
    if not os.path.isfile(path):
        add_paragraph(doc, "（图片缺失：%s）" % path, cfg)
        return
    doc.add_picture(path, width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


# --------------------------------------------------------------------------- #
# markdown driver
# --------------------------------------------------------------------------- #
def render_markdown(doc, text, cfg):
    lines = text.splitlines()
    i, n = 0, len(lines)
    if lines and lines[0].strip() == "---":  # skip YAML front matter
        for j in range(1, min(n, 30)):
            if lines[j].strip() == "---":
                i = j + 1
                break

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            add_code_block(doc, buf, cfg)
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|?$", lines[i + 1].strip()):
            rows = [_split_row(stripped)]
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                rows.append(_split_row(lines[i]))
                i += 1
            add_table(doc, rows, cfg)
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            add_heading(doc, m.group(2).strip(), len(m.group(1)), cfg)
            i += 1
            continue

        # blockquote -> callout
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            add_callout(doc, buf, cfg)
            continue

        # image
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if m:
            add_image(doc, m.group(2), cfg)
            i += 1
            continue

        # lists
        m = re.match(r"^(\s*)([-*+])\s+(.*)$", line)
        if m:
            level = len(m.group(1)) // 2
            add_bullet(doc, m.group(3), cfg, ordered=False, level=min(level, 2))
            i += 1
            continue
        m = re.match(r"^(\s*)\d+[.)]\s+(.*)$", line)
        if m:
            level = len(m.group(1)) // 2
            add_bullet(doc, m.group(2), cfg, ordered=True, level=min(level, 2))
            i += 1
            continue

        add_paragraph(doc, stripped, cfg)
        i += 1


# --------------------------------------------------------------------------- #
# page furniture
# --------------------------------------------------------------------------- #
def build_cover(doc, cfg):
    sec = doc.sections[0]
    band = doc.add_table(rows=1, cols=1)
    cell = band.rows[0].cells[0]
    _shade(cell._tc, cfg["accent"])
    cell.paragraphs[0].text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(46)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(cfg["title"])
    _set_run_font(run, cfg["font_head"], 26, bold=True, color="FFFFFF")

    if cfg["subtitle"]:
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(40)
        r2 = p2.add_run(cfg["subtitle"])
        _set_run_font(r2, cfg["font_head"], 12.5, color="D6E0F0")

    doc.add_paragraph()
    if cfg["meta"]:
        t = doc.add_table(rows=len(cfg["meta"]), cols=2)
        for idx, (k, v) in enumerate(cfg["meta"]):
            for c, txt in enumerate((k, v)):
                cell = t.cell(idx, c)
                cell.paragraphs[0].text = ""
                run = cell.paragraphs[0].add_run(txt)
                if c == 0:
                    _shade(cell._tc, "EDF1F8")
                    _set_run_font(run, cfg["font_head"], 10, bold=True)
                else:
                    _set_run_font(run, cfg["font_body"], 10)

    for _ in range(3):
        doc.add_paragraph()
    if cfg["date"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(cfg["date"])
        _set_run_font(run, cfg["font_body"], 11, color="555555")
    doc.add_page_break()


def build_toc(doc, cfg):
    p = doc.add_paragraph()
    run = p.add_run("目　录")
    _set_run_font(run, cfg["font_head"], 18, bold=True, color=cfg["accent"])
    _para_border(p, "bottom", cfg["accent"], 12)
    note = doc.add_paragraph()
    r = note.add_run("（在 Word 中按 Ctrl+A 后 F9 可刷新页码）")
    _set_run_font(r, cfg["font_body"], 9, color="888888")
    field_p = doc.add_paragraph()
    _add_field(field_p, 'TOC \\o "1-2" \\h \\z \\u', "打开后如未显示目录，请右键→更新域")
    doc.add_page_break()


def build_header_footer(doc, cfg):
    sec = doc.sections[0]
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.2)

    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if cfg["header"]:
        run = hp.add_run(cfg["header"])
        _set_run_font(run, cfg["font_body"], 8.5, color="999999")
        _para_border(hp, "bottom", "CCCCCC", 6)

    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cfg["footer_note"]:
        r = fp.add_run(cfg["footer_note"] + "　")
        _set_run_font(r, cfg["font_body"], 8, color="999999")
    r1 = fp.add_run("第 ")
    _set_run_font(r1, cfg["font_body"], 8, color="999999")
    _add_field(fp, "PAGE", "1")
    r2 = fp.add_run(" 页 / 共 ")
    _set_run_font(r2, cfg["font_body"], 8, color="999999")
    _add_field(fp, "NUMPAGES", "1")
    r3 = fp.add_run(" 页")
    _set_run_font(r3, cfg["font_body"], 8, color="999999")


def base_styles(doc, cfg):
    normal = doc.styles["Normal"]
    normal.font.name = cfg["font_body"]
    normal.font.size = Pt(10.5)
    rpr = normal.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    rf.set(qn("w:eastAsia"), cfg["font_body"])
    for name in ("List Bullet", "List Number"):
        st = doc.styles[name]
        st.font.name = cfg["font_body"]
        st.font.size = Pt(10.5)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Render Markdown into a styled .docx")
    ap.add_argument("files", nargs="*", help="markdown files (chapters)")
    ap.add_argument("-o", "--out", default="report.docx")
    ap.add_argument("--config", default=None, help="JSON config with cover/toc/files")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--header", default=None)
    ap.add_argument("--no-toc", action="store_true")
    args = ap.parse_args(argv)

    cfg = dict(DEFAULTS)
    chapters = []
    if args.config:
        with io.open(args.config, "r", encoding="utf-8") as fh:
            conf = json.load(fh)
        cfg.update({k: v for k, v in conf.items() if k in DEFAULTS or k == "files"})
        chapters = conf.get("files", [])
    for path in args.files:
        chapters.append({"path": path, "pagebreak": True})

    for key, val in (("title", args.title), ("subtitle", args.subtitle),
                     ("date", args.date), ("header", args.header)):
        if val:
            cfg[key] = val
    if args.no_toc:
        cfg["toc"] = False
    if not chapters:
        sys.stderr.write("no input files\n")
        return 2

    doc = Document()
    base_styles(doc, cfg)
    build_cover(doc, cfg)
    if cfg["toc"]:
        build_toc(doc, cfg)
    build_header_footer(doc, cfg)
    _enable_update_fields(doc)

    base = os.path.dirname(os.path.abspath(args.config)) if args.config else ""
    for idx, ch in enumerate(chapters):
        path = ch["path"]
        if base and not os.path.isabs(path):
            path = os.path.join(base, path)
        if not os.path.isfile(path):
            sys.stderr.write("missing chapter: %s\n" % path)
            return 2
        if idx > 0 and ch.get("pagebreak", True):
            doc.add_page_break()
        if ch.get("title"):
            add_heading(doc, ch["title"], 1, cfg)
        with io.open(path, "r", encoding="utf-8") as fh:
            render_markdown(doc, fh.read(), cfg)

    out = os.path.abspath(args.out)
    doc.save(out)

    # Reopen once: catches a corrupt package before a reader does.
    try:
        check = Document(out)
        heads = sum(1 for p in check.paragraphs if p.style.name.startswith("Heading"))
        print("verify: paragraphs=%d headings=%d tables=%d"
              % (len(check.paragraphs), heads, len(check.tables)))
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write("saved but failed verification: %s\n" % exc)
        return 1

    size = os.path.getsize(out)
    print("saved: %s" % out)
    print("chapters: %d | size: %.1f KiB" % (len(chapters), size / 1024.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
