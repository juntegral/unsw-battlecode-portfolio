"""Early eating by version and map: pearls our side ate in r0-49 and r0-99 (stops reading each replay at r100).
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_early.py > data/codex/astra/weak13-opus/early.txt
One row a game in early-rows.tsv; a table by map x version on stdout."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict
from pathlib import Path

OUT = Path('data/codex/astra/weak13-opus')
SM = Path('data/online/smoke')
folders = sorted(SM.glob('one*-old')) + [Path('data/online/live-one1/b1508960'), Path('data/online/live-one1/b1513119'),
                                           Path('data/online/live-one1/b1483679')]
BOT = {'21377': 'one13'}


def early(path, j):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = int(q[2])
            teams[i] = int(q[1])
    own = 0 if j['teamAId'] == 1119 else 1
    n0 = sum(1 for i in teams if teams[i] == own)
    eat = [[0, 0], [0, 0]]
    rnd, actor = -1, None
    alive = set(bodies)
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd >= 100:
                break
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            if not p.u32(0):
                s = 0 if teams[actor] == own else 1
                eat[s][0 if rnd < 50 else 1] += 1
        elif k == 10:
            for i in (p.i32(0), p.i32(4)):
                teams[i] = p.u16(8)
                alive.add(i)
        elif k == 11:
            alive.discard(p.i32(0))
    n100 = [sum(1 for i in alive if (teams[i] == own) == (s == 0)) for s in (0, 1)]
    bot = [root.text(1), root.text(2)][own]
    return bot, n0, eat, n100, rnd


rows = []
for folder in folders:
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        try:
            bot, n0, eat, n100, last = early(rp, j)
        except Exception as e:
            print('ERR', rp, repr(e)[:80], file=sys.stderr)
            continue
        m = re.match(r'(one\d+)', folder.name)
        ver = m.group(1) if m else BOT.get(bot, 'bot' + bot)
        own = 0 if j['teamAId'] == 1119 else 1
        opp = j['team' + 'AB'[1 - own] + 'Name']
        won = (j.get('winner') or '').lower() == 'ab'[own]
        rows.append((folder.name, j['id'], j['mapName'], ver, bot, opp, n0, eat[0][0], eat[0][0] + eat[0][1], eat[1][0],
                     eat[1][0] + eat[1][1], n100[0], n100[1], last, int(won)))
with open(OUT / 'early-rows.tsv', 'w') as f:
    f.write('set\tgid\tmap\tver\tbot\topp\tn0\tus49\tus99\tth49\tth99\tusN100\tthN100\tlast\twon\n')
    for r in rows:
        f.write('\t'.join(map(str, r)) + '\n')
agg = defaultdict(list)
for r in rows:
    agg[r[2], r[3]].append(r)
vers = sorted({r[3] for r in rows}, key=lambda v: int(re.sub(r'\D', '', v) or 0))
maps = sorted({r[2] for r in rows})
print('our pearls eaten r0-99, mean per game (games) by map x version; start dragons n0 in brackets')
print('%-18s' % 'map' + ''.join('%-11s' % v for v in vers))
for m in maps:
    line = '%-18s' % (m[:14] + '[%d]' % agg[m, [v for v in vers if agg[m, v]][0]][0][6])
    for v in vers:
        g = agg[m, v]
        line += '%-11s' % ('%.1f(%d)' % (sum(x[8] for x in g) / len(g), len(g)) if g else '-')
    print(line)
print()
print('opponent pearls eaten r0-99 in the same games')
for m in maps:
    line = '%-18s' % m[:17]
    for v in vers:
        g = agg[m, v]
        line += '%-11s' % ('%.1f(%d)' % (sum(x[10] for x in g) / len(g), len(g)) if g else '-')
    print(line)
