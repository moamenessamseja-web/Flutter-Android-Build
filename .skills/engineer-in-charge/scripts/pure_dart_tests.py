#!/usr/bin/env python3
"""Run the PURE-Dart tests of a Flutter project without a Flutter SDK (sanity level, not CI).

Why: CI is the only place Flutter code compiles when the authoring sandbox has no Flutter SDK, and every CI round trip
costs minutes. Logic kept free of Flutter imports (lib/domain, planners, parsers, string tables) can be tested before the push.

How: downloads a plain Dart SDK from conda-forge once (cached), classifies every test/**/*_test.dart as pure or not
(a test is pure when it and every project file it imports use only dart:*, the project itself and package:flutter_test,
and it does not use testWidgets), maps `package:flutter_test` to a tiny stand-in (async-aware test/group/expect + common
matchers) and runs the pure ones. `dart analyze` does NOT work in that SDK (analyzer snapshots are stripped): this checks
compilation and behaviour of the pure files only. Flutter widgets/plugins are still verified by CI.

Usage: python3 pure_dart_tests.py [--list] [project_dir]      (needs network to conda.anaconda.org the first time)
Env:   DART_SDK=/path/to/dart-sdk  to use an existing SDK;  GATEWAY_CACHE=dir to change the cache (default ~/.cache/gateway)
"""
import io, json, os, re, shutil, subprocess, sys, tarfile, tempfile, urllib.request, zipfile

CACHE = os.environ.get("GATEWAY_CACHE", os.path.expanduser("~/.cache/gateway"))

SHIM = r'''// Minimal stand-in for package:flutter_test (pure-Dart tests only).
import 'dart:io';

class Matcher {
  Matcher(this.description, this.test);
  final String description;
  final bool Function(Object? actual) test;
}

Matcher equals(Object? expected) => Matcher('equals $expected', (a) => a == expected);
final Matcher isNull = Matcher('null', (a) => a == null);
final Matcher isNotNull = Matcher('not null', (a) => a != null);
final Matcher isTrue = Matcher('true', (a) => a == true);
final Matcher isFalse = Matcher('false', (a) => a == false);
final Matcher isEmpty = Matcher('empty', (a) => (a as dynamic).isEmpty == true);
final Matcher isNotEmpty = Matcher('not empty', (a) => (a as dynamic).isNotEmpty == true);
Matcher closeTo(num value, num delta) => Matcher('close to $value +-$delta', (a) => a is num && (a - value).abs() <= delta);
Matcher contains(Object? element) => Matcher('contains $element', (a) {
      if (a is String && element is String) return a.contains(element);
      if (a is Iterable) return a.contains(element);
      if (a is Map) return a.containsKey(element);
      return false;
    });
Matcher hasLength(int n) => Matcher('has length $n', (a) => (a as dynamic).length == n);
Matcher isA<T>() => Matcher('is a $T', (a) => a is T);
Matcher greaterThan(num n) => Matcher('> $n', (a) => a is num && a > n);
Matcher lessThan(num n) => Matcher('< $n', (a) => a is num && a < n);

int _passed = 0, _failed = 0;
String _prefix = '';
final List<Future<void> Function()> _queue = [];

void group(String name, void Function() body) {
  final old = _prefix;
  _prefix = '$old$name > ';
  body();
  _prefix = old;
}

void test(String name, dynamic Function() body) {
  final label = '$_prefix$name';
  _queue.add(() async {
    try {
      await body();
      _passed++;
    } catch (e) {
      _failed++;
      stdout.writeln('FAIL  $label\n      $e');
    }
  });
}

void setUp(dynamic Function() body) {}
void tearDown(dynamic Function() body) {}
void addTearDown(dynamic Function() body) {}

void expect(Object? actual, Object? matcher) {
  final m = matcher is Matcher ? matcher : equals(matcher);
  if (!m.test(actual)) throw 'expected ${m.description}, got $actual';
}

Future<void> finish() async {
  for (final t in _queue) {
    await t();
  }
  stdout.writeln('passed: $_passed, failed: $_failed');
  if (_failed > 0) exitCode = 1;
}
'''

IMPORT = re.compile(r"""^\s*(?:import|export)\s+['"]([^'"]+)['"]""", re.M)


def log(msg):
    print(msg, flush=True)


def find_dart():
    env = os.environ.get("DART_SDK")
    if env and os.path.exists(os.path.join(env, "bin", "dart")):
        return os.path.join(env, "bin", "dart")
    cached = os.path.join(CACHE, "dart-sdk", "bin", "dart")
    if os.path.exists(cached):
        return cached
    w = shutil.which("dart")
    if w:
        return w
    return download_dart()


