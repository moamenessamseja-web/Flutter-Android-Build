#!/usr/bin/env python3
"""Compare two APKs without a device - used to prove WHAT changed between a working and a broken build.
Usage: apk_compare.py A.apk B.apk [--probe STRING ...]
Prints sizes, hashes of engine/manifest/resources/dex, Dart AOT (libapp.so) readable-identifier diff, and
whether each --probe string (e.g. 'SharedPreferencesApiForNativeInterop') exists in each libapp.so.
Same libflutter.so hash = same Flutter engine. Same size + empty identifier diff = same Dart code+deps."""
import hashlib, re, sys, zipfile
a, b = sys.argv[1], sys.argv[2]
probes = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == '--probe' and i + 1 < len(sys.argv)]
ABI = 'lib/arm64-v8a/'
def info(p):
    z = zipfile.ZipFile(p); r = {'size': len(open(p, 'rb').read())}
    for n in ('AndroidManifest.xml', 'resources.arsc', 'classes.dex', ABI + 'libflutter.so', ABI + 'libapp.so'):
        try: r[n] = hashlib.md5(z.read(n)).hexdigest()[:8]
        except KeyError: r[n] = '-'
    app = z.read(ABI + 'libapp.so') if ABI + 'libapp.so' in z.namelist() else b''
    r['ids'] = set(m.decode() for m in re.findall(rb'[A-Za-z_][A-Za-z0-9_:/.]{7,}', app))
    r['app'] = app; return r
x, y = info(a), info(b)
for k in ('size', 'AndroidManifest.xml', 'resources.arsc', 'classes.dex', ABI + 'libflutter.so', ABI + 'libapp.so'):
    print(f"{k:34} {x[k]!s:>12} {y[k]!s:>12} {'same' if x[k]==y[k] else 'DIFF'}")
only_a, only_b = sorted(x['ids'] - y['ids']), sorted(y['ids'] - x['ids'])
print(f"identifiers only in A: {len(only_a)}, only in B: {len(only_b)}")
for t, L in (('A', only_a), ('B', only_b)):
    for s in L[:15]: print(f"  only {t}: {s}")
for p in probes:
    print(f"probe {p!r}: A={p.encode() in x['app']} B={p.encode() in y['app']}")
