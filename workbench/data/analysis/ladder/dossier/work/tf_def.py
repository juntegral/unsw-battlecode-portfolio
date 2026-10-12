"""Scratch (diag-topfight): rams suffered, by where the victim ended its own last turn and what rammed it.
Usage: python3 tf_def.py <file> [file...]"""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad gdp', 91: 'SSS', 264: 'forgot', 842: 'horse', 1119: 'ours'}
STUDY = {'T3': {454, 157, 306, 70}, 'T1': {306, 91, 264, 842, 454}}


def grp(rec, s):
    team = rec['a'] if s == 0 else rec['b']
    lab = rec['label']
    if lab in STUDY:
        return '%s:%s' % (lab, NAMES.get(team, team)) if team in STUDY[lab] else lab + ':opp'
    return lab + (':us' if team == 1119 else ':' + str(NAMES.get(team, 'opp')) if lab == 'OT' else ':opp')


def main():
    G = defaultdict(lambda: dict(games=0, c=Counter(), n=0, big=Counter()))
    seen = set()
    pair = sys.argv[1] == 'p'
    for f in sys.argv[2:]:
        p = Path(f)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if (r['label'], r['game']) in seen:
                continue
            seen.add((r['label'], r['game']))
            gs = [grp(r, 0), grp(r, 1)]
            if pair:
                gs = [gs[0] + '>' + str(NAMES.get(r['b'], r['b'])), gs[1] + '>' + str(NAMES.get(r['a'], r['a']))]
            for s in (0, 1):
                G[gs[s]]['games'] += 1
            for h in r['hos']:
                if not h['cross']:
                    continue
                g = G[gs[1 - h['ms']]]
                g['n'] += 1
                vc = 'queen' if h['vk'] == 1 else '2-4' if h['Lv'] <= 4 else '5-7' if h['Lv'] <= 7 else '8+'
                mc = 'by2' if h['L0'] <= 2 else 'by3-4' if h['L0'] <= 4 else 'by5+'
                own = (h['L0'] + 3) // 4 + h['L0'] - 2
                how = 'pearl' if h['k'] > own else 'paid' if h['k'] > (h['L0'] + 3) // 4 else 'free'
                st = {2: 'in-free', 1: 'in-paid', 0: 'outside', -1: 'no-turn'}[h['vs']]
                g['c'][(vc, st, 'safe' if h['vsafe'] else 'nosafe' if h['vs'] > 0 else '-', mc, how)] += 1
                g['big'][(vc, st, 'safe' if h['vsafe'] else 'nosafe' if h['vs'] > 0 else '-')] += 1
    for k in sorted(G):
        g = G[k]
        if not g['n']:
            continue
        print('==', k, 'games', g['games'], 'rams suffered a game %.1f' % (g['n'] / g['games']))
        for vc in ('2-4', '5-7', '8+', 'queen'):
            tot = sum(n for (v, st, sf), n in g['big'].items() if v == vc)
            if not tot:
                continue
            print('  victim %-5s %.2f/g: ' % (vc, tot / g['games']) + ' | '.join('%s %s %.2f' % (st, sf, n / g['games']) for (v, st, sf), n in sorted(g['big'].items(), key=lambda t: -t[1]) if v == vc))
            det = [(key, n) for key, n in g['c'].items() if key[0] == vc]
            det.sort(key=lambda t: -t[1])
            print('        top: ' + ' ; '.join('%s/%s/%s/%s %.2f' % (key[1], key[2], key[3], key[4], n / g['games']) for key, n in det[:8]))


main()
