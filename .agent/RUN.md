# Delivery recipe: from an app idea to a green build with an APK

Use this when the owner gives an app idea or a change request. It is the sequence the owner expects; the rules behind it are in the Engineering in Charge skill. Variables: `OWNER=moamenessamseja-web`, `APP=<repo name>`, `GW=/tmp/gateway` (see `README.md`), `GH_TOKEN` in the environment (never in files, URLs or logs; see `ACCESS.md`).

No bash/git in your harness? Do the clone/commit/push/PR/build/report parts through the GitHub REST API as described in `HTTP_ONLY.md`; the order and the report format here still apply.

Auth for git, without storing the token: `AUTH="Authorization: Basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)"` then `git -c http.extraheader="$AUTH" <push|fetch|clone ...>`.

## A. New app (a new repository from the template)
1. Pick `APP` (lowercase, hyphens are fine) and the Dart package name for `pubspec.yaml` (`snake_case`). **The package name becomes the applicationId `com.moamen.<name>`; it cannot change after the first install on the phone.** Choose it from the idea and tell the owner.
2. Create the repository (public) from the template:
   `curl -s -X POST -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/$OWNER/Flutter-App-Template/generate -d '{"owner":"'$OWNER'","name":"'$APP'","private":false}'`
   Wait a few seconds, then clone it with the `AUTH` header.
3. Work inside it (section C). Existing app instead: clone it, skip to C.

## B. Existing app
Clone it, read its own `.agent/` after the gateway, inspect before changing anything.

## C. Implement, push, build
1. `bash $GW/.skills/engineer-in-charge/scripts/orient.sh .`; if there is no `.agent/`, run `init_agent.py` (README step 5) and put the owner's request verbatim in `BRIEF.md`.
2. Branch `agent/<short-task>`; small commits; never commit to `main`.
3. Keep `pubspec.yaml` dependencies pinned exactly. Design work: `design` skill.
4. Push the branch and open a Pull Request (`POST /repos/$OWNER/$APP/pulls`). The PR starts the `Build APK` workflow.
5. Wait: `REPO=$OWNER/$APP bash $GW/.skills/flutter-ci-engineering/scripts/gh_ci.sh wait <branch> 270` (exit 0 green, 1 red, 2 still running: call again). `status <branch>` shows the last runs.
   `wait` may print a harmless Python traceback while the run has not been created yet; just let it continue. Only `push-run`, `status` and `wait` of that script apply here; its `log`/`notes`/`download` expect release assets that this pipeline does not produce.
6. Red build: read the failure annotation (the tail of the failing log), fix on the same branch, push, wait again. After three failures with the same cause, stop and report (loop rule in the skill).
   ```bash
   RUN=<run id>; J=$(curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/$OWNER/$APP/actions/runs/$RUN/jobs | python3 -c "import sys,json;print(json.load(sys.stdin)['jobs'][0]['id'])")
   curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/$OWNER/$APP/check-runs/$J/annotations | python3 -c "import sys,json;[print(a['title'],'\n',a['message']) for a in json.load(sys.stdin) if a['annotation_level']=='failure']"
   ```
7. Green build: read the `APK ready` annotation the same way (`a['title']=='APK ready'`) and the artifact id: `GET /repos/$OWNER/$APP/actions/runs/$RUN/artifacts`.

## D. Report to the owner (exactly these items, short, in Arabic)
- Repository and PR links; branch name.
- **Commit SHA** that was built (the owner quotes it back when confirming the install).
- Build result and run link; the APK download place: run page -> Artifacts -> `android-apk` (link `https://github.com/$OWNER/$APP/actions/runs/$RUN`).
- The package name (applicationId) printed in the `APK ready` annotation, the file size and the signing fingerprint. The fingerprint is the same across builds, so a new APK installs over the old one without uninstalling. If it ever differs, say so: the owner must uninstall first.
- What was verified and what was not, using the verification ladder (typically: "CI green, APK built; not run on a device").
- Open questions or decisions that need the owner.

## E. After the owner's feedback
Continue on the same branch (or a new `agent/<task>` branch) and repeat C and D. Merge to `main` only when the owner says the build was tested on the phone.

## Known limits
- The APK is signed with the shared public debug key (fine for testing, not for publishing). Real release signing is a later step.
- `android/` is generated on each build, so native customisation (permissions, icon, label) needs a pre-build step; see `flutter-ci-engineering/references/android-ci-injection.md` and the `pre_build_command` input.
- Every new repository starts with a cold cache: the first build takes about 6 minutes, later ones about 2-3.
