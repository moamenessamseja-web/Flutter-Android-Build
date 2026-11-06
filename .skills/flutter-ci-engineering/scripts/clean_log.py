#!/usr/bin/env python3
"""Make a CI log readable with minimal tokens.
Usage: clean_log.py <file> [tail_lines=60]
Strips ANSI/control characters (test runners embed them - printing raw can crash the tool with 'not valid UTF-8'),
drops Dart analyzer 'info' lines (non-fatal under --no-fatal-infos), prints error/warning/test-failure lines
first, then the tail. Warnings ARE fatal for `flutter analyze --no-fatal-infos` - look for ' warning • '."""
import re, sys
path = sys.argv[1]; tail = int(sys.argv[2]) if len(sys.argv) > 2 else 60
b = open(path, 'rb').read().decode('utf-8', 'replace')
b = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', b)
b = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '\n', b)
lines = [l.rstrip() for l in b.split('\n') if l.strip()]
body = [l for l in lines if not re.match(r'^\s+info\b', l)]
key = [l for l in body if re.search(r'(^\s+(error|warning)\b)|\[E\]|Expected:|Actual:|FAILED|Some tests failed|Error:|Exception', l)]
print(f"{len(lines)} lines ({len(lines)-len(body)} analyzer infos hidden)")
if key:
    print("--- key lines ---")
    for l in key[:40]: print(l[:240])
print("--- tail ---")
for l in body[-tail:]: print(l[:240])
