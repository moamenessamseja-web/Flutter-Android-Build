# New app / new stack — first-hour checklist

Goal: the new project feels like the old environment — same memory folder, same gates, same honesty — and its first build is green before any feature work.

## 1. Orient the harness (10 min)
- [ ] Which verification path exists? **(a)** local SDK in the sandbox (run builds/tests directly) · **(b)** CI only (GitHub Actions etc.; no SDK locally) · **(c)** neither (then write
      scripts + tests that can run in the sandbox, and say plainly what can't be verified). Record the answer in `ENGINEERING_RULES.md` §3 and `BRIEF.md`.
- [ ] Can the sandbox reach what you need? Test the registry/host with one `curl -sI`; note denials.
- [ ] Owner profile: language, technical level, how they want reports. Write it in `BRIEF.md` (verbatim quotes).

## 2. Repository and memory (15 min)
- [ ] Repo exists (clone/init). Default branch protected by habit: work on a branch.
- [ ] `python3 scripts/init_agent.py --project "<name>" --stack "<stack>" --repo .` then fill: BRIEF (verbatim), STATE (baseline SHA/date), DECISIONS (anything frozen already).
- [ ] Tag the baseline: `git tag -a baseline-<date> <sha> -m "owner-designated start"`. Commit `docs: bootstrap .agent`.
- [ ] Load the stack skill if one exists (Flutter/Android-by-CI: `flutter-ci-engineering`; Office files: the docx/xlsx/pptx skills; frontend: `frontend-design`). No skill? Create
      `.agent/ENGINEERING_RULES.md` §3 "Stack facts" as you verify them, with dates.

## 3. First green build before features (20–30 min)
- [ ] Pin the toolchain version (Flutter/Node/Python/Java) — an unpinned "latest" silently changed behaviour once and cost a day.
- [ ] CI runs: format/lint → tests → build artifact. Warnings policy decided (fatal warnings, non-fatal infos is a good default). Failure logs are published as an artifact so the
      sandbox can read them (see `gh_ci.sh result`).
- [ ] Add an environment fingerprint to every build (toolchain versions, resolved key dependency versions) in the release notes — it makes later drift diagnosable.
- [ ] A smoke test that boots the app/service and a startup path that **shows an error instead of a blank screen** on failure.

## 4. Seams before features
- [ ] Put platform/IO behind small interfaces (notifications, files, network, clock) so tests can fake them.
- [ ] One storage layer with a write gate and additive schema rules; a test that re-initialises storage and reads back.
- [ ] One place for formatting/localization helpers (`money`, dates, text direction) — check before adding.

## 5. Feature order
Smallest vertical slice that crosses **entry → storage → consumer → real effect → display** first (e.g. create a reminder → saved → listed → notification scheduled). It exposes the seams while they're cheap.
Then widen. Each feature: definition of done (ENGINEERING_RULES §1), tests, docs after green.

## 6. Hand-over rhythm
Docs after every green build; stop gate before every report; owner tests the newest build; only owner-tested builds reach the default branch (tag the old one first).

## 7. Adapting this skill to the new stack
Do the work once with discipline, then capture reusable stack knowledge as `references/<stack>-lessons.md` in a stack skill (or in the project's rules) — facts with dates, symptoms with
causes, scripts for the repetitive parts. Tell the owner the skill should be updated and deliver the new version.