def download_dart():
    try:
        import zstandard
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "zstandard"])
        import zstandard
    os.makedirs(CACHE, exist_ok=True)
    log("downloading the conda-forge package index (one time, ~90 MB)...")
    with urllib.request.urlopen("https://conda.anaconda.org/conda-forge/linux-64/current_repodata.json", timeout=300) as r:
        repo = json.load(r)
    pk = {**repo.get("packages", {}), **repo.get("packages.conda", {})}
    cands = sorted((v["version"], k) for k, v in pk.items() if v["name"] == "dart-sdk")
    if not cands:
        sys.exit("no dart-sdk package found in conda-forge/linux-64")
    fname = cands[-1][1]
    log(f"downloading {fname} (~230 MB)...")
    data = urllib.request.urlopen(f"https://conda.anaconda.org/conda-forge/linux-64/{fname}", timeout=600).read()
    z = zipfile.ZipFile(io.BytesIO(data))
    inner = [n for n in z.namelist() if n.startswith("pkg-") and n.endswith(".tar.zst")][0]
    stream = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(z.read(inner)))
    tmp = os.path.join(CACHE, "dart-sdk-tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tarfile.open(fileobj=stream, mode="r|").extractall(tmp)
    shutil.rmtree(os.path.join(CACHE, "dart-sdk"), ignore_errors=True)
    shutil.move(tmp, os.path.join(CACHE, "dart-sdk"))
    for root, _, files in os.walk(os.path.join(CACHE, "dart-sdk", "bin")):
        for f in files:
            os.chmod(os.path.join(root, f), 0o755)
    return os.path.join(CACHE, "dart-sdk", "bin", "dart")


def package_name(project):
    text = open(os.path.join(project, "pubspec.yaml"), encoding="utf-8").read()
    m = re.search(r"^name:\s*([A-Za-z0-9_]+)", text, re.M)
    if not m:
        sys.exit("pubspec.yaml has no name")
    return m.group(1)


def classify(project, pkg, test_file):
    """Returns (is_pure, reason)."""
    seen, stack = set(), [test_file]
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        try:
            text = open(f, encoding="utf-8").read()
        except OSError:
            return False, f"cannot read {os.path.relpath(f, project)}"
        if "testWidgets(" in text:
            return False, "uses testWidgets"
        for imp in IMPORT.findall(text):
            if imp.startswith("dart:"):
                if imp in ("dart:ui", "dart:html"):
                    return False, f"imports {imp}"
                continue
            if imp.startswith("package:"):
                name, _, rest = imp[len("package:"):].partition("/")
                if name == pkg:
                    stack.append(os.path.join(project, "lib", rest))
                elif name == "flutter_test":
                    continue
                else:
                    return False, f"{os.path.relpath(f, project)} imports package:{name}"
            else:
                stack.append(os.path.normpath(os.path.join(os.path.dirname(f), imp)))
    return True, ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    list_only = "--list" in sys.argv
    project = os.path.abspath(args[0] if args else ".")
    pkg = package_name(project)
    tests = []
    for root, _, files in os.walk(os.path.join(project, "test")):
        tests += [os.path.join(root, f) for f in files if f.endswith("_test.dart")]
    tests.sort()
    pure, skipped = [], []
    for t in tests:
        ok, why = classify(project, pkg, t)
        (pure if ok else skipped).append((t, why))
    for t, _ in pure:
        log(f"PURE      {os.path.relpath(t, project)}")
    for t, why in skipped:
        log(f"skipped   {os.path.relpath(t, project)}  ({why}; verified by CI only)")
    if list_only or not pure:
        return 0
    dart = find_dart()
    work = tempfile.mkdtemp(prefix="pure_dart_")
    os.makedirs(os.path.join(work, "shim", "lib"))
    open(os.path.join(work, "shim", "lib", "flutter_test.dart"), "w").write(SHIM)
    cfg = {"configVersion": 2, "packages": [
        {"name": pkg, "rootUri": "file://" + project + "/", "packageUri": "lib/", "languageVersion": "3.0"},
        {"name": "flutter_test", "rootUri": "file://" + os.path.join(work, "shim") + "/", "packageUri": "lib/", "languageVersion": "3.0"}]}
    os.makedirs(os.path.join(work, ".dart_tool"))
    cfg_path = os.path.join(work, ".dart_tool", "package_config.json")
    json.dump(cfg, open(cfg_path, "w"))
    lines = ["import 'package:flutter_test/flutter_test.dart' as shim;"]
    calls = []
    for i, (t, _) in enumerate(pure):
        lines.append(f"import 'file://{t}' as t{i};")
        calls.append(f"t{i}.main();")
    lines.append("void main() { " + " ".join(calls) + " shim.finish(); }")
    open(os.path.join(work, "runner.dart"), "w").write("\n".join(lines) + "\n")
    env = dict(os.environ, HOME=work)
    r = subprocess.run([dart, "run", f"--packages={cfg_path}", "runner.dart"], cwd=work, env=env, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    out = [l for l in out if "pub.dev" not in l]   # `dart run` tries to resolve a pubspec it does not need
    print("\n".join(out))
    shutil.rmtree(work, ignore_errors=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
