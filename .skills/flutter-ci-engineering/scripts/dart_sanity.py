#!/usr/bin/env python3
"""Pre-push sanity for a repo with NO local Dart SDK. Catches the commonest blind-edit mistake: unbalanced brackets.
Usage: dart_sanity.py [--base REF]      (default base: HEAD; compares changed .dart files against it)
Brackets inside string literals/comments are stripped first. Existing imbalance in the BASE file is tolerated
(approximate stripper); what matters is that your edit did not change the balance. Also validates changed
*.yml/*.yaml. It is NOT a compiler: unused private members/imports/locals still fail CI (analyzer warnings are fatal),
and a mis-grouped `case` or wrong fallthrough compiles fine - only regression tests catch those."""
import re, subprocess, sys
base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'HEAD'
sh = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
def strip(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"//[^\n]*", "", s)
    s = re.sub(r"r?'''.*?'''", "''", s, flags=re.S)
    s = re.sub(r'r?""".*?"""', '""', s, flags=re.S)
    s = re.sub(r"r?'(?:\\.|[^'\\\n])*'", "''", s)
    s = re.sub(r'r?"(?:\\.|[^"\\\n])*"', '""', s)
    return s
def bal(s):
    t = strip(s); return tuple(t.count(a) - t.count(b) for a, b in ('()', '{}', '[]'))
files = sorted(set(sh('git', 'diff', '--name-only', base).split() + sh('git', 'ls-files', '--others', '--exclude-standard').split()))
bad = 0
for f in files:
    if f.endswith('.dart'):
        new = open(f, encoding='utf-8').read()
        old = sh('git', 'show', f'{base}:{f}')
        b0, b1 = (bal(old) if old else (0, 0, 0)), bal(new)
        ok = b1 == b0 or b1 == (0, 0, 0)
        print(('OK  ' if ok else 'BAD ') + f, 'base', b0, 'now', b1); bad += (not ok)
    elif f.endswith(('.yml', '.yaml')):
        try:
            import yaml; yaml.safe_load(open(f, encoding='utf-8')); print('OK   ' + f + ' (yaml)')
        except Exception as e:
            print('BAD  ' + f, e); bad += 1
print(sh('git', 'diff', '--stat', base).strip().split('\n')[-1] if files else 'no changes')
sys.exit(1 if bad else 0)
