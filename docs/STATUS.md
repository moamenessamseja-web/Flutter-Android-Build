# STATUS — where the gateway stands (2026-11-28)

**Read this first if you are a new conversation (any Claude model) asked to continue or maintain this gateway.**
The full story is in `JOURNEY.md`, what is left in `BACKLOG.md`. Rules for agents working on *other* repositories are in `.agent/README.md`.

## What exists (three repositories, all public, owner `moamenessamseja-web`)
| Repository | Role | Version / state |
|---|---|---|
| `Flutter-Android-Build` (this one) | the gateway: reusable build workflow, PR method check, three skills, agent entry point, scripts | **current tag `v1.1.0`** (callers in the template and the ready file use it); `v1.0.0` is still used by addadi and works unchanged |
| `Flutter-App-Template` | template repository for new apps: caller workflow, layered Dart skeleton, `tool/ci_android.sh`, `tool/rename_app.sh`, `docs/RECIPES.md` | **v2 merged to `main` on 2026-11-27** (PR #4, merge commit `444128d`); its caller pins gateway `v1.1.0`. Tested end to end through a throw-away repository: renamed, CI green (analyze, tests, release APK), and the APK ran on the owner's phone (launcher label and first screen) |
| `addadi` | the first real app (Ɛaddady / عَدّادي): reference implementation of everything | Phase 1 + 2 finished, merged, tag `phase2-paused-2026-11-16`, last code commit `5520f0b`, installed and approved by the owner |

## The owner and how they work (do not re-ask)
Not a programmer; works from a phone with free GitHub accounts; speaks Arabic (Egyptian) with English technical terms; wants a green build, the **commit number**, and the APK from the run page to install by hand, then replies with feedback. Wants honesty (never "done" without evidence). The owner provides a GitHub token in the chat when work needs it (never store it anywhere; it is only used as a transient header). A family member once merged a PR by tapping the phone: before assuming who did something, check `merged_by` and the issue events through the API.

## How to start working (any conversation)
Update the header date on every edit — the same "docs not older than code" rule the audit enforces on apps applies to these docs.
1. Sandbox reset? Run `GH_TOKEN=... bash .skills/engineer-in-charge/scripts/setup_sandbox.sh moamenessamseja-web/Flutter-Android-Build ...` (it recreates tools and clones). **Commit and push early**: the sandbox was reset once mid-work and unpushed changes in `/tmp` and `/home/claude` were lost.
2. Read `harness-tools.md` section 8 (measured facts about the chat sandbox: `/bin/sh` is dash, 300 s per command, blocked hosts, no Flutter SDK).
3. Work on a branch, open a PR, wait with `gh_ci.sh wait <branch>`, read with `gh_ci.sh result <branch>`; merge only when the owner says so (exception: the owner has explicitly delegated closing a project).
4. Gateway changes follow the upgrade process in `README.md` section 7: branch → `Smoke test` green → merge → new tag → one app first.
5. Pure-Dart logic can be tested without Flutter: `python3 .skills/engineer-in-charge/scripts/pure_dart_tests.py <project>`.

## Verified vs not verified (honest)
Verified on GitHub Actions: the reusable workflow (debug/release, scaffold generation, analyze, test, APK, failure diagnostics), fixed debug signing (same signer across runs, asserted in the smoke test), the PR method check (three paths), cross-repository calls with a pinned tag, template-generated repositories building green, the HTTP-only profile end to end, the `gh_ci.sh` fixes (stale `head_sha`, `result`, hints), notifications/tariff/language/export compiled and tested in CI (addadi).
**Not verified:** installing/running on a device beyond what the owner reported (addadi Phase 1 fully; Phase 2 approved overall without per-feature results), downloading Actions artifacts and logs from the authoring sandbox (blob hosts are blocked there), release signing with a private key (not built), the two failure paths `android_scaffold: never` and an invalid package name are verified manually only, `share_plus`/`flutter_local_notifications` behaviour on the phone, any harness other than Claude.

## Rules that proved themselves
Fix the signals before adding enforcement; every claim states its evidence level (read < sanity < CI < artifact < device); dry-run native-injection scripts on a mock project before CI; keep logic pure and behind interfaces so it can be tested without a device; never merge unasked; never put a token anywhere but a transient header.

## Housekeeping evidence (2026-11-28)
- A1: deleted the 12 gateway and 4 template merged branches after re-checking each head against a merged PR through the API; both repos now have only `main`.
- A2: `zz-tpl-e2e` run [45966298363](https://github.com/moamenessamseja-web/zz-tpl-e2e/actions/runs/45966298363) (2026-11-27, commit `8af143decec622d17d58874529218a35696687c2`) was green. `Resolved dependencies`: shared_preferences 2.5.6, shared_preferences_android 2.5.5, 63 packages. `APK ready`: package com.example.tpl_e2e, app-release.apk 43M, APK SHA-256 `2ae75ba806c65879fae137240e7e674d0a1181933373fa54dea67b2b983e90e0`, signer SHA-256 `136966601854d1bd1397841d7d5ef10f1145bd8ac71c49f8ac6812857f136233`. Owner authorized archiving (never deleting) the evidence repo; archive status is recorded in JOURNEY once executed.
- Owner decisions this session: D2 real release signing deferred; D3 branch protection deferred (instructions prepared); D6 keep the single fat APK artifact.
