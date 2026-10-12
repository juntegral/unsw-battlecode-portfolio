#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import hashlib
from collections import Counter, deque
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
spec = importlib.util.spec_from_file_location('dossier', ROOT / 'data/analysis/ladder/dossier/count_dossier.py')
dossier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dossier)
replay, Geometry = dossier.replay, dossier.Geometry
SIDES = ('us', 'them')
MARKS = (100, 200, 300, 400)

def scan(path, meta, label):
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w + int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geometry(w, h, raw)
    ours = 'A' if meta['teamAId'] == 1119 else 'B'
    assert meta['team'+ours+'Id'] == 1119
    assert meta['team'+('B' if ours == 'A' else 'A')+'Id'] == 946
    side = lambda i: 'us' if teams[i] == ours else 'them'
    queens = {s: min(i for i in bodies if side(i) == s) for s in SIDES}
    initial = Counter(side(i) for i in bodies)
    eats, splits, qsplit, deathcounts = Counter(), Counter(), Counter(), Counter()
    queen_death = {s: None for s in SIDES}
    snaps, turn_deaths, present = {}, [], set()
    rnd, actor, used, started = 0, None, 0, False
    dirs, action_cause, pending = [], None, None
    births = 0
    queen_split_keys = set()

    def state():
        return {s: dict(alive=sum(side(i) == s for i in bodies),
                       longest=max((len(b) for i, b in bodies.items() if side(i) == s), default=0),
                       total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                       queen_length=len(bodies.get(queens[s], ())),
                       pearls=eats[s], splits=splits[s], queen_split_turns=qsplit[s]) for s in SIDES}

    def snapshot():
        if rnd in MARKS:
            snaps[str(rnd)] = state()

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            assert pending is None
            turn_deaths.clear()
        if k == 0:
            if started:
                snapshot()
            started = True
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            assert actor in bodies
            dirs, used, action_cause = [], 0, None
        elif k == 4:
            assert actor == p.i32(0)
            a, fuel = p.pointer(0), p.pointer(1)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            action_cause = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[a.u16(0)] if a and a.u16(0) < 3 else 'no action')
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                assert c not in present
                present.add(c)
                births += 1
            else:
                assert c in present and actor in bodies and pending is None
                present.remove(c)
                pending = (actor, c)
                eats[side(actor)] += 1
        elif k == 9:
            i = p.i32(0)
            head, tail = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b, old = bodies[i], bodies[i][0]
            moved = old != head
            if moved:
                b.appendleft(head)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            assert b[-1] == tail
            if pending is not None:
                assert pending == (i, head) and moved
                pending = None
            if i == actor and moved:
                assert used < len(dirs)
                kind, dest = g.moves[old][dirs[used]]
                assert kind != 1 and dest == head
                used += 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            assert parent == actor and child not in teams
            length, s = len(bodies[parent]), side(parent)
            splits[s] += 1
            qsplit[s] += parent == queens[s]
            if parent == queens[s]:
                assert (rnd, parent) not in queen_split_keys
                queen_split_keys.add((rnd, parent))
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            assert len(bodies[parent]) + len(bodies[child]) == length
        elif k == 11:
            assert pending is None
            i, reason = p.i32(0), p.u16(4)
            s, b = side(i), bodies[i]
            dest = g.moves[b[0]][dirs[used]][1] if i == actor and used < len(dirs) else None
            cause = ('wall', 'own body', 'another body',
                     'head-on mover' if i == actor else 'head-on hit', action_cause or 'no action')[reason]
            hit = None
            before = dict(bodies)
            before.update({d['id']: d['body'] for d in turn_deaths if d['reason'] == 3})
            if reason == 2:
                owners = [z for z, bb in bodies.items() if z != i and dest in bb]
                assert len(owners) == 1
                hit = owners[0]
            elif reason == 3:
                if i != actor:
                    hit = actor
                else:
                    hit = next(d['id'] for d in turn_deaths if d['reason'] == 3)
            if i == queens[s]:
                assert queen_death[s] is None
                late = None
                if rnd >= 300:
                    if hit is not None:
                        candidates, method, distance = [hit], 'collision dragon', None
                    else:
                        distances = g.distances(b[0])
                        others = [z for z in before if z != i]
                        distance = min((distances[before[z][0]] for z in others), default=None)
                        candidates = [z for z in others if distances[before[z][0]] == distance]
                        method = 'nearest head by traversable path (portals included)'
                    longest = max((len(bb) for z, bb in before.items() if side(z) == s), default=0)
                    details = [dict(id=z, side=side(z), length=len(before[z]),
                                    is_own_longest=side(z) == s and len(before[z]) == longest) for z in sorted(candidates)]
                    late = dict(method=method, distance=distance, candidates=details,
                                own_longest_length=longest,
                                is_own_longest=any(z['is_own_longest'] for z in details),
                                candidate_length_mean=sum(z['length'] for z in details)/len(details) if details else None)
                queen_death[s] = dict(round=rnd, cause=cause, reason=reason, length=len(b),
                                      actor=actor, collision_dragon_id=hit, late_context=late)
            turn_deaths.append(dict(id=i, reason=reason, body=deque(b)))
            deathcounts[s] += 1
            bodies.pop(i)
    assert pending is None
    snapshot()
    final = state()
    result = root.pointer(4)
    for z, team in enumerate('AB'):
        s = 'us' if team == ours else 'them'
        st = result.pointer(z)
        assert [final[s][key] for key in ('alive', 'longest', 'total', 'queen_length')] == [st.i32(o) for o in (0, 4, 8, 12)]
        assert initial[s] + splits[s] - deathcounts[s] == final[s]['alive']
    assert births == sum(eats.values()) + len(present)
    winner = 'AB'[result.u16(6)] if result.u16(4) == 1 else None
    outcome = 'draw' if winner is None else 'win' if winner == ours else 'loss'
    assert (winner.lower() if winner else None) == meta['winner']
    us, them = final['us'], final['them']
    ending = ('elimination' if result.u16(2) == 0 else 'longer queen' if us['queen_length'] != them['queen_length'] else
              'longest dragon' if us['longest'] != them['longest'] else 'total length' if us['total'] != them['total'] else 'draw')
    key = 'alive' if ending == 'elimination' else 'queen_length' if ending == 'longer queen' else 'longest' if ending == 'longest dragon' else 'total'
    expected = None if us[key] == them[key] else ours if us[key] > them[key] else ('B' if ours == 'A' else 'A')
    assert winner == expected
    if ending == 'elimination':
        assert not us['alive'] or not them['alive']
    else:
        assert rnd == 499
    sides = {}
    for s in SIDES:
        sides[s] = dict(queen=dict(id=queens[s], alive_end=queens[s] in bodies, death=queen_death[s],
                                  length={**{str(n): snaps.get(str(n), {}).get(s, {}).get('queen_length') for n in MARKS}, 'end': final[s]['queen_length']}),
                        longest={**{str(n): snaps.get(str(n), {}).get(s, {}).get('longest') for n in (300, 400)}, 'end': final[s]['longest']},
                        dragons_alive={**{str(n): snaps.get(str(n), {}).get(s, {}).get('alive') for n in (300, 400)}, 'end': final[s]['alive']},
                        total_length_end=final[s]['total'],
                        pearls_eaten={str(n): snaps[str(n)][s]['pearls'] if str(n) in snaps else final[s]['pearls'] for n in (100, 300)},
                        splits_by_r100=snaps['100'][s]['splits'] if '100' in snaps else final[s]['splits'],
                        queen_split_turns=qsplit[s], result=outcome if s == 'us' else {'win':'loss','loss':'win','draw':'draw'}[outcome])
    return dict(set=label, game=meta['id'], map=meta['mapName'], map_id=meta['mapId'], our_side=ours,
                result=outcome, ended_by=ending, last_round=rnd, sides=sides, replay=str(path.relative_to(ROOT)),
                validation=dict(final_matches_replay=True, winner_matches_metadata=True, winner_matches_rules=True))

