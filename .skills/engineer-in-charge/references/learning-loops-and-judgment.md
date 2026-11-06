# Learning, judgment, and loop-breaking

Contents: 1 Lesson loop · 2 Promotion ladder · 3 Prediction check · 4 The out-of-the-box test · 5 Case studies · 6 Loop-breaking playbook · 7 When to ask the owner

## 1. The lesson loop (after every red build, surprise, or owner correction)
1. Reproduce the evidence in words: the *exact* error/symptom, not your summary.
2. Find the cause **and say how it was proven** (log line, diff, artifact comparison, minimal repro). "Unknown" is a valid entry; a guess labelled as fact is not.
3. Decide the guard: a regression test, a CI check, a script, a template line. A lesson without a guard repeats.
4. Write it in `.agent/LESSONS.md` (symptom → cause → action → guard). Keep it 4–6 lines.
5. Promote if general (see ladder). If it helps other projects, tell the owner it belongs in this skill (or the stack skill) and ship the updated file.

## 2. Promotion ladder
`LESSONS.md` (project, specific) → `ENGINEERING_RULES.md` (project rule) → stack skill `references/lessons.md` (any project on that stack) → this skill (any stack).
Promote only what survived at least one recurrence or is clearly structural. Delete nothing; supersede with a dated note.

## 3. Prediction check
Before running CI or a risky command, write one line: "I expect X". After the result, compare. Matches build trust in your model of the system; mismatches are the
most valuable data you get — stop and explain them before continuing (e.g. "I expected the lockfile to pin the plugin; the APK says otherwise" led to the pin + CI guard).

## 4. The out-of-the-box test (all four = go; otherwise stay incremental)
1. **Evidence**: do I have data that the current frame is wrong (two failed fixes, contradicting artifact, a measurement)?
2. **Root cause**: would one change remove a whole class of problems (a seam, a pure module, a guard) rather than patch one symptom?
3. **Reversible**: branch/tag exists; no force-push; no data loss; no identity/signing/publishing change.
4. **Inside decisions**: not on the owner's frozen list; no new dependency/service without a demonstrated limitation.
Radical ≠ reckless: the bolder the idea, the cheaper its rollback must be.

## 5. Case studies (field-tested)
| Situation | Naive move | What worked | Why it worked |
|---|---|---|---|
| App opens to a black screen after a "green" build; no device logs | guess at the parser change that shipped | rebuild the *older* source on CI, then diff the APKs' compiled identifiers → plugin implementation differed (dependency drift despite a lockfile); pinned the dependency, guarded it in CI, made startup failures render an error screen | an experiment that separates hypotheses beats staring at code |
| "Rules & Notifications" looked finished but never notified | add a save button/toast | traced save → schedule → list; found (1) reminders only created for already-past dates (never scheduled), (2) inexact-only alarms, (3) nothing written to the records other screens read | follow data across seams; fix root causes together |
| UI tests hung for three sessions | more print-debugging, delete the test | reasoned about the test zone: storage writes started inside the fake-async body never resume; seed with `runAsync`, settle with pump loops, reset the static write gate in `init()` | understand the runtime, then fix the pattern once (and document it) |
| Repeating alarms with the obvious time-of-day API | use it | the app's timezone is UTC → wrong hour; pre-schedule a bounded series of absolute instants instead | check the premise of the "standard" solution against this app's facts |
| Platform plugin can't run in unit tests | skip tests | put the plugin behind a tiny `Backend` interface; tests inject a recording fake and assert what was *really* scheduled/cancelled | testability is a design property |
| Docs contradicted reality (470-line state file) | keep appending | archive with banners, write a short current state + rules file, add an audit script | docs are code: refactor them |

## 6. Loop-breaking playbook
- **Detect**: same symptom after 2 attempts, or you are about to repeat a command. Use `loop_guard.py record/check`.
- **Strike 1**: fix the obvious cause. **Strike 2**: read deeper (full log slice, diff vs last green, inspect the artifact). **Strike 3**: STOP — list 2–3 hypotheses,
  design the cheapest discriminating experiment (A/B, rebuild old source, minimal repro, a probe log in a throwaway branch), run it. **Strike 4**: escalate.
- **Different error each cycle** = progress (peeling layers), not a loop — but still record each.
- **Budget**: ≤ 3 red CI cycles on one concern before the hypothesis step; one concern at a time; don't touch unrelated code while waiting.
- **Escalation message** (to the owner): symptom · what was tried (3 bullets) · what the evidence says · 1–2 smallest options · what you recommend.
- **Never**: weaken/delete the test, comment out the feature, add a retry loop to mask a race, or declare success without the level of evidence you'd demand from someone else.

## 7. When to ask the owner (and when not to)
Ask: product behavior with several valid answers, identity/legal/irreversible matters (package id, signing, publishing, data deletion), scope that changes cost/time
materially, anything they froze. Don't ask: library choices, test structure, file layout, naming, how to fix a bug. When you must ask, ask one question with evidence
and a recommendation, and keep working on everything that doesn't depend on the answer.
