"""Scratch (diag-whq): recount of the merge-situation shares by another path. Bundle-build games against WeHaveQuizzes above
1200 cells; state rebuilt with the shared reader's own parser helpers but sampled at the start of every round after 400
(not at turn starts): for each non-queen dragon of each side the nearest team mate at least twice its length and 4 or more long.
Usage: python3 data/analysis/ladder/dossier/work/wq_recount.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

LABELS = ('agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')


def main():
    tot = [Counter(), Counter()]
    games = 0
    for label in LABELS:
        folder = Path('data/online/smoke') / (label + '-new')
        if not folder.is_dir():
            continue
        for mp in sorted(folder.glob('game-*.json')):
            j = json.loads(mp.read_text())
            names = (j['teamAName'], j['teamBName'])
            if 'WeHaveQuizzes' not in names:
                continue
            root = replay.load(folder / ('M%d.replay' % j['id'])).root()
            lines = root.text(0).splitlines()
            W, H = map(int, lines[0].split()[1:3])
            if W * H <= 1200:
                continue
            games += 1
            pos = {}
            team = {}
            for line in lines:
                q = line.split()
                if q and q[0] == 'DRAGON':
                    i = len(pos)
                    pos[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
                    team[i] = int(q[1])
            mine = 0 if j['teamAId'] == 1119 else 1
            queens = {}
            for i in sorted(pos):
                queens.setdefault(team[i], i)
            rnd = -1
            for ev in root.pointer(3):
                k = ev.u16(0)
                p = ev.pointer(0)
                if k == 0:
                    rnd = p.i32(0)
                    if rnd > 400:
                        for i, b in pos.items():
                            if i == queens[team[i]]:
                                continue
                            L = len(b)
                            best = 99
                            for z, bb in pos.items():
                                if z != i and team[z] == team[i] and len(bb) >= 2 * L and len(bb) >= 4:
                                    dx = abs(b[0][0] - bb[0][0])
                                    dy = abs(b[0][1] - bb[0][1])
                                    g = min(dx, W - dx) + min(dy, H - dy)
                                    if g < best:
                                        best = g
                            s = 0 if team[i] == mine else 1
                            tot[s]['within 3' if best <= 3 else '4 to 6' if best <= 6 else '7 to 15' if best <= 15 else 'farther or none'] += 1
                            tot[s]['all'] += 1
                elif k == 9:
                    i = p.i32(0)
                    hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
                    b = pos[i]
                    if b[0] != hd:
                        b.appendleft(hd)
                    while len(b) > 1 and b[-1] != tl:
                        b.pop()
                elif k == 10:
                    for z, i in enumerate((p.i32(0), p.i32(4))):
                        pos[i] = deque(replay.point(c) for c in p.pointer(z))
                        team[i] = p.u16(8)
                elif k == 11:
                    pos.pop(p.i32(0))
    print('games', games)
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        a = tot[s]['all']
        print(nm, 'dragon-rounds after r400 a game %.0f:' % (a / max(1, games)), '; '.join('%s %.1f%%' % (k, 100 * tot[s][k] / max(1, a)) for k in ('within 3', '4 to 6', '7 to 15', 'farther or none')))


main()