def main():
    rows, inputs = [], {}
    for label in ('old', 'new'):
        folder = ROOT / f'data/online/smoke/qn48v1-bob1-{label}'
        metas = sorted(folder.glob('game-*.json'))
        assert len(metas) == 15
        for mp in metas:
            meta = json.loads(mp.read_text())
            path = folder / f'M{meta["id"]}.replay'
            for p in (mp, path):
                inputs[p] = hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append(scan(path, meta, label))
            print(label, meta['mapName'], rows[-1]['result'], flush=True)
    assert len(rows) == 30
    for p, sha in inputs.items():
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha
    (OUT / 'rows.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    report(rows)

def report(rows):
    lines = ['# Card 48 v1: 15 old + 15 new online games', '',
             'Raw rounds; snapshots after the named round. Unreached state markers are null, and means use reached games (n shown); dead queens are 0. Cumulative pearls/splits include every game through the marker or its earlier end. Means rounded to two decimals.',
             'Late-death context (r300 onward): collision dragon, otherwise nearest head by traversable path including portals; all nearest ties retained, yes if any is our longest (length ties count). Lengths are immediately before the death; paired head-on deaths are treated together.', '',
             '## A. Set totals and means', '', '| Set | Games | W/L/D | Endings: elimination / longer queen / longest dragon / total length / draw | Mean last round |', '|---|---:|---|---|---:|']
    sets = {label: [r for r in rows if r['set'] == label] for label in ('old', 'new')}
    for label, rs in sets.items():
        c, e = Counter(r['result'] for r in rs), Counter(r['ended_by'] for r in rs)
        lines.append(f'| {label} | {len(rs)} | {c["win"]}/{c["loss"]}/{c["draw"]} | '+ ' / '.join(str(e[k]) for k in ('elimination','longer queen','longest dragon','total length','draw')) + f' | {sum(r["last_round"] for r in rs)/len(rs):.2f} |')
    lines += ['', '| Set / side | Queen alive end mean | Queen death round / length means (n) | Late death: own-longest yes / n; candidate length mean | Queen length r100 / r200 / r300 / r400 / end | Longest r300 / r400 / end | Alive r300 / r400 / end | Total end | Pearls ≤r100 / ≤r300 | Splits ≤r100 | Queen split turns |', '|---|---:|---|---|---|---|---|---:|---|---:|---:|']
    def mean(vs, denominator=False):
        vs = [v for v in vs if v is not None]
        return (f'{sum(vs)/len(vs):.2f}' + (f' (n={len(vs)})' if denominator else '')) if vs else '— (n=0)' if denominator else '—'
    for label, rs in sets.items():
        for s in SIDES:
            ss = [r['sides'][s] for r in rs]
            deaths = [z['queen']['death'] for z in ss if z['queen']['death']]
            late = [d['late_context'] for d in deaths if d['late_context']]
            curve = lambda key, marks: ' / '.join(mean([z[key][str(n)] for z in ss], n != 'end') for n in marks)
            q = ' / '.join(mean([z['queen']['length'][str(n)] for z in ss], n != 'end') for n in (*MARKS, 'end'))
            lines.append(f'| {label} / {s} | '+mean([z['queen']['alive_end'] for z in ss])+' | '+mean([d['round'] for d in deaths], True)+' / '+mean([d['length'] for d in deaths], True)+f' | {sum(c["is_own_longest"] for c in late)}/{len(late)}; '+mean([c['candidate_length_mean'] for c in late])+' | '+q+' | '+curve('longest',(300,400,'end'))+' | '+curve('dragons_alive',(300,400,'end'))+' | '+mean([z['total_length_end'] for z in ss])+' | '+curve('pearls_eaten',(100,300))+' | '+mean([z['splits_by_r100'] for z in ss])+' | '+mean([z['queen_split_turns'] for z in ss])+' |')
    lines += ['', '## B. Queen deaths (counts)', '', '| Cause or round band | Ours old | Ours new | Theirs old | Theirs new |', '|---|---:|---:|---:|---:|']
    ds = {(label,s): [r['sides'][s]['queen']['death'] for r in rs if r['sides'][s]['queen']['death']] for label, rs in sets.items() for s in SIDES}
    for cause in dossier.CAUSES:
        lines.append('| '+cause+' | '+' | '.join(str(sum(d['cause'] == cause for d in ds[label,s])) for s in SIDES for label in ('old','new'))+' |')
    for band, lo, hi in [('0–100',0,100),('101–300',101,300),('301–499',301,499)]:
        lines.append('| '+band+' | '+' | '.join(str(sum(lo <= d['round'] <= hi for d in ds[label,s])) for s in SIDES for label in ('old','new'))+' |')
    lines += ['', '## C. Per map (our side; old → new)', '', '| Map | Result | Queen end/death | Longest end | Alive r400 |', '|---|---|---|---|---|']
    def queen(z):
        q = z['queen']
        return f'alive L{q["length"]["end"]}' if q['alive_end'] else f'r{q["death"]["round"]} {q["death"]["cause"]}'
    for old in sets['old']:
        new = next(r for r in sets['new'] if r['map_id'] == old['map_id'])
        a, b = old['sides']['us'], new['sides']['us']
        lines.append(f'| {old["map"]} | {old["result"]} → {new["result"]} | {queen(a)} → {queen(b)} | {a["longest"]["end"]} → {b["longest"]["end"]} | {a["dragons_alive"]["400"] if a["dragons_alive"]["400"] is not None else "unreached"} → {b["dragons_alive"]["400"] if b["dragons_alive"]["400"] is not None else "unreached"} |')
    lines += ['', '## D. Count differences', '',
              'Neither set records a late queen death into our longest dragon: old has one death from r300 onward (Tower Defense r320, hit by an enemy L2), new has none. '
              'Our queens alive at the end rose from 2/15 to 4/15 (two games), theirs fell from 9/15 to 8/15 (one game), and our queen deaths at r0–100 fell from 9 to 3 while deaths at r101–300 rose from 3 to 8. '
              'Results stayed the same on 12 maps; Stripes, Default and Schooltime changed from win to loss, with no loss-to-win changes; elimination endings stayed at 4/15, while longest-dragon endings rose from 2 to 4 and longer-queen endings fell from 9 to 7 (two games each). '
              'Our per-game means changed from 125.00 to 114.13 pearls by r100, 436.13 to 426.27 by r300, 53.80 to 49.93 splits by r100, 3.13 to 4.33 queen split turns, and 32.07 to 23.53 longest length at the end.']
    assert len(lines) <= 60
    (OUT / 'table.md').write_text('\n'.join(lines)+'\n')
    print('Table lines:', len(lines))

if __name__ == '__main__':
    main()
