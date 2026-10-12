"""1) Stop the second ladder-check instance (mOrb4), which would play the live bot's games on the new maps at the same time as
the first one, and restart it with the variant that plays only its own arm. 2) Build leave-one-out arms of one14 and play
them, with one11 and one14 themselves, on the two maps where pearls did not come back (Queen Of Spades, Trophy)."""
import os, signal, subprocess, time, glob, shutil
T = '~/.claude/jobs/e2109d93/tmp'
H = os.path.expanduser('~/meow-redteam/solo')
out = subprocess.run(['ps', '-Ao', 'pid=,ppid=,command='], capture_output=True, text=True).stdout.splitlines()
procs = {}
for line in out:
    a = line.split(None, 2)
    if len(a) == 3:
        procs[int(a[0])] = (int(a[1]), a[2])
roots = [p for p, (pp, c) in procs.items() if c.startswith('zsh ' + T + '/lcheck2.zsh')]
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
print('stopped', len(seen))
for d in glob.glob(H + '/runs/lc_mOrb4/*/') + glob.glob(H + '/runs/lc_mTd0/*/') + glob.glob(H + '/runs/lc_mNps/*/'):
    if not os.path.exists(d + 'result.txt'):
        shutil.rmtree(d)
sw = open(T + '/one14.switches').read().strip()
def without(s, name):
    return ','.join(x for x in s.split(',') if not x.startswith(name + ':'))
arms = {
    'mLcg': without(sw, 'QUEEN_CORRIDOR_GUARD'),
    'mLfh': without(sw, 'QUEEN_FAR_HEADS'),
    'mLbe': without(without(sw, 'BIG_ESCAPE_STEPS'), 'BIG_ESCAPE_MIN_LENGTH'),
    'mLk6': sw.replace('QS_KEEP_MIN_UNITS:2', 'QS_KEEP_MIN_UNITS:6'),
}
for n, s in arms.items():
    r = subprocess.run(['python3', 'tools/mkbots.py', '%s=%s' % (n, s)], cwd=H, capture_output=True, text=True,
                       env=dict(os.environ, MKSRC='src/w-one16/main.cpp'))
    print(n, (r.stdout + r.stderr).strip().splitlines()[-1][:60], len(s.split(',')))
subprocess.Popen('nohup zsh %s/lcchain.zsh > /dev/null 2>&1 &' % T, shell=True)
time.sleep(2)
print(subprocess.run(['pgrep', '-fl', 'tmp/lcheck'], capture_output=True, text=True).stdout)
