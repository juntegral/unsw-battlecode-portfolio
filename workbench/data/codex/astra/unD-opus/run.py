import json, subprocess, sys, time, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HOME = Path.home()
RT = HOME / 'meow-redteam'
ROOT = Path('~/01. Project/개인 프로젝트/unsw-swarm')
MAPS = ROOT / 'data/codex/astra/unseen/maps'
man = json.load(open(ROOT / 'data/codex/astra/unseen/maps_manifest.json'))
man.sort(key=lambda m: m['cells'])
ARM = 'ud_mD17'
OPP = sys.argv[1] if len(sys.argv) > 1 else 'm3base'
SUF = '' if OPP == 'm3base' else '_v' + OPP
STOP = float(sys.argv[2]) if len(sys.argv) > 2 else time.time() + 1200
LOG = open(ROOT / 'data/codex/astra/unD-opus/run.log', 'a')


def one(job):
    m, k = job
    if time.time() > STOP:
        return
    name = m['file'][:-4]
    out = RT / 'solo/runs' / (ARM + SUF) / ('%s-seed1-side%d' % (name, k))
    if (out / 'result.txt').exists():
        return
    out.mkdir(parents=True, exist_ok=True)
    a, b = ('mD17', OPP) if k == 0 else (OPP, 'mD17')
    t = time.time()
    try:
        p = subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / a), str(RT / 'solo/bots' / b), str(RT / 'maps/un2' / ('ud_' + m['file'])), '1', str(out)],
                           capture_output=True, text=True, timeout=420)
        rc = p.returncode
        tail = (p.stdout + p.stderr)[-200:].replace('\n', ' | ')
    except subprocess.TimeoutExpired:
        rc, tail = 'TIMEOUT', ''
    LOG.write('%s side%d cells=%d rc=%s %.0fs %s\n' % (name, k, m['cells'], rc, time.time() - t, tail))
    LOG.flush()


PRI = ['queen600', 'symmetry', 'startlayout', 'center700', 'center1000', 'aggressive1200', 'portalid', 'edgewrap', 'portalonly', 'startlength_1', 'aspect', 'timers', 'width64', 'cells409']


def pri(m):
    for n, p in enumerate(PRI):
        if p in m['file']:
            return n
    return 99


man.sort(key=lambda m: (pri(m), m['cells']))
jobs = [(m, k) for m in man for k in (0, 1)]
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, jobs))
LOG.write('DONE %s\n' % OPP)
