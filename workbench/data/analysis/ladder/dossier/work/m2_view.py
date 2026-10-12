"""Scratch (diag-med20): one game turn by turn from m2_scan-*.jsonl; for ours the rebuilt score of every step on offer.
Usage: python3 m2_view.py <game id> <side 0|1> [dragon id or -1] [last round]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
FILES = ('m2_scan-T3.jsonl', 'm2_scan-O.jsonl', 'm2_scan-test.jsonl')
NAMES = 'NESW'
TERMS = ('centre', 'room', 'terr', 'cramped', 'pearl', 'soon', 'hot', 'unseen', 'portal', 'far', 'eat', 'look', 'mate', 'pocket', 'sc', 'queen')


def tb(d, wt):
    return 0.0 if d < 0 else max(0.0, wt * (260 - 40 * d))


def parts(row, o, k):
    dest, room, terr, tailhit, dp, ds, dh, du, dpo, dk, eat, sc, pocket, look, mate, cd, pk, kr, dsa, dpa = o
    L, r = row['L'], row['r']
    cr = 0.0
    want = 3.0 * L + 8.0
    if room < want:
        cr += 400.0 * (want - room)
    if room < L + 2.0:
        cr += 5000.0 * (L + 2.0 - room)
    if not tailhit:
        cr += 600.0
    t = dict.fromkeys(TERMS, 0.0)
    t['room'] = 1.5 * room
    t['terr'] = 1.5 * terr
    t['cramped'] = -cr
    if row['isq']:
        q = 0.0
        if ((not tailhit) and room < want) or room < L + 8:
            q += 6000.0
        if kr > 0:
            q += 6000.0 + 400.0 * kr
        t['queen'] = -q
    cand = (('pearl', tb(dp, 2.0)), ('soon', tb(ds, 0.45)), ('hot', tb(dh, 1.2)), ('unseen', tb(du, 0.2)), ('portal', tb(dpo, 0.4)))
    name, val = max(cand, key=lambda kv: kv[1])
    if val > 0:
        t[name] = val
    far = [x for x in (dp, ds, dh, du) if x >= 0]
    if far:
        t['far'] = 2.0 * max(0, 80 - min(far))
    grown = L + eat
    full = pocket < 48 and grown > pocket // 2
    if full:
        t['pocket'] = -1000.0 * (grown - pocket // 2)
    if eat and not full:
        t['eat'] = 300.0
    if sc:
        t['sc'] = -300.0
    if mate:
        t['mate'] = -450.0
    t['look'] = look
    if pk == 1:
        t['portal'] -= 150.0
    t['tie'] = 0.25 * ((row['i'] * 31 + r * 17 + k * 7) % 5)
    return t


def scores(row):
    out, ps = [None] * 4, [None] * 4
    base = None
    blind = []
    for k, o in enumerate(row['o']):
        if o is None:
            continue
        if len(o) == 2:
            blind.append(k)
            continue
        t = parts(row, o, k)
        ps[k] = t
        out[k] = sum(t.values())
        if o[16] == 0:
            b = out[k] - t['tie'] - max(t['pearl'], t['soon'], t['hot'], t['unseen'], max(t['portal'], 0.0))
            if base is None or b > base:
                base = b
    for k in blind:
        if base is not None:
            out[k] = base + 88.0 + 0.25 * ((row['i'] * 31 + row['r'] * 17 + k * 7) % 5)
            ps[k] = dict(blind=out[k])
    return out, ps


def main():
    gid, side = int(sys.argv[1]), int(sys.argv[2])
    only = int(sys.argv[3]) if len(sys.argv) > 3 else -1
    last = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    for f in FILES:
        p = WORK / f
        if not p.exists():
            continue
        g, on = None, False
        for line in p.read_text().splitlines():
            if not line:
                continue
            r = json.loads(line)
            if r['k'] == 'g':
                if on:
                    return
                on = r['gid'] == gid
                g = r
                if on:
                    print(g['map'], g['w'], g['h'], 'studied', g['name'], 'vs', g['opp'], 'arm', g['arm'], 'starters', g['starters'])
                continue
            if not on or r['s'] != side:
                continue
            w = g['w']
            xy = lambda t: '(%d,%d)' % (t % w, t // w)
            if r['k'] == 'p':
                if r['r'] <= last and (only < 0 or r['i'] == only):
                    print('      ATE r%d #%d at %s born r%d nat %d first seen by it r%d by side r%d from-start %d portal-line %d step %d' % (r['r'], r['i'], xy(r['t']), r['born'], r['nat'], r['fsd'], r['fss'], r['down'], r['pc'], r['step']))
                continue
            if r['r'] > last or (only >= 0 and r['i'] != only):
                continue
            act = 'split' if r['act'] == 's' else ('move ' + ''.join(NAMES[d] for d in r.get('dirs', [])) if r['act'] == 'm' else 'none')
            tw = ''
            if r['act'] == 'm':
                for nm, a, b in (('pearl-in-view', 'dpv', 'dpv2'), ('any-pearl', 'dpa', 'dpa2'), ('spawn', 'dsp', 'dsp2'), ('soon10', 'dsn', 'dsn2'), ('own-unseen', 'du', 'du2'),
                                 ('team-unseen', 'dut', 'dut2'), ('mouth', 'dma', 'dma2'), ('centre', 'cd', 'cd2'), ('enemy', 'des', 'des2')):
                    if r[a] >= 0 and r[b] >= 0 and r[b] < r[a]:
                        tw += ' ' + nm
            print('r%-2d #%-2d %s L%d at %s face %s free %d | pearls %d (d %d) soon %d (d %d in %d) spawn tiles %d mouths %d (d %d) | unseen own %d team %d | spawn d %d soon10 d %d mouth d %d | %s%s%s -> nearer:%s'
                  % (r['r'], r['i'], r['ro'], r['L'], xy(r['h']), NAMES[r['fc']] if r['fc'] >= 0 else '?', r['fr'], r['np'], r['dpv'], r['nso'], r['dso'], r['cso'], r['nsp'], r['nmo'], r['dmo'],
                     r['du'], r['dut'], r['dsp'], r['dsn'], r['dma'], act, ' PORTAL' if r['ps'] else '', ' ATE' if r['ate'] else '', tw))
            if 'o' in r:
                sc, ps = scores(r)
                for k in range(4):
                    if sc[k] is None:
                        continue
                    t = ps[k]
                    if 'blind' in t:
                        print('        %s %8.1f blind portal step' % (NAMES[k], sc[k]))
                    else:
                        print('        %s %8.1f ' % (NAMES[k], sc[k]) + ' '.join('%s %.0f' % (n, v) for n, v in t.items() if abs(v) >= 0.5) + ' tie %.2f' % t['tie'])


main()
