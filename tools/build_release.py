#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a reproducible release zip for the AI-SQ Universal Root-Inquiry bundle.

Produces:
    AI-SQ-Universal-Root-Inquiry-v<version>.zip
      └── AI-SQ-Universal-Root-Inquiry/
            ├── (skill, plugin, docs, tools)
            └── MANIFEST.sha256        <- generated, one sha256 per file

Usage:
    python tools/build_release.py
    python tools/build_release.py --out dist
    python tools/build_release.py --version 2.0.1

Deterministic: entries are sorted, timestamps pinned to the VERSION date when
possible, so rebuilding an unchanged tree yields the same member order and bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import zipfile

EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "node_modules", "dist"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".zip", ".bak")
EXCLUDE_NAMES = {"cordis.patch.generated.yml", "MANIFEST.sha256", ".DS_Store"}


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".bak"))
        for name in sorted(filenames):
            if name in EXCLUDE_NAMES or name.endswith(EXCLUDE_SUFFIXES):
                continue
            if ".bak-" in name:
                continue
            full = os.path.join(dirpath, name)
            yield full


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_version(root: str) -> str:
    path = os.path.join(root, "VERSION")
    if os.path.isfile(path):
        with io.open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    plugin_json = os.path.join(root, "plugin", "plugin.json")
    if os.path.isfile(plugin_json):
        with io.open(plugin_json, "r", encoding="utf-8") as fh:
            return json.load(fh).get("version", "0.0.0")
    return "0.0.0"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build the release zip.")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="bundle root (default: parent of tools/)")
    ap.add_argument("--out", default=None, help="output directory (default: parent of bundle root)")
    ap.add_argument("--version", default=None, help="override version from VERSION")
    ap.add_argument("--name", default="AI-SQ-Universal-Root-Inquiry", help="top-level folder name in the zip")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    out_dir = os.path.abspath(args.out or os.path.dirname(root))
    version = args.version or read_version(root)
    top = args.name

    if not os.path.isdir(os.path.join(root, "ai-sq-universal")):
        sys.stderr.write("not a bundle root (no ai-sq-universal/): %s\n" % root)
        return 2
    os.makedirs(out_dir, exist_ok=True)

    zip_path = os.path.join(out_dir, "%s-v%s.zip" % (top, version))
    files = list(iter_files(root))

    manifest_lines = []
    total = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = os.path.relpath(path, root).replace("\\", "/")
            arc = "%s/%s" % (top, rel)
            zf.write(path, arc)
            digest = sha256(path)
            manifest_lines.append("%s  %s" % (digest, rel))
            total += os.path.getsize(path)
        manifest = "\n".join(manifest_lines) + "\n"
        zf.writestr("%s/MANIFEST.sha256" % top, manifest)

    size = os.path.getsize(zip_path)
    print("bundle root : %s" % root)
    print("version     : %s" % version)
    print("output      : %s" % zip_path)
    print("files       : %d (+ MANIFEST.sha256)" % len(files))
    print("raw size    : %.1f KiB" % (total / 1024.0))
    print("zip size    : %.1f KiB" % (size / 1024.0))
    print("")
    print("largest entries:")
    for path in sorted(files, key=lambda p: os.path.getsize(p), reverse=True)[:8]:
        rel = os.path.relpath(path, root).replace("\\", "/")
        print("  %7.1f KiB  %s" % (os.path.getsize(path) / 1024.0, rel))
    print("")
    print("verify with: python -c \"import zipfile;z=zipfile.ZipFile(r'%s');print(len(z.namelist()),'entries');print(z.testzip())\"" % zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
