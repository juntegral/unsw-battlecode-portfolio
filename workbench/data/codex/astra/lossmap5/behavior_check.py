import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
from collections import Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
import o1_mid

OUT = Path(__file__).resolve().parent
G = [json.loads(l) for l in (OUT/'games.jsonl').read_text().splitlines()]
A = {g['gid']: g for g in G if g['bucket'] == 'a' and g['label'] != 'one5-d1'}
rows = []
for name in ('o5', 'c5'):
    for line in Path(f'data/analysis/ladder/dossier/work/o1_mid-{name}.jsonl').read_text().splitlines():
        g = json.loads(line)
        if g['gid'] not in A:
            continue
        assert g['bot'] == '20980'
        assert g['snaps']['100'] == [[A[g['gid']]['snapshots']['100'][s][k] for k in ('alive', 'total')] for s in ('us', 'them')] if A[g['gid']]['last_round'] >= 100 else True
        sides = [Counter(), Counter()]
        for s, w, k, v in g['C']:
            if s < 2 and w == 0:
                sides[s][k] += v
        rows.append(dict(gid=g['gid'], map=g['map'], turns=[c['turns'] for c in sides],
                         away=[c['away'] for c in sides], adjacent_away=[c['away d1'] for c in sides],
                         blind=[c['blind'] for c in sides]))
assert len(rows) == 11
(OUT/'early_behavior.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')

moments = []
for gid in (1472007, 1472010, 1472015):
    g = next(g for g in G if g['gid'] == gid)
    captured = {}
    def profile(frame, event, arg):
        if frame.f_code.co_name != 'close' or frame.f_code.co_filename != o1_mid.__file__:
            return
        if event == 'call':
            cur = frame.f_locals.get('cur')
            if cur:
                captured[id(frame)] = dict(cur)
        elif event == 'return':
            cur = captured.pop(id(frame), None)
            if not cur or cur['s'] != 0 or cur.get('d') != 1 or frame.f_locals.get('key') != 'away':
                return
            if cur.get('foe') or cur.get('exits', 0) <= 0:
                return
            end = frame.f_locals['bodies'][cur['i']][0]
            moments.append(dict(gid=gid, map=g['map'], round=cur['r'], id=cur['i'], length=cur['L'],
                                start=cur['h0'], pearl=cur['tgt'], end=end, mate_tie=cur['tie'],
                                exits=cur['exits'], cls='adjacent own pearl not approached',
                                context=cur.get('d1ctx', 'queen')))
    o1_mid.LAST = 100
    meta = json.loads(Path(g['path']).with_name(f'game-{gid}.json').read_text())
    sys.setprofile(profile)
    counted = o1_mid.scan(g['label'], Path(g['path']), meta)
    sys.setprofile(None)
    cached = next(json.loads(l) for l in Path('data/analysis/ladder/dossier/work/o1_mid-o5.jsonl').read_text().splitlines() if json.loads(l)['gid'] == gid)
    assert [r for r in counted['C'] if r[1] == 0] == [r for r in cached['C'] if r[1] == 0]
    print(gid, [m for m in moments if m['gid'] == gid], flush=True)
(OUT/'moments.json').write_text(json.dumps(moments, ensure_ascii=False, indent=2)+'\n')
print('away higher rate', sum(r['away'][0]*r['turns'][1] > r['away'][1]*r['turns'][0] for r in rows))
print('adjacent nonapproach games', sum(r['adjacent_away'][0] > 0 for r in rows))
