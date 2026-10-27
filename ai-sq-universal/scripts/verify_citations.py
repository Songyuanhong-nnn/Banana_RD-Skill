#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Make "cite to the sentence" mechanically checkable.

The 2026-10 audit of this skill found that author-declared fields (verified_by,
traceability %, grade) could be filled without ever opening the source. This
script closes that gap the only way it can be closed: by holding a **snapshot**
of each source and checking that the quoted sentence is literally inside it.

Three evidence tracks (see schemas/citation.json):
  sentence                -> quote must be a substring of the snapshot
  reproducible_query      -> no sentence; check the query spec is complete
  accountable_provenance  -> not publicly verifiable; must name why + consequence

Usage:
    python scripts/verify_citations.py citations.json --snapshots snapshots/
    python scripts/verify_citations.py report.json --snapshots snapshots/ --fetch --out metrics.json

Exit codes: 0 all verified, 1 at least one failed, 2 bad input.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (compatible; ai-sq-citation-verifier/1.0)"
WS = re.compile(r"\s+")


def norm(text: str) -> str:
    return WS.sub(" ", (text or "")).strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(url: str, path: str) -> bytes:
    if os.path.isfile(path):
        with io.open(path, "rb") as fh:
            return fh.read()
    if url:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - explicit user URL
            return resp.read()
    raise FileNotFoundError("no snapshot file and no url")


def decode(data: bytes) -> str:
    for enc in ("utf-8", "gb18030", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "ignore")


def iter_citations(doc):
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for key in ("citations", "evidence", "citation_table"):
            if isinstance(doc.get(key), list):
                return doc[key]
    return []


def check_one(c: dict, snap_dir: str, fetch: bool) -> dict:
    cid = c.get("citation_id") or c.get("evidence_id") or "?"
    track = c.get("evidence_track") or "sentence"
    result = {"citation_id": cid, "track": track, "ok": False, "reasons": []}

    if track == "reproducible_query":
        q = c.get("query") or {}
        need = ("dataset", "fields", "filter", "period", "row_key")
        missing = [k for k in need if not q.get(k)]
        result["ok"] = not missing
        if missing:
            result["reasons"].append("query spec missing: %s" % missing)
        return result

    if track == "accountable_provenance":
        need = ("provenance", "why_not_public", "if_false_consequence")
        missing = [k for k in need if not c.get(k)]
        result["ok"] = not missing
        if missing:
            result["reasons"].append("provenance fields missing: %s" % missing)
        return result

    # track == "sentence"
    snap = c.get("snapshot") or {}
    path = snap.get("file") or ""
    if path and not os.path.isabs(path):
        path = os.path.join(snap_dir, path)
    quote = norm(c.get("quote", ""))
    if len(quote) < 12:
        result["reasons"].append("quote shorter than 12 chars")
        return result

    try:
        raw = load(c.get("url", ""), path) if (path or (fetch and c.get("url"))) else None
    except Exception as exc:  # noqa: BLE001 - report, do not crash the batch
        result["reasons"].append("cannot load snapshot: %s" % exc)
        return result

    if raw is None:
        result["reasons"].append(
            "no snapshot: cannot machine-verify; captured_at+sha256 required for 'opened_original'")
        return result

    digest = sha256_bytes(raw)
    if snap.get("sha256") and snap["sha256"] != digest:
        result["reasons"].append("snapshot sha256 mismatch (file changed or wrong file)")

    text = norm(decode(raw))
    if quote not in text:
        result["reasons"].append("quote is NOT a verbatim substring of the snapshot")
        near = text[:200]
        result["hint"] = "snapshot begins: %s" % near

    qhash = sha256_bytes(quote.encode("utf-8"))
    if c.get("quote_sha256") and c["quote_sha256"] != qhash:
        result["reasons"].append("quote_sha256 mismatch")

    result["ok"] = not result["reasons"]
    result["snapshot_sha256"] = digest
    result["quote_sha256"] = qhash
    return result


def main(argv):
    ap = argparse.ArgumentParser(description="Verify citations against snapshots.")
    ap.add_argument("input", help="citations.json, or a report.json containing citations/evidence")
    ap.add_argument("--snapshots", default="snapshots", help="snapshot directory")
    ap.add_argument("--fetch", action="store_true",
                    help="download url when the snapshot file is missing (writes nothing)")
    ap.add_argument("--out", default=None, help="write metrics json here")
    args = ap.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    with io.open(args.input, "r", encoding="utf-8") as fh:
        doc = json.load(fh)

    citations = [c for c in iter_citations(doc) if isinstance(c, dict)]
    if not citations:
        sys.stderr.write("no citations found in %s\n" % args.input)
        return 2

    results = [check_one(c, args.snapshots, args.fetch) for c in citations]
    pass_n = sum(1 for r in results if r["ok"])
    total = len(results)
    sentence = [r for r in results if r["track"] == "sentence"]
    verified_sentence = sum(1 for r in sentence if r.get("snapshot_sha256"))

    print("citations: %d | passed: %d | failed: %d" % (total, pass_n, total - pass_n))
    print("sentence-track citations: %d | with verified snapshot: %d"
          % (len(sentence), verified_sentence))
    for r in results:
        if not r["ok"]:
            print("  FAIL %-6s %s" % (r["citation_id"], "; ".join(r["reasons"])))

    metrics = {
        "citation_total": total,
        "citation_passed": pass_n,
        "citation_pass_rate": round(pass_n / float(total), 4),
        "sentence_total": len(sentence),
        "sentence_snapshot_verified": verified_sentence,
        "sentence_snapshot_rate": round(verified_sentence / float(len(sentence)), 4) if sentence else 1.0,
        "results": results,
    }
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, ensure_ascii=False, indent=2)
        print("metrics -> %s" % args.out)

    return 0 if pass_n == total else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
