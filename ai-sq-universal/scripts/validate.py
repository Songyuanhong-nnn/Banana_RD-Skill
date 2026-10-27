#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate an ai-sq-universal skill package.

Checks the SKILL.md frontmatter, the required file layout, every domain pack
against schemas/domain_pack.json, and evals/cases.yaml coverage.

Usage:
    python scripts/validate.py                 # validate the package containing this script
    python scripts/validate.py --root <dir>    # validate another checkout
    python scripts/validate.py --packs         # only domain packs
    python scripts/validate.py --json          # machine-readable result

Exit code 0 = all checks pass, 1 = at least one failure.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required: pip install pyyaml\n")
    raise SystemExit(2)

REQUIRED_FILES = [
    "SKILL.md",
    "prompts/planner.md",
    "prompts/question_generator.md",
    "prompts/factor_mapper.md",
    "prompts/briefer.md",
    "prompts/narrator.md",
    "prompts/citation_auditor.md",
    "prompts/extractor.md",
    "prompts/verifier.md",
    "prompts/reporter.md",
    "schemas/question_node.json",
    "schemas/evidence.json",
    "schemas/factor.json",
    "schemas/citation.json",
    "schemas/report.json",
    "schemas/domain_pack.json",
    "references/brief_and_stakeholders.md",
    "references/dimension_outline.md",
    "references/complexity_patterns.md",
    "references/domain_fit.md",
    "references/omissions_audit.md",
    "templates/report.md",
    "scripts/build_docx.py",
    "evals/cases.yaml",
    "examples/README.md",
    "examples/04-industry-direction.md",
    "examples/05-equipment.md",
]

PACK_REQUIRED = [
    "domain",
    "display_name",
    "version",
    "high_risk",
    "entity_levels",
    "relations",
    "structure_semantics",
    "authoritative_sources",
    "evidence_grades",
    "counterexample_rule",
    "disambiguation",
    "answer_patterns",
    "stop_hints",
    "frontier_sources",
]

RELATIONS = {
    "is_a", "part_of", "has_property", "causes", "contributes_to", "encoded_by",
    "located_in", "requires", "regulates", "precedes", "conflicts_with",
    "evidence_for", "counterexample_to", "correlates_with", "measured_by",
}

EVAL_CATEGORIES = {
    "科学": "science",
    "法律": "law",
    "金融": "finance",
    "历史": "history",
    "技术": "technology",
    "政策": "policy",
    "商业": "business",
    "歧义": "ambiguity",
    "无答案": "no_answer",
    "高风险": "high_risk",
}

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Result:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, ok: bool, area: str, message: str) -> None:
        self.checks.append({"ok": bool(ok), "area": area, "message": message})

    @property
    def failed(self) -> list[dict]:
        return [c for c in self.checks if not c["ok"]]

    def report(self) -> str:
        lines = []
        for c in self.checks:
            lines.append("%s  [%s] %s" % ("PASS" if c["ok"] else "FAIL", c["area"], c["message"]))
        bad = len(self.failed)
        lines.append("")
        lines.append("%d checks, %d failed" % (len(self.checks), bad))
        return "\n".join(lines)


