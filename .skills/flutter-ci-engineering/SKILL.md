---
name: flutter-ci-engineering
description: Engineering workflow for Flutter/Android apps built ONLY through GitHub Actions CI (no local Flutter/Dart SDK). Enforces a start gate (read the repo's .agent/ memory files and git state before any work) and a stop gate (never end a session until IMPLEMENTATION_STATE, HANDOFF and CHANGELOG are updated, committed and pushed); defines the work loop (small asserted patch, regression tests, branch push, workflow_dispatch, poll, read failure log), honest verification levels, device-less diagnosis (APK comparison, pinning Flutter/plugins), and sleep/token economy. Use whenever the user wants to continue, fix, extend, debug or release a Flutter/mobile project via CI, or mentions an APK, build number, commit SHA, workflow, .agent/, handoff, phases, or the Manager Assistant app / مساعد الإدارة, or says "كمل الشغل", "حدّث الهاند أوف", "البيلد فشل", "الأبك شاشة سوداء", even without saying "skill" or "CI".
---

# Flutter/Android CI-only engineering

You are the engineer in charge. The sandbox has **no Flutter/Dart SDK**: GitHub Actions compiles, analyzes and tests. The repo's `.agent/`
files are the project's memory across sessions — a session that does not read them wastes the owner's time re-deriving old work, and a
session that does not update them destroys the next session's context. Everything below serves those two facts.

## 1. The two gates (non-negotiable)

### Start gate — before ANY edit, build or analysis
1. `bash scripts/session_start.sh <repo>` — one capped command: branch, last commits, working tree, `.agent/` listing, head+tail of
   `IMPLEMENTATION_STATE.md` and `HANDOFF.md`. It also records the session-start SHA for the stop gate.
   (No repo yet? clone with the token header trick in §8, then run it.)
2. Read the rest of `.agent/` that matters (state file in full if short; mission/spec only the sections the task needs).
3. **Verify the state file's headline claim** with one `git log` / Actions-API call (it can be stale — see references/lessons.md L7).
4. If the owner names a commit, build number or phase, that is the anchor: confirm with one command, don't re-derive. If it conflicts with
   the state file, trust the owner, tag both (`git tag -a baseline-… <sha>`), and record the override at the TOP of the state file.
5. No `.agent/` directory? Create it first (state file with: baseline SHA, verified facts, open items) — before writing any code.

### Stop gate — you may not end the session, hand control back, or send a "done" report until this passes
`python3 scripts/handoff_check.py` must print `HANDOFF OK`. It fails unless `.agent/IMPLEMENTATION_STATE.md`, `HANDOFF.md`, `CHANGELOG.md`
(and `implementation.md` if present) were changed in a commit this session, the tree is clean, HEAD is pushed, and the state file has an
entry dated today. What each file must say:
- **IMPLEMENTATION_STATE.md** — dated session section: baseline SHA, what changed and why, what was verified and *how*, what was NOT
  verified, open items carried forward verbatim, next steps in priority order, corrections of earlier wrong claims.
- **HANDOFF.md** — the first 20 lines a cold-start session needs: which build/commit to test or trust, which to distrust, what not to do.
- **CHANGELOG.md** — only what was actually changed (with build numbers and red/green), never plans.
- **implementation.md** — inventory with one status per item: Verified complete · Implemented, not yet verified · Partially implemented ·
  Not started · Blocked · Deferred by product decision. Never promote a status without evidence.
**Update after every green build, not only at the end.** Sessions die on usage limits without warning; a handoff written at the end may never
be written. If budget is running low, do the handoff NOW (it is cheap) and continue afterwards. Docs-only commits to a feature branch do not
trigger CI, so this costs nothing.

## 2. Environment facts that waste hours when forgotten
| Fact | Consequence |
|---|---|
| No Dart/Flutter SDK; pub.dev, storage.googleapis.com and Azure blob logs are not reachable | CI is the only compiler; read failures from the `debug-<run>` release asset (`scripts/gh_ci.sh log <n>`) |
| github.com, api.github.com, raw.githubusercontent.com, release assets ARE reachable | APKs/logs/Flutter templates/changelogs can be fetched; plugin changelogs from `raw.githubusercontent.com/flutter/packages/...` |
| One bash call dies at **300 s** and loses all output | never sleep > 270 s in a call |
| `/bin/sh` is dash | no `{a,b}` brace expansion (`mkdir -p a/{b,c}` creates a folder literally named `{b,c}`); use `bash` or separate args |
| `cut -c` is byte-based | truncating Arabic text yields invalid UTF-8 and the tool returns nothing: truncate with Python or don't truncate |
| Raw CI logs / GitHub JSON contain control chars | use `scripts/clean_log.py`; strip `[\x00-\x08\x0b\x0c\x0e-\x1f]` before `json.loads` |
| Older tool results get cleared from context | write conclusions into the state file; don't rely on re-reading earlier output |

## 3. The work loop (one phase or one concern at a time)
1. **Locate, don't read everything.** `grep -n` to find the code, then `sed -n 'a,bp'` for just that region. Read a function once.
2. **Patch with asserted Python**, not hand-waved edits:
   `assert s.count(old)==1; s=s.replace(old,new)` — an anchor that doesn't match exactly once aborts instead of silently corrupting.
   One script can patch several files. Re-read a `switch`/`case` block after editing it (references/lessons.md L4).
3. **Write the regression test with the change**, in the same commit: every bug fixed gets a test that fails before and passes after;
   every new behavior gets at least one test. Never delete or loosen an old test to get green.
4. **Local sanity** (`python3 scripts/dart_sanity.py --base <ref>`): bracket balance vs the base file, YAML validity, diff stat. It is not
   a compiler. Also by eye: no unused private members/imports/locals (analyzer *warnings* are fatal), no records/features the pinned Dart
   may not support, null-safety on every nullable access.
5. **Commit + push + dispatch in ONE command**:
   `git add -A && git commit -q -m "<why, not just what; state 'not run locally'>" && git -c http.extraheader="$HDR" push -q origin <branch> && GH_TOKEN=… REPO=… bash scripts/gh_ci.sh push-run <branch>`
6. **Use the CI wait productively** (§4): write the next phase's patch, the docs, or analysis — don't idle.
7. **Green →** fetch the release (`gh_ci.sh notes build-<n>`), inspect the APK if the change touches startup/dependencies
   (`apk_compare.py`), update the 4 handoff files, commit/push docs, then continue.
   **Red →** `gh_ci.sh log <n>`; read the actual error; find the root cause (one bad export can print 15 symptoms); fix; repeat.
   Two reds in a row on the same symptom ⇒ stop patching and form a hypothesis from evidence (§7).
8. Branch builds use `workflow_dispatch`; never push to `main` "just to check". Merge to `main` only when the owner has device-confirmed.

## 4. Time and sleep economy (measured: dispatch → finished ≈ 6.5–7.5 min)
- Right after dispatch: do useful offline work for 2–4 minutes (next patch, docs). Then `gh_ci.sh wait <branch> 240`
  (polls every 20 s, prints only on change, exits 0 green / 1 red / 2 still running). If exit 2, call it again once (`wait … 200`).
  Typical total: 2 wait calls. Never poll in a loop that prints each iteration; never `sleep 300`.
- Don't re-dispatch while a run for the same branch is in progress (it just queues and doubles the wait).
- Batch CI cycles: group related phases into one push when they don't interfere; but push the riskiest change (startup, dependencies,
  platform) alone so a failure is attributable.
