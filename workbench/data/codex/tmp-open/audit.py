import sys
sys.dont_write_bytecode = True
import json
import re
from collections import deque
from pathlib import Path
from op_scan import RUNS, load, point

HERE = Path(__file__).resolve().parent
GROUPS = [('A', ['m4bq_vb', 'm5op_vb', 'm5og_vb'], 16),
          ('B', ['m3b7qk_vh', 'm5og_vh'], 12)]


def audit(path, side):
    root = load(path).root()
    result = root.pointer(4)
    assert result.bit(0), 'unfinished replay'
    winner = result.u16(6) if result.u16(4) == 1 else None
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            teams[i] = int(q[1])
            bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
    queen = min(i for i in bodies if teams[i] == side)
    last_split, death = None, None
    rnd, actor = -1, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
        elif k == 9:
            b = bodies[p.i32(0)]
            hd, tl = point(p.pointer(0)), point(p.pointer(1))
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(point(c) for c in p.pointer(z))
            teams[child] = teams[parent]
            if parent == queen:
                x, y = bodies[queen][0]
                ds = []
                for i, b in bodies.items():
                    if teams[i] != side:
                        dx, dy = abs(x-b[0][0]), abs(y-b[0][1])
                        ds.append(min(dx, w-dx) + min(dy, h-dy))
                last_split = dict(round=rnd, nearest=min(ds) if ds else None,
                                  within6=any(d <= 6 for d in ds))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies.pop(i)
            if i == queen:
                cause = ('ran into a head' if actor == i else 'rammed') if reason == 3 else 'boxed in'
                death = dict(round=rnd, length=len(b), cause=cause, reason=reason,
                             actor=actor, actor_team=teams.get(actor), last_split=last_split)
    for s in (0, 1):
        lengths = [len(b) for i, b in bodies.items() if teams[i] == s]
        st = result.pointer(s)
        assert (len(lengths), max(lengths, default=0), sum(lengths)) == (st.i32(0), st.i32(4), st.i32(8))
    assert len(bodies.get(queen, ())) == result.pointer(side).i32(12)
    return dict(winner=winner, outcome='무승부' if winner is None else '승' if winner == side else '패',
                death=death, last_round=rnd)


def main():
    output = {}
    for label, arms, expected in GROUPS:
        dirs = [{d.name for d in (RUNS/a).iterdir() if d.is_dir()} for a in arms]
        candidates = sorted(set.intersection(*dirs))
        assert len(candidates) == expected, (label, len(candidates))
        data, issues = {}, []
        for arm in arms:
            data[arm] = {}
            for game in candidates:
                d = RUNS/arm/game
                missing = [f for f in ('game.replay', 'result.txt') if not (d/f).exists()]
                if missing:
                    issues.append(f'{arm}/{game}: missing {missing}')
                    continue
                result_text = (d/'result.txt').read_text().strip()
                try:
                    row = audit(d/'game.replay', int(game.rsplit('-side', 1)[1]))
                    match = re.search(r'\bwinner=(\d+)\b', result_text)
                    assert match and int(match[1]) == row['winner'], result_text
                    rounds = re.search(r'\brounds=(\d+)\b', result_text)
                    assert rounds and int(rounds[1]) == row['last_round'] + 1, result_text
                    data[arm][game] = row
                except Exception as e:
                    issues.append(f'{arm}/{game}: {e!r}; result.txt={result_text}')
            print(label, arm, len(data[arm]), flush=True)
        output[label] = dict(arms=arms, candidates=candidates, data=data, issues=issues)
    (HERE/'audit.json').write_text(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
