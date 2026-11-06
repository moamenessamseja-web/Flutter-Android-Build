# Android scaffolding that is generated on every CI run

Applies when `android/` is not committed and the workflow runs `flutter create --platforms=android` each build
(true for Manager Assistant). Any native change must be injected by the workflow, because hand-edited files vanish.

- Make injections idempotent: guard each with `grep -q` so a re-run never duplicates content.
- `<uses-permission>` goes inside `<manifest>`: anchor on `/<manifest /a\...` (single-line tag in Flutter's template).
- `<receiver>`/`<service>` goes inside `<application>`: do NOT anchor on `<application` (multi-line tag; inserting after it lands mid-attribute
  list and corrupts XML). Anchor on the line that closes it (currently `android:icon="@mipmap/ic_launcher">`).
- Before trusting an anchor, fetch the real template and test the exact `sed` locally, then validate with
  `python3 -c "import xml.dom.minidom as m; m.parse('test.xml')"`:
  `https://raw.githubusercontent.com/flutter/flutter/master/packages/flutter_tools/templates/app/android.tmpl/app/src/main/AndroidManifest.xml.tmpl`
  (relocate with the GitHub contents/search API if the path moved).
- Need a custom native class? First check whether a plugin already in `pubspec.yaml` ships it. Precedent: `flutter_local_notifications`
  already ships the boot receiver; the fix was two manifest entries, no new dependency, no second scheduling architecture.
- If a real architectural decision is still needed after that check: stop, document the blocker + evidence, offer 1–2 smallest options,
  let the owner decide.
- Notification sound: an Android channel's sound is immutable after creation; a different sound needs a new channel id + a `res/raw` file
  (injected by CI). Not implemented in Manager Assistant.
