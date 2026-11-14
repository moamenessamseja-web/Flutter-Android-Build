#!/usr/bin/env python3
"""Audit a project's .agent/ folder. Usage: python3 agent_audit.py [--repo .] [--brief]
Checks (exit 1 if any ERROR): required files; README index mentions every file; no secrets; status vocabulary on EVERY inventory item of
implementation.md (a vague status such as "Done" is an ERROR); archived files carry a banner; state file not bloated; docs not older than the code (WARN);
leftover template placeholders (WARN)."""
import argparse, pathlib, re, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument('--repo', default='.'); ap.add_argument('--brief', action='store_true')
a = ap.parse_args()
root = pathlib.Path(a.repo); ag = root / '.agent'
errs, warns = [], []
REQ = ['README.md', 'IMPLEMENTATION_STATE.md', 'HANDOFF.md', 'CHANGELOG.md', 'implementation.md']
if not ag.is_dir():
    print('ERROR: no .agent/ directory'); sys.exit(1)
files = {p.name: p for p in ag.glob('*.md')}
for r in REQ:
    if r not in files: errs.append(f'missing required file: {r}')
readme = files['README.md'].read_text(encoding='utf-8') if 'README.md' in files else ''
for n in files:
    if n != 'README.md' and n not in readme: warns.append(f'README index does not mention {n}')
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[0-9A-Za-z_\-]{30,}|sk-[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16})')
for p in ag.rglob('*.md'):
    t = p.read_text(encoding='utf-8', errors='replace')
    if SECRET.search(t): errs.append(f'possible SECRET in {p.relative_to(root)}')
    if p.parent == ag and re.search(r'<<[A-Z_ ]+>>', t): warns.append(f'unfilled template placeholder in {p.name}')
VALID = ['Verified complete', 'Implemented, not yet verified', 'Partially implemented', 'Not started', 'Blocked', 'Deferred by product decision']
if 'implementation.md' in files:
    t = files['implementation.md'].read_text(encoding='utf-8')
    VAGUE = re.compile(r'\b(done|works|working|complete|finished|ok|should work|ready)\b', re.I)
    inventory = re.split(r'^#+\s*Verification log', t, flags=re.I | re.M)[0]   # the log below holds free-text evidence, not statuses
    items = [l for l in inventory.split('\n') if l.strip().startswith(('-', '*', '|')) and len(l.strip()) > 3]
    if not items: warns.append('implementation.md has no inventory items')
    for l in items:
        if any(v.lower() in l.lower() for v in VALID): continue
        if VAGUE.search(l): errs.append(f'implementation.md item uses a non-standard status: {l.strip()[:90]}')
    if not any(v.lower() in t.lower() for v in VALID): warns.append('implementation.md uses none of the standard status words')
arch = ag / 'archive'
if arch.is_dir():
    for p in arch.glob('*.md'):
        if 'ARCHIVED' not in p.read_text(encoding='utf-8', errors='replace')[:700].upper(): warns.append(f'archive/{p.name} has no ARCHIVED banner')
if 'IMPLEMENTATION_STATE.md' in files:
    t = files['IMPLEMENTATION_STATE.md'].read_text(encoding='utf-8'); n = len(t.split('\n'))
    if n > 200: warns.append(f'IMPLEMENTATION_STATE.md is {n} lines — archive old sessions, keep the checkpoint short (<200)')
    if not re.search(r'20\d\d-\d\d-\d\d', t): warns.append('IMPLEMENTATION_STATE.md has no dated entry')
def last(path):
    try: return int(subprocess.run(['git', 'log', '-1', '--format=%ct', '--', path], capture_output=True, text=True, cwd=root).stdout.strip() or 0)
    except Exception: return 0
code = max([last(d) for d in ('lib', 'src', 'app', 'test', 'tests') if (root / d).exists()] or [0])
for k in ('IMPLEMENTATION_STATE.md', 'HANDOFF.md'):
    if k in files and code and last(f'.agent/{k}') + 3600 < code: warns.append(f'{k} is older than the latest code change — docs may be stale')
if not a.brief or errs or warns:
    for e in errs: print('ERROR:', e)
    for w in warns: print('WARN: ', w)
print(f'audit: {len(errs)} error(s), {len(warns)} warning(s), {len(files)} top-level docs')
sys.exit(1 if errs else 0)
