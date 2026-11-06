# Project facts — Manager Assistant (مساعد الإدارة)

Use only for this repo; the method in SKILL.md is general.

- Repo: `moamenessamseja-web/manager-assistant-ready`. Flutter app, Arabic-first (Egyptian dialect), offline-first, local storage
  (`shared_preferences`), optional Gemini (never required), local notifications, `speech_to_text`.
- Owner: Arabic speaker, non-developer; exhausted by very long contexts and usage limits ⇒ wants visible progress, short reports,
  no re-discovery. Gives tokens in chat: use them via header only, never write them anywhere, remind once to revoke.
- Memory files (the project's real memory — read first, update last): `.agent/IMPLEMENTATION_STATE.md`, `HANDOFF.md`, `CHANGELOG.md`,
  `implementation.md` (inventory + roadmap + verification log), `.agent/mission_2026-10-16.md` (mission brief, do not edit),
  `.agent/ARCHITECTURE_AUDIT.md`, `.agent/VERIFICATION_REPORT.md`. Product master lives in the Claude Project (`master_light.md`).
- Anchors: `32df13f` = Build 75 = owner-designated baseline (tag `baseline-build-75-user-confirmed`). `25dbffe` = Build 76 = broken (black
  screen; tag `build-76-untrusted`); `main` may still point at it until the owner device-confirms a newer build. Work branch:
  `phase-b/from-32df13f`. Build 78 (startup fix) device-confirmed by the owner.
- CI: `.github/workflows/build-apk.yml`. `workflow_dispatch` on a branch = verification build without touching `main`. Success → release
  `build-<run>` with `app-release.apk` (+ toolchain in notes). Failure → release `debug-<run>` with `build_log_tail.txt`. ~7 min per run.
  Steps: flutter pinned (3.47.7) → pub get → plugin-drift guard → analyze (`--no-fatal-infos`, warnings fatal) →
  `flutter test --exclude-tags live` → release APK. `android/` regenerated each run (see references/android-ci-injection.md).
- Product rules that shaped code (spec: `master_light.md`): offline-first; one source of truth; never guess (ask: value / day / hour);
  no false success; idempotent operations; expected delivery ≠ received purchase; Gemini optional and validated; Brief/reports/PDF deferred.
- Key code: `lib/services/local_command_parser.dart` (offline parser, `extractSlots`), `assistant_controller.dart` (dispatch, pending
  clarification, `_missingFor`, duplicate guard), `storage_service.dart`, `reminder_service.dart`, `notification_prefs.dart`,
  `screens/memory_lists.dart`, `screens/notification_settings_screen.dart`, `main.dart` (guarded startup).
- Open decisions for the owner: final application id (not `com.example`), fixed upload keystore, when to merge the branch into `main`.
