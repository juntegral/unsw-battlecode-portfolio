"""Scratch (diag-attack): independent recount of the head-on account with the shared reader tools/ladder_replay.scan
(not my state machine). Per game: meetings by mover side, the class "mover 4 or shorter at death, victim at least twice
that", lengths lost and drops eaten within 15 rounds by side. Usage: python3 .../at_recount.py <shard> <shards>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import scan
from collections import Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
    rows = sorted(rows, key=lambda r: r['game'])
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    tot = Counter()
    for n, r in enumerate(rows):
        folder = Path('data/online/ladder') / str(r['battle'])
        j = json.loads((folder / ('game-%d.json' % r['game'])).read_text())
        g = scan(folder / ('M%d.replay' % r['game']), j, str(folder), set())
        deaths = dict((d['death'], d) for d in g['deaths'])
        pearls = dict((p['pearl'], p) for p in g['pearls'])
        tot['games'] += 1
        for c in g['collisions']:
            if not c['cross_team']:
                continue
            a, b = [deaths[x] for x in c['deaths']]
            mover, victim = (a, b) if a['id'] == a['actor'] else (b, a)
            assert mover['id'] == mover['actor'] and victim['id'] != victim['actor']
            ms = mover['side']
            vs = victim['side']
            k = 'they' if ms == 'them' else 'we'
            eat_m = eat_v = 0
            for d in (mover, victim):
                for pid in d['pearls']:
                    p = pearls[pid]
                    if p['eater'] != 'nobody' and p['wait'] <= 15:
                        if p['eater'] == ms:
                            eat_m += 1
                        else:
                            eat_v += 1
            for tag in ('all', 'big') if (mover['length'] <= 4 and victim['length'] >= 2 * mover['length']) else ('all',):
                tot[(k, tag, 'n')] += 1
                tot[(k, tag, 'Lm')] += mover['length']
                tot[(k, tag, 'Lv')] += victim['length']
                tot[(k, tag, 'eat_m')] += eat_m
                tot[(k, tag, 'eat_v')] += eat_v
                tot[(k, tag, 'drops')] += mover['dropped'] + victim['dropped']
        if n % 10 == 9:
            print(n + 1, len(rows), flush=True)
    body = json.dumps([[list(k) if isinstance(k, tuple) else k, v] for k, v in tot.items()])
    if shard == 0:
        Path(OUT + 'at_rc-0.json').write_text(body)
    elif shard == 1:
        Path(OUT + 'at_rc-1.json').write_text(body)
    elif shard == 2:
        Path(OUT + 'at_rc-2.json').write_text(body)
    else:
        Path(OUT + 'at_rc-3.json').write_text(body)
    print('done', shard)


main()
