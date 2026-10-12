"""run.py <jobs file>: lines 'arm map seed side'; plays 2 at a time against mNps; skips finished games.
The trace of a QDK_TRACE build goes to <runs>/<arm>/<game>.qdk through the QDK_LOG environment variable."""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
R = os.path.expanduser('~/meow-redteam')


def play(line):
    arm, mp, seed, side = line.split()
    out = f'{R}/solo/runs/{arm}/{mp}-seed{seed}-side{side}'
    if os.path.exists(out + '/result.txt'):
        return
    if os.path.isdir(out):
        for f in os.listdir(out):
            os.remove(out + '/' + f)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    trace = out + '.qdk'
    open(trace, 'w').close()
    path = f'{R}/maps/gx/{mp}.map' if mp.startswith('gx_') else f'{R}/maps/{mp}.map'
    a, b = f'{R}/solo/bots/{arm}', f'{R}/solo/bots/mNps'
    if side == '1':
        a, b = b, a
    r = subprocess.run([f'{R}/play.sh', a, b, path, seed, out], capture_output=True, text=True, cwd=R,
                       env=dict(os.environ, QDK_LOG=trace))
    print(arm, mp, seed, side, (r.stdout.strip() or r.stderr.strip())[-150:], flush=True)


jobs = [l for l in open(sys.argv[1]).read().splitlines() if l.strip()]
with ThreadPoolExecutor(2) as ex:
    list(ex.map(play, jobs))
print('ALLDONE', flush=True)
