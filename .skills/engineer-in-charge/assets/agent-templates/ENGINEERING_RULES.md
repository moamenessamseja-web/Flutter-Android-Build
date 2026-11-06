# ENGINEERING_RULES.md — how to work on <<PROJECT>> (read before coding)

Audience: any engineer or AI agent. The owner may not be a programmer: explain results in plain language, never claim what was not verified,
do not ask for routine technical decisions (decide, then report), do ask for product/identity/irreversible ones.

## 1. Definition of done — UI-only vs a real feature
A screen that looks right is NOT a feature. A feature is done only if ALL are true:
1. **Persisted** through the project's storage layer and survives restart (a test re-initialises storage and re-reads).
2. **Consumed**: something reads it (a list, a scheduler, a report). A record nobody reads is UI-only.
3. **Same pipeline for every entry point** (UI, chat, import…): they write the same records. No parallel store "for the UI".
4. **Visible** where the owner looks (lists/dashboards that should show it).
5. **Real effect** (notification really scheduled, request really sent) — assert on a fake of the platform seam, not on a status string.
6. **Honest errors**: failures are visible states; never "success" for something that did not happen.
7. **Tested**: pure-logic unit tests + a flow/widget test + a restart-persistence test; CI green.
8. **Verification level stated** (CI-green ≠ device-verified).

## 2. Reuse map — do not duplicate
| Need | Use (file) |
|---|---|
| … | … |
Before adding a model/service/screen: grep for an existing one. Extend before creating.

## 3. Stack facts (verified, with dates) — <<STACK>>
<<Fill as verified: toolchain versions pinned, platform quirks, permissions, generated-file rules, what CI injects, known device-only behaviours.>>

## 4. Data / storage rules
<<Engine, write discipline, schema evolution (additive only), keys/tables in use, what is deferred.>>

## 5. Testing and regression
- How verification works here (local SDK? CI only? where do logs live?).
- Known test gotchas (write each as: symptom → cause → what to do). Add to `LESSONS.md` first, promote here when general.
- Every bug fixed gets a regression test. Never weaken or delete an old test to get green.
- Pre-push checklist: imports used · no name clashes · tests for the change · docs updated.

## 6. Process
- Start gate: read `README.md`, `IMPLEMENTATION_STATE.md`, `HANDOFF.md`; inspect git + latest CI; trust code over docs and fix the docs.
- Work on a branch; the default branch gets only what the owner has tested; never force-push; tag anchors before risky merges.
- After every green build update: STATE, `implementation.md`, CHANGELOG, HANDOFF. Archive, never delete.
- Final report: plain language · what changed · verified (level) · needs device test · deliberately not done · decisions needed.
- Secrets: use tokens only via transient headers; never write to files/remotes/logs; tell the owner to revoke.

## 7. Owner-frozen / out of scope
(see `DECISIONS.md` — keep the list there, one source of truth)
