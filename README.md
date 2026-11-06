# Flutter-Android-Build — central engineering gateway

## 1. What this repository is
One place that holds everything reusable for building Flutter/Android apps from a phone with free GitHub features and AI coding agents:

- a **reusable GitHub Actions workflow** that builds an Android APK (`.github/workflows/flutter-android-build.yml`);
- three **skills** for agents (`.skills/`): Engineering in Charge, Flutter CI, Design;
- the **agent entry point** (`AGENTS.md` -> `.agent/`) that tells any agent how to use the above on any repository.

It contains no application code and no project state.

## 2. Why it exists
So the human never has to re-explain the engineering rules, rebuild a CI pipeline, or copy agent instructions into every app. Each app repository keeps only a ~15-line caller workflow; everything else is maintained once, here.

## 3. Directory structure
```
AGENTS.md                         entry point read by most coding agents -> points to .agent/README.md
.agent/
  README.md                       the path every agent follows + when to use which skill
  ACCESS.md                       how to fetch the gateway; agent auth vs repo access vs workflow permissions
  TARGET_REPO_AGENTS.md           snippet to copy into a target repo as its AGENTS.md
.skills/
  engineer-in-charge/             method, start/stop gates, scripts, and the .agent/ templates (assets/agent-templates/)
  flutter-ci-engineering/         Flutter + GitHub Actions workflow, CI scripts, lessons
  design/                         DESIGN.md (visual/UI guide, Arabic) + SKILL.md
.github/workflows/
  flutter-android-build.yml       THE reusable workflow (workflow_call)
  smoke-test.yml                  self-test: builds fixtures/smoke_app through the reusable workflow
fixtures/smoke_app/               minimal Flutter app (no android/ folder) used only by the smoke test
```

## 4. The three skills
| Skill | Use it for | Start with |
|---|---|---|
| `engineer-in-charge` | Always first. How to orient in a repo, work in small verified steps, report honestly, stop loops. Holds the ten `.agent/` templates and the start/stop-gate scripts. | `.skills/engineer-in-charge/SKILL.md` |
| `flutter-ci-engineering` | Flutter/Android built only on GitHub Actions: CI loop, APK comparison, dependency-drift diagnosis, lessons L1-L18. | `.skills/flutter-ci-engineering/SKILL.md` |
| `design` | UI and visual identity for every Flutter app: tokens, RTL/LTR, typography, components, accessibility. | `.skills/design/SKILL.md` -> `DESIGN.md` |

The skills were extracted from the uploaded archives without content changes. Differences from what was uploaded, and why:
- The archives are named `engineer-in-charge` and `flutter-ci-engineering`; those real names are used for the folders.
- The uploaded "design" material was a single file (`design 2.md`), not a package. It was moved unchanged to `.skills/design/DESIGN.md` and a short `SKILL.md` was added so it works as a skill.
- The two zip files were removed after extraction (they remain in Git history).
- `flutter-ci-engineering/references/manager-assistant.md` describes one specific project; it is kept as supplied and marked as project-specific in `.agent/README.md`.

## 5. How an agent enters and navigates
`AGENTS.md` -> `.agent/README.md` -> `engineer-in-charge/SKILL.md` -> other skills as needed -> inspect the target repo -> implement -> branch/commit/push/PR -> CI -> report. The agent retrieves the gateway with `git clone --depth 1 https://github.com/moamenessamseja-web/Flutter-Android-Build.git /tmp/gateway` (public repo, no token). GitHub Actions does **not** hand skills to an agent; the clone is the mechanism. To make agents find the gateway automatically, put `.agent/TARGET_REPO_AGENTS.md` in each target repo as `AGENTS.md`.

Example task from a phone: *"In repo X add a dark-mode toggle to settings."* The agent clones the gateway, runs `orient.sh` on X, reads X's `.agent/`, reads `design/DESIGN.md`, implements on a branch, opens a PR, and reports the PR link plus the APK artifact from the CI run.

## 6. Connect another Flutter repository
1. Make sure this repository's workflow is usable: it is public, so nothing to enable. (If it becomes private: *Settings -> Actions -> General -> Access* -> allow access from your other repositories.)
2. In the app repository add `.github/workflows/build-apk.yml` (see section 7). The name `build-apk.yml` matters: `flutter-ci-engineering/scripts/gh_ci.sh push-run` dispatches that file by default.
3. Commit `pubspec.lock` (the pub cache key uses its hash).
4. Optional: copy `.agent/TARGET_REPO_AGENTS.md` into the repo as `AGENTS.md`.

## 7. Caller workflow
Minimal:
```yaml
name: Build Android

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true

jobs:
  android:
    uses: moamenessamseja-web/Flutter-Android-Build/.github/workflows/flutter-android-build.yml@main
    with:
      flutter_version: "3.47.9"   # pin it; empty = latest of the channel
      build_mode: release
    secrets: inherit
```
`@main` always uses the latest central version. For a frozen pipeline, reference a commit SHA (no release tags exist yet).

All inputs (defaults in brackets):

