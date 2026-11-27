# BACKLOG — what is left (priority order), 2026-11-19

Legend: [open] not started · [partial] some done · [manual] verified by hand, not automated.

## Gateway
1. [partial] **Reproducible dependencies without Flutter:** `v1.1.0` prints the resolved direct dependencies and platform implementations in every build (annotation `Resolved dependencies`). Not done: a workflow that opens a PR committing `pubspec.lock`, or uploading it as an artifact.
2. [open] **Release signing with a private key:** design = secrets passed by name from the caller (`ANDROID_KEYSTORE_BASE64` ...), `fixed_debug_keystore: false`, a release workflow input. Needs the owner's decision on where the key lives and who may publish.
3. [manual] `android_scaffold: never` without `android/` and an invalid pubspec name fail with clear errors; they cannot be tested inside the smoke test (a job that calls a reusable workflow cannot use `continue-on-error`). Option: a dedicated negative-test workflow that dispatches a run and asserts its failure through the API.
4. [open] **Artifact and log download from environments that can reach the blob hosts** (`*.blob.core.windows.net`): not exercised; whether forwarding the `Authorization` header to the redirect breaks the download is unknown (see `.agent/HTTP_ONLY.md`). Measured 2026-11-27 in a sandbox with a domain allowlist: the artifact zip and job-log URLs redirect to a blocked host, so results there come only from check-run annotations.
5. [open] **Other harnesses:** the rows for DSH BOX, MiniMax, Kimi, Qwen in `harness-tools.md` §7 are empty on purpose: fill them only after listing each harness's real tools.
6. [open] **Flutter pin maintenance:** `3.47.9` is pinned in callers and the smoke test; the weekly `canary.yml` shows drift against the latest stable. Update through the upgrade process.
7. [open] Make `method-check` friendlier for docs-only or tiny PRs if it becomes noisy (it requires `IMPLEMENTATION_STATE.md`, `HANDOFF.md`, `CHANGELOG.md` to change in every PR).
8. [open] A guard for "PR closed but the branch keeps receiving commits": `gh_ci.sh wait` now prints a hint; a GitHub check or comment is not built.
9. [open] `agent_audit.py` only flags double-angle-bracket upper-case placeholders: a bootstrap whose files still hold template text with ellipses or angle-bracket hints passes with 0 warnings (seen 2026-11-27 in the lab repository). Consider flagging them.
10. [open] The template's own PRs always fail the `method / Agent memory audit` job (the template has no `.agent/` state by design); it failed on template PRs #2, #3 and #4, all merged because the job does not block the build and `main` is not protected. Skipping it when `.agent/IMPLEMENTATION_STATE.md` is absent would remove the noise, but it changes the caller every app copies: decide deliberately.

## Template (`Flutter-App-Template`)
1. [manual] v2 is merged (PR #4, 2026-11-27) and was tested end to end: a repository created from it was renamed, built green in CI and the APK ran on the owner's phone (label and first screen). Not exercised on a device: the notifications and `SharedPreferences` APIs (recipes only, no code uses them). The throw-away repository `zz-tpl-e2e` can be deleted by the owner.
2. [open] A real `PrefsStorage` and a `notifications` skeleton are recipes, not code: add them as code only when a second app needs them.
3. [open] Design skill review (the owner reports the card/widget sizes in addadi differ from the design foundation; the design skills are being reviewed in other conversations).

## Reference app (`addadi`)
Paused. Open items are in its `.agent/IMPLEMENTATION_STATE.md` (photos, PDF export, font, signing, LICENSE, exact pins).
