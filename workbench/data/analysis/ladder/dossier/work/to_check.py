# Scratch (diag-topopen): independent recount.
# (1) dragons alive, total length, longest, pearls of both sides at every round end to r300 for our 60 live-build games, from the
#     shared reader tools/ladder_replay.py (scan), against the series of to_scan.py.
# (2) by separate code: games with a starter of 4+, of them with a split in round 0; queen turns at length 4+ in r0-40 and how
#     many of them are splits; for our live build (OQ, OT) and for the studied side of the top3 folder.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay
from ladder_replay import replay
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')


def mine():
    out = {}
    for f in sorted(W.glob('to_scan-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if line.strip():
                g = json.loads(line)
                if 'error' not in g:
                    out[g['game']] = g
    return out


def part1(games):
    cells = bad = n = 0
    for folder in ('data/online/smoke/agg8-q1-new', 'data/online/smoke/top-l1-old'):
        for gp in sorted(Path(folder).glob('game-*.json')):
            j = json.loads(gp.read_text())
            rp = Path(folder) / ('M%d.replay' % j['id'])
            if not rp.exists() or j['id'] not in games:
                continue
            res = ladder_replay.scan(rp, j, folder, set())
            g = games[j['id']]
            n += 1
            for rd, snap in res['snapshots'].items():
                if rd > 300:
                    continue
                for s, side in (('u', 'us'), ('t', 'them')):
                    ser = g['sides'][s]['series']
                    if len(ser['alive']) <= rd:
                        continue
                    for a, c in (('alive', 'alive'), ('total', 'total'), ('longest', 'longest'), ('eaten', 'pearls')):
                        cells += 1
                        if ser[a][rd] != snap[side][c]:
                            bad += 1
                            if bad <= 5:
                                print('MISMATCH', j['id'], rd, s, a, ser[a][rd], snap[side][c])
    print('part 1: %d games, %d cells compared, %d differ' % (n, cells, bad))


def recount(path, letter):
    root = replay.load(Path(path)).root()
    text = root.text(0)
    length, team = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(length)
            length[i] = int(q[2])
            team[i] = 'AB'[int(q[1])]
    queen = min(i for i in team if team[i] == letter)
    long_start = any(length[i] >= 4 for i in team if team[i] == letter)
    r0 = False
    qturns = qsplits = 0
    rnd, actor, pend = 0, None, 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd > 40:
                break
        elif k == 1:
            actor = p.i32(0)
            if actor == queen and length.get(actor, 0) >= 4:
                qturns += 1
        elif k == 3:
            if p.u32(0) == 0 and actor is not None:
                length[actor] = length.get(actor, 0) + 1
        elif k == 4:
            a = p.pointer(0)
            if a and a.u16(0) == 0 and a.pointer(0) is not None:
                steps = len(list(a.pointer(0)))
                pay = max(0, steps - (length.get(actor, 0) + 3) // 4)
                if pay and actor in length:
                    length[actor] -= pay
        elif k == 9:
            if p.i32(0) == actor and pend:
                pass
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            team[child] = 'AB'[p.u16(8)]
            length[parent] = len(list(p.pointer(0)))
            length[child] = len(list(p.pointer(1)))
            if team[parent] == letter:
                if rnd == 0:
                    r0 = True
                if parent == queen and length[parent] + length[child] >= 4:
                    qsplits += 1
        elif k == 11:
            length.pop(p.i32(0), None)
        if k == 1:
            pend = 0
    return long_start, r0, qturns, qsplits


def part2():
    acc = defaultdict(lambda: [0, 0, 0, 0, 0])
    jobs = []
    for folder, lab in (('data/online/smoke/agg8-q1-new', 'ours live, ladder'), ('data/online/smoke/top-l1-old', 'ours live, direct')):
        for gp in sorted(Path(folder).glob('game-*.json')):
            j = json.loads(gp.read_text())
            jobs.append((Path(folder) / ('M%d.replay' % j['id']), 'A' if j['teamAId'] == 1119 else 'B', lab))
            if 'top-l1' in folder:
                jobs.append((Path(folder) / ('M%d.replay' % j['id']), 'B' if j['teamAId'] == 1119 else 'A', 'larp and Cutlery, direct'))
    names = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp'}
    for line in Path('data/online/top3/index.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        folder = Path('data/online/top3/%d' % r['battle'])
        for gp in sorted(folder.glob('game-*.json')):
            j = json.loads(gp.read_text())
            if j['mapName'].startswith('Autarky') or j['mapName'].startswith('Prisoners'):
                continue
            rp = folder / ('M%d.replay' % j['id'])
            if rp.exists() and r['team'] in (j['teamAId'], j['teamBId']):
                jobs.append((rp, 'A' if j['teamAId'] == r['team'] else 'B', names.get(r['team'], str(r['team'])) + ', today'))
    seen = set()
    for rp, letter, lab in jobs:
        if (str(rp), letter) in seen or not rp.exists():
            continue
        seen.add((str(rp), letter))
        try:
            ls, r0, qt, qs = recount(rp, letter)
        except Exception as e:
            print('ERR', rp, repr(e)[:100])
            continue
        a = acc[lab]
        a[0] += 1
        a[1] += int(ls)
        a[2] += int(ls and r0)
        a[3] += qt
        a[4] += qs
    for lab in sorted(acc):
        a = acc[lab]
        print('part 2: %-26s games %3d | with a starter of 4+: %3d, of them a split in round 0: %3d | queen turns at 4+ in r0-40: %.1f a game, splits %d%%' % (
            lab, a[0], a[1], a[2], a[3] / a[0], round(100.0 * a[4] / a[3]) if a[3] else 0))


part1(mine())
part2()