| Input | Meaning |
|---|---|
| `flutter_version` [""] | Exact Flutter version; empty = newest release of the channel |
| `flutter_channel` [stable] | stable / beta / main |
| `java_version` [17] | Temurin JDK for Gradle |
| `build_mode` [release] | release / debug / profile |
| `working_directory` [.] | Folder with `pubspec.yaml` (monorepos) |
| `android_scaffold` [auto] | auto = run `flutter create --platforms=android` only if `android/` is missing; never = fail instead |
| `scaffold_args` [""] | Extra `flutter create` args, e.g. `--org com.example` |
| `pre_build_command` [""] | Shell command after `pub get`/scaffold and before analyze/test/build (e.g. `bash tool/ci_inject_android.sh` for repos that inject native changes into a generated `android/`) |
| `run_analyze` [true], `analyze_args` [--no-fatal-infos] | Analyzer step; warnings and errors fail, infos do not |
| `run_tests` [true] | `flutter test`; skipped if there is no `test/` directory |
| `build_args` [""] | Extra `flutter build apk` args, e.g. `--build-number=42` |
| `artifact_name` [android-apk], `artifact_retention_days` [14] | APK artifact |
| `gradle_cache_read_only` [false] | See caching |
| `timeout_minutes` [30] | Job timeout |

Outputs: `artifact_name`, `flutter_version` (version actually used).

Release-mode APKs use whatever signing the app's Android project defines (Flutter's default template signs with the debug key). Production signing is not part of this workflow.

## 8. Caching
- **Flutter SDK + pub cache:** `subosito/flutter-action@v2` with `cache: true` and `pub-cache: true`. The SDK cache key follows channel/version/architecture; the pub cache key additionally appends the hash of `pubspec.lock`. With an unpinned version the SDK cache changes whenever a new release appears.
- **Gradle:** `gradle/actions/setup-gradle@v6` caches `~/.gradle`. Its own default is read-only on branches other than the default branch; this workflow sets `cache-read-only: false` so feature-branch/PR builds also save a cache. Set `gradle_cache_read_only: true` to stop that.
- GitHub scoping: a branch can read caches from itself and the default branch, not from sibling branches. Total cache is limited (10 GB per repository) and unused entries expire after 7 days, so the first build after a quiet week is slow.
- Check the "Post ..." steps and the Gradle job summary of a run to see hits/misses.

## 9. Branches, commits, Pull Requests
Agents work on a dedicated branch (e.g. `agent/<short-task>`), one concern per commit, never on the default branch. Push the branch, open a PR; the caller's `pull_request` trigger builds it through this workflow. The default branch only receives what the owner has tested on a device. Details: `engineer-in-charge/SKILL.md` section 4 and `flutter-ci-engineering/SKILL.md` section 3/8.

## 10. Permissions and secrets
See `.agent/ACCESS.md`. In short:
- Agent token (fine-grained PAT, or whatever the agent platform stores as `AGENT_CLOUD_SONNET`): Contents RW, Pull requests RW, Actions RW, Metadata R on the target repos. An Actions secret is only visible to workflow runs, not to an external agent.
- Caller workflow: `permissions: contents: read` is enough.
- `secrets: inherit` forwards the caller repo's secrets only.
- Never print or commit tokens.

## 11. Troubleshooting
Every failed run publishes a step summary with the tail of each log and an artifact `ci-logs` (pub-get, flutter-create, pre-build, analyze, test, build logs).

Download from a phone: open the run page in the browser and tap the artifact. From an agent:
```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/artifacts"
curl -sL -o logs.zip -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip"
```
`flutter-ci-engineering/scripts/gh_ci.sh` works for `push-run`, `status`, `wait`; its `log`, `notes` and `download` commands read release assets that this workflow does not create, so use the artifacts above.

| Symptom | Likely cause / action |
|---|---|
| "Invalid workflow file ... workflow is not reusable" / `uses` not found | Path or ref wrong, or repo private without Actions access. Check `owner/repo/.github/workflows/flutter-android-build.yml@ref` |
| "No pubspec.yaml in ..." | Set `working_directory` |
| `android/ is missing and android_scaffold=never` | Use `auto`, or commit `android/` |
| `flutter pub get` fails: SDK constraint | App needs a different Dart/Flutter: set `flutter_version` |
| Analyze fails | Warnings/errors are fatal by design; fix them. Infos are not fatal |
| Gradle/Java errors (e.g. "requires Java 21") | Set `java_version` to what the Android Gradle Plugin needs |
| Plugin/dependency behaviour changed between builds | Unpinned Flutter or dependencies: pin `flutter_version`, commit `pubspec.lock`; compare toolchain in the run's "Toolchain" summary (see skill lesson L1) |
| "No files were found" on APK upload | Build did not produce an APK; read `build.log`; check `working_directory` |
| Builds are slow every time | Check cache hit/miss; `pubspec.lock` missing; first run on a new branch |
| PR opened by an agent did not start CI | PR was created with `GITHUB_TOKEN`; create it with the agent's PAT |

## 12. Extending the gateway
- **New skill:** add `.skills/<name>/SKILL.md` (frontmatter `name`, `description`), keep its files together, add one row to the table in `.agent/README.md` and section 4 here.
- **New workflow** (e.g. app bundle, signing): add `.github/workflows/<name>.yml` with `on: workflow_call`, declare inputs/permissions explicitly, lint it, add a smoke job.
- **Change the Android build:** edit the one workflow; callers pick it up on `@main`. Run the smoke test (Actions -> "Smoke test" -> Run workflow) before relying on it.
- Lessons that apply to all projects belong in the relevant skill (as the skills themselves ask); project facts belong in the target repo's `.agent/`.

## Verification status of this repository
Verified: file structure, extraction completeness (all files from both archives present), `actionlint` 1.7.12 (with shellcheck) passes on both workflows, reusable-workflow syntax (`workflow_call`, inputs, outputs, permissions), action versions exist (checkout v7, setup-java v6, setup-gradle v6, upload-artifact v7, flutter-action v2).
Not yet verified: an actual run on GitHub Actions (run `Smoke test` once), the inputs of `flutter-action` with an empty `flutter-version`, and a real call from another repository.
