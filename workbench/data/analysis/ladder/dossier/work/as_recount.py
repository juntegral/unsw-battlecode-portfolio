"""Scratch (diag-aahsplit): independent recount. Lengths only (no board): for every turn of a studied-side dragon that
starts 4 long or longer, did it split, by own dragons alive. Compared with as_scan rows of the same games.
Usage: python3 as_recount.py <tag a|q> <every n-th game>"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'


def cls(a):
    return 0 if a < 32 else 1 if a < 44 else 2 if a < 48 else 3 if a < 52 else 4 if a < 56 else 5 if a < 60 else 6


def recount(path, focus_is_a):
    root = replay.load(path).root()
    length = {}
    team = {}
    n = 0
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            length[n] = int(q[2])
            team[n] = int(q[1])
            n += 1
    mine = 0 if focus_is_a else 1
    c = Counter()
    actor = None
    start_len = 0
    start_alive = 0
    did_split = False
    names = replay.EVENT_NAMES

    def close():
        if actor is not None and team.get(actor, team_of_actor) == mine and start_len >= 4:
            k = ('L4' if start_len == 4 else 'L5', cls(start_alive))
            c[k + ('t',)] += 1
            c[k + ('s',)] += int(did_split)
    team_of_actor = -1
    for ev in root.pointer(3):
        name = names[ev.u16(0)]
        p = ev.pointer(0)
        if name in ('roundStart', 'turnStart'):
            close()
            actor = None
        if name == 'turnStart':
            actor = p.i32(0)
            team_of_actor = team[actor]
            start_len = length[actor]
            start_alive = sum(1 for i in length if team[i] == team_of_actor)
            did_split = False
        elif name == 'dragonSplit':
            parent, child = p.i32(0), p.i32(4)
            a = len(list(p.pointer(0)))
            b = len(list(p.pointer(1)))
            assert a + b == length[parent]
            length[parent] = a
            length[child] = b
            team[child] = team[parent]
            if parent == actor:
                did_split = True
        elif name == 'dragonDeath':
            i = p.i32(0)
            length.pop(i)
        elif name == 'tileChange':
            if p.u32(0) == 0 and actor is not None:
                length[actor] += 1
        elif name == 'dragonAction':
            a = p.pointer(0)
            if a and a.u16(0) == 0 and a.pointer(0) is not None and actor in length:
                steps = len(list(a.pointer(0)))
                pay_from = (length[actor] + 3) // 4
                length[actor] -= max(0, steps - pay_from)
        elif name == 'dragonUpdate':
            pass
    close()
    return c


def main():
    tag, nth = sys.argv[1], int(sys.argv[2])
    idx = [json.loads(x) for x in Path(WORKREL + 'as_index.jsonl').read_text().splitlines()]
    if tag == 'a':
        todo = [(r, r['a'] == 454) for r in idx if 'online/top3' in r['src'] and 454 in (r['a'], r['b'])]
    else:
        todo = [(r, r['a'] == 1119) for r in idx if 'agg8-q1-new' in r['src']]
    todo = [x for z, x in enumerate(todo) if z % nth == 0]
    gids = set(r['gid'] for r, f in todo)
    mine = Counter()
    for r, f in todo:
        mine.update(recount(Path(r['path']), f))
    ref = Counter()
    for line in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines():
        g = json.loads(line)
        if g['gid'] not in gids:
            continue
        for row in g['rows']:
            k = ('L4' if row[2] == 4 else 'L5', cls(min(row[3], 63)))
            ref[k + ('t',)] += 1
            ref[k + ('s',)] += int(row[16] >= 2)
    print(tag, len(todo), 'games; class of own dragons alive: under 32, 32-43, 44-47, 48-51, 52-55, 56-59, 60+')
    for L in ('L4', 'L5'):
        print('  %s recount: ' % L + ' | '.join('%d/%d = %.1f%%' % (mine[L, k, 's'], mine[L, k, 't'], 100.0 * mine[L, k, 's'] / max(1, mine[L, k, 't'])) for k in range(7)))
        print('  %s scanner: ' % L + ' | '.join('%d/%d = %.1f%%' % (ref[L, k, 's'], ref[L, k, 't'], 100.0 * ref[L, k, 's'] / max(1, ref[L, k, 't'])) for k in range(7)))


main()
