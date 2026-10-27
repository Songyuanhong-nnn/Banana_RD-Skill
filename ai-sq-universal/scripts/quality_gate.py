#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated part of the ai-sq-universal quality gate.

Reads a generated report.md (and optionally its report.json) and checks the
mechanically verifiable gates from SKILL.md section 11. Human judgement gates
(counterexample quality, conflict handling, hierarchy correctness) stay human —
this script only catches the failures that are cheap to detect and expensive
to miss.

Usage:
    python scripts/quality_gate.py report.md
    python scripts/quality_gate.py report.md --json report.json
    python scripts/quality_gate.py report.md --risk high
    python scripts/quality_gate.py report.md --min-traceability 0.9

Exit code 0 = gate passed, 1 = gate failed.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

SECTIONS = [
    "一句话结论", "定义与归属", "属性与范围", "机制与因果链", "载体与要素清单",
    "结构细节", "功能", "反例与边界", "证据与争议", "前沿与未解问题",
    "下一步追问", "证据表", "假设、歧义与免责声明", "覆盖度与饱和声明",
]

MAGNITUDES = ("dominant", "major", "minor", "unknown")
COVERAGE_ITEMS = ("轴覆盖", "量级覆盖", "饱和", "负空间", "交互检查", "分层检查", "维度覆盖")

ABSOLUTE_WORDS = ("都", "所有", "全部", "一定", "必然", "唯一", "总是", "从不", "毫无")
# A line carrying any of these is not asserting the absolute: it is scoping,
# negating, or flagging the claim as unverified.
HEDGES = ("条件", "多数", "部分", "除", "反例", "范围", "限定", "通常", "可能",
          "待验证", "未见", "未获", "待重复", "存疑")

RISK_DOMAINS = {"medicine", "law", "finance", "security", "policy", "psychology"}


class Gate:
    def __init__(self) -> None:
        self.items: list[tuple[bool, str, str]] = []

    def add(self, ok: bool, name: str, detail: str) -> None:
        self.items.append((bool(ok), name, detail))

    @property
    def failed(self) -> list[tuple[bool, str, str]]:
        return [i for i in self.items if not i[0]]

    def render(self) -> str:
        out = []
        for ok, name, detail in self.items:
            out.append("%s  %-34s %s" % ("PASS" if ok else "FAIL", name, detail))
        out.append("")
        out.append("%d gates, %d failed -> %s" % (
            len(self.items), len(self.failed), "PASS" if not self.failed else "FAIL"))
        return "\n".join(out)


def load_text(path: str) -> str:
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def check_sections(text: str, gate: Gate) -> None:
    missing = [s for s in SECTIONS if s not in text]
    gate.add(not missing, "13 report sections present",
             "all present" if not missing else "missing: %s" % ", ".join(missing))

    headings = re.findall(r"^##\s+\d+\.", text, flags=re.M)
    gate.add(len(headings) >= 14, "14 numbered headings", "found %d" % len(headings))


def check_placeholders(text: str, gate: Gate) -> None:
    leftovers = re.findall(r"⟨[^⟩]{0,40}⟩", text)
    bracket = re.findall(r"\[[^\]\n]{2,30}\]", text)
    gate.add(not leftovers, "no placeholder left",
             "none" if not leftovers else "%d left, e.g. %s" % (len(leftovers), leftovers[0]))
    gate.add(len(bracket) <= 2, "few bracketed placeholders",
             "%d found" % len(bracket))


def check_evidence_ids(text: str, gate: Gate) -> None:
    # Evidence ids are E# in some reports and C# (citations) in others; both count.
    ids = set(re.findall(r"\b[CE]\d{1,3}\b", text))
    gate.add(len(ids) >= 3, "evidence ids referenced", "%d distinct (need >=3)" % len(ids))

    table_rows = 0
    for line in text.splitlines():
        if re.match(r"^\|\s*\**[CE]\d+", line.strip()):
            table_rows += 1
    gate.add(table_rows >= 3, "evidence table rows", "%d rows (need >=3)" % table_rows)


