"""killtree.py <command prefix> : stop every process whose command line starts with the prefix, and its descendants, by PID."""
import os, signal, subprocess, sys, time
pre = sys.argv[1]
out = subprocess.run(['ps', '-Ao', 'pid=,ppid=,command='], capture_output=True, text=True).stdout.splitlines()
procs = {}
for line in out:
    a = line.split(None, 2)
    if len(a) == 3:
        procs[int(a[0])] = (int(a[1]), a[2])
me = os.getpid()
roots = [p for p, (pp, c) in procs.items() if c.startswith(pre) and p != me]
kids = {}
for p, (pp, c) in procs.items():
    kids.setdefault(pp, []).append(p)
seen, todo = set(), list(roots)
while todo:
    x = todo.pop()
    if x not in seen:
        seen.add(x); todo.extend(kids.get(x, []))
for sig in (signal.SIGTERM, signal.SIGKILL):
    for p in seen:
        try: os.kill(p, sig)
        except ProcessLookupError: pass
    time.sleep(2)
print('roots', len(roots), 'stopped', len(seen))
