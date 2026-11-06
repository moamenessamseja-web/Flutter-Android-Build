# .agent/ — start here (every session, human or AI)

Project: **<<PROJECT>>** · Owner: <<OWNER>> · Stack: <<STACK>> · Bootstrapped: <<DATE>>

This folder is the project's memory. Sessions die without warning and context gets cleared, so **anything not written here is lost**.
Read in this order; update the marked files after every green build / verified step.

| # | File | Purpose | Update when |
|---|---|---|---|
| 1 | `BRIEF.md` | The owner's standing brief, in their words (verbatim) + the latest priorities | owner changes priorities (append dated) |
| 2 | `ENGINEERING_RULES.md` | How to work here: definition of done, reuse map, stack facts, testing gotchas, process | a lesson becomes a rule |
| 3 | `IMPLEMENTATION_STATE.md` | Current checkpoint: baselines, latest build, device-test checklist, next steps (<200 lines) | **every green build** |
| 4 | `HANDOFF.md` | 60-second pointer: what to test/trust/distrust, what not to do | **every green build** |
| 5 | `implementation.md` | Inventory: each feature + ONE honest status + verification log | **every green build** |
| 6 | `ARCHITECTURE.md` | Current architecture & data flow (not history) | structure changes |
| 7 | `CHANGELOG.md` | What actually changed (completed work, with build numbers, red/green) | **every green build** |
| 8 | `LESSONS.md` | Symptom → real cause → action (evidence-based) | after any red/surprise |
| 9 | `DECISIONS.md` | Owner decisions + frozen/out-of-scope items + open decisions | owner decides / freezes |
| 10 | `archive/` | Superseded docs, each with an ARCHIVED banner. Never delete history | when a doc is replaced |

Non-negotiables: never claim verification that did not happen · keep verification levels separate (read < sanity < CI < artifact < owner's device) ·
secrets never in the repo · a screen that does not persist/schedule/show real data is **not** a finished feature · reuse existing components.