def check_traceability(text: str, gate: Gate, minimum: float) -> None:
    m = re.search(r"可追溯率[^\n]{0,80}", text)
    pcts = re.findall(r"(\d+(?:\.\d+)?)\s*%", m.group(0)) if m else []
    if not pcts:
        gate.add(False, "traceability declared", "no '可追溯率: X%' line found")
    else:
        ratio = float(pcts[-1]) / 100.0
        gate.add(ratio >= minimum, "traceability >= %.0f%%" % (minimum * 100),
                 "declared %.0f%%" % (ratio * 100))

    id_hits = len(re.findall(r"(PMID|DOI|https?://|第\d+条|acc(?:ession)?[_\s]?\w+|GCF_|NC_)", text))
    gate.add(id_hits >= 3, "resolvable source ids", "%d id-like tokens" % id_hits)


def _negated(line: str, index: int) -> bool:
    """True when the absolute word at `index` is negated, e.g. 不是所有 / 并非唯一."""
    window = line[max(0, index - 6):index]
    return any(n in window for n in ("不是", "并非", "而非", "非", "不", "未", "无"))


def check_absolutes(text: str, gate: Gate) -> None:
    offenders = []
    section8 = text.split("反例与边界", 1)[1] if "反例与边界" in text else ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("|") or len(stripped) < 8:
            continue
        if any(h in stripped for h in HEDGES):
            continue
        unhedged = False
        for word in ABSOLUTE_WORDS:
            start = 0
            while True:
                idx = stripped.find(word, start)
                if idx < 0:
                    break
                start = idx + 1
                if not _negated(stripped, idx):
                    unhedged = True
                    break
            if unhedged:
                break
        if unhedged:
            offenders.append(stripped[:70])
    gate.add(not offenders, "absolute claims hedged or countered",
             "none" if not offenders else "%d unhedged, e.g. %s" % (len(offenders), offenders[0]))
    gate.add(len(section8.strip()) > 80, "counterexample section substantive",
             "%d chars" % len(section8.strip()))


def check_stop_log(text: str, gate: Gate) -> None:
    gate.add("停止原因" in text or "stop_reason" in text, "stop reason present",
             "found" if ("停止原因" in text or "stop_reason" in text) else "missing section 13 stop log")
    m = re.search(r"停止原因\**\s*[：:](.{0,400})", text, flags=re.S)
    detail = (m.group(1).strip() if m else "")
    gate.add(len(detail) > 8, "stop reason non-empty", "%d chars" % len(detail))


def check_disclaimer(text: str, gate: Gate, risk: str, domain: str) -> None:
    needed = risk == "high" or domain in RISK_DOMAINS or "免责声明" in text
    has = "免责声明" in text
    gate.add(has if needed else True, "disclaimer when high-risk",
             ("present" if has else "missing") if needed else "not required")
    if needed:
        gate.add(any(w in text for w in ("不构成", "复核", "执业", "持牌")),
                 "disclaimer is actionable",
                 "mentions review/professional" if any(w in text for w in ("不构成", "复核", "执业", "持牌")) else "too generic")


def check_unknowns(text: str, gate: Gate) -> None:
    marks = [w for w in ("未知", "未找到", "无法确定", "待验证", "需实验", "未能检验") if w in text]
    gate.add(len(marks) >= 1, "unknowns stated explicitly", "markers: %s" % (marks or "none"))


def factor_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if re.match(r"^\|\s*\**F\d+\**\s*\|", line.strip())]


