#!/usr/bin/env python3
"""STOP GATE. Run before ending ANY session: python3 handoff_check.py [--since SHA] [--no-push-check] [--require f1 f2 ...]
Fails (exit 1) unless: the handoff files exist, each was modified in a commit since the session start,
nothing is uncommitted, and HEAD is on the remote. Default --since = /tmp/session_start_sha (written by session_start.sh).
Default required: .agent/IMPLEMENTATION_STATE.md HANDOFF.md CHANGELOG.md (+ implementation.md if the repo has one).
A passing check is the ONLY condition for ending the session."""
import datetime, os, subprocess, sys
sh = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout.strip()
args = sys.argv[1:]
since = args[args.index('--since') + 1] if '--since' in args else (open('/tmp/session_start_sha').read().strip() if os.path.exists('/tmp/session_start_sha') else '')
req = args[args.index('--require') + 1:] if '--require' in args else ['.agent/IMPLEMENTATION_STATE.md', 'HANDOFF.md', 'CHANGELOG.md'] + (['implementation.md'] if os.path.exists('implementation.md') else [])
problems = []
if not since: problems.append('no session-start SHA: run session_start.sh first (or pass --since)')
changed = set(sh('git', 'diff', '--name-only', f'{since}..HEAD').split()) if since else set()
dirty = sh('git', 'status', '--porcelain')
today = datetime.date.today().isoformat()
for f in req:
    if not os.path.exists(f): problems.append(f'MISSING {f}'); continue
    if f not in changed: problems.append(f'NOT UPDATED this session: {f}')
st = '.agent/IMPLEMENTATION_STATE.md'
if os.path.exists(st) and today not in open(st, encoding='utf-8').read():
    problems.append(f'{st} has no entry dated {today} (add a dated session section)')
if dirty: problems.append('uncommitted changes:\n' + dirty[:400])
if '--no-push-check' not in args:
    br = sh('git', 'branch', '--show-current'); local = sh('git', 'rev-parse', 'HEAD')
    remote = sh('git', 'ls-remote', 'origin', br).split('\t')[0] if br else ''
    if remote != local: problems.append(f'HEAD not pushed to origin/{br}')
if problems:
    print('HANDOFF INCOMPLETE - do NOT end the session:'); [print(' -', p) for p in problems]; sys.exit(1)
print('HANDOFF OK: files updated, committed, pushed. Safe to write the final report.')
