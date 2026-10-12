# Scratch (diag-split): independent recount of the head figures with the stock parser (battlecode/replay.py parse),
# not with sl_scan.py's state machine. Every 5th game of each team. Per game: focal turns, turns at length 4+,
# turns by length bucket, splits, splits of a 4-long, splits whose child is 2, splits that leave the parent 2, deaths.
# Usage: python3 data/analysis/ladder/dossier/work/sl_recount.py <shard 0|1>   -> sl_recount-<shard>.jsonl
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, '~/01. Project/개인 프로젝트/battlecode')
import replay
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def one(row):
    info, events, team_of = replay.parse(row['replay'])
    length = {}
    for line in info['map'].splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            length[len(length)] = int(q[2])
    focal = row['our_side']
    out = dict(game=row['game'], tm=row['tm'], turns=0, ge4=0, by=[0, 0, 0, 0, 0], splits=0, p4=0, child2=0, rem2=0, deaths=0)
    for e in events:
        k = e['kind']
        if k == 'action':
            i = e['id']
            if team_of.get(i) == focal and i in length:
                n = length[i]
                out['turns'] += 1
                out['ge4'] += n >= 4
                out['by'][0 if n == 2 else 1 if n == 3 else 2 if n == 4 else 3 if n <= 7 else 4] += 1
        elif k == 'update':
            length[e['id']] = e['length']
        elif k == 'split':
            if e['team'] == focal:
                out['splits'] += 1
                out['p4'] += e['parentLength'] + e['childLength'] == 4
                out['child2'] += e['childLength'] == 2
                out['rem2'] += e['parentLength'] == 2
            length[e['id']] = e['parentLength']
            length[e['child']] = e['childLength']
        elif k == 'death':
            if e['team'] == focal:
                out['deaths'] += 1
            length.pop(e['id'], None)
    return out


def main():
    shard = int(sys.argv[1])
    rows = []
    for tm, f in (('O', 'data/analysis/ladder/dossier/per-game.jsonl'),
                  ('R', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl')):
        for line in open(f):
            r = json.loads(line)
            if r['relation'] == 'us':
                rows.append(dict(game=r['game'], tm=tm, replay=r['replay'], our_side=r['our_side']))
    rows.sort(key=lambda r: (r['tm'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % 5 == 0]
    rows = [r for n, r in enumerate(rows) if n % 2 == shard]
    out = [json.dumps(one(r), separators=(',', ':')) for r in rows]
    text = '\n'.join(out) + '\n'
    if shard == 0:
        Path(OUT + 'sl_recount-0.jsonl').write_text(text)
    else:
        Path(OUT + 'sl_recount-1.jsonl').write_text(text)
    print('done', shard, len(out))


main()
