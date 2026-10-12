"""Scratch (diag-longest): recount with the shared reader (tools/ladder_replay.py scan) against lg_scan / lg_far rows.
python3 lg_check.py <tag>   tag = m1 m2 m3 b1 b2 q1. Compares per game: who won, how it was decided, the longest of both
sides at the end of rounds 100..499, alive and total at 300/400/499 (also against lg_far), deaths by no valid action per
side and century, and the peak-against-final class of lost race games."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
LABELS = dict(m1='agg7-m1', m2='agg7-m2', m3='agg7-m3', b1='agg7-b1', b2='agg7-b2', q1='agg8-q1')


def main():
    tag = sys.argv[1]
    mine = dict((g['game'], g) for g in (json.loads(l) for l in (WORK / ('lg_scan-%s.jsonl' % tag)).read_text().splitlines() if l))
    far = dict((g['game'], g) for g in (json.loads(l) for l in (WORK / ('lg_far-%s.jsonl' % tag)).read_text().splitlines() if l))
    folder = Path('data/online/smoke') / (LABELS[tag] + '-new')
    n = bad = 0
    cells = dict(snap=0, far=0, noact=0, cls=0)
    diffs = []
    never = had = 0
    for rp in sorted(folder.glob('M*.replay')):
        gid = int(rp.stem[1:])
        j = json.loads((folder / ('game-%d.json' % gid)).read_text())
        s = ladder_replay.scan(rp, j, folder.name, set())
        g = mine[gid]
        n += 1
        ours = s['ours']
        win = None if s['winner'] is None else int(s['winner'] == ours)
        fin = s['final']
        if not fin['us']['alive'] or not fin['them']['alive']:
            dec = 'elimination'
        elif fin['us']['queen_length'] != fin['them']['queen_length']:
            dec = 'queen'
        elif fin['us']['longest'] != fin['them']['longest']:
            dec = 'longest'
        else:
            dec = 'total'
        ok = win == g['win'] and dec == g['decided']
        snaps = s['snapshots']
        last = s['last_round']
        for r in (100, 150, 200, 250, 300, 350, 400, 450, 499):
            rr = min(r, last)
            a = snaps[rr] if rr in snaps else None
            b = g['snaps'][min(r, len(g['snaps']) - 1)]
            if a is None:
                continue
            cells['snap'] += 1
            if (a['us']['longest'], a['them']['longest'], a['us']['alive'], a['them']['alive'], a['us']['total'], a['them']['total']) != (b[0], b[1], b[4], b[5], b[6], b[7]):
                ok = False
                diffs.append((gid, 'snap', r, a['us'], b[:8]))
        f = far.get(gid)
        if f:
            for r in ('300', '400'):
                m = f['marks'].get(r)
                if m and int(r) in snaps:
                    for k, side in enumerate(('us', 'them')):
                        if m[k]:
                            cells['far'] += 1
                            a = snaps[int(r)][side]
                            if (a['longest'], a['alive'], a['total']) != (m[k][0], m[k][1], m[k][2]):
                                ok = False
                                diffs.append((gid, 'far', r, side, a, m[k][:3]))
        cnt = [[0] * 5 for _ in (0, 1)]
        for d in s['deaths']:
            if d['reason'] == 4:
                cnt[0 if d['side'] == 'us' else 1][min(d['round'] // 100, 4)] += 1
        for k in (0, 1):
            for bk in range(5):
                cells['noact'] += 1
                if cnt[k][bk] != sum(g['deaths'][k][bk][5:8]):
                    ok = False
                    diffs.append((gid, 'noact', k, bk, cnt[k][bk], g['deaths'][k][bk][5:8]))
        bqd = g['qdeath'][0] is not None and g['qdeath'][1] is not None
        qa = (ladder_replay_queen_dead(s, 'us'), ladder_replay_queen_dead(s, 'them'))
        if (qa[0] and qa[1]) != bqd:
            ok = False
            diffs.append((gid, 'queens', qa, g['qdeath']))
        if win == 0 and dec in ('longest', 'total'):
            cells['cls'] += 1
            pk = max(v['us']['longest'] for r, v in snaps.items() if r >= 150)
            if pk > fin['them']['longest']:
                had += 1
            else:
                never += 1
        if not ok:
            bad += 1
    print(tag, 'games', n, 'with any difference', bad, 'cells compared', cells, 'lost on longest or total: peak above their final', had, 'never', never)
    for d in diffs[:10]:
        print('   ', d)


def ladder_replay_queen_dead(s, side):
    return any(d['id'] == s['queens'][side] for d in s['deaths'])


main()
