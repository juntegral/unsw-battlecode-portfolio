"""unA-opus: play mD17 on the ua maps and the baseline maps, 3 games at a time."""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
RT = Path.home() / 'meow-redteam'
UN = Path('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unseen/maps')
new = sorted((RT / 'maps/un2').glob('ua_*.map'))
base = [RT / 'maps/ladder/ladder_portals_1.map', RT / 'maps/ladder/ladder_stripes_1.map'] + [UN / (n + '.map') for n in ('un_portalonly_1', 'un_portalid_1', 'un_queen600_1', 'un_queen600_2')]
jobs = []
for group in (new, base):
    for mp in group:
        jobs.append(('ua_m3base', 'mD17', 'm3base', mp, 0))
        jobs.append(('ua_mirror', 'mD17', 'mD17', mp, 0))
        jobs.append(('ua_m3base', 'm3base', 'mD17', mp, 1))


def play(j):
    arm, a, b, mp, k = j
    out = RT / 'solo/runs' / arm / ('%s-seed1-side%d' % (mp.stem, k))
    if (out / 'result.txt').exists():
        return
    out.mkdir(parents=True, exist_ok=True)
    t = time.time()
    with open(str(out) + '.log', 'w') as f:
        subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / a), str(RT / 'solo/bots' / b), str(mp), '1', str(out)], cwd=str(RT), stdout=f, stderr=subprocess.STDOUT)
    print(arm, out.name, '%.0fs' % (time.time() - t), (out / 'result.txt').read_text().strip()[:120] if (out / 'result.txt').exists() else 'NO RESULT', flush=True)


with ThreadPoolExecutor(3) as ex:
    list(ex.map(play, jobs))
print('ALL DONE', flush=True)
