#!/usr/bin/env bash
# Re-creates the working environment of the claude.ai chat sandbox after it was reset (this happened mid-conversation:
# /home/claude and /tmp were emptied and uncommitted work was lost). Idempotent and safe to run any time.
#
#   GH_TOKEN=<token> bash setup_sandbox.sh owner/repo [owner/repo ...]
#
# Installs what the method needs (actionlint, shellcheck, jq, zstandard) and clones the given repositories into
# ${WORK:-/home/claude}. The token is used only as a transient HTTP header; it is never written to a remote URL or file.
# Rule that follows from the reset: COMMIT AND PUSH WORK-IN-PROGRESS EARLY (a branch is cheap), never keep it only in /tmp.
set -u
WORK="${WORK:-/home/claude}"
mkdir -p "$WORK"

echo "== tools"
pip install -q --break-system-packages actionlint-py shellcheck-py zstandard >/dev/null 2>&1 || echo "pip install failed (continuing)"
if ! command -v jq >/dev/null 2>&1; then
  (apt-get install -y -q jq >/dev/null 2>&1 || { apt-get update -q >/dev/null 2>&1; apt-get install -y -q jq >/dev/null 2>&1; }) || echo "jq install failed (only needed for local tests of jq expressions)"
fi
for t in actionlint shellcheck jq git python3; do
  printf '%-11s %s\n' "$t" "$(command -v "$t" || echo MISSING)"
done

if [ "$#" -gt 0 ]; then
  : "${GH_TOKEN:?set GH_TOKEN to clone repositories}"
  auth="Authorization: Basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)"
  echo "== repositories in $WORK"
  for repo in "$@"; do
    dir="$WORK/${repo##*/}"
    if [ -d "$dir/.git" ]; then
      git -C "$dir" -c http.extraheader="$auth" fetch -q origin && echo "fetched  $dir"
    else
      git -c http.extraheader="$auth" clone -q "https://github.com/$repo.git" "$dir" && echo "cloned   $dir"
    fi
  done
fi
echo "done. Pure-Dart tests: python3 <gateway>/.skills/engineer-in-charge/scripts/pure_dart_tests.py <project>"
