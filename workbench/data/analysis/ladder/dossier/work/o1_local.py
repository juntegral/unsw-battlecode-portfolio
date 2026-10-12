"""Scratch (diag-one1): card 1 on local games. Scans ~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay
(finished games only, cached by folder) and prints the works-if rows per game and per arm for capped games.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_local.py <arm> [<arm> ...]"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import Counter
from o1_scan import scan, OUT
RUNS = Path.home() / 'meow-redteam/solo/runs'


def rows(arm):
    cache_path = Path(OUT) / ('o1_local-%s.jsonl' % arm)
    cache = {}
    if cache_path.exists():
        for l in cache_path.read_text().splitlines():
            g = json.loads(l)
            cache[g['folder']] = g
    out = []
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if not (folder / 'result.txt').exists() or not (folder / 'game.replay').exists():
            continue
        if folder.name not in cache:
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
            k = int(m[3])
            j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
            g = scan(arm, folder / 'game.replay', j)
            g['folder'] = folder.name
            cache[folder.name] = g
        out.append(cache[folder.name])
    with open(cache_path, 'w') as f:
        for g in cache.values():
            f.write(json.dumps(g, separators=(',', ':')) + '\n')
    return out


def snap(g, r):
    r = min(r, g['last'])
    return g['snaps'].get(str(r), g['snaps'][str(g['last'])])


def measures(g):
    m = {}
    st = [d for d in g['deaths'] if d[1] == 0 and d[4] == 'stop' and d[5] > 0]
    m['u200'] = snap(g, 200)[0][0]
    m['first'] = min((d[0] for d in st if d[0] > 150), default=999)
    m['feeders201_300'] = sum(1 for d in st if 200 < d[0] <= 300)
    m['feeders301_350'] = sum(1 for d in st if 300 < d[0] <= 350)
    m['stopL201_350'] = sum(d[2] for d in st if 200 < d[0] <= 350)
    m['stopnet201_350'] = sum(d[2] - d[10] for d in st if 200 < d[0] <= 350)
    m['ramnet5_201_350'] = sum(d[2] - d[10] for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[2] >= 5 and 200 < d[0] <= 350)
    m['maxL'] = max(snap(g, r)[0][2] for r in range(200, 500, 25))
    m['feeders351_499'] = sum(1 for d in st if 350 < d[0])
    nat = Counter()
    for r, s, role, origin, kd, L0 in g['eats']:
        if s == 0 and origin == 'n' and r > 0:
            nat[(r - 1) // 25] += 1
    m['nat151_200'] = (nat[6] + nat[7]) / 2
    m['nat201_300'] = (nat[8] + nat[9] + nat[10] + nat[11]) / 4
    m['nat301_350'] = (nat[12] + nat[13]) / 2
    for r in (200, 300, 350, 400):
        m['T%d' % r] = snap(g, r)[0][1]
        m['oT%d' % r] = snap(g, r)[1][1]
        m['L%d' % r] = snap(g, r)[0][2]
        m['u%d' % r] = snap(g, r)[0][0]
    m['Tend'], m['oTend'], m['Lend'], m['oLend'] = g['ends'][0][1], g['ends'][1][1], g['ends'][0][2], g['ends'][1][2]
    m['uend'] = g['ends'][0][0]
    m['n5_9_r300'] = snap(g, 300)[0][7]
    m['n10_r300'] = snap(g, 300)[0][8]
    m['ram5_201_350'] = sum(d[2] for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[2] >= 5 and 200 < d[0] <= 350)
    m['ram5_9_201_350'] = sum(d[2] for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and 5 <= d[2] <= 9 and 200 < d[0] <= 350)
    m['lead'] = ['r%d L%d' % (d[0], d[2]) for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[2] >= 10 and d[0] > 200]
    m['ramsOn'] = sum(1 for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and 200 < d[0] <= 350)
    m['ramsBy'] = sum(1 for d in g['deaths'] if d[1] == 1 and d[4] == 'rammed' and 200 < d[0] <= 350)
    m['q'] = g['ends'][0][3]
    return m


if __name__ == '__main__':
    allrows = {}
    for arm in sys.argv[1:]:
        gs = rows(arm)
        allrows[arm] = gs
        print('==', arm, len(gs), 'games finished')
        for g in gs:
            m = measures(g)
            print(' %-40s %-5s %-7s u200 %2d | first stop %3d | feeders 201-300 %2d, 301-350 %2d, 351+ %3d | nat/25: r151-200 %.1f r201-300 %.1f r301-350 %.1f | T 200/300/350/400/end %d/%d/%d/%d/%d (them %d/%d/%d/%d/%d) | longest 300/400/end %d/%d/%d (them end %d) | n5-9 r300 %d n10+ %d | rammed L5+ r201-350 %d (5-9: %d) | leaders rammed %s | units 300/350/400/end %d/%d/%d/%d | rams r201-350 on us %d by us %d' % (
                g['folder'][:40], g['result'], g['how'], m['u200'], m['first'], m['feeders201_300'], m['feeders301_350'], m['feeders351_499'], m['nat151_200'], m['nat201_300'], m['nat301_350'],
                m['T200'], m['T300'], m['T350'], m['T400'], m['Tend'], m['oT200'], m['oT300'], m['oT350'], m['oT400'], m['oTend'], m['L300'], m['L400'], m['Lend'], m['oLend'], m['n5_9_r300'], m['n10_r300'],
                m['ram5_201_350'], m['ram5_9_201_350'], m['lead'], m['u300'], m['u350'], m['u400'], m['uend'], m['ramsOn'], m['ramsBy']))
    print()
    print('capped games (56+ dragons at r200), mean per arm')
    keys = ['stopL201_350', 'stopnet201_350', 'ramnet5_201_350', 'maxL', 'first', 'feeders201_300', 'feeders301_350', 'feeders351_499', 'nat151_200', 'nat201_300', 'nat301_350', 'T200', 'T300', 'T350', 'T400', 'Tend', 'oT300', 'oTend', 'L300', 'L400', 'Lend', 'oLend', 'n5_9_r300', 'n10_r300', 'ram5_201_350', 'ram5_9_201_350', 'ramsOn', 'ramsBy', 'u300', 'u350', 'uend']
    for arm, gs in allrows.items():
        cap = [measures(g) for g in gs if snap(g, 200)[0][0] >= 56]
        if not cap:
            print(arm, 'no capped games yet')
            continue
        print('%-9s n=%d wins %d | ' % (arm, len(cap), sum(1 for g in gs if snap(g, 200)[0][0] >= 56 and g['result'] == 'win')) + ' '.join('%s %.1f' % (k, sum(m[k] for m in cap) / len(cap)) for k in keys) + ' | games with a leader of 10+ rammed after r200: %d' % sum(1 for m in cap if m['lead']))
