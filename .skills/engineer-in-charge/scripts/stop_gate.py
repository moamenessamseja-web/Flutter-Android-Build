#!/usr/bin/env python3
"""STOP GATE (stack-agnostic). Run before ending ANY session / sending a 'done' report.
Usage: python3 stop_gate.py [--since SHA] [--no-push-check] [--require f1 f2 ...]
Passes only if: the handoff docs exist (in .agent/ or repo root), each changed in a commit since session start,
the tree is clean, HEAD is on origin, and IMPLEMENTATION_STATE has an entry dated today. Prints 'HANDOFF OK' on success.
Default --since = /tmp/session_start_sha (written by orient.sh)."""
import datetime, hashlib, os, subprocess, sys
sh = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout.strip()
args = sys.argv[1:]
def opt_value(flag):
    if flag not in args: return None
    i = args.index(flag)
    if i + 1 >= len(args) or args[i + 1].startswith('--'):
        print(f'ERROR: {flag} requires a value', file=sys.stderr); sys.exit(2)
    return args[i + 1]
def session_file():
    root = os.path.realpath('.')
    key = os.path.basename(root) + '_' + hashlib.sha1(root.encode()).hexdigest()[:10]
    return f'/tmp/session_start_sha_{key}'
since = opt_value('--since')
if since is None:
    for f in (session_file(), '/tmp/session_start_sha'):
        if os.path.exists(f): since = open(f).read().strip(); break
    else: since = ''
def find(n):
    for p in (f'.agent/{n}', n):
        if os.path.exists(p): return p
    return f'.agent/{n}'
if '--require' in args:
    i = args.index('--require') + 1; req = []
    while i < len(args) and not args[i].startswith('--'): req.append(args[i]); i += 1
    if not req: print('ERROR: --require requires at least one file', file=sys.stderr); sys.exit(2)
else:
    req = [find(n) for n in ('IMPLEMENTATION_STATE.md', 'HANDOFF.md', 'CHANGELOG.md')] + ([find('implementation.md')] if os.path.exists(find('implementation.md')) else [])
problems = []
if not since: problems.append('no session-start SHA: run orient.sh first (or pass --since)')
changed = set(sh('git', 'diff', '--name-only', f'{since}..HEAD').split()) if since else set()
today = datetime.date.today().isoformat()
for f in req:
    if not os.path.exists(f): problems.append(f'MISSING {f}')
    elif f not in changed: problems.append(f'NOT UPDATED this session: {f}')
st = find('IMPLEMENTATION_STATE.md')
if os.path.exists(st) and today not in open(st, encoding='utf-8').read(): problems.append(f'{st} has no entry dated {today}')
dirty = sh('git', 'status', '--porcelain')
if dirty: problems.append('uncommitted changes:\n' + dirty[:400])
if '--no-push-check' not in args:
    br = sh('git', 'branch', '--show-current'); local = sh('git', 'rev-parse', 'HEAD')
    remote = sh('git', 'ls-remote', 'origin', br).split('\t')[0] if br else ''
    if remote != local: problems.append(f'HEAD not pushed to origin/{br}')
if problems:
    print('HANDOFF INCOMPLETE - do NOT end the session:'); [print(' -', p) for p in problems]; sys.exit(1)
print('HANDOFF OK: docs updated, committed, pushed. Safe to write the final report.')