def read_frontmatter(path: str) -> dict:
    with io.open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        raise ValueError("no YAML frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    return yaml.safe_load(text[3:end]) or {}


def check_layout(root: str, res: Result) -> None:
    missing = [p for p in REQUIRED_FILES if not os.path.isfile(os.path.join(root, p))]
    res.add(not missing, "layout", "all required files present" if not missing
            else "missing files: %s" % ", ".join(missing))
    for d in ("prompts", "schemas", "domain_packs", "templates", "evals", "examples", "scripts"):
        res.add(os.path.isdir(os.path.join(root, d)), "layout", "directory %s/" % d)


def check_frontmatter(root: str, res: Result) -> None:
    path = os.path.join(root, "SKILL.md")
    try:
        fm = read_frontmatter(path)
    except (ValueError, yaml.YAMLError) as exc:
        res.add(False, "frontmatter", "SKILL.md: %s" % exc)
        return
    name = fm.get("name")
    desc = fm.get("description")
    res.add(isinstance(name, str) and bool(SKILL_NAME_RE.match(name or "")), "frontmatter",
            "name is kebab-case: %r" % (name,))
    res.add(isinstance(desc, str) and len(desc) >= 40, "frontmatter",
            "description present and substantive (%d chars)" % (len(desc) if isinstance(desc, str) else 0))
    res.add(isinstance(fm.get("version"), str), "frontmatter", "version present: %r" % (fm.get("version"),))
    res.add("triggers" in fm and isinstance(fm.get("triggers"), list), "frontmatter",
            "triggers list present")
    res.add("not_for" in fm, "frontmatter", "not_for present")


def check_pack(path: str, res: Result) -> None:
    rel = os.path.basename(path)
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
    except (yaml.YAMLError, OSError) as exc:
        res.add(False, "pack", "%s: cannot parse YAML: %s" % (rel, exc))
        return
    if not isinstance(doc, dict):
        res.add(False, "pack", "%s: top level is not a mapping" % rel)
        return

    missing = [k for k in PACK_REQUIRED if k not in doc]
    res.add(not missing, "pack", "%s: required keys present" % rel
            if not missing else "%s: missing keys %s" % (rel, missing))

    levels = doc.get("entity_levels") or []
    res.add(isinstance(levels, list) and 6 <= len(levels) <= 20, "pack",
            "%s: entity_levels has %d entries (need 6-20)" % (rel, len(levels) if isinstance(levels, list) else -1))

    rels = doc.get("relations") or []
    bad_rel = [r for r in rels if r not in RELATIONS]
    res.add(isinstance(rels, list) and bool(rels) and not bad_rel, "pack",
            "%s: relations valid" % rel if not bad_rel else "%s: unknown relations %s" % (rel, bad_rel))

    sem = doc.get("structure_semantics") or {}
    need_sem = [k for k in ("segment", "copy", "variant") if not sem.get(k)]
    res.add(not need_sem, "pack", "%s: structure_semantics complete" % rel
            if not need_sem else "%s: structure_semantics missing %s" % (rel, need_sem))

    srcs = doc.get("authoritative_sources") or []
    src_ok = isinstance(srcs, list) and len(srcs) >= 3 and all(
        isinstance(s, dict) and s.get("name") and s.get("priority") for s in srcs)
    prios = sorted({s.get("priority") for s in srcs if isinstance(s, dict)})
    res.add(src_ok, "pack", "%s: authoritative_sources valid (%d, priorities %s)" % (rel, len(srcs), prios))

    grades = doc.get("evidence_grades") or {}
    have = sorted(k for k in grades if k in ("A", "B", "C", "D"))
    res.add(have == ["A", "B", "C", "D"], "pack",
            "%s: evidence_grades A-D present" % rel if have == ["A", "B", "C", "D"]
            else "%s: evidence_grades has %s" % (rel, have))
    res.add(isinstance(doc.get("high_risk"), bool), "pack",
            "%s: high_risk is boolean (%r)" % (rel, doc.get("high_risk")))

    dis = doc.get("disambiguation") or []
    res.add(isinstance(dis, list) and len(dis) >= 1 and all(
        isinstance(d, dict) and d.get("term") and d.get("candidates") and d.get("resolve_by") for d in dis),
        "pack", "%s: disambiguation entries complete (%d)" % (rel, len(dis)))

    res.add(bool(doc.get("counterexample_rule")), "pack", "%s: counterexample_rule present" % rel)

    for sub_name, sub in (doc.get("sub_packs") or {}).items():
        sub_missing = [k for k in PACK_REQUIRED if k not in (sub or {})]
        res.add(not sub_missing, "pack", "%s#sub_packs.%s: complete" % (rel, sub_name)
                if not sub_missing else "%s#sub_packs.%s: missing %s" % (rel, sub_name, sub_missing))


def check_evals(root: str, res: Result) -> None:
    path = os.path.join(root, "evals", "cases.yaml")
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
    except (yaml.YAMLError, OSError) as exc:
        res.add(False, "evals", "cases.yaml: cannot parse: %s" % exc)
        return
    cases = (doc or {}).get("cases") or []
    res.add(len(cases) >= 10, "evals", "10+ cases (found %d)" % len(cases))
    ids = [c.get("id") for c in cases]
    res.add(len(set(ids)) == len(ids), "evals", "case ids unique")
    required = ("id", "title", "domain", "pack", "risk", "prompt", "goal",
                "probes", "must_show", "must_not", "expected_stop")
    for case in cases:
        miss = [k for k in required if not case.get(k)]
        if miss:
            res.add(False, "evals", "%s: missing %s" % (case.get("id"), miss))
    res.add(all(not [k for k in required if not c.get(k)] for c in cases), "evals",
            "all cases carry prompt/probes/must_show/must_not/expected_stop")

    default_level = ((doc or {}).get("grading") or {}).get("complexity_default", 2)
    levels = []
    for case in cases:
        level = case.get("complexity", default_level)
        res.add(isinstance(level, int) and 1 <= level <= 4, "evals",
                "%s: complexity in 1-4 (%r)" % (case.get("id"), level))
        levels.append(level if isinstance(level, int) else 0)
    hard = sum(1 for level in levels if level >= 3)
    res.add(hard >= 2, "evals",
            "%d cases at L3+ (need >=2, else multi-factor ability is untested)" % hard)

    domains = {c.get("domain") for c in cases}
    res.add(len(domains) >= 6, "evals", "domain diversity: %s" % sorted(d for d in domains if d))
    prompts = [c.get("prompt", "") for c in cases]
    res.add(all(p and len(p.strip()) >= 6 for p in prompts), "evals", "prompts non-empty")
    # One case (the ambiguity probe) is deliberately a single short sentence, so require
    # that most prompts are substantial rather than every prompt.
    substantial = sum(1 for p in prompts if len(p) >= 25)
    res.add(substantial >= 6, "evals",
            "%d prompts are substantial (>=25 chars), need >=6" % substantial)


def check_schemas(root: str, res: Result) -> None:
    for name in ("question_node.json", "evidence.json", "factor.json", "report.json", "domain_pack.json"):
        path = os.path.join(root, "schemas", name)
        try:
            with io.open(path, "r", encoding="utf-8") as fh:
                doc = json.load(fh)
            res.add(isinstance(doc, dict) and "$schema" in doc, "schema", "%s: valid JSON Schema" % name)
        except (ValueError, OSError) as exc:
            res.add(False, "schema", "%s: %s" % (name, exc))

    grade_schema = os.path.join(root, "schemas", "evidence.json")
    if os.path.isfile(grade_schema):
        with io.open(grade_schema, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        enum = (doc.get("properties", {}).get("evidence_grade", {}) or {}).get("enum")
        res.add(enum == ["A", "B", "C", "D"], "schema",
                "evidence_grade enum is A-D" if enum == ["A", "B", "C", "D"] else "evidence_grade enum %r" % (enum,))


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:  # Windows consoles default to GBK and would fail on Chinese details
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Validate an ai-sq-universal skill package.")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--packs", action="store_true", help="only validate domain packs")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    res = Result()

    if not os.path.isdir(root):
        sys.stderr.write("not a directory: %s\n" % root)
        return 2

    if not args.packs:
        check_layout(root, res)
        check_frontmatter(root, res)
        check_evals(root, res)
        check_schemas(root, res)

    pack_dir = os.path.join(root, "domain_packs")
    packs = sorted(f for f in os.listdir(pack_dir) if f.endswith(".yaml")) if os.path.isdir(pack_dir) else []
    res.add(len(packs) >= 7, "pack", "7+ domain packs shipped (found %d)" % len(packs))
    for name in packs:
        check_pack(os.path.join(pack_dir, name), res)

    if args.json:
        json.dump({"root": root, "ok": not res.failed, "checks": res.checks},
                  sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(res.report() + "\n")

    return 0 if not res.failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