def check_factor_space(text: str, gate: Gate, level: int) -> None:
    """L2+ requires an enumerated factor space with a magnitude on every factor."""
    if level < 2:
        gate.add(True, "factor space (L2+)", "not required at L1")
        return

    rows = factor_rows(text)
    gate.add(len(rows) >= 3, "factor space has >=3 factors",
             "%d factor rows" % len(rows))
    vague = [row for row in rows if not any(m in row for m in MAGNITUDES)]
    gate.add(not vague, "every factor carries a magnitude",
             "all magnitudes present" if not vague
             else "%d rows without dominant/major/minor/unknown, e.g. %s" % (len(vague), vague[0][:60]))
    gate.add("量级依据" in text, "magnitude basis column", "present" if "量级依据" in text else "missing")

    if level < 3:
        return

    gate.add("分层" in text, "L3: stratification section", "present" if "分层" in text else "missing")
    gate.add("交互" in text, "L3: interaction section", "present" if "交互" in text else "missing")
    checked = any(k in text for k in ("checked-none", "checked_none", "未检出", "查过无"))
    gate.add(checked, "L3: 'checked-none' recorded",
             "present" if checked else "missing - reader cannot tell 'checked and found none' from 'never checked'")

    if level < 4:
        return
    gate.add(any(k in text for k in ("反馈", "时滞")), "L4: feedback / lag analysed",
             "present" if any(k in text for k in ("反馈", "时滞")) else "missing")
    gate.add("模型局限" in text or "局限声明" in text, "L4: model limits declared",
             "present" if ("模型局限" in text or "局限声明" in text) else "missing")


def check_coverage(text: str, gate: Gate, level: int) -> None:
    """Section 14 is the acceptance sheet for 'comprehensive'."""
    gate.add("覆盖度与饱和声明" in text, "section 14 present",
             "present" if "覆盖度与饱和声明" in text else "missing")
    if level < 2:
        return
    section = text.split("覆盖度与饱和声明", 1)[-1] if "覆盖度与饱和声明" in text else ""
    missing = [item for item in COVERAGE_ITEMS if item not in section]
    gate.add(not missing, "seven coverage criteria stated",
             "all seven" if not missing else "missing %s" % missing)
    gate.add(any(k in section for k in ("负空间", "应有但未找到")), "negative space listed",
             "present" if "负空间" in section else "missing")

    # 7th criterion: dimension coverage must be content-bearing, not just named.
    drows = [line for line in text.splitlines()
             if re.match(r"^\|\s*D\d+\b", line.strip())
             and any(s in line for s in ("已答", "不适用", "未查", "激活"))]
    dim_row = next((line for line in text.splitlines() if "维度覆盖" in line), "")
    has_counts = bool(re.search(r"\d+\s*/\s*14", dim_row))
    has_unchecked = ("未查" in dim_row and re.search(r"D\d+", dim_row) is not None)
    gate.add(len(drows) >= 5 or (has_counts and has_unchecked),
             "dimension coverage enumerated",
             "full table (%d rows)" % len(drows) if len(drows) >= 5
             else ("compact line with counts+unchecked" if (has_counts and has_unchecked)
                   else "needs 5+ D-rows, or one line with 'n/14' + 未查 + dimension ids"))


VAGUE_ATTRIBUTION = ("据报道", "有消息称", "业内人士", "相关人士", "多家媒体", "据悉", "有分析认为")
LOCATOR_RE = re.compile(
    r"(p\.\s?\d+"
    r"|第\s?\d+\s?[段条款页章节行项]"
    r"|第[一二三四五六七八九十]+[段条款章节行项]"
    r"|表\s?\d+|图\s?\d+"
    r"|\d{1,2}:\d{2}(:\d{2})?"
    r"|\d+(\.\d+)?\s?[节章]"
    r"|摘要|正文|方法|结果|讨论|附录|脚注|封面|小节"
    r")"
)


def citation_rows(text: str) -> list[str]:
    # A citation row may use its own C# series or reuse the evidence E# series.
    return [line for line in text.splitlines()
            if re.match(r"^\|\s*\**[CE]\d+\**\s*\|", line.strip())]


