"""Restart the head-to-head batch with the new order and width: stop the running batch script and its own games by PID,
remove the unfinished game folders it leaves, start it again detached. Also report whether the online queue runner is alive."""
import os, signal, subprocess, time, glob, shutil
T = '~/.claude/jobs/e2109d93/tmp'
out = subprocess.run(['ps', '-Ao', 'pid=,ppid=,command='], capture_output=True, text=True).stdout.splitlines()
procs = {}
for line in out:
    a = line.split(None, 2)
    if len(a) == 3:
        procs[int(a[0])] = (int(a[1]), a[2])
roots = [p for p, (pp, c) in procs.items() if c.startswith('zsh ' + T + '/h2h15.zsh')]
kids = {}
for p, (pp, c) in procs.items():
    kids.setdefault(pp, []).append(p)
seen, todo = set(), list(roots)
while todo:
    x = todo.pop()
    if x in seen:
        continue
    seen.add(x)
    todo.extend(kids.get(x, []))
for sig in (signal.SIGTERM, signal.SIGKILL):
    for p in seen:
        try:
            os.kill(p, sig)
        except ProcessLookupError:
            pass
    time.sleep(2)
print('stopped', len(seen), 'processes')
gone = 0
for arm in ('mHid8', 'mQsn4'):
    for d in glob.glob(os.path.expanduser('~/meow-redteam/solo/runs/h2h_%s_v14/*/' % arm)):
        if not os.path.exists(d + 'result.txt'):
            shutil.rmtree(d)
            gone += 1
print('unfinished folders removed', gone)
subprocess.Popen('nohup zsh %s/h2h15.zsh mQsn4 > %s/h2h15.out 2>&1 &' % (T, T), shell=True)
time.sleep(2)
print('queue runner alive:', subprocess.run(['pgrep', '-fl', 'at-q.sh'], capture_output=True, text=True).stdout.strip()[:80] or 'NO')
