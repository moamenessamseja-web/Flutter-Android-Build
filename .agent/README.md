# Central agent gateway

Reusable engineering rules, skills and CI for all of the owner's repositories (mainly Flutter/Android).
**This folder holds instructions only.** Project state (`IMPLEMENTATION_STATE`, `HANDOFF`, `CHANGELOG`, ...) lives in each *target* repository's own `.agent/` folder, created from the templates below. Never put project state, tokens or app data here.

**No bash/git in your harness?** Follow `HTTP_ONLY.md` (this folder) for every git/shell step below; everything else (read the skills, inspect the target, branch + PR, report) is unchanged.

## The path every agent follows
1. **Get this repository** (public, no token needed): `git clone --depth 1 https://github.com/moamenessamseja-web/Flutter-Android-Build.git /tmp/gateway`. Below, `$GW=/tmp/gateway`. (Details and alternatives: `ACCESS.md`.)
2. **Read this file**, then `ACCESS.md` if you must push/open PRs/dispatch workflows.
3. **Read the Engineering in Charge skill first and fully:** `$GW/.skills/engineer-in-charge/SKILL.md` (then the references it points to, only as deep as the task needs). It defines how you work; do not re-derive its conclusions.
4. **Pick the other skills** from the table below.
5. **Inspect the target repository** before changing anything. Never assume it is a standard Flutter project or that it shares another project's architecture.
   Start gate: `bash $GW/.skills/engineer-in-charge/scripts/orient.sh <target-repo-dir>`.
   No `.agent/` there yet? `python3 $GW/.skills/engineer-in-charge/scripts/init_agent.py --project "<name>" --stack "Flutter/Android" --repo <target-repo-dir>` (copies the templates, never overwrites existing files), then fill `BRIEF.md` with the owner's words verbatim.
6. **Implement** in small verified steps on a branch (never on the default branch).
7. **Deliver** (full recipe in `RUN.md`): commit -> push branch -> open a Pull Request -> the target's caller workflow builds the APK through the central reusable workflow -> report PR link, run result, artifact name, and what is NOT verified.
   Stop gate before reporting: `python3 $GW/.skills/engineer-in-charge/scripts/stop_gate.py` (run inside the target repo) must print `HANDOFF OK`.

## Skills and when to activate each
| Skill (folder under `.skills/`) | Activate when | Entry file |
|---|---|---|
| `engineer-in-charge` | **Always, at the start of any task** on any code project; also when work loops, is unverified, or "looks done but doesn't work". | `SKILL.md` |
| `flutter-ci-engineering` | Flutter/Android work where builds happen on GitHub Actions (no local SDK): APK builds, CI failures, black-screen/dependency drift, handoff/state files. | `SKILL.md` |
| `design` | Any UI, theme, screen or visual-identity work in a Flutter app. | `SKILL.md` -> `DESIGN.md` |

Notes on `flutter-ci-engineering`: its `references/manager-assistant.md` contains facts about one specific project (`manager-assistant-ready`); use it only for that repository. Its scripts assume a caller workflow named `build-apk.yml` (see README "Connect another Flutter repository") and read failure logs from a `debug-<n>` release asset; the central workflow instead uploads an `ci-logs` artifact on failure (see README "Troubleshooting").

## Where things are
| What | Path |
|---|---|
| `.agent/` file templates (single source of truth) | `.skills/engineer-in-charge/assets/agent-templates/` |
| Start/stop gates, audit, loop guard, CI helper | `.skills/engineer-in-charge/scripts/` and `.skills/flutter-ci-engineering/scripts/` |
| Reusable Flutter Android build | `.github/workflows/flutter-android-build.yml` |
| Workflow self-test (builds `fixtures/smoke_app`) | `.github/workflows/smoke-test.yml` |
| Snippet to put in a target repo so agents find this gateway | `.agent/TARGET_REPO_AGENTS.md` |
| Idea -> new repo -> green build -> report (the recipe) | `.agent/RUN.md` |
| Same, for harnesses with no bash/git (GitHub REST API only) | `.agent/HTTP_ONLY.md` |
| Ready caller workflow to copy into an app repo | `.agent/templates/build-apk.yml` |
| Template repository for new apps | https://github.com/moamenessamseja-web/Flutter-App-Template |
| Authentication and access | `.agent/ACCESS.md` |
| Human manual | `README.md` |

The templates are deliberately not copied into this folder: `init_agent.py` reads them from the skill, and a second copy would drift.

## Non-negotiables (from the skills)
Never claim verification that did not happen (read < sanity < CI green < artifact inspected < owner's device) · secrets never in files, URLs, logs or commits · one concern per commit, work on branches, never force-push the default branch · reuse before rebuild · decide routine technical questions yourself and report; ask the owner only for product, identity or irreversible decisions.
