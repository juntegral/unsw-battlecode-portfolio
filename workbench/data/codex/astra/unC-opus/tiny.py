"""unC-opus: play arms against m3base on a map set, both seats, several seeds, 2 games at a time; then one table.
Usage: python3 tiny.py <set> <seeds, e.g. 1,2,3> <arm> ...      set: tiny | cost | t9
Runs go to ~/meow-redteam/solo/runs/uc_T_<arm>/<map>-seed<S>-side<K>/. Finished games are not replayed."""
import sys, json, subprocess, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
R = Path.home() / 'meow-redteam'
SETS = dict(tiny=['un2/uc_tiny7x7', 'un2/uc_tiny7x9', 'gx/gx_corridors_7x7_911100'],
            t9=['un2/uc_tiny9x9_2', 'un2/uc_tiny9x9_6'],
            cost=['un2/uc_tiny9x9_2', 'gx/gx_open_24x12_910901', 'ladder/ladder_stripes_1'])
maps = SETS[sys.argv[1]]
seeds = [int(x) for x in sys.argv[2].split(',')]
arms = sys.argv[3:]
STOP = 1433


def play(job):
    arm, mp, seed, side = job
    name = mp.split('/')[1]
    out = R / 'solo/runs' / ('uc_T_' + arm) / ('%s-seed%d-side%d' % (name, seed, side))
    if not (out / 'result.json').exists():
        if int(time.strftime('%H%M')) >= STOP:
            return job, None
        if out.exists() and any(out.iterdir()):
            return job, None
        out.mkdir(parents=True, exist_ok=True)
        a, b = (arm, 'm3base') if side == 0 else ('m3base', arm)
        subprocess.run([str(R / 'play.sh'), str(R / 'solo/bots' / a), str(R / 'solo/bots' / b), str(R / 'maps' / (mp + '.map')), str(seed), str(out)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not (out / 'result.json').exists():
        return job, None
    return job, json.loads((out / 'result.json').read_text())


jobs = [(arm, mp, s, k) for s in seeds for mp in maps for k in (0, 1) for arm in arms]
with ThreadPoolExecutor(2) as ex:
    res = dict(ex.map(play, jobs))
print('cells: W/L/D for the arm, then per game seat0,seat1 per seed as result:rounds (W win, L loss, D draw; e elimination, q round limit)')
for arm in arms:
    tot = [0, 0, 0]
    row = []
    for mp in maps:
        cell = []
        for s in seeds:
            for k in (0, 1):
                r = res.get((arm, mp, s, k))
                if r is None:
                    cell.append('--')
                    continue
                w = r['winner']
                o = 'D' if w == 'draw' else 'W' if w == k else 'L'
                tot['WLD'.index(o)] += 1
                cell.append('%s%s%d' % (o, 'e' if r['how'] == 'elimination' else 'q', r['rounds']))
        row.append(mp.split('/')[1].replace('gx_corridors_7x7_911100', 'corr7x7').replace('uc_', '') + ' ' + ','.join(cell))
    print('%-9s %d/%d/%d | %s' % (arm, tot[0], tot[1], tot[2], ' | '.join(row)))
