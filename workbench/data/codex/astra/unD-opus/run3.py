"""jobs: bot:mapfile:side:seed ... ; folder solo/runs/ud_<bot>/<map>-seed<S>-side<k>; two at a time"""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
RT = Path.home() / 'meow-redteam'
LOG = open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/run.log', 'a')
OPP = 'm3base'
STOP = time.mktime(time.strptime(time.strftime('%Y-%m-%d') + ' 14:33', '%Y-%m-%d %H:%M'))


def one(job):
    bot, mp, k, seed = job.split(':')
    k = int(k)
    if time.time() > STOP:
        return
    name = Path(mp).stem
    if name.startswith('ud_'):
        name = name[3:]
    arm = 'ud_' + bot.replace('ud_', '')
    out = RT / 'solo/runs' / arm / ('%s-seed%s-side%d' % (name, seed, k))
    if (out / 'result.txt').exists():
        return
    out.mkdir(parents=True, exist_ok=True)
    a, b = (bot, OPP) if k == 0 else (OPP, bot)
    t = time.time()
    try:
        p = subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / a), str(RT / 'solo/bots' / b), str(RT / 'maps' / mp), seed, str(out)],
                           capture_output=True, text=True, timeout=400)
        rc, tail = p.returncode, (p.stdout + p.stderr)[-200:].replace('\n', ' | ')
    except subprocess.TimeoutExpired:
        rc, tail = 'TIMEOUT', ''
    LOG.write('%s %s seed%s side%d rc=%s %.0fs %s\n' % (arm, name, seed, k, rc, time.time() - t, tail))
    LOG.flush()


with ThreadPoolExecutor(2) as ex:
    list(ex.map(one, sys.argv[1:]))
LOG.write('DONE3\n')
LOG.flush()
