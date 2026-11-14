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
  RUN.md                          the recipe: idea -> new repo from the template -> green build -> report
  HTTP_ONLY.md                    the same recipe for harnesses with no bash/git (GitHub REST API only)
  templates/build-apk.yml         ready caller workflow for an app repository (single source)
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
- Changes to the supplied skills, each with its reason (false signals found by review, then verified):
  - `gh_ci.sh` `wait` took the newest run of the branch, so after a new push it could report the *previous* commit's green result; it now waits for the run of `$EXPECT_SHA`/`HEAD`. New `result` command reads the annotations this pipeline actually produces.
  - Duplicate scripts removed from `flutter-ci-engineering/scripts/` (`gh_ci.sh`, `clean_log.py`: identical copies; `session_start.sh`, `handoff_check.py`: older versions of `orient.sh`, `stop_gate.py`). The single copies live in `engineer-in-charge/scripts/`; `flutter-ci-engineering/SKILL.md`, its `lessons.md` and `engineer-in-charge` docs now point there.
  - `flutter-ci-engineering/SKILL.md` described reading failures from `debug-<run>` release assets and `gh_ci.sh notes build-<n>`; the central workflow publishes annotations and artifacts instead, so those instructions now describe `gh_ci.sh result` (the release-based commands are kept and labelled legacy).
- `engineer-in-charge/references/harness-tools.md` got a new section 7, "Minimum capability contract", at the owner's request (what any harness needs, and one row per harness); sections 1-6 are unchanged.

## 5. How an agent enters and navigates
`AGENTS.md` -> `.agent/README.md` -> `engineer-in-charge/SKILL.md` -> other skills as needed -> inspect the target repo -> implement -> branch/commit/push/PR -> CI -> report. The agent retrieves the gateway with `git clone --depth 1 https://github.com/moamenessamseja-web/Flutter-Android-Build.git /tmp/gateway` (public repo, no token). GitHub Actions does **not** hand skills to an agent; the clone is the mechanism. To make agents find the gateway automatically, put `.agent/TARGET_REPO_AGENTS.md` in each target repo as `AGENTS.md`.

**No bash or git?** An agent that only has an HTTP tool follows `.agent/HTTP_ONLY.md`: it reads the gateway files through `raw.githubusercontent.com` and does clone/commit/push/PR/build/report through the GitHub REST API. `.agent/HTTP_ONLY.md` is also copied into every app created from the template, which is where the target repo's `AGENTS.md` sends such an agent.

Example task from a phone: *"In repo X add a dark-mode toggle to settings."* The agent clones the gateway, runs `orient.sh` on X, reads X's `.agent/`, reads `design/DESIGN.md`, implements on a branch, opens a PR, and reports the PR link plus the APK artifact from the CI run.

## 6. Connect another Flutter repository
**New apps:** do not copy anything by hand. Create the repository from the public template [Flutter-App-Template](https://github.com/moamenessamseja-web/Flutter-App-Template) (it already contains the caller workflow with a pinned Flutter version, `AGENTS.md` and a minimal app); `.agent/RUN.md` has the exact commands. **Existing apps:**
1. Make sure this repository's workflow is usable: it is public, so nothing to enable. (If it becomes private: *Settings -> Actions -> General -> Access* -> allow access from your other repositories.)
2. In the app repository add `.github/workflows/build-apk.yml` as an unchanged copy of the ready file `.agent/templates/build-apk.yml` (section 7). The name `build-apk.yml` matters: `engineer-in-charge/scripts/gh_ci.sh push-run` dispatches that file by default.
3. Commit `pubspec.lock` (the pub cache key uses its hash).
4. Optional: copy the block of `.agent/TARGET_REPO_AGENTS.md` (between the `---` lines) into the repo as `AGENTS.md`, and `.agent/HTTP_ONLY.md` to the repo's `.agent/HTTP_ONLY.md` (the `AGENTS.md` block refers to it).

## 7. Caller workflow
The ready file is [`.agent/templates/build-apk.yml`](.agent/templates/build-apk.yml); copy it unchanged (it is the single source, this README does not repeat its content). It triggers on pull requests, pushes to `main` and manual dispatch, pins `flutter_version: "3.47.9"`, builds `release`, passes `--org com.moamen` to the scaffold, and passes no secrets because the workflow uses none. Fetch it with, for example:
```bash
curl -fsSL https://raw.githubusercontent.com/moamenessamseja-web/Flutter-Android-Build/main/.agent/templates/build-apk.yml -o .github/workflows/build-apk.yml
```
The app repositories created from `Flutter-App-Template` already contain the same file; when the ready file changes, update the template's copy too.

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
| `fixed_debug_keystore` [true] | Sign with one fixed, public debug key so every APK has the same signature (see section 7a) |
| `gradle_cache_read_only` [false] | See caching |
| `timeout_minutes` [30] | Job timeout |

Outputs: `artifact_name`, `flutter_version` (version actually used), `signer_sha256` (fingerprint of the signing certificate).

Every run also publishes an `APK ready` annotation and summary with the built commit, the package name (applicationId), size, APK SHA-256 and signing fingerprint; a mismatch with the fixed key raises a warning. The annotation is readable through the API (`check-runs/<job>/annotations`), no artifact download needed.

`flutter create` is run with `--project-name` taken from `pubspec.yaml`, because it would otherwise use the checkout directory (the repository name, which can contain hyphens that are not valid in a Dart package name). The generated `analysis_options.yaml` is discarded when the app has none of its own.

Release-mode APKs use whatever signing the app's Android project defines (Flutter's default template signs with the debug key). Production signing is not part of this workflow.

