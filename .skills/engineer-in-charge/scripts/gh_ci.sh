#!/usr/bin/env bash
# GitHub Actions helper for CI-only projects. Token is read from $GH_TOKEN and is NEVER written to disk.
# Usage: GH_TOKEN=... REPO=owner/name gh_ci.sh <cmd> [args]
#   push-run  <branch> [workflow.yml]  dispatch a build on a branch (default workflow: build-apk.yml)
#   status    [branch]                 last 5 runs, one line each (run_number sha7 status conclusion event)
#   wait      [branch] [seconds<=270]  wait for the run OF THE COMMIT YOU PUSHED; exit 0=success 1=failure 2=still running
#                                      The commit is $EXPECT_SHA, else the current `git rev-parse HEAD`. Without either, the
#                                      newest run is used and a WARNING is printed: it may belong to an older commit.
#   result    [branch|run_id]          what the run says: its commit, failure/warning annotations, the `APK ready` annotation
#                                      (commit, package, size, SHA-256, signer, tests/analyze status) and the artifacts.
#                                      With a branch it picks the run of $EXPECT_SHA / HEAD like `wait`.
# Legacy commands, only for pipelines that publish GitHub Releases (debug-<n> / build-<n> assets). The central
# reusable workflow does NOT publish releases, so these return 404 there: use `result` instead.
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
# The commit whose run we want: EXPECT_SHA, else HEAD of the current git repo, else empty (unsafe, warned about).
want_sha() {
  local w="${EXPECT_SHA:-}"
  if [ -z "$w" ] && git rev-parse HEAD >/dev/null 2>&1; then
    w="$(git rev-parse HEAD)"; echo "note: looking for the run of commit ${w:0:7} (set EXPECT_SHA to override)" >&2
  fi
  [ -z "$w" ] && echo "WARNING: no EXPECT_SHA and not inside a git repo: the newest run may belong to an OLDER commit" >&2
  printf '%s' "$w"
}
# Print "<run_id> <run_number> <sha7> <status> <conclusion>" for the newest run of the wanted commit, or "none".
pick_run() { # $1 branch query (may be empty)  $2 wanted sha (may be empty)
  EXPECT_SHA="$2" jget "$API/actions/runs?per_page=20$1" "
import os
want=os.environ.get('EXPECT_SHA','')
runs=d.get('workflow_runs',[])
if want: runs=[r for r in runs if r['head_sha'].startswith(want)]
print(runs[0]['id'],runs[0]['run_number'],runs[0]['head_sha'][:7],runs[0]['status'],runs[0]['conclusion']) if runs else print('none')"
}
cmd="${1:-}"; shift || true
case "$cmd" in
  push-run)
    br="${1:?branch}"; wf="${2:-build-apk.yml}"
    curl -s -o /dev/null -w "dispatch http %{http_code}\n" -X POST "${H[@]}" "$API/actions/workflows/$wf/dispatches" -d "{\"ref\":\"$br\"}" ;;
  status)
    q=""; [ -n "${1:-}" ] && q="&branch=$1"
    jget "$API/actions/runs?per_page=5$q" "
for r in d['workflow_runs']: print(r['run_number'],r['head_sha'][:7],r['status'],r['conclusion'],r['event'])" ;;
  wait)
    q=""; [ -n "${1:-}" ] && q="&branch=$1"; max="${2:-240}"; [ "$max" -gt 270 ] && max=270   # bash tool hard limit is 300 s
    want="$(want_sha)"; t=0; last=""
    while [ "$t" -lt "$max" ]; do
      s=$(pick_run "$q" "$want")
      if [ "$s" = "none" ]; then line="waiting-for-run${want:+ of ${want:0:7}}"; else line="${s#* }"; fi
      [ "$line" != "$last" ] && echo "$line" && last="$line"
      case "$line" in *" completed success") exit 0;; *" completed "*) exit 1;; esac
      sleep 20; t=$((t+20))
    done; echo "still running after ${max}s - call again"; exit 2 ;;
  result)
    arg="${1:-}"
    if [[ "$arg" =~ ^[0-9]{8,}$ ]]; then rid="$arg"
    else
      q=""; [ -n "$arg" ] && q="&branch=$arg"
      s=$(pick_run "$q" "$(want_sha)"); [ "$s" = "none" ] && { echo "no run found for that commit/branch yet"; exit 2; }
      rid="${s%% *}"
    fi
    jget "$API/actions/runs/$rid" "print('run',d['id'],'commit',d['head_sha'],d['status'],d['conclusion'],d['html_url'])"
    for j in $(jget "$API/actions/runs/$rid/jobs" "print(' '.join(str(x['id']) for x in d['jobs']))"); do
      jget "$API/check-runs/$j/annotations" "
for a in d:
    if a['annotation_level'] in ('failure','warning') or (a.get('title') or '')=='APK ready':
        print(a['annotation_level'],'|',a.get('title') or '','|',a['message'][:1500])"
    done
    jget "$API/actions/runs/$rid/artifacts" "
for a in d['artifacts']: print('artifact',a['id'],a['name'],a['size_in_bytes']//1048576,'MB')" ;;
  log)
    n="${1:?run_number}"; f=/tmp/ci_log_$n.txt
    curl -sL -o "$f" "https://github.com/$REPO/releases/download/debug-$n/build_log_tail.txt"
    python3 "$here/clean_log.py" "$f" ;;
  notes)
    jget "$API/releases/tags/${1:?tag}" "
print(d['tag_name'],d['target_commitish'][:7],[(a['name'],a['size']) for a in d.get('assets',[])]); print(d.get('body','')[:700])" ;;
  download)
    curl -sL -o "${2:?outfile}" "https://github.com/$REPO/releases/download/${1:?tag}/app-release.apk"; ls -l "$2" ;;
  *) sed -n 2,17p "$0"; exit 2 ;;
esac
