"""run4.py <jobs file>: lines 'runname botA botB map seed'; plays 2 at a time; trace of both bots to <out>.qdk."""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
R = os.path.expanduser('~/meow-redteam')


def play(line):
    if line.startswith('WAIT '):
        import time
        while not os.path.exists(line[5:]):
            time.sleep(2)
        return
    run, a, b, mp, seed = line.split()
    out = f'{R}/solo/runs/{run}/{mp}-seed{seed}-side0'
    if os.path.exists(out + '/result.txt'):
        return
    if os.path.isdir(out):
        for f in os.listdir(out):
            os.remove(out + '/' + f)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    trace = out + '.qdk'
    open(trace, 'w').close()
    path = f'{R}/maps/gx/{mp}.map' if mp.startswith('gx_') else f'{R}/maps/{mp}.map'
    r = subprocess.run([f'{R}/play.sh', f'{R}/solo/bots/{a}', f'{R}/solo/bots/{b}', path, seed, out], capture_output=True,
                       text=True, cwd=R, env=dict(os.environ, QDK_LOG=trace))
    print(line, (r.stdout.strip() or r.stderr.strip())[-150:], flush=True)


jobs = [l for l in open(sys.argv[1]).read().splitlines() if l.strip()]
with ThreadPoolExecutor(2) as ex:
    list(ex.map(play, jobs))
print('ALLDONE', flush=True)
