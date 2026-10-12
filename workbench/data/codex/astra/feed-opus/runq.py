#!/usr/bin/env python3
import os, subprocess, threading, time, datetime
H = os.path.expanduser('~/meow-redteam')
OUT = os.path.dirname(os.path.abspath(__file__))
STOP = datetime.datetime(2026, 10, 9, 14, 8, 30)
S = 'ladder_slithery_fight_1'; I = 'ladder_islands_1'; U = 'ladder_around_unsw_1'
A = 'ladder_australia_1'; P = 'ladder_portals_1'; D = 'ladder_default_1'
jobs = []
def h2h(m, arms, sides=(0,)):
    for k in sides:
        for a in arms:
            jobs.append((a, 'mD17', m, 1, k))
def base(m, arms):
    for a in arms:
        jobs.append((a, 'm3base', m, 1, 0))
M3 = ['fd400', 'fdNo', 'fd200']
h2h(S, M3); jobs.append(('fdL', 'mD17', S, 1, 0))
h2h(S, M3, (1,)); base(S, ['fdL'])
h2h(I, M3); jobs.append(('fdL', 'mD17', I, 1, 0))
h2h(I, M3, (1,)); base(I, ['fdL'])
base(S, M3);
h2h(U, M3); jobs.append(('fdL', 'mD17', U, 1, 0))
h2h(U, M3, (1,))
h2h(S, ['fdR4'], (0, 1)); h2h(I, ['fdR4'], (0, 1))
base(I, M3)
for m in (A, P, D):
    h2h(m, M3); jobs.append(('fdL', 'mD17', m, 1, 0)); h2h(m, M3, (1,))
lock = threading.Lock()
pids = open(f'{OUT}/pids.txt', 'a')
log = open(f'{OUT}/runq.log', 'a')
def work():
    while True:
        with lock:
            if not jobs or datetime.datetime.now() > STOP:
                return
            arm, opp, m, seed, side = jobs.pop(0)
        out = f'{H}/solo/runs/fd_{arm}_{opp}/{m}-seed{seed}-side{side}'
        if os.path.exists(f'{out}/result.txt'):
            continue
        os.makedirs(out, exist_ok=True)
        a, b = f'{H}/solo/bots/{arm}', f'{H}/solo/bots/{opp}'
        if side == 1:
            a, b = b, a
        t = time.time()
        p = subprocess.Popen([f'{H}/play.sh', a, b, f'{H}/maps/ladder/{m}.map', str(seed), out],
                             stdout=open(f'{out}.log', 'w'), stderr=subprocess.STDOUT)
        with lock:
            pids.write(f'{p.pid} {out}\n'); pids.flush()
        p.wait()
        with lock:
            log.write(f'{datetime.datetime.now():%H:%M:%S} {time.time()-t:.0f}s rc={p.returncode} {out}\n'); log.flush()
ts = [threading.Thread(target=work) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
log.write('queue done\n'); log.flush()
