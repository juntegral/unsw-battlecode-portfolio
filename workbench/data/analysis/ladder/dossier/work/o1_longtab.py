import json, sys, os
from collections import Counter
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
OURS = ('20850', '20880', '20910')
G = []
for nm in ('w1', 'd1', 'o2', 'o3', 'o3d', 'live'):
    p = W + 'o1_long-%s.jsonl' % nm
    if not os.path.exists(p):
        print('missing', nm); continue
    for l in open(p):
        g = json.loads(l)
        if g['bot'] in OURS:
            g['set'] = nm
            G.append(g)
ids = set()
G = [g for g in G if not (g['gid'] in ids or ids.add(g['gid']))]
print('games', len(G), Counter(g['bot'] for g in G))
T = [Counter(), Counter()]
for g in G:
    for s in (0, 1):
        T[s].update(g['T'][s])
for s, nm in ((0, 'ours'), (1, 'theirs')):
    t = T[s]; n = max(1, t['turns'])
    print('%s 20+ after r300: turns %d (queen %d) | steps a turn %.2f, no move %.1f%% | mates within 5: %.1f | enemy head within 5 on %.1f%% of turns, within 3 on %.1f%%, in view %.1f%% | ends inside free+1 reach of a head in view %.2f%% | deaths %d: rammed %d, as rammer %d, other %d | rammed per 1000 turns %.1f, per 100 turns with a head within 3: %.1f' % (
        nm, t['turns'], t['queen turns'], t['steps'] / n, 100 * t['still'] / n, t['mates5'] / n, 100 * t['foe5'] / n, 100 * t['foe3'] / n, 100 * t['foe in view'] / n,
        100 * t['ends in free+1 reach of a head in view'] / n, t['deaths'], t['death rammed'], t['death as rammer'], t['death other'], 1000 * t['death rammed'] / n, 100 * t['death rammed'] / max(1, t['foe3'])))
for s, nm in ((0, 'OURS rammed'), (1, 'THEIRS rammed by us')):
    R = [(g, r) for g in G for r in g['rams'] if r['s'] == s]
    c = Counter()
    print('==', nm, len(R), '(queen %d)' % sum(r['q'] for g, r in R))
    for g, r in R:
        la = r['last'] or {}
        paid = r['rammer_steps'] - r['rammer_free']
        c['n'] += 1
        c['rammer L<=4'] += r['rammer_L'] <= 4
        c['rammer paid'] += paid > 0
        c['rammer steps 1'] += r['rammer_steps'] == 1; c['rammer steps 2'] += r['rammer_steps'] == 2; c['rammer steps 3+'] += r['rammer_steps'] >= 3
        c['rammer in view one turn before'] += r['in_view1']
        c['rammer in view two turns before'] += r['in_view2'] == 1
        c['d1<=2'] += r['d1'] <= 2; c['d1 3-4'] += 3 <= r['d1'] <= 4; c['d1 5+'] += r['d1'] >= 5
        if la:
            c['has last'] += 1
            c['rammer seen at her last turn'] += la['rammer_seen']
            c['she did not move'] += la['used'] == 0
            c['boxed: no free tile'] += la['open1'] == 0
            c['ended inside free reach'] += la['end_free']
            c['ended inside free+1 reach (plain veto flags it)'] += la['end_pay1']
            c['.. and a first step outside free+1 reach was open'] += la['end_pay1'] and la['clean1_pay1'] > 0
            c['.. and some tile within her free steps was outside'] += la['end_pay1'] and la['clean_pay1'] > 0
            c['ended inside full reach'] += la['end_full']
            c['.. and a tile outside full reach was open'] += la['end_full'] and la['clean_full'] > 0
            c['no enemy head in her view at her last turn'] += len(la['foes']) == 0
        c['a mate within 5'] += len(r['mates']) > 0
        c['a mate of 4 or less with the rammer in reach'] += any(m[3] for m in r['mates'])
        if s == 0 or len(R) <= 40:
            print('  %s %d %-14s r%d %s L%d%s | rammer L%d %d steps (free %d) from %s steps, in view %d; two turns before %s steps, in view %s | her last turn: %s | mates<=5 %s' % (
                g['set'], g['gid'], g['map'][:14], r['r'], 'QUEEN' if r['q'] else 'leader' if r['top'] else 'long', r['L'], '', r['rammer_L'], r['rammer_steps'], r['rammer_free'], r['d1'], r['in_view1'], r['d2'], r['in_view2'],
                ('moved %d, open first steps %d, rammer seen %d (parts %d), heads in view %s, ended in free/free+1/full reach %d/%d/%d, clean first step (free+1 rule) %d of %d, clean tile in her free steps %d of %d (full rule %d)' % (
                    la['used'], la['open1'], la['rammer_seen'], la['rammer_parts'], [(f[1], f[2]) for f in la['foes']], la['end_free'], la['end_pay1'], la['end_full'], la['clean1_pay1'], la['open1'], la['clean_pay1'], la['cand'], la['clean_full'])) if la else 'none',
                [(m[0], m[1], m[2] if m[2] < 99 else '-', m[3]) for m in r['mates']]))
    for k, v in c.items():
        print('    %-52s %d' % (k, v))
