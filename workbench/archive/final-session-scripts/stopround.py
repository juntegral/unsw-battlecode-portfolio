"""Stop the game-analysis loop and every job of its round 1055 (it fanned out over the whole backlog and overloaded the machine).
Kills by PID: the loop, its round runner, each Codex job of that round, and their descendants. Nothing else."""
import os, signal, subprocess, time
me = os.getpid()
out = subprocess.run(['ps', '-Ao', 'pid=,ppid=,command='], capture_output=True, text=True).stdout.splitlines()
procs = {}
for line in out:
    parts = line.split(None, 2)
    if len(parts) < 3:
        continue
    procs[int(parts[0])] = (int(parts[1]), parts[2])
anc = set()
p = me
while p in procs:
    anc.add(p)
    p = procs[p][0]
keys = ('sweep/1055', 'sweep-1055', 'tools/sweep_loop.sh', 'sweep_games.py')
roots = {pid for pid, (pp, cmd) in procs.items() if any(k in cmd for k in keys) and pid not in anc}
kids = {}
for pid, (pp, cmd) in procs.items():
    kids.setdefault(pp, []).append(pid)
todo, seen = list(roots), set()
while todo:
    x = todo.pop()
    if x in seen or x in anc:
        continue
    seen.add(x)
    todo.extend(kids.get(x, []))
print('roots', len(roots), 'with descendants', len(seen))
for sig in (signal.SIGTERM, signal.SIGKILL):
    for pid in seen:
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
    time.sleep(3)
left = subprocess.run(['pgrep', '-f', 'sweep/1055|sweep-1055|sweep_loop.sh'], capture_output=True, text=True).stdout.split()
print('left', len([x for x in left if int(x) != me]))
print(subprocess.run(['uptime'], capture_output=True, text=True).stdout.strip()[-40:])
print('codex exec jobs alive:', subprocess.run(['pgrep', '-fl', 'codex exec -m'], capture_output=True, text=True).stdout.count('\n'))
