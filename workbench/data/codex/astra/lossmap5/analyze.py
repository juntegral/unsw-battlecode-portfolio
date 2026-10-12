import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import hashlib
from datetime import datetime
from collections import Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/online', 'data/analysis/ladder/dossier/work']
import label_report
import ladder_replay
import o1_scan

OUT = Path(__file__).resolve().parent

def snapshot(g, r):
    if r < 0:
        return g['initial']
    return g['snapshots'][str(min(r, g['last_round']))]

def classify(g):
    e, u, t = g['final'], snapshot(g, 150), snapshot(g, 300)
    if not e['us']['alive'] or not e['them']['alive']:
        how = 'elim'
    elif e['us']['queen_length'] != e['them']['queen_length']:
        how = 'queen'
    elif e['us']['longest'] != e['them']['longest']:
        how = 'longest'
    else:
        how = 'total'
    result = 'draw' if g['winner'] is None else 'win' if g['winner'] == g['ours'] else 'loss'
    bucket = result
    if result == 'loss':
        if how == 'elim' or u['us']['alive'] * 2 < u['them']['alive']:
            bucket = 'a'
        elif how == 'queen' and e['us']['queen_length'] == 0 and t['us']['total'] >= .8 * t['them']['total']:
            bucket = 'b'
        elif how == 'longest':
            bucket = 'c'
        else:
            bucket = 'd'
    measure = {'elim': 'alive', 'queen': 'queen_length', 'longest': 'longest', 'total': 'total'}[how]
    def last_level(m):
        return max((int(r) for r, s in g['snapshots'].items() if s['us'][m] >= s['them'][m]), default=-1)
    g.update(how=how, result=result, bucket=bucket, measure=measure,
             last_level=last_level(measure), last_count_level=last_level('alive'))

def main():
    existing = {g['gid']: g for g in (json.loads(l) for l in (OUT/'games.jsonl').read_text().splitlines())} if (OUT/'games.jsonl').exists() else {}
    manifest = []
    temporary = OUT/'games.complete.jsonl'
    with temporary.open('w') as handle:
        for label in ('one5-w1', 'one5-c1', 'one5-d1'):
            inv = label_report.inventory(label, 'old')
            assert len(inv['jobs']) == 15, (label, inv['notes'])
            for path, meta in inv['jobs']:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                root = ladder_replay.replay.load(path).root()
                initial_lengths = {'us': [], 'them': []}
                ours = 'A' if meta['teamAId'] == 1119 else 'B'
                for line in root.text(0).splitlines():
                    q = line.split()
                    if q and q[0] == 'DRAGON':
                        initial_lengths['us' if 'AB'[int(q[1])] == ours else 'them'].append(int(q[2]))
                initial = {s: dict(alive=len(ls), total=sum(ls), longest=max(ls), queen_length=ls[0]) for s, ls in initial_lengths.items()}
                manifest.append(dict(label=label, gid=meta['id'], path=str(path), sha256=digest, inventory_notes=inv['notes']))
                if meta['id'] in existing:
                    g = existing[meta['id']]
                    assert g['label'] == label and g['bots'][ours] == '20980'
                    g['initial'] = initial
                    classify(g)
                    handle.write(json.dumps(g, ensure_ascii=False) + '\n')
                    continue
                g = ladder_replay.scan(path, meta, label, set())
                ledger = o1_scan.scan(label, path, meta)
                w, h = map(int, g.pop('text').splitlines()[0].split()[1:3])
                g.update(cells=w*h, width=w, height=h, label=label, path=str(path), initial=initial,
                         splits=ledger['splits'], paid=ledger['paids'], ledger_deaths=ledger['deaths'],
                         ledger_eats=ledger['eats'])
                for rnd, pair in ledger['snaps'].items():
                    for s, values in zip(('us', 'them'), pair):
                        assert values[:4] == [g['snapshots'][int(rnd)][s][k] for k in ('alive', 'total', 'longest', 'queen_length')]
                assert len(g['deaths']) == len(g['ledger_deaths'])
                for d, ld in zip(g['deaths'], g['ledger_deaths']):
                    assert [d['round'], int(d['side'] == 'them'), d['length']] == ld[:3]
                    d.update(detail=ld[4], free_exits=ld[5], queen=bool(ld[6]), mates5=ld[8], foes5=ld[9])
                assert not g['anomalies'], (g['gid'], g['anomalies'])
                g['snapshots'] = {str(r): s for r, s in g['snapshots'].items()}
                classify(g)
                assert g['how'] == ledger['how'] and g['result'] == ledger['result']
                assert g['winner'].lower() == meta['winner']
                for k in ('pearls', 'natural', 'intervals', 'eaten_rounds', 'ledger_deaths'):
                    g.pop(k)
                handle.write(json.dumps(g, ensure_ascii=False) + '\n')
                handle.flush()
                print(label, g['gid'], g['map'], g['result'], g['bucket'], g['how'], g['last_level'], flush=True)
    assert len(manifest) == 45
    temporary.replace(OUT/'games.jsonl')
    (OUT/'manifest.json').write_text(json.dumps(dict(measured_at=datetime.now().astimezone().isoformat(), games=manifest), ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
