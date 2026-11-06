#!/usr/bin/env bash
# Session start gate: load the project's memory in ONE capped command.
# Usage: bash session_start.sh [repo_dir]   (default: current dir)
cd "${1:-.}" || exit 2
# NEVER use `cut -c` on Arabic/UTF-8 text: it cuts bytes, splits characters and the tool rejects the whole output.
trunc() { python3 -c "import sys;sys.stdin.reconfigure(errors='replace');sys.stdout.reconfigure(errors='replace');[print(l.rstrip('\\n')[:${1:-200}]) for l in sys.stdin]"; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo"; exit 2; }
echo "== branch / HEAD =="; git branch --show-current; git log --oneline -6 | trunc 120
git rev-parse HEAD > /tmp/session_start_sha   # handoff_check.py uses this
echo "== working tree =="; git status --short | head -15
echo "== .agent/ =="; ls -la .agent 2>/dev/null | trunc 120 || echo "NO .agent/ DIRECTORY (create it before working)"
for f in .agent/IMPLEMENTATION_STATE.md HANDOFF.md; do
  [ -f "$f" ] && { echo; echo "== $f (first 40 lines, then last 70) =="; head -40 "$f" | trunc 240; echo "   [...]"; tail -70 "$f" | trunc 240; }
done
echo; echo "== other state/spec files =="; ls *.md .agent/*.md 2>/dev/null | tr '\n' ' '
echo; echo
echo "NEXT: verify the state file's headline claim with ONE git/API call (stale-state check),"
echo "      then read ONLY the mission/spec sections the current task needs."
echo "BEFORE STOPPING: python3 handoff_check.py --since \$(cat /tmp/session_start_sha)"