### 7a. Signing
Debug-signed APKs (debug mode, and release mode until an app defines real release signing) are signed with one shared key stored in the workflow (alias `androiddebugkey`, password `android`, certificate SHA-256 `136966601854d1bd1397841d7d5ef10f1145bd8ac71c49f8ac6812857f136233`). Without it each CI run generates a random debug key and Android refuses to install a build over the previous one. The key is public and shared between all your apps: fine for testing on your own phone, not for publishing (anyone could sign an update to your sideloaded app). Gradle ignored `~/.android/debug.keystore` on the runner (measured: three different fingerprints in three runs), so the key is injected through the `android.injected.signing.*` Gradle properties. Real release signing (a private key in repository secrets) is a later step; set `fixed_debug_keystore: false` when an app brings its own signing config.

## 8. Caching
- **Flutter SDK + pub cache:** `subosito/flutter-action@v2` with `cache: true` and `pub-cache: true`. The SDK cache key follows channel/version/architecture; the pub cache key additionally appends the hash of `pubspec.lock`. With an unpinned version the SDK cache changes whenever a new release appears.
- **Gradle:** `gradle/actions/setup-gradle@v6` caches `~/.gradle`. Its own default is read-only on branches other than the default branch; this workflow sets `cache-read-only: false` so feature-branch/PR builds also save a cache. Set `gradle_cache_read_only: true` to stop that.
- GitHub scoping: a branch can read caches from itself and the default branch, not from sibling branches. The limit is 10 GB **per repository** (each app repository has its own, they do not compete), and unused entries expire after 7 days, so the first build of a new repository, or after a quiet week, is cold (about 6 minutes instead of 2-3).
- Check the "Post ..." steps and the Gradle job summary of a run to see hits/misses.

## 9. Branches, commits, Pull Requests
Agents work on a dedicated branch (e.g. `agent/<short-task>`), one concern per commit, never on the default branch. Push the branch, open a PR; the caller's `pull_request` trigger builds it through this workflow. The default branch only receives what the owner has tested on a device. Details: `engineer-in-charge/SKILL.md` section 4 and `flutter-ci-engineering/SKILL.md` section 3/8.

## 10. Permissions and secrets
See `.agent/ACCESS.md`. In short:
- Agent token (fine-grained PAT, or whatever the agent platform stores as `AGENT_CLOUD_SONNET`): Contents RW, Pull requests RW, Actions RW, Metadata R on the target repos. An Actions secret is only visible to workflow runs, not to an external agent.
- Caller workflow: `permissions: contents: read` is enough.
- The caller passes no secrets (the workflow uses none). `secrets: inherit` would forward the caller repo's secrets only, never this repository's.
- Never print or commit tokens.

## 11. Troubleshooting
Every failed run publishes a step summary with the tail of each log and an artifact `ci-logs` (pub-get, flutter-create, pre-build, analyze, test, build logs).

Download from a phone: open the run page in the browser and tap the artifact. From an agent:
```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/artifacts"
curl -sL -o logs.zip -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO/actions/artifacts/ARTIFACT_ID/zip"
```
`engineer-in-charge/scripts/gh_ci.sh` (the single copy; the duplicate in `flutter-ci-engineering` was removed): `wait` waits for the run of your HEAD commit (`EXPECT_SHA` overrides it), so a stale green run is never reported; `result <branch>` prints the failure tail or the `APK ready` annotation and the artifacts. Its `log`, `notes` and `download` commands read release assets that this workflow does not create, so they only apply to release-based legacy pipelines.

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
Verified on GitHub Actions:
- Reusable workflow built the smoke app (debug) and a template-generated app (release, 42 MB), including generating `android/`, analyze, test, APK upload, failure diagnostics (annotation + `ci-logs` artifact).
- **Cross-repository call:** a repository generated from the template (name with hyphens) called this workflow from another repository, built green, and reported `package=com.moamen.<pubspec name>`.
- **Stable signing:** three consecutive runs produced the same certificate fingerprint (and, for the same commit, a bit-identical APK).
- Cache effect on the same ref: cold 5 min 48 s, warm 2 min 16 s.
- `actionlint` 1.7.12 with shellcheck; gateway scripts run on a scratch repository; `gh_ci.sh wait`/`result` work against a template-generated repository.

- **HTTP-only path:** every step of `.agent/HTTP_ONLY.md` sections 8, 1a, 2, 1, 3, 4, 5, 6 and 7 was executed with REST calls only (no git): repository generated from the template, single-file commit, multi-file Git Data commit, pull request, build matched by `head_sha`, annotations and artifact listing. The build that went green was exactly the commit written through the API, with `package=com.moamen.http_test`.

Not verified: installing the APK on a device (the owner does that), release signing with a private key, and apps with native plugins that need Android changes (use `pre_build_command`). Also not verified: downloading the artifact zip through the redirect (my sandbox cannot reach the blob host) and the unchanged bash/git path for the three skills' scripts beyond `init_agent.py`, `orient.sh`, `agent_audit.py` and `gh_ci.sh wait`.

Lessons from the real runs that are built into the workflow: `flutter create` generates an `analysis_options.yaml` referencing `flutter_lints` (analysis failed) and takes the project name from the directory; Gradle ignored the default debug keystore location; the Flutter SDK cache is about 1.6 GB and the Gradle cache about 1.3 GB per repository. GitHub announced that `ubuntu-latest` moves to Ubuntu 26 from 19 Oct 2026; Java is installed by the workflow, so this should be harmless.