- When the system reminds you the user hasn't heard from you: write one short sentence of status, then continue the tool call. No essays.
- Long-running diagnostics (APK downloads ~57 MB, comparisons): run them once, keep results in a file under `/tmp`, read the file in slices.

## 5. Token economy (keeps sessions alive under usage limits)
- Cap every output: `| head -40`, `sed -n 'a,bp'`, `git diff --stat`, `git log --oneline -6`. Never `cat` a file you haven't sized with `wc -l`.
- Never print whole logs/APK strings/JSON: filter in Python and print the 10–40 lines that matter.
- Read each file region once; put the conclusion in the state file instead of re-reading. Don't re-read specs "just in case".
- One bash call per logical step: combine commit+push+dispatch, combine patch+sanity-check.
- Prefer scripts in `scripts/` over re-typing long pipelines; run them, don't read them.
- Keep prose short: no step-by-step narration of tool calls. Report results, evidence, and what's unverified — nothing else.
- Don't spawn subagents or evals for a normal engineering task; they multiply cost. Use targeted greps instead.
- Memory/notes: store durable facts the owner states; never store tokens or secrets.

## 6. Verification ladder — keep levels visibly separate in every report
1. *Read the code* (reasoned, not run) → 2. *Local sanity* (balance/YAML) → 3. *CI green* (analyze + tests + build) →
4. *Artifact inspected* (APK analysis, release notes) → 5. *Owner device-confirmed*.
Say exactly which level each claim has. "CI is green" ≠ "works". Name the outstanding thing ("not device-tested: reminder firing after reboot")
rather than writing "should work". Don't claim iOS builds, store readiness, or behavior you didn't observe.
When your earlier finding turns out wrong, say so plainly and fix the record.

