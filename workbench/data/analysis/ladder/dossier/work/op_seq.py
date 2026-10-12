# Scratch (diag-opening): round-by-round curves, rounds 0-60, ours against rank-1 (followed side), from op_scan-*.jsonl.
# A value is the mean inside a layout, then the mean over layouts (equal weight); "hi" = layouts where rank-1 is higher.
# Also by group of starting configuration. Usage: python3 data/analysis/ladder/dossier/work/op_seq.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
FILES = ['op_scan-O0.jsonl', 'op_scan-O1.jsonl', 'op_scan-O2.jsonl', 'op_scan-O3.jsonl',
         'op_scan-R0.jsonl', 'op_scan-R1.jsonl', 'op_scan-R2.jsonl', 'op_scan-R3.jsonl']
ROUNDS = (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60)


def load():
    games = []
    for f in FILES:
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


def val(g, sd, name, r):
    if name == 'contact %':
        if g['last_round'] < r:
            return None
        return 100.0 if sd['contact'] is not None and sd['contact'] <= r else 0.0
    if name == 'fed %':
        if g['last_round'] < r:
            return None
        return 100.0 if any(d[2] is not None and d[2] <= r for d in sd['dragons']) else 0.0
    if name == 'split %':
        if g['last_round'] < r:
            return None
        return 100.0 if any(s[0] <= r for s in sd['splits']) else 0.0
    if name == 'adv':
        v = sd['series']['toward']
        if len(v) <= r or v[r] < 0 or g['sep'] >= 9999:
            return None
        return g['sep'] - v[r]
    if name == 'seen %':
        v = sd['series']['seen']
        return 100.0 * v[r] / g['cells'] if len(v) > r else None
    v = sd['series'][name]
    if len(v) <= r or v[r] < 0:
        return None
    return v[r] / 10 if name in ('meand', 'spread', 'cd') else v[r]


def curves(games, layouts, title):
    lines = ['', '== ' + title + ' (%d layouts) ==' % len(layouts)]
    lines.append('%-10s' % 'round' + ''.join('%7d' % r for r in ROUNDS))
    for name in ('alive', 'total', 'eaten', 'split %', 'fed %', 'contact %', 'seen %', 'front', 'meand', 'adv', 'spread', 'cd', 'qd', 'ql'):
        rows = {tag: [] for tag in ('O', 'R', 'hi', 'n')}
        for r in ROUNDS:
            acc = defaultdict(list)
            for g in games:
                if g['layout'] not in layouts:
                    continue
                v = val(g, g['sides']['u'], name, r)
                if v is not None:
                    acc[(g['who'], g['layout'])].append(v)
            both = [l for l in layouts if acc.get(('O', l)) and acc.get(('R', l))]
            if not both:
                for tag in rows:
                    rows[tag].append(None)
                continue
            mo = [sum(acc[('O', l)]) / len(acc[('O', l)]) for l in both]
            mr = [sum(acc[('R', l)]) / len(acc[('R', l)]) for l in both]
            rows['O'].append(sum(mo) / len(mo))
            rows['R'].append(sum(mr) / len(mr))
            rows['hi'].append(sum(1 for a, b in zip(mo, mr) if b > a + 1e-9))
            rows['n'].append(len(both))
        fmt = lambda v, f: '%7s' % '-' if v is None else f % v
        lines.append('%-10s' % (name + ' O') + ''.join(fmt(v, '%7.1f') for v in rows['O']))
        lines.append('%-10s' % (name + ' R') + ''.join(fmt(v, '%7.1f') for v in rows['R']))
        lines.append('%-10s' % '  R hi' + ''.join(fmt(v, '%7d') for v in rows['hi']) + '   of ' + str(max(v for v in rows['n'] if v is not None)))
    return lines


def main():
    games = load()
    layouts = sorted({g['layout'] for g in games})
    cfg = {}
    for g in games:
        cfg[g['layout']] = tuple(g['sides']['u']['cfg'])
    lines = curves(games, layouts, 'all layouts')
    groups = defaultdict(list)
    for l in layouts:
        c = cfg[l]
        key = 'starts with a dragon of 4+' if max(c) >= 4 else 'starts all short (2-3)'
        groups[key].append(l)
    for key, ls in sorted(groups.items()):
        lines += curves(games, ls, key + ': ' + ', '.join(ls))
    body = '\n'.join(lines) + '\n'
    Path(OUT + 'op_seq.txt').write_text(body)
    print(body)


main()
