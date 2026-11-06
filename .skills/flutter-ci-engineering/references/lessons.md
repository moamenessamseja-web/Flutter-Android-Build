# Lessons learned (evidence-based) — read when a symptom matches

Each entry: symptom → what was actually true → what to do. These come from real sessions on the Manager Assistant app.

## L1. "App opens to a black screen" after a green CI build
- Cause found: **dependency drift**, not the feature commit. `pubspec.lock` pinned `shared_preferences_android 2.4.28`, but CI built
  with `2.5.0` (new "Pigeon JNI" backend). `main()` awaited storage init with no try/catch before `runApp`, so any failure/hang = black screen.
- Proof method (no device, no logcat): build the *previous* source again on CI (controlled experiment) and compare APKs with
  `scripts/apk_compare.py`. Same size + zero identifier diff vs the broken APK ⇒ the toolchain/deps changed, not the code.
  Probe strings (`--probe SharedPreferencesApiForNativeInterop`) show which plugin path each APK contains.
- Fix pattern: `dependency_overrides` pin + CI guard step that fails if the resolved version differs + pin Flutter version +
  make `main()` render a readable error screen (with a timeout on init) instead of staying black.
- Unknown to this day: why the lock was not honoured. Say so; don't invent a reason.

## L2. Green build ≠ working app
CI proves analyze + unit/widget tests + compile. It does not prove startup, permissions, notifications, real speech input, or behavior of
anything the tests don't cover. Always list "not device-verified" items. The owner's device report is the only device evidence.

## L3. Analyzer warnings are fatal, infos are not
`flutter analyze --no-fatal-infos` failed a whole build for one unused private function (`unused_element`) left after a refactor.
Before pushing: grep that every private helper you replaced is deleted; no unused imports/locals. Infos (style) are tolerated.

## L4. A `case` grouping edit compiled fine and broke an unrelated feature
Re-grouping `switch` cases left `mark_attendance` falling into the `supplier_delivery` branch. Only an *existing* regression test caught it.
Rules: never delete/relax old tests to get green; after editing a switch, re-read the whole switch; run the old test group for neighbours.

## L5. Parsing Arabic: write patterns against the NORMALIZED text
The app normalizes before matching (ة→ه, أ/إ/آ→ا, ى→ي, ئ→ي, digits→ASCII, punctuation incl. `:` → space). So match `بكره`, `الساعه`,
`اكتوبر`, and "5:30" arrives as two tokens "5 30". Never match raw spellings. `cut`/regex on raw text is a bug source.
Safer designs that worked: token-index bookkeeping (mark tokens consumed by date/time/quantity so they can't become amount/name),
ask when ambiguous (hour 1–12 without am/pm → ask), never default a date or hour.

## L6. Dates: avoid `DateTime.add(Duration(days:n))`
Across DST it shifts the hour/day. Use `DateTime(y, m, d + n)`. Compare against `DateTime.now()` with a 1-minute tolerance.

## L7. A stale state file can lie
`.agent/IMPLEMENTATION_STATE.md` said "Phase B not started" while a commit had already implemented part of it (and broke the app).
Verify the headline claim with `git log`/Actions API before building on it, and correct the file when it's wrong. When *you* were wrong
(e.g. claiming `هيجيب` wasn't recognized — it was), write the correction in the state file, don't silently move on.

## L8. Don't trust a "Build N" label — trust the commit and the artifact
Releases created from a branch can point at the default branch HEAD (`gh release create` without `--target`). The workflow now passes
`--target "$GITHUB_SHA"` and writes the toolchain into the notes. Identify a build by SHA + APK analysis, not by name.

## L9. Per-runner debug signing
Without a fixed keystore every CI APK has a different signature; installing over an older build may be refused, and uninstalling wipes the
(local-only) app data. Warn the owner before suggesting uninstall. A fixed upload key (as a GitHub secret) is a pre-Play-Store requirement.
Also `flutter create --org com.example` ⇒ `com.example.*` application id, which Google Play rejects — an owner decision (changing it = new app).

## L10. Tool-output hazards in the sandbox
- `cut -c` is byte-based: truncating Arabic lines yields invalid UTF-8 and the tool returns NOTHING. Truncate with Python (`line[:200]`).
- Raw CI logs contain ANSI/control chars: use `scripts/clean_log.py`.
- GitHub JSON can contain control chars: strip `[\x00-\x08\x0b\x0c\x0e-\x1f]` before `json.loads`.
- `/bin/sh` here is dash: `mkdir -p a/{b,c}` creates a literal folder named `{b,c}`. Use `bash -c` or separate args.
- A single command is killed at 300 s and its output is lost: never `sleep` more than ~270 s in one call.
