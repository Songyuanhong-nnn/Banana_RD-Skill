#!/usr/bin/env bash
# Install the AI-SQ Universal Root-Inquiry skill bundle.
#
#   ./install.sh            # copy into ~/.dsh/skills (default)
#   ./install.sh plugin     # emit a Cordis patch, no copy
#   ./install.sh verify     # run the package self-check
#
# Env overrides: SKILLS_DIR, DSH_HOME
set -euo pipefail

MODE="${1:-copy}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_ROOT="$(cd "$HERE/.." && pwd)"
SKILL_SRC="$BUNDLE_ROOT/ai-sq-universal"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.dsh/skills}"
DSH_HOME="${DSH_HOME:-$HOME/.dsh}"
SKILL_NAME="ai-sq-universal"

step() { printf '\033[36m==> %s\033[0m\n' "$1"; }
ok()   { printf '\033[32m    %s\033[0m\n' "$1"; }
warn() { printf '\033[33m    %s\033[0m\n' "$1"; }

printf '\nAI-SQ Universal Root-Inquiry / 通用求根问底调研  v2.4.0\n'
printf 'bundle root : %s\nskill source: %s\nmode        : %s\n\n' "$BUNDLE_ROOT" "$SKILL_SRC" "$MODE"

[ -f "$SKILL_SRC/SKILL.md" ] || { echo "SKILL.md not found under $SKILL_SRC" >&2; exit 1; }

do_copy() {
    step "Copying skill to $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
    target="$SKILLS_DIR/$SKILL_NAME"
    if [ -e "$target" ]; then
        backup="$target.bak-$(date +%Y%m%d-%H%M%S)"
        mv "$target" "$backup"
        warn "existing install moved to $backup"
    fi
    cp -R "$SKILL_SRC" "$target"
    [ -f "$target/SKILL.md" ] || { echo "copy failed: $target/SKILL.md missing" >&2; exit 1; }
    ok "installed: $target"
    printf '\nRestart DSH (or start a new session); ai-sq-universal-root-inquiry should appear in the skill catalog.\n'
}

do_plugin() {
    step 'Emitting a Cordis patch (nothing is copied)'
    template="$HERE/cordis.patch.yml"
    [ -f "$template" ] || { echo "missing $template" >&2; exit 1; }
    escaped="${BUNDLE_ROOT//\\/\\\\}"
    out="$HERE/cordis.patch.generated.yml"
    sed "s|__SKILL_ROOT__|$escaped|g" "$template" > "$out"
    ok "wrote $out"
    printf '\nMerge the "insert:" block from that file into:\n    %s/cordis.patch.yml\nthen restart DSH.\n' "$DSH_HOME"
    warn 'This script does not edit your config automatically.'
}

do_verify() {
    step 'Self-check'
    validator="$SKILL_SRC/scripts/validate.py"
    if command -v python3 >/dev/null 2>&1; then py=python3
    elif command -v python >/dev/null 2>&1; then py=python
    else py=""; fi

    if [ -n "$py" ] && [ -f "$validator" ]; then
        "$py" "$validator"
        ok 'package validation passed'
    else
        warn 'python or validate.py unavailable - checking layout only'
        for rel in SKILL.md prompts/planner.md schemas/report.json templates/report.md evals/cases.yaml; do
            [ -f "$SKILL_SRC/$rel" ] && ok "ok  $rel" || { echo "missing $rel" >&2; exit 1; }
        done
    fi

    if [ -f "$SKILLS_DIR/$SKILL_NAME/SKILL.md" ]; then
        ok "copy-install present at $SKILLS_DIR/$SKILL_NAME"
    else
        warn "not installed under $SKILLS_DIR (copy mode not run yet)"
    fi
}

case "$MODE" in
    copy)   do_copy ;;
    plugin) do_plugin ;;
    verify) do_verify ;;
    *)      echo "unknown mode: $MODE (copy|plugin|verify)" >&2; exit 2 ;;
esac

printf '\n'