STRICT_LOCATOR = re.compile(
    r"^(p\.\s?\d{1,4}"
    r"|第\s?\d{1,4}\s?[条款页段行项]"
    r"|第[一二三四五六七八九十]{1,3}[条款段章节行项]"
    r"|表\s?\d{1,3}(\s?第\s?\d{1,3}\s?行)?"
    r"|图\s?\d{1,3}"
    r"|\d{1,2}:\d{2}(:\d{2})?"
    r"|\d+(\.\d+){1,2}\s?[节章]"
    r"|查询[:：].+"
    # Web sources have no page numbers; a *named* section is locatable by in-page
    # search, while a generic "正文/摘要" is not (that was the 2026-10 audit finding).
    r"|[「『][^」』]{1,60}[」』](第\s?\d{1,3}\s?[段条])?"
    r")$"
)


def parse_cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def check_citation(text: str, gate: Gate, level: int) -> None:
    """Verifiable to the sentence, not to the link.

    The 2026-10 audit found this gate could be satisfied by a structurally perfect
    but semantically empty table (author-declared verified_by/open rates, locators
    matching section *names* instead of positions). Fixes applied: per-column
    parsing, digit-bearing locator requirement, and a traceability rate that the
    script computes instead of trusting the author.
    """
    head = text.split("### 12.1", 1)[0]
    rows = citation_rows(head)
    gate.add(len(rows) >= 3, "citation rows >=3", "%d rows" % len(rows))

    # Header must be the real column set, not a mention somewhere in the prose.
    lines = head.splitlines()
    first_idx = next((i for i, line in enumerate(lines) if line in rows), None)
    header = ""
    if first_idx is not None:
        for back in range(1, 4):  # header, then |---| separator, then data
            if first_idx - back >= 0 and "定位" in lines[first_idx - back]:
                header = lines[first_idx - back]
                break
    gate.add("定位" in header and "原文句" in header, "citation table header has 定位 + 原文句",
             "header ok" if ("定位" in header and "原文句" in header) else "header missing columns: %r" % header[:60])

    parsed = [parse_cells(r) for r in rows]
    structured = [c for c in parsed if len(c) >= 12]
    gate.add(len(structured) == len(parsed), "all rows have >=12 columns",
             "%d/%d structured" % (len(structured), len(parsed)))

    bad_locator, short_quote, bad_grade = [], [], []
    for cells in structured:
        locator, quote, grade = cells[6], cells[7], cells[9]
        if not STRICT_LOCATOR.match(locator):
            bad_locator.append(locator[:30])
        if len(quote) < 12:
            short_quote.append(quote[:20])
        if grade not in ("A", "B", "C", "D"):
            bad_grade.append(grade)
    gate.add(not bad_locator, "locator is a position (页/段/条/表行/时间戳/查询)",
             "all positional" if not bad_locator
             else "%d are section names, not positions: %s" % (len(bad_locator), bad_locator[:3]))
    gate.add(not short_quote, "verbatim quote >=12 chars",
             "all substantial" if not short_quote else "%d too short: %s" % (len(short_quote), short_quote[:3]))
    gate.add(not bad_grade, "grade in A-D", "ok" if not bad_grade else "bad: %s" % bad_grade[:3])

    # Computed traceability, compared against the author's claim.
    total = len(structured) or 1
    computed = sum(1 for c in structured
                   if STRICT_LOCATOR.match(c[6]) and len(c[7]) >= 12) / float(total)
    declared_m = re.search(r"可追溯率[^\n]{0,80}", text)
    pcts = re.findall(r"(\d+(?:\.\d+)?)\s*%", declared_m.group(0)) if declared_m else []
    if not pcts:
        gate.add(False, "traceability declared", "no '可追溯率: X%' line")
    else:
        declared = float(pcts[-1]) / 100.0
        gate.add(declared <= computed + 0.05, "declared traceability not above computed",
                 "declared %.0f%% vs computed %.0f%%" % (declared * 100, computed * 100))
        gate.add(computed >= 0.90, "computed traceability >= 90%",
                 "%.0f%%" % (computed * 100))

    # Closure both ways: ids cited in the body must exist; ids in the table must be used.
    body = text.split("## 12.", 1)[0]
    body_ids = set(re.findall(r"\b([CE]\d{1,3})\b", body))
    table_ids = {c[0].strip("*") for c in structured}
    dangling = sorted(body_ids - table_ids)
    gate.add(not dangling, "no dangling citation ids",
             "closed" if not dangling else "cited but not in table: %s" % dangling[:5])
    unused = sorted(table_ids - body_ids)
    gate.add(len(unused) <= max(1, len(table_ids) // 3), "table rows are actually used",
             "%d unused (appendix-only is fine if few)" % len(unused))

    vague = [line.strip() for line in text.splitlines()
             if any(v in line for v in VAGUE_ATTRIBUTION) and not line.strip().startswith("|")]
    gate.add(not vague, "no vague attribution in prose",
             "none" if not vague else "%d lines, e.g. %s" % (len(vague), vague[0][:60]))

    media_overbid = [c[0] for c in structured
                     if any(k in c[2] for k in ("公众号", "媒体", "自媒体", "新闻"))
                     and c[9] in ("A", "B")]
    gate.add(not media_overbid, "media/公众号 not graded A/B",
             "none" if not media_overbid else "overbid: %s" % media_overbid[:3])

    chained = [c[0] for c in structured if c[11].isdigit() and int(c[11]) >= 2]
    if chained:
        gate.add("回溯" in text or "一手" in text, "second-hand chain traced",
                 "traced" if ("回溯" in text or "一手" in text)
                 else "%d chained citations without any trace-back note" % len(chained))

    # Sampling log: the heading alone must not satisfy this (template would pass).
    if "抽样核验记录" in text:
        tail = text.split("抽样核验记录", 1)[1]
        srows = [line for line in tail.splitlines()
                 if line.strip().startswith("|") and ("是" in line or "否" in line)]
        gate.add(len(srows) >= 2, "sampling log has >=2 filled rows",
                 "%d filled rows" % len(srows))
    else:
        gate.add(False, "sampling verification recorded", "missing section 12.1")
    provenance_only = [c[0] for c in structured if "provenance" in " ".join(c).lower()]
    if provenance_only:
        gate.add("可追责" in text or "不可公开复核" in text, "provenance-only citations flagged",
                 "flagged" if ("可追责" in text or "不可公开复核" in text)
                 else "provenance citations without accountability note")


BRIEF_ROLES = ("决策者", "付费者", "使用者", "被影响者", "守门人")
NARRATIVE_BAD_OPEN = ("下表", "如下表", "本表", "以下是", "如下所示", "数据如下", "详见下表")


def check_brief(text: str, gate: Gate) -> None:
    """Purpose + stakeholders + scope expansion: without them a report is precise but useless."""
    gate.add("调研目的与受益方" in text, "section 0 present",
             "present" if "调研目的与受益方" in text else "missing - nobody knows who this is for")
    for item in ("支撑什么决定", "成功标准", "明确不做什么"):
        gate.add(item in text, "brief: %s" % item, "present" if item in text else "missing")

    roles = [r for r in BRIEF_ROLES if re.search(r"\|\s*\**%s" % r, text)]
    gate.add(len(roles) >= 3, "stakeholders >=3 roles",
             "%d roles: %s" % (len(roles), roles))
    gate.add(len(roles) >= 4 or "为何不适用" in text, "missing roles explained",
             "ok" if (len(roles) >= 4 or "为何不适用" in text) else "only %d roles and no explanation" % len(roles))

    gate.add("需求外扩审计" in text, "scope expansion audit", "present" if "需求外扩审计" in text else "missing")
    if "需求外扩审计" in text:
        tail = text.split("需求外扩审计", 1)[1][:2000]
        rows = [l for l in tail.splitlines() if l.strip().startswith("|") and "⟨" not in l and "---" not in l]
        gate.add(len(rows) >= 3, "scope expansion has >=2 entries", "%d table lines" % len(rows))


def check_narrative(text: str, gate: Gate) -> None:
    """Each section must open with a judgement, not with a table pointer."""
    bad = []
    blocks = re.split(r"^##\s+\d+\.[^\n]*\n", text, flags=re.M)
    for block in blocks[1:]:
        for line in block.splitlines():
            s = line.strip()
            if not s or s.startswith("|") or s.startswith("<!--") or s.startswith("###"):
                continue
            if s.startswith(NARRATIVE_BAD_OPEN):
                bad.append(s[:40])
            break
    gate.add(not bad, "sections open with a judgement",
             "ok" if not bad else "%d sections open with a table pointer: %s" % (len(bad), bad[:2]))

    gate.add("serves" in text or "对谁" in text or "谁据此" in text,
             "conclusions tagged with stakeholder impact",
             "tagged" if ("serves" in text or "对谁" in text or "谁据此" in text) else "no stakeholder tagging")


def check_json(path: str, gate: Gate) -> None:
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (ValueError, OSError) as exc:
        gate.add(False, "report.json parses", str(exc))
        return
    gate.add(isinstance(doc, dict), "report.json parses", "object")
    required = ["target", "goal", "domain", "params", "one_line_conclusion", "conclusions",
                "evidence", "conflicts", "gaps", "stop_log", "risks", "metrics", "nodes"]
    missing = [k for k in required if k not in doc]
    gate.add(not missing, "report.json required keys", "all present" if not missing else "missing %s" % missing)
    gate.add(bool(doc.get("stop_log")), "report.json stop_log non-empty",
             "%d entries" % len(doc.get("stop_log") or []))
    conclusions = doc.get("conclusions") or []
    unsupported = [c.get("text", "")[:40] for c in conclusions
                   if isinstance(c, dict) and not c.get("evidence_ids")]
    gate.add(not unsupported, "every conclusion has evidence_ids",
             "all supported" if not unsupported else "%d unsupported, e.g. %s" % (len(unsupported), unsupported[0]))
    ev = doc.get("evidence") or []
    bad_grade = [e.get("evidence_id") for e in ev
                 if isinstance(e, dict) and e.get("evidence_grade") not in ("A", "B", "C", "D")]
    gate.add(not bad_grade, "evidence grades valid",
             "all A-D" if not bad_grade else "bad grades: %s" % bad_grade)
    no_quote = [e.get("evidence_id") for e in ev if isinstance(e, dict) and not e.get("quote")]
    gate.add(not no_quote, "every evidence has a quote",
             "all quoted" if not no_quote else "missing quote: %s" % no_quote)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:  # Windows consoles default to GBK and would fail on Chinese details
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Automated quality gate for an ai-sq report.")
    ap.add_argument("report", help="path to report.md")
    ap.add_argument("--json", dest="json_path", default=None, help="path to the matching report.json")
    ap.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--domain", default="general")
    ap.add_argument("--complexity", type=int, choices=[1, 2, 3, 4], default=2,
                    help="L1 单链 / L2 多因素 / L3 多因素+交互异质 / L4 动态系统")
    ap.add_argument("--min-traceability", type=float, default=0.90)
    args = ap.parse_args(argv)

    if not os.path.isfile(args.report):
        sys.stderr.write("no such report: %s\n" % args.report)
        return 2

    text = load_text(args.report)
    gate = Gate()
    check_sections(text, gate)
    check_placeholders(text, gate)
    check_evidence_ids(text, gate)
    check_traceability(text, gate, args.min_traceability)
    check_absolutes(text, gate)
    check_stop_log(text, gate)
    check_disclaimer(text, gate, args.risk, args.domain)
    check_unknowns(text, gate)
    check_factor_space(text, gate, args.complexity)
    check_coverage(text, gate, args.complexity)
    check_citation(text, gate, args.complexity)
    check_brief(text, gate)
    check_narrative(text, gate)
    if args.json_path:
        check_json(args.json_path, gate)

    sys.stdout.write(gate.render() + "\n")
    return 0 if not gate.failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
