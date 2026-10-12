"""run.py <jobfile>: lines `arm bot opp mapfile seed side`; exactly 6 games at a time; skips games already played."""
import os, subprocess, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~/meow-redteam')
B = H + '/solo/bots'
LOG = os.path.dirname(os.path.abspath(__file__)) + '/logs'
os.makedirs(LOG, exist_ok=True)


def mine():
    out = subprocess.run(['ps', '-axo', 'command'], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if 'run_game.py' in l and 'solo/runs/qb_' in l)


def play(job):
    arm, bot, opp, mp, seed, side = job
    name = os.path.basename(mp)[:-4]
    out = '%s/solo/runs/%s/%s-seed%s-side%s' % (H, arm, name, seed, side)
    if os.path.exists(out):
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    a, b = (bot, opp) if side == '0' else (opp, bot)
    with open('%s/%s-%s-%s-%s.txt' % (LOG, arm, name, seed, side), 'w') as f:
        with LOCK:
            while mine() >= 6:
                time.sleep(1)
            p = subprocess.Popen(['./play.sh', B + '/' + a, B + '/' + b, mp, seed, out], cwd=H, stdout=f, stderr=subprocess.STDOUT)
            time.sleep(1.5)
        p.wait()


LOCK = threading.Lock()
jobs = [l.split() for l in open(sys.argv[1]) if l.strip()]
with ThreadPoolExecutor(6) as ex:
    list(ex.map(play, jobs))
print('done')