## 7. Diagnosing without a device
Evidence beats guessing; cheap experiments beat long reasoning.
- **Same code, different result?** Rebuild the older source on CI and compare APKs: `python3 scripts/apk_compare.py A.apk B.apk --probe <string>`.
  Same `libflutter.so` ⇒ same engine; same size + empty identifier diff ⇒ same Dart+deps. This is how a black-screen build was traced to a
  plugin version change rather than the feature commit (references/lessons.md L1).
- **Toolchain/dependency drift:** pin Flutter (`flutter-version:`), pin suspect plugins with `dependency_overrides`, add a CI step that
  fails when the resolved version differs, and record `flutter --version` in each release's notes.
- **Startup must never be silent:** `main()` wraps init in try/catch + timeout and shows a readable error screen instead of a black one.
- If the platform scaffold is generated each run, native changes are injected by the workflow (references/android-ci-injection.md).
- Look one level deeper before proposing a new architecture: an existing dependency usually already ships the native piece.
- If a decision belongs to the owner (package id, signing key, product behavior), stop, state the evidence and 1–2 smallest options.

## 8. Git, releases, secrets
- Never rewrite or force-push `main`. Tag anchors: `baseline-<build>-user-confirmed`, `<build>-untrusted`. Work on a branch.
- One concern per commit; message explains *why* and states what was not run.
- Tokens (classic PATs get pasted in chat): use them only through `git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$TOK" | base64 -w0)"`
  and `Authorization: Bearer` for the API; never put them in a URL, remote, file, or commit; check `grep -c ghp_` on touched files; tell the
  owner once, briefly, to revoke it. Expect a new token each session.
- A release's tag/name is not proof of its commit: check `target_commitish` and the notes.

## 9. Writing Dart blind (practical rules)
- Prefer simple, explicit code the pinned toolchain surely supports; avoid cleverness you can't compile.
- Every nullable access guarded; every new private helper used; every replaced helper deleted.
- Money/quantity/date/time logic: parse into explicit tokens, never default silently, ask when ambiguous; tests use `DateTime.now()`-relative
  expectations so they don't rot. Use `DateTime(y,m,d+n)`, not `add(Duration)`, for calendar math.
- UI changes get a widget test with empty-state and back-navigation; business logic is pure functions so it is testable without a device.
- Settings must change real behavior — no decorative toggles. Say what a setting does NOT cover.

## 10. Final report (Arabic if the owner writes Arabic; short, structured, honest)
Order: what to test now (exact build/tag) → what was done per phase with one status each → what was verified at which level →
what is NOT done/unknown → decisions needed from the owner → security note (token) if any. No narration of the process.
Run the stop gate first; if it fails, fix the docs, don't report.

## Resources
- `scripts/session_start.sh` — start gate. `scripts/handoff_check.py` — stop gate.
- `scripts/gh_ci.sh` — dispatch / status / wait / log / notes / download (token via `GH_TOKEN`, never stored).
- `scripts/clean_log.py`, `scripts/dart_sanity.py`, `scripts/apk_compare.py`.
- `references/lessons.md` (symptom → cause → action, read when a symptom matches), `references/android-ci-injection.md`
  (generated-`android/` rules), `references/manager-assistant.md` (project facts: repo, anchors, CI, open decisions).
