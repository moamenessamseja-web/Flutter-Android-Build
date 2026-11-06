#!/usr/bin/env python3
"""LOOP GUARD — stops you from spinning on the same problem. State lives in /tmp/loop_guard.json (or --file).
  loop_guard.py record "<symptom>" "<what you tried>" "<result>"   # after every failed attempt
  loop_guard.py check  "<symptom>"                                  # BEFORE the next attempt: strike level + what to do
  loop_guard.py reset  "<symptom>"                                  # once solved (then write the lesson in LESSONS.md)
Strikes: 0-1 = fix the obvious · 2 = read deeper evidence, never repeat the same command · 3 = STOP patching: hypotheses +
ONE cheapest discriminating experiment · 4+ = escalate to the owner with evidence + options.
Symptoms are matched by normalised word sets, so word order does not matter."""
import json, os, re, sys, time
args = sys.argv[1:]
path = '/tmp/loop_guard.json'
if '--file' in args:
    i = args.index('--file'); path = args[i + 1]; del args[i:i + 2]
if len(args) < 2: print(__doc__); sys.exit(2)
cmd, symptom = args[0], args[1]
key = ' '.join(sorted(set(re.findall(r'\w+', symptom.lower()))))
db = json.load(open(path)) if os.path.exists(path) else {}
e = db.setdefault(key, {'symptom': symptom, 'tries': []})
if cmd == 'record':
    e['tries'].append({'t': int(time.time()), 'action': args[2] if len(args) > 2 else '', 'result': args[3] if len(args) > 3 else ''})
    json.dump(db, open(path, 'w'), ensure_ascii=False, indent=1)
if cmd == 'reset':
    db.pop(key, None); json.dump(db, open(path, 'w'), ensure_ascii=False, indent=1); print('reset. Now write the lesson in LESSONS.md.'); sys.exit(0)
if cmd not in ('record', 'check'): print(__doc__); sys.exit(2)
n = len(e['tries'])
print(f'symptom: {symptom!r} - attempts so far: {n}')
acts = [t['action'] for t in e['tries'] if t['action']]
if len(acts) != len(set(acts)): print('!! You repeated an identical action. Identical actions give identical results - change the approach.')
if n <= 1: print('Strike %d: fix the most likely cause, but first re-read the exact error text (not your summary of it); add the regression test with the fix.' % n)
elif n == 2: print('Strike 2: read deeper evidence (full log slice, git diff of the last green, artifact comparison). Do NOT re-run the same fix.')
elif n == 3: print('Strike 3: STOP PATCHING. Write 2-3 competing hypotheses, pick the cheapest experiment that separates them (rebuild old source, A/B, minimal repro), run it, then decide.')
else: print('Strike 4+: ESCALATE. Report to the owner: symptom, what was tried, evidence, and 1-2 smallest options. Do not keep burning budget.')
for t in e['tries'][-4:]: print(f"  - {t['action'][:100]} -> {t['result'][:100]}")
