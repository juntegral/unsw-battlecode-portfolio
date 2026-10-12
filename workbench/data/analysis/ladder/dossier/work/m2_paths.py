"""Scratch (diag-med20): the walk of every dragon in rounds 0-20, one line per dragon, from m2_scan-*.jsonl.
Letters: N E S W the first step of a turn (lower case = a second step follows), s split, P after a step = through a portal,
* ate, m = a portal mouth is in the 7 by 7 at the turn start (shown once, with path steps to it), ! died.
Usage: python3 m2_paths.py <layout prefix> <group prefix or all> [A|B] [max games per group]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict

WORK = Path('data/analysis/ladder/dossier/work')
FILES = ('m2_scan-T3.jsonl', 'm2_scan-O.jsonl')
TOP = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse'}
NAMES = 'NESW'


def group(g, side):
    if g['src'] == 'T3':
        return TOP.get(g['team'], '?') if side == 0 else 'top opp'
    if g['label'].startswith('top-l'):
        return 'B7Q direct' if side == 0 else 'direct ' + TOP.get(g['oppid'], str(g['oppid']))
    return g['arm'] if side == 0 else 'ladder opp'


def main():
    lay, want = sys.argv[1], sys.argv[2]
    letter = sys.argv[3] if len(sys.argv) > 3 else ''
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 99
    shown = defaultdict(int)
    for f in FILES:
        p = WORK / f
        if not p.exists():
            continue
        g, rows = None, []

        def flush():
            if g is None or not g['map'].startswith(lay):
                return
            w = g['w']
            for s in (0, 1):
                grp = group(g, s)
                if want != 'all' and not grp.startswith(want):
                    continue
                tl = 'AB'[g['own'] if s == 0 else 1 - g['own']]
                if letter and tl != letter:
                    continue
                if shown[(grp, tl)] >= cap:
                    continue
                shown[(grp, tl)] += 1
                m20 = g['marks'].get('20', [[0] * 14, [0] * 14])[s]
                print('%s %s game %d side %s vs %s | by r20: pearls %d alive %d portal steps %d' % (grp, g['map'], g['gid'], tl, g['opp'] if s == 0 else g['name'], m20[2], m20[0], m20[9]))
                per = defaultdict(list)
                for r in rows:
                    if r['s'] == s:
                        per[r['i']].append(r)
                for i in sorted(per):
                    v = per[i]
                    first = v[0]
                    out = []
                    seen_m = False
                    for r in v:
                        tok = ''
                        if r['nmo'] > 0 and not seen_m:
                            seen_m = True
                            tok += '[r%d m%d]' % (r['r'], r['dmo'])
                        if r['act'] == 's':
                            tok += 's'
                        elif r['act'] == 'm':
                            c = NAMES[r['dir']] if r['dir'] >= 0 else '?'
                            tok += c.lower() if r['ns'] >= 2 else c
                            if r['ps']:
                                tok += 'P'
                            if r['ate']:
                                tok += '*' * r['ate']
                        else:
                            tok += '-'
                        if 'died' in r:
                            tok += '!'
                        out.append(tok)
                    print('   #%-2d %s born r%-2d at (%d,%d) len %d: %s' % (i, first['ro'], first['born'], first['h'] % w, first['h'] // w, first['L'], ' '.join(out)))
        for line in p.read_text().splitlines():
            if not line:
                continue
            r = json.loads(line)
            if r['k'] == 'g':
                flush()
                g, rows = r, []
            elif r['k'] == 't':
                rows.append(r)
        flush()


main()
