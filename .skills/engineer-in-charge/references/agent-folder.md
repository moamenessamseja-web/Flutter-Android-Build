# The `.agent/` folder — spec, decision tree, hygiene

Contents: 1 Why · 2 Files (purpose, must contain, anti-patterns) · 3 Where does this fact go? · 4 Start/stop gates · 5 Archive procedure · 6 Style · 7 Real example

## 1. Why a folder in the repo
Agents lose context (clearing, usage limits, new sessions, a different model). The folder gives every newcomer the same orientation in minutes and gives the
owner one place to see the truth. It must be **short enough to read, honest enough to trust, and updated often enough not to lie**.

## 2. Files
| File | Must contain | Anti-patterns |
|---|---|---|
| `README.md` | index table (file · purpose · update trigger) + non-negotiables | listing files that don't exist; no update triggers |
| `BRIEF.md` | owner's words **verbatim**, dated, newest first; then a labelled "engineering reading"; owner profile (language, level, pet peeves) | paraphrasing the owner; editing their text |
| `ENGINEERING_RULES.md` | definition of done (UI-only vs real), reuse map, verified stack facts (dated), storage rules, testing gotchas, process, frozen list pointer | generic advice with no project facts; contradicting DECISIONS |
| `IMPLEMENTATION_STATE.md` | baselines & branches, this session's changes with *how verified*, NOT verified, corrections of earlier errors, device-test checklist, next steps (priority), build log; **<200 lines** | session diaries that grow forever; "done" with no level |
| `HANDOFF.md` | first 20 lines a cold start needs: test target, last confirmed, distrusted builds, current task list with status, "do not" list | narrative; stale target |
| `implementation.md` | inventory table, ONE standard status per item, evidence, verification log (build · commit · CI · device) | "works", "done", "should work" |
| `ARCHITECTURE.md` | layers, data-flow diagram per important feature, naming/navigation gotchas, known limits | history; aspirational design |
| `CHANGELOG.md` | completed work with build numbers and red/green; red causes one line each | plans, TODOs |
| `LESSONS.md` | symptom → cause (and how proven; "unknown" allowed) → action → guard added | lessons without guards |
| `DECISIONS.md` | decided / frozen / open (with evidence + smallest options), dated, quoting the owner | hiding open questions in prose |
| `archive/` | superseded docs, each starting with an `ARCHIVED` banner saying why and what replaced it | deleting history; archived docs without a banner |
Optional: `mission_<date>.md` for a one-off brief that is executed (add a STATUS banner when done). `agent_audit.py` checks most of the above.

## 3. Where does this fact go?
- Owner said it (priority, decision, preference, freeze) → `BRIEF.md` (verbatim) and `DECISIONS.md` (if it freezes/decides) and project memory (if durable).
- "This broke because…" → `LESSONS.md` (+ promote to RULES if general).
- "The system works like this" → `ARCHITECTURE.md`. "How we must work" → `ENGINEERING_RULES.md`.
- "Feature X is at status S" → `implementation.md`. "What happened this session / what's next" → `IMPLEMENTATION_STATE.md`.
- "What changed" → `CHANGELOG.md`. "What should the next agent do first" → `HANDOFF.md`.
- Superseded anything → `archive/` with banner. Secrets → nowhere.

## 4. Gates
Start: `orient.sh` (+ verify the headline claim). Stop: `stop_gate.py` must print `HANDOFF OK`. **Update after every green build**; docs-only commits to a feature branch trigger no CI.

## 5. Archive procedure (when a doc is superseded)
`git mv` it to `archive/<name>_<what>.md` → add a banner (`> **ARCHIVED (date).** Superseded by …; kept for the diagnostic trail; these statements are outdated: …`)
→ write the replacement concise → carry over every still-true fact and gotcha → update README index → run `agent_audit.py`.

## 6. Style
Dated, specific, falsifiable. Evidence beats adjectives ("CI #93 green, 119 tests; not device-tested" not "works great"). Name unknowns ("why the lock was ignored:
unknown"). Plain sentences; tables for inventories. Arabic quotes from the owner stay Arabic. No emojis needed. Corrections of your own earlier claims go in the state
file, visibly.

## 7. Real example (compressed)
A rules screen "worked" in the UI but `.agent/` had no entry saying the feature was only *UI-complete*. The restructure added: a definition of done (8 criteria),
a reuse map, Android notification facts (exact vs inexact, past times never scheduled, tz.local=UTC → pre-scheduled series), testing gotchas (FakeAsync + storage),
and moved 470 lines of history to `archive/`. `agent_audit.py` went from untested to 0 errors/0 warnings.
