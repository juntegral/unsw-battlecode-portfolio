"""Scratch (diag-topaah): a pearl beside the head after round 100: taken or not, by who else is beside it (ta_s4-*.jsonl).
Row columns: 0 round, 1 length, 2 queen, 3 mover is the side's longest, 4 longest length, 5 tiles mover to longest, 6 tiles pearl to longest,
7 own dragons alive, 8 origin (0 natural 1 own dead 2 their dead), 9 enemy head within 2 of the pearl, 10 room behind the pearl (cap 20),
11 action (0 ate 1 split 2 stepped elsewhere 3 died), 12 cells, 13 turns since last meal or birth, 14 own heads also beside the pearl,
15 one of them acts earlier, 16 one acts later, 17 enemy heads beside it, 18 tiles to nearest enemy head (cap 9), 19 pearls beside the head,
20 free tiles beside the head, 21 pearl age, 22 dragon id, 23 head tile, 24 pearl tile, 25 pearl through a portal, 26 head tile after the turn.
Usage: python3 ta_s4agg.py            tables for every tag
       python3 ta_s4agg.py trace <tag> <gid> [n]   declined turns of one game with coordinates"""
import sys
import json
from collections import Counter
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TAGS = ('q', 'm', 't', 'a', 'l', 'c1', 'g')


def plain(r):
    """Not the queen, not the side's longest, no enemy head within 2 of the pearl, room of 3L+8 or more, pearl not through a portal."""
    return not r[2] and not r[3] and not r[9] and r[10] >= 3 * r[1] + 8 and not r[25]


def roomclass(r):
    return 'a nook' if r[10] == 0 else 'b under L+2' if r[10] < r[1] + 2 else 'c under 3L+8' if r[10] < 3 * r[1] + 8 else 'd 3L+8 or more'


def tab(rows, name, f):
    c, t = Counter(), Counter()
    for r in rows:
        k = f(r)
        c[k] += 1
        t[k] += r[11] == 0
    print('   %-42s %s' % (name, '  '.join('%s: %.0f%% of %d' % (k, 100 * t[k] / c[k], c[k]) for k in sorted(c, key=str))))


def win(r):
    return '101-200' if r[0] <= 200 else '201-300' if r[0] <= 300 else '301-400' if r[0] <= 400 else '401+'


def age(r):
    return '0' if r[21] == 0 else '1' if r[21] == 1 else '2-3' if r[21] <= 3 else '4-9' if r[21] <= 9 else '10+'


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'trace':
        tag, gid = sys.argv[2], int(sys.argv[3])
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 40
        gs = [json.loads(x) for x in Path(WORK + 'ta_s4-' + tag + '.jsonl').read_text().splitlines() if x.strip()]
        g = [x for x in gs if x['gid'] == gid][0]
        w = g['w']
        shown = 0
        for r in g['rows']:
            if r[11] == 2 and plain(r) and r[14] == 0 and r[18] >= 4:
                print('r%d dragon %d len %d head (%d,%d) pearl (%d,%d) age %d origin %d -> head after (%d,%d); longest %d long at %d tiles (pearl %d from it); alive %d; free tiles beside head %d; pearls beside %d; turns since meal %d' % (
                    r[0], r[22], r[1], r[23] % w, r[23] // w, r[24] % w, r[24] // w, r[21], r[8], r[26] % w, r[26] // w, r[4], r[5], r[6], r[7], r[20], r[19], r[13]))
                shown += 1
                if shown >= n:
                    break
        return
    for tag in TAGS:
        p = Path(WORK + 'ta_s4-' + tag + '.jsonl')
        if not p.exists():
            continue
        gs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        rows = [r for g in gs for r in g['rows']]
        n = len(rows)
        took = sum(1 for r in rows if r[11] == 0)
        print('==', tag, 'games', len(gs), 'turns with a pearl beside the head (round 101+):', n, 'taken %.1f%%' % (100 * took / max(1, n)), 'not taken a game %.0f' % ((n - took) / len(gs)))
        tab(rows, 'own heads also beside the pearl', lambda r: min(r[14], 2))
        tab(rows, 'a mate beside it acts later (higher id)', lambda r: r[16])
        tab(rows, 'enemy heads beside the pearl', lambda r: min(r[17], 1))
        tab(rows, 'tiles to nearest enemy head', lambda r: min(r[18], 7))
        tab(rows, 'pearl through a portal', lambda r: r[25])
        tab(rows, 'pearl age in rounds', age)
        tab(rows, 'free tiles beside the head', lambda r: r[20])
        tab(rows, 'room behind the pearl (head tile shut)', roomclass)
        base = [r for r in rows if not r[2] and not r[3] and not r[9] and not r[25] and r[14] == 0 and r[18] >= 4 and r[20] >= 2]
        tab(base, 'lone, a choice, by room behind the pearl', roomclass)
        pl = [r for r in rows if plain(r)]
        print('  plain turns (not queen, not longest, no enemy within 2, room 3L+8, no portal): %d, taken %.1f%%' % (len(pl), 100 * sum(1 for r in pl if r[11] == 0) / max(1, len(pl))))
        tab(pl, 'plain: own heads beside the pearl', lambda r: min(r[14], 2))
        tab(pl, 'plain: nearest enemy head', lambda r: min(r[18], 7))
        tab(pl, 'plain: pearl age', age)
        tab(pl, 'plain: length', lambda r: min(r[1], 5))
        tab(pl, 'plain: window', win)
        alone = [r for r in pl if r[14] == 0 and r[18] >= 4]
        print('  plain, no mate beside the pearl, no enemy head within 3: %d, taken %.1f%%, not taken a game %.1f' % (len(alone), 100 * sum(1 for r in alone if r[11] == 0) / max(1, len(alone)), sum(1 for r in alone if r[11] != 0) / len(gs)))
        tab(alone, 'alone: action 0 ate 1 split 2 other 3 died', lambda r: r[11])
        tab(alone, 'alone: window', win)
        tab(alone, 'alone: pearl origin 0 nat 1 own 2 foe', lambda r: r[8])
        tab(alone, 'alone: tiles to own longest', lambda r: '0-9' if r[5] <= 9 else '10-15' if r[5] <= 15 else '16+')
        tab(alone, 'alone: pearl tiles to longest', lambda r: '0-9' if r[6] <= 9 else '10+')
        tab(alone, 'alone: own dragons alive', lambda r: '<40' if r[7] < 40 else '40-55' if r[7] < 56 else '56+')
        tab(alone, 'alone: cells', lambda r: 'small' if r[12] <= 1200 else 'big')
        tab(alone, 'alone: pearl age', age)
        tab(alone, 'alone: turns since meal', lambda r: '0-1' if r[13] <= 1 else '2-5' if r[13] <= 5 else '6-20' if r[13] <= 20 else '21+')
        tab(alone, 'alone: free tiles beside the head', lambda r: r[20])
        tab(alone, 'alone: length', lambda r: min(r[1], 5))


main()
