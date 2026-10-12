#!/usr/bin/env python3
"""Run a heavy pass under nice 15 after checking memory_pressure and disk.

One extraction worker is used by extract.js; never more than two workers.
exit 75 = resource pause, rerun only after a fresh successful check.
"""
import re
import subprocess
import sys

p = subprocess.run(['memory_pressure'], text=True, capture_output=True, check=True)
d = subprocess.run(['df', '-g', '/'], text=True, capture_output=True, check=True)
memory = re.search(r'System-wide memory free percentage:\s*(\d+)%', p.stdout)
disk = int(d.stdout.splitlines()[-1].split()[3])
if not memory:
    raise SystemExit('Cannot verify memory pressure; pausing.')
free = int(memory.group(1))
print(f'Guard: memory free {free}%; disk available {disk} GB', flush=True)
if free < 10 or disk < 20:
    raise SystemExit(75)
raise SystemExit(subprocess.call(['nice', '-n', '15', *sys.argv[1:]]))
