"""Scratch (diag-aahsplit): the report tables in compact form.
Usage: python3 as_final.py <tag> [<tag> ...]"""
import sys
import json
from collections import Counter
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
CN = ('<32', '32-43', '44-47', '48-51', '52-55', '56-59', '60-63')


def cc(a):
    return 0 if a < 32 else 1 if a < 44 else 2 if a < 48 else 3 if a < 52 else 4 if a < 56 else 5 if a < 60 else 6


def grp(L):
    return 0 if L <= 3 else 1 if L == 4 else 2 if L <= 8 else 3


def per(a, b, k=1000.0):
    return '%.1f' % (k * a / b) if b else '-'


def main():
    for tag in sys.argv[1:]:
        games = [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]
        n = len(games)
        S = [s for g in games for s in g['splits']]
        print('== %s: %d games, won %d; splits a game %.1f; at exactly 4 %.1f%%; head boxed %.1f%%; of splits of 5+: child of 2 %.1f%%, parent keeps 2 %.1f%%; queen splits a game %.1f' % (
            tag, n, sum(1 for g in games if g['won'] == 1), len(S) / n, 100.0 * sum(1 for s in S if s[2] == 4) / len(S), 100.0 * sum(1 for s in S if s[8] == 0) / len(S),
            100.0 * sum(1 for s in S if s[2] > 4 and s[3] == 2) / max(1, sum(1 for s in S if s[2] > 4)),
            100.0 * sum(1 for s in S if s[2] > 4 and s[4] == 2) / max(1, sum(1 for s in S if s[2] > 4)), sum(1 for s in S if s[6]) / n))
        for bn, lo, hi in (('0-20', 0, 20), ('21-60', 21, 60), ('61-150', 61, 150), ('151-300', 151, 300), ('301+', 301, 999)):
            sel = [s for s in S if lo <= s[0] <= hi]
            if sel:
                m = len(sel)
                print('   rounds %-8s splits a game %5.1f | at 4: %4.1f%% | 5-8: %4.1f%% | 9+: %4.1f%% | boxed %4.1f%% | child 2 off 5+: %4.1f%% | keeps 2: %4.1f%% | mean parent %.2f child %.2f' % (
                    bn, m / n, 100.0 * sum(1 for s in sel if s[2] == 4) / m, 100.0 * sum(1 for s in sel if 5 <= s[2] <= 8) / m, 100.0 * sum(1 for s in sel if s[2] >= 9) / m,
                    100.0 * sum(1 for s in sel if s[8] == 0) / m, 100.0 * sum(1 for s in sel if s[2] > 4 and s[3] == 2) / m, 100.0 * sum(1 for s in sel if s[2] > 4 and s[4] == 2) / m,
                    sum(s[2] for s in sel) / m, sum(s[3] for s in sel) / m))
        c = Counter()
        for g in games:
            for r in g['rows']:
                sp = int(r[16] >= 2)
                if r[3] >= 64:
                    k = 'cap'
                elif r[6] == 0:
                    k = 'boxed'
                elif r[4]:
                    k = 'queen'
                elif r[10] == 1:
                    k = 'pearl'
                else:
                    k = cc(r[3])
                    c['L4' if r[2] == 4 else 'L5', k, 't'] += 1
                    c['L4' if r[2] == 4 else 'L5', k, 's'] += sp
                    if r[13] == 0:
                        c['first', k, 't'] += 1
                        c['first', k, 's'] += sp
                c[k, 't'] += 1
                c[k, 's'] += sp
        print('   boxed head: %.1f turns a game, split %s%% | pearl beside (head free, not queen): %.1f turns, split %s%% | queen at 4+, head free: %.1f turns, split %s%% | at 64: %.1f turns' % (
            c['boxed', 't'] / n, per(c['boxed', 's'], c['boxed', 't'], 100.0), c['pearl', 't'] / n, per(c['pearl', 's'], c['pearl', 't'], 100.0),
            c['queen', 't'] / n, per(c['queen', 's'], c['queen', 't'], 100.0), c['cap', 't'] / n))
        print('   head free, not queen, no pearl beside, by own dragons alive: splits per 100 turns (turns a game)')
        print('      all 4+ : ' + ' | '.join('%s: %s (%.0f)' % (CN[k], per(c[k, 's'], c[k, 't'], 100.0), c[k, 't'] / n) for k in range(7)))
        print('      at 4   : ' + ' | '.join('%s: %s' % (CN[k], per(c['L4', k, 's'], c['L4', k, 't'], 100.0)) for k in range(7)))
        print('      5+     : ' + ' | '.join('%s: %s' % (CN[k], per(c['L5', k, 's'], c['L5', k, 't'], 100.0)) for k in range(7)))
        print('      first turn at a length: ' + ' | '.join('%s: %s' % (CN[k], per(c['first', k, 's'], c['first', k, 't'], 100.0)) for k in range(7)))
        for nm, bands in (('r61-300', (2, 3)), ('all', (0, 1, 2, 3, 4))):
            T = Counter()
            for g in games:
                for key, v in g['T'].items():
                    W, L, name = key.split('|')
                    if int(W) in bands:
                        T[grp(int(L)), name] += v
                        T['L', int(L), name] += v
            tot = sum(T[z, 't'] for z in range(4))
            print('   by length, %s: turns %%; 2+ steps %%; pearls /1k; deaths /1k; rammed /1k; rams started /1k; boxed-in deaths /1k; length lost /1k' % nm)
            for z, gn in enumerate(('2-3', '4', '5-8', '9+')):
                t = T[z, 't']
                if t:
                    two = T[z, 'n2'] + T[z, 'n3'] + T[z, 'n4']
                    print('      %-4s %5.1f; %5.1f; %6.1f; %5.1f; %5.2f; %5.2f; %5.1f; %6.1f' % (gn, 100.0 * t / tot, 100.0 * two / t, 1000.0 * T[z, 'e'] / t, 1000.0 * T[z, 'd'] / t,
                          1000.0 * T[z, 'dv'] / t, 1000.0 * T[z, 'da3e'] / t, 1000.0 * T[z, 'dab'] / t, 1000.0 * T[z, 'll'] / t))
            if nm == 'r61-300':
                print('      rammed /1k turns by exact length: ' + ' '.join('%d: %s' % (L, per(T['L', L, 'dv'], T['L', L, 't'])) for L in range(2, 10)))
                print('      all deaths /1k turns by exact length: ' + ' '.join('%d: %s' % (L, per(T['L', L, 'd'], T['L', L, 't'])) for L in range(2, 10)))
            S2 = Counter()
            for g in games:
                for key, v in g['SP'].items():
                    W, G, paid, name = key.split('|')
                    if int(W) in bands and G == '2' and paid == '0':
                        S2[name] += v
            nn = S2['n']
            if nn:
                print('      free two-step turns of 5-8, %s: %.0f a game | two pearls %s%% | ends on its only pearl %s%% | eats on step 1 and goes on %s%% | away from an enemy head within 3 %s%% | nearer to one within 5 %s%% | nearer to a pearl in view %s%% | a pearl comes into view %s%% | nothing %s%% | ram %s%% | straight %s%%' % (
                    nm, nn / n, per(S2['eat2'], nn, 100.0), per(S2['endp'], nn, 100.0), per(S2['eatgo'], nn, 100.0), per(S2['esc'], nn, 100.0), per(S2['app'], nn, 100.0),
                    per(S2['topearl'], nn, 100.0), per(S2['found'], nn, 100.0), per(S2['plain'], nn, 100.0), per(S2['ram'], nn, 100.0), per(S2['straight'], nn, 100.0)))
        # our-side counts for the card
        free = [(g, s) for g in games for s in g['splits'] if s[8] > 0 and not s[6]]
        for N in (48, 52, 56):
            sel = [(g, s) for g, s in free if N <= s[5] < 60]
            print('   voluntary splits (head free, not queen) at %d-59 own dragons: %d (%.1f a game, in %d games); before round 201: %.1f a game; on boards above 1,200 cells %.0f%%; parent of exactly 4 %.0f%%; child dead in 3 rounds %.1f%%, parent %.1f%%' % (
                N, len(sel), len(sel) / n, len(set(g['gid'] for g, s in sel)), sum(1 for g, s in sel if s[0] <= 200) / n,
                100.0 * sum(1 for g, s in sel if g['w'] * g['h'] > 1200) / max(1, len(sel)), 100.0 * sum(1 for g, s in sel if s[2] == 4) / max(1, len(sel)),
                100.0 * sum(s[21] for g, s in sel) / max(1, len(sel)), 100.0 * sum(s[20] for g, s in sel) / max(1, len(sel))))


main()
