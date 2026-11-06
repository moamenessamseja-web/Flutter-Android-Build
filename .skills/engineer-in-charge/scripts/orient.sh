#!/usr/bin/env bash
# START GATE (stack-agnostic). Load the project's memory in ONE capped command.
# Usage: bash orient.sh [repo_dir]      (default: current dir)
# Prints branch/HEAD, dirty tree, the .agent/ file list, the head of the README/handoff/state files, a quick audit,
# and records the session-start SHA (used by stop_gate.py). Never use `cut -c` on Arabic: it splits bytes.
cd "${1:-.}" || exit 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
trunc() { python3 -c "import sys;sys.stdin.reconfigure(errors='replace');sys.stdout.reconfigure(errors='replace');[print(l.rstrip('\n')[:${1:-200}]) for l in sys.stdin]"; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo -> init/clone first"; exit 2; }
echo "== branch / HEAD =="; git branch --show-current; git log --oneline -6 | trunc 120
git rev-parse HEAD > /tmp/session_start_sha
echo "== working tree =="; git status --short | head -15
if [ ! -d .agent ]; then
  echo; echo "!! NO .agent/ DIRECTORY -> run: python3 $HERE/init_agent.py --project \"<name>\""; exit 0
fi
echo "== .agent/ =="; ls -1 .agent | tr '\n' ' '; echo
for f in .agent/README.md .agent/HANDOFF.md .agent/IMPLEMENTATION_STATE.md; do
  [ -f "$f" ] && { echo; echo "== $f (first 45 lines) =="; head -45 "$f" | trunc 220; }
done
echo; echo "== audit =="; python3 "$HERE/agent_audit.py" --repo . --brief 2>&1 | head -12
echo; echo "NEXT: verify the state file's headline claim with ONE git/API call (docs can be stale), then read only"
echo "      the sections of ENGINEERING_RULES.md / BRIEF.md the task needs. Before stopping: python3 $HERE/stop_gate.py"
