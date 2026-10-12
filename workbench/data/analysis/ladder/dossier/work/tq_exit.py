"""Scratch (diag-theirqueen): did she walk out or was she pushed out? Every queen death in open-start games, by where it
happened against R = min(8, (w + h) // 8) and how she last left the radius.
inside  = died at most R+2 tiles from her start.
pushed  = on the turn she last stepped out of R, or on one of the 3 turns before it, an enemy head (not the queen) was within 5 steps.
walked  = no enemy head within 5 steps on those turns.
Usage: python3 tq_exit.py [online|ladder] [list]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

W = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q'}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    tags = ('m1', 'm2', 'b1', 'b2', 'q1') if mode == 'online' else ('L0', 'T0')
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    c = defaultdict(Counter)
    gaps = defaultdict(list)
    bymap = defaultdict(Counter)
    for g in games:
        R = min(8, (g['w'] + g['h']) // 8)
        for s in (0, 1):
            if g['scomp'][s] * 2 < g['cells']:
                continue
            if mode == 'online':
                who = ARM[g['label']] + ' ours' if s == 0 else ('Bob' if g['opp'].startswith('Big') else 'Quiz')
            else:
                who = ('ours ladder', 'ladder opp')[s] if g['label'] == 'ladder' else ('rank1', 'rank1 opp')[s]
            keys = [who] + (['ALL ours'] if s == 0 and mode == 'online' else [])
            recs = g['recs'][s]
            f = g['fate'][s]
            for k in keys:
                c[k]['games'] += 1
            # every exit from R during the game: walked or pushed
            for n, t in enumerate(recs):
                if t[3] <= R and t[23] >= 0:
                    nxt = recs[n + 1] if n + 1 < len(recs) else None
                    if nxt is not None and nxt[3] > R:
                        pushed = any(x[31] > 0 for x in recs[max(0, n - 3):n + 1])
                        for k in keys:
                            c[k]['exit_pushed' if pushed else 'exit_walked'] += 1
            if f is None:
                for k in keys:
                    c[k]['alive'] += 1
                continue
            kind = 'self' if f['own_move'] else 'ram'
            if f['ds'] <= R + 2:
                cls = 'inside'
                gap = 0
            else:
                last = max((n for n, t in enumerate(recs) if t[3] <= R), default=None)
                if last is None:
                    cls, gap = 'walked', f['r']
                else:
                    pushed = any(x[31] > 0 for x in recs[max(0, last - 3):last + 1])
                    cls = 'pushed' if pushed else 'walked'
                    gap = f['r'] - recs[last][0]
            for k in keys:
                c[k][kind + ' ' + cls] += 1
                c[k][cls] += 1
                c[k]['dead'] += 1
                if cls != 'inside':
                    gaps[k, cls].append(gap)
                    c[k][cls + ' gap>=10'] += 1 if gap >= 10 else 0
                    lost = g['win'] is None or (g['win'] == 1) != (s == 0)
                    c[k][cls + ' lost'] += 1 if lost else 0
                    c[k][cls + ' lostq'] += 1 if lost and g['decided'] == 'queen' else 0
            if s == 0 or mode != 'online':
                bymap[who.split(' ')[-1] if mode == 'online' else who, g['map']][cls] += 1
            if 'list' in sys.argv and s == 0 and mode == 'online':
                print('  %d %-5s %-14s %2dx%-2d R%d r%-3d %-4s %-6s %2d tiles out, %3d rounds after leaving' % (
                    g['game'], ARM[g['label']], g['map'][:14], g['w'], g['h'], R, f['r'], kind, cls, f['ds'], gap))
    for k in sorted(c):
        x = c[k]
        gw, gp = gaps[k, 'walked'], gaps[k, 'pushed']
        print('%-11s games %3d alive %3d dead %3d | inside R+2: %2d (ram %d, own move %d) | walked out: %2d (ram %d, own move %d; median %s rounds after leaving, %d of them 10+; lost %d, on queen length %d) | pushed out: %2d (ram %d, own move %d; median %s) | exits from R in all: walked %d, pushed %d' % (
            k, x['games'], x['alive'], x['dead'], x['inside'], x['ram inside'], x['self inside'], x['walked'], x['ram walked'], x['self walked'],
            int(median(gw)) if gw else '-', x['walked gap>=10'], x['walked lost'], x['walked lostq'], x['pushed'], x['ram pushed'], x['self pushed'],
            int(median(gp)) if gp else '-', x['exit_walked'], x['exit_pushed']))
    if mode == 'online':
        print('ours by layout: inside / walked / pushed')
        for (who, m), x in sorted(bymap.items()):
            if who == 'ours':
                print('   %-18s %d / %d / %d' % (m[:18], x['inside'], x['walked'], x['pushed']))


main()
