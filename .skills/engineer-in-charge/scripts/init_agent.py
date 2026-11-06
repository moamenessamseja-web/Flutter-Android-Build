#!/usr/bin/env python3
"""Bootstrap a project's .agent/ memory from the templates (never overwrites existing files).
Usage: python3 init_agent.py --project "My App" [--repo .] [--owner "Owner name"] [--stack "Flutter/Android"]
Creates .agent/{README,BRIEF,ENGINEERING_RULES,ARCHITECTURE,IMPLEMENTATION_STATE,HANDOFF,implementation,CHANGELOG,LESSONS,DECISIONS}.md
and .agent/archive/. Fill the <<PLACEHOLDERS>> as you learn facts; do not leave guesses in the files."""
import argparse, datetime, pathlib
ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True); ap.add_argument('--repo', default='.')
ap.add_argument('--owner', default='the owner'); ap.add_argument('--stack', default='<<STACK>>')
a = ap.parse_args()
src = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'agent-templates'
dst = pathlib.Path(a.repo) / '.agent'
(dst / 'archive').mkdir(parents=True, exist_ok=True)
today = datetime.date.today().isoformat()
made, kept = [], []
for f in sorted(src.glob('*.md')):
    out = dst / f.name
    if out.exists(): kept.append(f.name); continue
    t = f.read_text(encoding='utf-8')
    for k, v in {'<<PROJECT>>': a.project, '<<DATE>>': today, '<<OWNER>>': a.owner, '<<STACK>>': a.stack}.items():
        t = t.replace(k, v)
    out.write_text(t, encoding='utf-8'); made.append(f.name)
(dst / 'archive' / '.gitkeep').touch()
print(f'created: {", ".join(made) or "-"}'); print(f'kept (already existed): {", ".join(kept) or "-"}')
print("NEXT: fill BRIEF.md (owner's words, verbatim), IMPLEMENTATION_STATE.md baseline SHA, then commit 'docs: bootstrap .agent'.")
