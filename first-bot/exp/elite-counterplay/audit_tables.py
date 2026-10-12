#!/usr/bin/env python3
"""Publish complete strata for the frozen population, without replay resampling.

Read only completed elite-counterplay caches. Writes new audit tables in this
study's cache directory. Death strata preserve cause AND phase; territory strata
preserve phase, eater side, and natural/death provenance. Reference strata use
all retained target team-games and show seats separately as well as combined.
The five independent replay recounts are in recount.js, not this formatter.
Run with guard.py; one computation process.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / '.cache/elite-counterplay'


def rows(name):
    with (C / name).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def avg(values):
    return statistics.mean(values) if values else None


def dump_csv(name, data):
    with (C / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def main():
    agg = json.loads((C / 'aggregate.json').read_text())
    games = list(rows('games.jsonl'))
    refs = list(rows('reference-games.jsonl'))
    primary = [g for g in games if g['era'] == 'primary']
    assert len(games) == 910 and len(primary) == 420 and len(refs) == 9321
    ds = defaultdict(list)
    ts = defaultdict(lambda: [0, 0, 0])
    counts = Counter()
    raid_rows = []
    for g in games:
        for map_key in [('map', g['map']), ('family', g['kind']), ('all', '*')]:
            base = (g['era'], g['oppId'], *map_key)
            counts[base] += 1
            for d in g['deaths']:
                ds[(*base, d['phase'], d['cause'])].append(d)
            for side, field in [('ours', 'stats'), ('theirs', 'enemyStats')]:
                for phase, p in enumerate(g[field]['intake']):
                    for origin in ['nat', 'drop']:
                        target = ts[(*base, side, phase, origin)]
                        for i, value in enumerate(p[origin]):
                            target[i] += value
        for d in g['deaths']:
            if d['king'] and d['cause'] == 'rammed':
                raid_rows.append(dict(key=g['key'], era=g['era'], opponent=g['oppId'], map=g['map'],
                                      round=d['r'], dragon=d['id'], kingLength=d['len'], killer=d['killerId'],
                                      killerLength=d['killerLen'], steps=d['killerSteps'], type='successful_king_ram'))
        for r in g['raids']:
            if r['approach']:
                raid_rows.append(dict(key=g['key'], era=g['era'], opponent=g['oppId'], map=g['map'],
                                      round=r['r'], dragon=r['kingId'], kingLength=r['kingLen'], killer=r['id'],
                                      killerLength=r['len'], steps=r['steps'], type='shorter_sprint_approach_proxy'))
    death_rows = []
    for base, values in sorted(ds.items()):
        era, team, level, label, phase, cause = base
        death_rows.append(dict(era=era, opponent=team, level=level, label=label, gameN=counts[base[:4]],
                               phase=phase, cause=cause, deathN=len(values),
                               substantiveKingN=sum(d['king'] for d in values),
                               killerLengthMean=avg([d['killerLen'] for d in values if d['killerLen'] is not None]),
                               **{k+'Mean': avg([d[k] for d in values]) for k in ['a3', 'e3', 'a8', 'e8', 'd3', 'd8']}))
    dump_csv('death-strata.csv', death_rows)
    territory_rows = []
    for base, values in sorted(ts.items()):
        era, team, level, label, side, phase, origin = base
        territory_rows.append(dict(era=era, opponent=team, level=level, label=label, gameN=counts[base[:4]],
                                   eater=side, phase=phase, origin=origin, own=values[0], neutral=values[1], enemy=values[2]))
    dump_csv('territory-phase.csv', territory_rows)
    dump_csv('raid-proxies.csv', raid_rows)
    ref_groups = defaultdict(list)
    for g in refs:
        for level, label in [('map', g['map']), ('family', g['kind']), ('all', '*')]:
            for seat in ['both', g['side']]:
                ref_groups[(g['oppId'], level, label, seat)].append(g)
    ref_rows = []
    for (team, level, label, seat), gs in sorted(ref_groups.items()):
        row = dict(opponent=team, level=level, label=label, seat=seat, N=len(gs),
                   W=sum(g['outcome'] == 'W' for g in gs), L=sum(g['outcome'] == 'L' for g in gs),
                   D=sum(g['outcome'] == 'D' for g in gs),
                   subjectEliminated=sum(g['A']['units'][-1] == 0 for g in gs),
                   otherEliminated=sum(g['B']['units'][-1] == 0 for g in gs),
                   subjectElimRoundMedian=statistics.median([g['rounds']-1 for g in gs if g['A']['units'][-1] == 0])
                   if any(g['A']['units'][-1] == 0 for g in gs) else None,
                   finalSubjectMean=avg([g['A']['longest'][-1] for g in gs]),
                   finalOtherMean=avg([g['B']['longest'][-1] for g in gs]))
        for label_side, field in [('subject', 'A'), ('other', 'B')]:
            for phase in range(5):
                row[f'{label_side}Nat_p{phase}'] = sum(g[field]['nat'][phase] for g in gs)
            for name in ['natOwn', 'natEnemy', 'natNeutral']:
                row[label_side+name] = sum(sum(g[field][name]) for g in gs)
        for sig in gs[0]['signature']:
            row[sig] = sum(g['signature'][sig] for g in gs)
        ref_rows.append(row)
    dump_csv('reference-strata.csv', ref_rows)
    auxiliary = {'primary': {}, 'byTeam': {}}
    for tid, gs in [('*', primary), *[(str(t), [g for g in primary if g['oppId'] == t])
                                     for t in [306, 70, 20, 801, 264, 46, 545]]]:
        deaths = [d for g in gs for d in g['deaths']]
        rams = [d for d in deaths if d['cause'] == 'rammed']
        kr = [d for d in rams if d['king']]
        item = dict(N=len(gs), kingDeathCauses=dict(Counter(d['cause'] for d in deaths if d['king'])),
                    rammedKillerAtMost3=sum(d['killerLen'] <= 3 for d in rams),
                    kingRammedKillerAtMost4=sum(d['killerLen'] <= 4 for d in kr),
                    ramPhases=[sum(d['phase'] == p for d in rams) for p in range(5)],
                    kingRamPhases=[sum(d['phase'] == p for d in kr) for p in range(5)],
                    approachingRaidProxyN=sum(r['approach'] for g in gs for r in g['raids']),
                    variants=dict(Counter(g['map']+'/'+str(g['variant']) for g in gs)))
        if tid == '*': auxiliary['primary'] = item
        else: auxiliary['byTeam'][tid] = item
    auxiliary['sourceRead'] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [ROOT/'exp/cand-stack10/bot/plan.cpp', ROOT/'exp/cand-stack10/bot/plan.hpp',
                  ROOT/'exp/cand-stack10/bot/params.hpp']}
    (C / 'auxiliary.json').write_text(json.dumps(auxiliary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'online': len(games), 'primary': len(primary), 'referenceTeamGames': len(refs),
                      'deathStrata': len(death_rows), 'territoryStrata': len(territory_rows),
                      'referenceStrata': len(ref_rows), 'primaryAux': auxiliary['primary']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
