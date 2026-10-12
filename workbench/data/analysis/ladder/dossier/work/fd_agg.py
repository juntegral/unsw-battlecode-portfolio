# Scratch (diag-feeding): one row per main game that reaches the start of our feeding. Reads fd_scan-*.jsonl,
# writes fd_games.jsonl and prints the tables of jobs 1 to 4.
# Start of feeding S (main.cpp 4919-4922, 522-527): the earliest of
#   cap   first round after 200 in which one of our dragons starts its turn with 56 or more of ours alive,
#   q300  round 301 when our queen is alive at the start of round 301 (she sets queen_game at round 300 and it spreads by sonar),
#   r400  round 401.
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
G = []
for k in range(4):
    G += [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open()]
G.sort(key=lambda g: g['game'])


def strict(d):
    return d['tgt'] >= 0 and d['L'] * 2 <= d['tgt_len'] and not d['q']


def chain(u, t):
    # u, t = (alive, longest, total, queen length)
    if u[0] == 0 or t[0] == 0:
        return ('elim', 'us' if u[0] > 0 else 'them' if t[0] > 0 else 'tie')
    for name, k in (('queen', 3), ('longest', 1), ('total', 2)):
        if u[k] != t[k]:
            return (name, 'us' if u[k] > t[k] else 'them')
    return ('tie', 'tie')


rows = []
for g in G:
    s = g['series']
    last = g['last_round']
    cap = g['cap_rounds'][0] if g['cap_rounds'] else None
    q300 = len(s) > 301 and s[301][3] > 0
    caps = set(g['cap_rounds'])
    # evidence of the queen-game start: a feeder dies in r301-400 in a round in which the 56 rule is off
    seen300 = [d['r'] for d in g['feeders'] if strict(d) and 300 < d['r'] <= 400 and d['r'] not in caps]
    cands = []
    if cap is not None and cap <= 400:
        cands.append((cap, 'cap'))
    if seen300 or (q300 and g['cells'] > 600):
        cands.append((301, 'q300'))
    cands.append((401, 'r400'))
    S, kind = min(cands)
    if last < S:
        continue
    a = s[S]
    f = g['final']
    U, T = (a[0], a[1], a[2], a[3]), (a[5], a[6], a[7], a[8])
    Ue, Te = (f[0], f[1], f[2], f[3]), (f[5], f[6], f[7], f[8])
    feed = [d for d in g['feeders'] if strict(d) and d['r'] >= S]
    early = [d for d in g['feeders'] if strict(d) and 150 < d['r'] < S]
    other_noact = [d for d in g['feeders'] if not strict(d) and d['r'] >= S]
    deaths = [d for d in g['our_deaths'] if d['r'] >= S]
    tg = Counter()
    for d in feed:
        tg[d['tgt']] += d['np']
    main_tgt = tg.most_common(1)[0][0] if tg else a[4]
    lead_ids = set([a[4]] + [i for i, n in tg.items() if n >= 3])
    lead_deaths = []
    for d in deaths + other_noact:
        if (d['top'] and d['L'] >= 8) or (d['id'] in lead_ids and d['L'] >= 8):
            lead_deaths.append(dict(r=d['r'], id=d['id'], L=d['L'], cause=d['cause'], o_side=d.get('o_side'), o_len=d.get('o_len'),
                                    mover=d['mover'], q=d['q'], top=d['top'], rest=d['rest'], n_left=d['n_side'], x=d['x'], y=d['y'],
                                    was_S_top=int(d['id'] == a[4]), main_tgt=int(d['id'] == main_tgt)))
    lead_deaths.sort(key=lambda d: d['r'])
    peak, peak_r = max((s[r][1], -r) for r in range(S, last + 1))
    peak = max(peak, f[1])
    dc = Counter()
    dl = Counter()
    for d in deaths:
        c = d['cause']
        if c in ('headon', 'body'):
            c += '-' + ('them' if d.get('o_side') == 't' else 'us' if d.get('o_side') == 'u' else '?')
        dc[c] += 1
        dl[c] += d['L']
    for d in other_noact:
        dc['noact-other'] += 1
        dl['noact-other'] += d['L']
    te = Counter()
    for r, v in g['top_eat'].items():
        if int(r) >= S:
            for k2, n in v.items():
                te[k2] += n
    qe = Counter()
    for r, v in g['queen_eat'].items():
        if int(r) >= S:
            for k2, n in v.items():
                qe[k2] += n
    sp = sum(n for b, n in g['split_bins']['u'].items() if int(b) * 25 + 1 >= S)
    at = chain(U, T)
    row = dict(game=g['game'], battle=g['battle'], layout=g['layout'], cells=g['cells'], rating=g['rating'], opp=g['opponent'],
               result=g['result'], ended_by=g['ended_by'], qend=g['queens_at_end'], last=last, S=S, kind=kind, cap=cap,
               ncap=len(g['cap_rounds']), q300=int(q300), U=U, T=T, Ue=Ue, Te=Te, at=at,
               ahead_all=int(at[1] == 'us' and U[3] >= T[3] and U[1] > T[1] and U[2] > T[2]),
               peak=peak, peak_r=-peak_r, top_S=a[4], top_end=f[4], main_tgt=main_tgt, tgt_is_queen=int(main_tgt == g['queen']['u']),
               n_feed=len(feed), feed_L=sum(d['L'] for d in feed), feed_np=sum(d['np'] for d in feed),
               e_tgt=sum(d['e_tgt'] for d in feed), e_top=sum(d['e_top'] for d in feed), e_us=sum(d['e_us'] for d in feed),
               e_them=sum(d['e_them'] for d in feed), n_early=len(early), first_feed=min([d['r'] for d in feed], default=None),
               last_feed=max([d['r'] for d in feed], default=None), feed_q=sum(1 for d in feed if d['tgt_q']),
               dc=dict(dc), dl=dict(dl), lead_deaths=lead_deaths, top_ate=dict(te), queen_ate=dict(qe), splits=sp,
               mid={str(r): s[r][:4] + s[r][5:9] for r in (201, 301, 401, 451, 476) if r <= last})
    rows.append(row)

body = '\n'.join(json.dumps(r, separators=(',', ':')) for r in rows) + '\n'
Path(OUT + 'fd_games.jsonl').write_text(body)
print('main games', len(G), 'reach feeding start', len(rows))
print('by start kind', Counter(r['kind'] for r in rows))
print('result by kind', Counter((r['kind'], r['result']) for r in rows))
print('ended_by x result', sorted(Counter((r['ended_by'], r['result']) for r in rows).items()))
print('games with any feeder death', sum(r['n_feed'] > 0 for r in rows), 'feeder deaths', sum(r['n_feed'] for r in rows))
