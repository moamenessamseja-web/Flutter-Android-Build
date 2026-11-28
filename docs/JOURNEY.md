# JOURNEY — how the gateway came to be (2026-11-06 .. 2026-11-19)

Written for a new conversation that did not live it. Dates are when the work happened; PR/commit numbers are real (public repositories).

## 0. The goal in the owner's words (summarised)
"I give an agent a short description of an app; the established process does the repetitive work: new repository, branch, build, a green APK I install by hand, then I give feedback." The owner works from an Android phone with free GitHub. Reuse and operational simplicity beat architectural sophistication.

## 1. Stages
1. **Gateway created (PR #1, 2026-11-06).** The owner uploaded three skill packages (`engineer-in-charge`, `flutter-ci-engineering` as zips, `design` as a single file). They were extracted unchanged into `.skills/` (the design file got a thin `SKILL.md`), the agent entry point `AGENTS.md` → `.agent/` was written, and the reusable workflow `flutter-android-build.yml` (`workflow_call`) with Flutter/pub/Gradle caching. First real runs found two defects in my own design: `flutter create` generated an `analysis_options.yaml` that failed analysis, and it used the *directory* name as project name. Both fixed in the workflow. Cache effect measured: 5 min 48 s cold, 2 min 16 s warm.
2. **Stable debug signing + template + run recipe (PR #2).** Every CI run signed with a random debug key, so Android refused updates. Gradle ignored `~/.android/debug.keystore` on the runner (measured three different signers); the fixed shared key is injected through `android.injected.signing.*`. Template repository `Flutter-App-Template` and `.agent/RUN.md` (idea → repo → green build → report) added; proven end to end with throw-away repositories.
3. **HTTP-only profile (PR #3, 2026-11-14).** For harnesses without bash/git: `.agent/HTTP_ONLY.md` (REST API equivalents), executed once end to end with curl only; a minimum capability contract in `harness-tools.md`. An existing draft by the owner's account was merged with the project file instead of keeping two competing files.
4. **False signals fixed before enforcement (PR #4).** A review (Claude Opus) proposed four fixes; each was verified before accepting: `gh_ci.sh wait` could report a *previous* commit's green run (proved live), a build without tests looked green (now flagged; it also exposed that `flutter create` generates a default failing test), duplicated scripts across skills (kept one copy), and instructions to read failures from release assets the pipeline never produced (replaced by annotations).
5. **Method check (PR #5).** A reusable PR workflow runs `agent_audit.py` and demands that `IMPLEMENTATION_STATE.md`, `HANDOFF.md`, `CHANGELOG.md` change in every PR. Tested in both directions on a real repository. Per-item status check ("Done" is an ERROR) with the free-text verification log excluded on purpose.
6. **Pinned smoke + canary, coverage, tag `v1.0.0` (PRs #6–#8).** `continue-on-error` is not allowed on a job that calls a reusable workflow (actionlint caught it; the mistake was mine: my command chain did not stop on the lint failure). The latest-stable canary became its own scheduled workflow. The smoke test now covers release mode, `pre_build_command`, `fixed_debug_keystore: false` and asserts the signing fingerprints. Callers pin `@v1.0.0`.
7. **addadi, the first real app (2026-11-15/16).** Built from the owner's README and design foundation; Phase 1 (meters, readings, reset segments, spike detection, local storage, three screens) green on the first CI compile because the code used conservative Flutter APIs and the pure logic was tested locally first. Phase 2: package renamed `addady`, local notifications reusing the proven injection from `manager-assistant-ready` (`d2a17ef`), meter editing + tariff, Arabic/English, CSV export. The owner installed and approved it; project paused with a full `.agent/` handoff.
8. **Continuity release (this branch, 2026-11-19).** At the owner's request, to let another conversation continue: resolved-dependency report in every build (`v1.1.0`), `gh_ci.sh` hints when no run appears, `pure_dart_tests.py` (pure-Dart tests without a Flutter SDK), `setup_sandbox.sh`, measured sandbox facts, template v2, and these documents.

## 2. Decisions and their reasons
- **Reusable workflow + tags, not copies:** one place to fix; apps pin a tag so a gateway change cannot break them silently; upgrade one app first.
- **Annotations as the result channel:** the authoring sandbox cannot download artifacts or logs (blob hosts blocked) and release assets were never produced; check-run annotations are readable through the API by any agent.
- **Fixed shared public debug key:** updates install over each other; it is public on purpose and not for publishing. Release signing is a later, separate decision.
- **`android/` generated in CI, not committed:** keeps the repository small; native changes go through `tool/ci_android.sh` (idempotent, verifies itself, dry-run on a mock first).
- **Pure logic behind interfaces:** the only verification available before CI is a plain Dart SDK, so everything testable is kept free of Flutter imports.
- **Honesty ladder:** read < sanity < CI < artifact < device; every report says which level was reached.

## 3. What went wrong (and what it taught)
- Unpushed work was lost when the sandbox reset mid-work → push early.
- An invalid workflow (my `continue-on-error`) was pushed because a command chain used `;` after the lint → chain with `&&` and stop on lint errors.
- A PR was closed and later commits built nothing; I assumed an actor merged it → check `merged_by` and the events; (it was an accidental tap on the phone by a family member).
- A label with `&` produced an invalid manifest in my first `ci_android.sh` → found by the dry-run with a real XML parser, before any CI run.
- A background download was killed at the end of a tool call → resumable, foreground steps.
- I once stated the cache limit was shared across repositories; it is per repository. Verify claims against documentation or measurements, and correct them in writing.

## 4. People and tools
Claude Opus reviewed the first design and proposed the ordering "fix the sensors before the referees"; Sonnet versions did earlier work in `manager-assistant-ready` (the notifications fix `d2a17ef` is the proven reference). The owner's other repositories (`mulkcare`, `note-me-`, `manager-assistant-ready`, `addadi`) are not touched by the gateway unless the owner asks.

## 5. Refinement session (2026-11-28)
Owner commissioned the master work order after a full review. Housekeeping first: merged branches deleted only after API re-verification; `zz-tpl-e2e` evidence snapshotted before archiving. Owner decisions: archive `zz-tpl-e2e` (agent authorized to execute); defer real release signing (D2) and branch protection (D3); keep one fat APK artifact (D6). Losing a future production signing key would lose the app's Play identity forever, so D2 stays blocked until key location, backup and publisher decisions are explicit.
