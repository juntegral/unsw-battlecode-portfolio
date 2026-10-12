"""jobs: bot:mapfile:side ... ; folder solo/runs/ud_<bot>/<map>-seed1-side<k>"""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
RT = Path.home() / 'meow-redteam'
LOG = open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/run.log', 'a')
OPP = 'm3base'


def one(job):
    bot, mp, k = job.split(':')
    k = int(k)
    name = Path(mp).stem
    if name.startswith('ud_'):
        name = name[3:]
    arm = 'ud_' + bot.replace('ud_', '')
    out = RT / 'solo/runs' / arm / ('%s-seed1-side%d' % (name, k))
    if (out / 'result.txt').exists():
        return
    out.mkdir(parents=True, exist_ok=True)
    a, b = (bot, OPP) if k == 0 else (OPP, bot)
    t = time.time()
    try:
        p = subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / a), str(RT / 'solo/bots' / b), str(RT / 'maps' / mp), '1', str(out)],
                           capture_output=True, text=True, timeout=420)
        rc, tail = p.returncode, (p.stdout + p.stderr)[-200:].replace('\n', ' | ')
    except subprocess.TimeoutExpired:
        rc, tail = 'TIMEOUT', ''
    LOG.write('%s %s side%d rc=%s %.0fs %s\n' % (arm, name, k, rc, time.time() - t, tail))
    LOG.flush()


with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, sys.argv[1:]))
LOG.write('DONE2\n')
LOG.flush()
