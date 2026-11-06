#!/usr/bin/env bash
# GitHub Actions helper for CI-only projects. Token is read from $GH_TOKEN and is NEVER written to disk.
# Usage: GH_TOKEN=... REPO=owner/name gh_ci.sh <cmd> [args]
#   push-run  <branch> [workflow.yml]  dispatch a build on a branch (no push-trigger side effects)
#   status    [branch]                 last 3 runs, one line each
#   wait      [branch] [seconds<=270]  poll until the newest run finishes; exit 0=success 1=failure 2=still running
#   log       <run_number>             failure log (debug-<n> release asset), cleaned and filtered
#   notes     <tag>                    release notes + asset names/sizes (toolchain fingerprint lives here)
#   download  <tag> <outfile>          download app-release.apk of a release
set -u
: "${GH_TOKEN:?set GH_TOKEN}"; : "${REPO:?set REPO=owner/name}"
API="https://api.github.com/repos/$REPO"
H=(-H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json")
here="$(cd "$(dirname "$0")" && pwd)"
jget() { curl -s "${H[@]}" "$1" | python3 -c "
import sys,json,re
raw=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',' ',sys.stdin.read())   # GitHub embeds control chars in commit messages
d=json.loads(raw); exec(sys.argv[1])" "$2"; }
cmd="${1:-}"; shift || true
case "$cmd" in
  push-run)
    br="${1:?branch}"; wf="${2:-build-apk.yml}"
    curl -s -o /dev/null -w "dispatch http %{http_code}\n" -X POST "${H[@]}" "$API/actions/workflows/$wf/dispatches" -d "{\"ref\":\"$br\"}" ;;
  status)
    q=""; [ -n "${1:-}" ] && q="&branch=$1"
    jget "$API/actions/runs?per_page=3$q" "
for r in d['workflow_runs']: print(r['run_number'],r['head_sha'][:7],r['status'],r['conclusion'],r['event'])" ;;
  wait)
    q=""; [ -n "${1:-}" ] && q="&branch=$1"; max="${2:-240}"; [ "$max" -gt 270 ] && max=270   # bash tool hard limit is 300 s
    t=0; last=""
    while [ "$t" -lt "$max" ]; do
      s=$(jget "$API/actions/runs?per_page=1$q" "
r=d['workflow_runs'][0]; print(r['run_number'],r['head_sha'][:7],r['status'],r['conclusion'])")
      [ "$s" != "$last" ] && echo "$s" && last="$s"
      case "$s" in *" completed success") exit 0;; *" completed "*) exit 1;; esac
      sleep 20; t=$((t+20))
    done; echo "still running after ${max}s - call again"; exit 2 ;;
  log)
    n="${1:?run_number}"; f=/tmp/ci_log_$n.txt
    curl -sL -o "$f" "https://github.com/$REPO/releases/download/debug-$n/build_log_tail.txt"
    python3 "$here/clean_log.py" "$f" ;;
  notes)
    jget "$API/releases/tags/${1:?tag}" "
print(d['tag_name'],d['target_commitish'][:7],[(a['name'],a['size']) for a in d.get('assets',[])]); print(d.get('body','')[:700])" ;;
  download)
    curl -sL -o "${2:?outfile}" "https://github.com/$REPO/releases/download/${1:?tag}/app-release.apk"; ls -l "$2" ;;
  *) sed -n 2,11p "$0"; exit 2 ;;
esac
