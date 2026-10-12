#!/usr/bin/env python3
"""Stage 2: classify the FULL frozen population and freeze deep-read selection.

Only elite-counterplay outputs are written. One process, streaming input ledgers.
Loss classes are mutually exclusive in the priority below; signatures overlap.
Never uses a sample. All denominators and exclusion keys are preserved.
Run after BOTH extraction passes and recount complete using guard.py.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json
import statistics
import csv
import sys

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / '.cache/elite-counterplay'
CODE = ROOT / 'exp/elite-counterplay'
MAN = json.loads((C / 'manifest.json').read_text())
NAMES = {int(k): v for k, v in MAN['names'].items()}
FL = ['eat_nat', 'eat_oSac', 'eat_oTrap', 'eat_oRammed', 'eat_oRam', 'eat_oOther', 'eat_eSac', 'eat_eTrap', 'eat_eRammed', 'eat_eRam', 'eat_eOther',
      'keat_nat', 'keat_oSac', 'keat_oTrap', 'keat_oRammed', 'keat_oRam', 'keat_oOther', 'keat_eSac', 'keat_eTrap', 'keat_eRammed', 'keat_eRam', 'keat_eOther',
      'nat_own', 'nat_enemy', 'nat_neutral', 'nat_fOwn', 'nat_fEnemy', 'spr_n', 'spr_ram', 'spr_eat', 'spr_esc', 'spr_other',
      *['dl_' + x for x in ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath']],
      *['dn_' + x for x in ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath']],
      'ram_elen', 'rammed_elen', 'bk_n', 'bk_len', 'trapE_n', 'trapE_len', 'split_n', 'split_child', 'split_stub', 'turns', 'kd_n', 'kd_len', 'eatTC']
FI = {v: i for i, v in enumerate(FL)}
BINS = [(0, 10), (10, 25), (25, 35), (35, 45), (45, 50)]
CLASSES = ['E1', 'E2', 'E3', 'E4', 'K5', 'I6', 'C7', 'G8']
CLASS_NAMES = {'E1': 'r100 이전 전멸', 'E2': '최장 피격 직후 전멸', 'E3': '중반 소모 전멸',
               'E4': '후반 소모 전멸', 'K5': '후반 최장 피격·생존 패배', 'I6': '섭취 열세·생존 패배',
               'C7': '집중 열세·생존 패배', 'G8': '기타 성장 경주 패배'}

def write(name, obj):
    (C / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def rows(name):
    with (C / name).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def phases(a):
    return [sum(a[i:j]) for i, j in BINS]

def side(g, t):
    v = g[t]
    def f(name):
        return v['fl'][FI[name]]
    kr, ks, kings, kl, killer, contacts, contact_own, contact_enemy = 0, 0, 0, 0, 0, 0, 0, 0
    for key, a in v['ct'].items():
        role, _, _, phase, sprint, king = key.split('|')
        contacts += a[0]
        contact_own += a[3] + a[5]
        contact_enemy += a[4] + a[6]
        if role == 'rammed' and king == '1':
            kr += a[0]
            ks += a[0] if sprint == '1' else 0
            kl += a[1]
            killer += a[2]
    for key, a in v['dt'].items():
        if key.split('|')[3] == '1':
            kings += a[0]
    return {'units': v['st']['units'], 'longest': v['st']['king'], 'total': v['st']['total'],
            'nat': phases(f('eat_nat')), 'natOwn': phases(f('nat_own')),
            'natEnemy': phases(f('nat_enemy')), 'natNeutral': phases(f('nat_neutral')),
            'ownSacEaten': phases(f('eat_oSac')), 'kingOwnSacEaten': phases(f('keat_oSac')),
            'splitPhase': phases(f('split_n')), 'splits': v['splits'], 'sonar': v['sonar'],
            'rammed': sum(f('dn_rammed')), 'trapEnemy': sum(f('trapE_n')), 'kingDeaths': kings,
            'kingRams': kr, 'kingSprint': ks, 'ramKingLen': kl, 'ramKillerLen': killer,
            'contacts': contacts, 'contactOwnEats': contact_own, 'contactEnemyEats': contact_enemy,
            'sacDeaths': sum(f('dn_sac')), 'sacLength': sum(f('dl_sac')), 'line': v.get('lin'),
            'lineSac350': (v.get('lin') or {}).get('cp', {}).get('350', {}).get('eat', [0, 0])[1],
            'ownSacEat350': sum(f('eat_oSac')[35:])}

def loss_class(g):
    u, e = g['U'], g['E']
    if g['outcome'] != 'L':
        return g['outcome']
    er = g['elim']
    hostile = [d for d in g['deaths'] if d['king'] and
               (d['cause'] in ['rammed', 'enemyBody'] or d['cause'] == 'trap' and d['enemyBlock'])]
    if er is not None:
        if er < 100:
            return 'E1'
        if any(d['r'] >= er - 30 for d in hostile):
            return 'E2'
        return 'E3' if er < 300 else 'E4'
    if any(d['r'] >= 400 for d in hostile):
        return 'K5'
    if sum(e['nat']) >= 1.5 * max(1, sum(u['nat'])) and sum(e['nat']) - sum(u['nat']) >= 20:
        return 'I6'
    if u['total'][-1] >= e['longest'][-1] > u['longest'][-1]:
        return 'C7'
    return 'G8'

def signatures(a, b, rounds):
    raid_den = sum(a['natEnemy']) + sum(b['natOwn'])
    return {'swarm50': a['units'][5] >= 8 and a['units'][5] >= 2 * max(1, b['units'][5]),
            'homeRaid': sum(a['natEnemy']) >= 10 and sum(a['natEnemy']) >= .3 * raid_den,
            'kingRam': b['kingRams'] >= 1, 'sprintKingRam': b['kingSprint'] >= 1,
            'lateResupply': rounds >= 350 and sum(a['splitPhase'][2:]) >= 20,
            'kingFeed': rounds == 500 and a['longest'][-1] >= 20 and sum(a['kingOwnSacEaten'][2:]) >= 10}

def mean(v):
    return sum(v) / len(v) if v else None

def med(v):
    return statistics.median(v) if v else None

def table(gs):
    ds = [d for g in gs for d in g['deaths']]
    rams = [d for d in ds if d['cause'] == 'rammed']
    king_rams = [d for d in rams if d['king']]
    behavior = {kind: {k: sum(g.get('behavior', {}).get(kind, {}).get(k, 0) for g in gs) for k in ['n', 'alive10']}
                for kind in ['retreat', 'stay', 'approach', 'split', 'other']}
    return {'N': len(gs), 'W': sum(g['outcome'] == 'W' for g in gs), 'L': sum(g['outcome'] == 'L' for g in gs),
            'D': sum(g['outcome'] == 'D' for g in gs), 'eliminated': sum(g['elim'] is not None for g in gs),
            'elimMedian': med([g['elim'] for g in gs if g['elim'] is not None]),
            'finalUsMean': mean([g['U']['longest'][-1] for g in gs]), 'finalEnemyMean': mean([g['E']['longest'][-1] for g in gs]),
            'u50': mean([g['U']['units'][5] for g in gs]), 'e50': mean([g['E']['units'][5] for g in gs]),
            'u100': mean([g['U']['units'][10] for g in gs]), 'e100': mean([g['E']['units'][10] for g in gs]),
            'intakeUs': [sum(g['U']['nat'][p] for g in gs) for p in range(5)],
            'intakeEnemy': [sum(g['E']['nat'][p] for g in gs) for p in range(5)],
            'usOwn': sum(sum(g['U']['natOwn']) for g in gs), 'usEnemy': sum(sum(g['U']['natEnemy']) for g in gs),
            'enemyOur': sum(sum(g['E']['natEnemy']) for g in gs), 'enemyOwn': sum(sum(g['E']['natOwn']) for g in gs),
            'usNeutral': sum(sum(g['U']['natNeutral']) for g in gs), 'enemyNeutral': sum(sum(g['E']['natNeutral']) for g in gs),
            'dropTerrUs': [sum(sum(p['drop'][j] for p in g['stats']['intake']) for g in gs) for j in range(3)],
            'dropTerrEnemy': [sum(sum(p['drop'][j] for p in g['enemyStats']['intake']) for g in gs) for j in range(3)],
            'classes': dict(Counter(g['class'] for g in gs)), 'deaths': len(ds),
            'causes': dict(Counter(d['cause'] for d in ds)), 'coarse': dict(Counter(d['coarse'] for d in ds)),
            'rawReasons': dict(Counter(d['reason'] for d in ds)), 'deathPhases': dict(Counter(d['phase'] for d in ds)),
            'ramKillerMean': mean([d['killerLen'] for d in rams]), 'ramVictimMean': mean([d['len'] for d in rams]),
            'ramD3Mean': mean([d['d3'] for d in rams]), 'ramD8Mean': mean([d['d8'] for d in rams]),
            'ramD3Negative': sum(d['d3'] < 0 for d in rams), 'ramD8Negative': sum(d['d8'] < 0 for d in rams),
            'rammed': len(rams), 'sprintRammed': sum(d['killerSteps'] >= 2 for d in rams),
            'trapEnemy': sum(g['U']['trapEnemy'] for g in gs), 'stubDeaths': sum(d['stub'] == 'stub' for d in ds),
            'stubTrap': sum(d['stub'] == 'stub' and d['cause'] == 'trap' for d in ds),
            'kingRamTrust': sum('T' in d['tag'].split('|')[0].split() for d in king_rams),
            'kingRamTgx': sum('tgx' in d['tag'].split('|')[0].split() for d in king_rams),
            'kingRamKs': sum('ks' in d['tag'].split('|')[0].split() for d in king_rams),
            'kingRamLabelAge2': sum(d['tagRound'] is not None and d['r'] - d['tagRound'] <= 2 for d in king_rams),
            'lineSac350': sum(g['U']['lineSac350'] for g in gs), 'ownSacEat350': sum(g['U']['ownSacEat350'] for g in gs),
            'enemyLineSac350': sum(g['E']['lineSac350'] for g in gs), 'enemyOwnSacEat350': sum(g['E']['ownSacEat350'] for g in gs),
            'kingRams': sum(g['U']['kingRams'] for g in gs), 'kingSprint': sum(g['U']['kingSprint'] for g in gs),
            'kingRamGames': sum(g['U']['kingRams'] > 0 for g in gs), 'kingRamLate': sum(d['king'] and d['cause'] == 'rammed' and d['r'] >= 400 for d in ds),
            'kingLenSum': sum(g['U']['ramKingLen'] for g in gs), 'kingKillerSum': sum(g['U']['ramKillerLen'] for g in gs),
            'sig': {k: sum(g['signature'][k] for g in gs) for k in gs[0]['signature']} if gs else {},
            'tagTurns': dict(sum((Counter(g['stats']['tagTurns']) for g in gs), Counter())),
            'tagPressure': dict(sum((Counter(g['stats']['tagPressure']) for g in gs), Counter())),
            'pressureTurns': sum(sum(p['under'] for p in g['stats']['pressure']) for g in gs),
            'turns': sum(sum(p['turns'] for p in g['stats']['pressure']) for g in gs),
            'splitUs': [sum(g['U']['splitPhase'][p] for g in gs) for p in range(5)],
            'splitEnemy': [sum(g['E']['splitPhase'][p] for g in gs) for p in range(5)], 'behavior': behavior}

def main():
    preview = '--online-only' in sys.argv
    expected = {t['key'] for t in MAN['tasks'] if not preview or t['src'] == 'online'}
    online, ref, seen, checks, excluded = [], [], set(), Counter(), []
    sources = ['online.jsonl'] if preview else ['online.jsonl', 'reference.jsonl'] + [p.name for p in sorted(C.glob('reference-shard-*.jsonl'))]
    for source in sources:
        for g in rows(source):
            if g['key'] in seen or g['key'] not in expected:
                raise ValueError(f"Unexpected/duplicate cache key {g['key']}")
            seen.add(g['key'])
            checks.update(g['chk'])
            a, b = side(g, 'A'), side(g, 'B')
            if g['src'] == 'top':
                if g['rounds'] >= 100 and any(s['sonar'] == 0 and s['splits'] <= 3 for s in [a, b]):
                    excluded.append({'key': g['key'], 'rounds': g['rounds'], 'teamA': g['teamA'], 'teamB': g['teamB'],
                                     'A': {'sonar': a['sonar'], 'splits': a['splits']}, 'B': {'sonar': b['sonar'], 'splits': b['splits']}})
                    continue
                for tid, name in NAMES.items():
                    for t in ['A', 'B']:
                        if g['team' + t] != name:
                            continue
                        own, enemy = (a, b) if t == 'A' else (b, a)
                        ref.append({'key': g['key'], 'gameId': g['gameId'], 'oppId': tid, 'side': t, 'map': g['map'], 'kind': g['kind'],
                                    'rounds': g['rounds'], 'outcome': 'D' if not g['winner'] else 'W' if g['winner'] == t else 'L',
                                    'A': own, 'B': enemy, 'signature': signatures(own, enemy, g['rounds'])})
                continue
            u, e = (a, b) if g['us'] == 'A' else (b, a)
            de = [d for d in g['extra']['deaths'] if d['team'] == g['us']]
            row = {k: g.get(k) for k in ['key', 'era', 'map', 'kind', 'gameId', 'oppId', 'us', 'set', 'rounds', 'variant', 'seed']}
            row.update({'U': u, 'E': e, 'outcome': 'D' if not g['winner'] else 'W' if g['winner'] == g['us'] else 'L',
                        'elim': g['extra']['stats'][g['us']]['elimination'], 'deaths': de,
                        'raids': [r for r in g['extra']['raids'] if r['team'] != g['us']],
                        'stats': g['extra']['stats'][g['us']], 'enemyStats': g['extra']['stats']['B' if g['us'] == 'A' else 'A'],
                        'signature': signatures(e, u, g['rounds'])})
            row['class'] = loss_class(row)
            online.append(row)
    if seen != expected:
        raise ValueError(f'Missing {len(expected - seen)} population keys')
    if any(checks.values()):
        raise ValueError(f'Nonzero ledger checks {checks}')
    recs = {r['key']: r for r in rows('recount.jsonl')}
    bad, recount_totals = Counter(), defaultdict(Counter)
    for g in online:
        r = recs.get(g['key'])
        if not r:
            raise ValueError(f"Missing independent recount {g['key']}")
        g['behavior'] = r.get('pressureBehavior', {})
        t = g['us']; et = 'B' if t == 'A' else 'A'
        a, b = r[t], r[et]
        values = {'eliminated': int(a['elim'] is not None), 'naturalUs': a['nat'],
                  'enemyOurTerritory': b['on' + t], 'kingRams': a['kingRams'], 'kingSprint': a['kingSprint']}
        original = {'eliminated': int(g['elim'] is not None), 'naturalUs': sum(g['U']['nat']),
                    'enemyOurTerritory': sum(g['E']['natEnemy']), 'kingRams': g['U']['kingRams'], 'kingSprint': g['U']['kingSprint']}
        for k, v in values.items():
            recount_totals[g['era']][k] += v
            if v != original[k]:
                bad[k] += 1
        for key, val in [('finalUs', a['longest']), ('finalEnemy', b['longest'])]:
            if val != g['U' if key == 'finalUs' else 'E']['longest'][-1]:
                bad[key] += 1
        if a['elim'] != g['elim']:
            bad['elimRound'] += 1
    if bad:
        raise ValueError(f'Independent disagreements: {dict(bad)}')
    primary = [g for g in online if g['era'] == 'primary']
    team_tables, map_tables, family_tables, contrast_tables, selection, references = {}, {}, {}, {}, {}, {}
    for tid, name in NAMES.items():
        p = [g for g in primary if g['oppId'] == tid]
        team_tables[tid] = table(p)
        map_tables[tid] = {m: table([g for g in p if g['map'] == m]) for m in sorted({g['map'] for g in p})}
        family_tables[tid] = {kind: table([g for g in p if g['kind'] == kind]) for kind in ['elim', 'r500']}
        contrast_tables[tid] = table([g for g in online if g['era'] == 'contrast' and g['oppId'] == tid])
        cnt = Counter(g['class'] for g in p if g['outcome'] == 'L')
        largest = max(CLASSES, key=lambda k: (cnt[k], -CLASSES.index(k)))
        losses = sorted([g for g in p if g['class'] == largest], key=lambda g: g['gameId'])[:2]
        wins = sorted([g for g in p if g['outcome'] == 'W'], key=lambda g: g['gameId'])[:1]
        selection[tid] = {'largestClass': largest, 'largestN': cnt[largest],
                          'losses': [g['key'] for g in losses], 'win': [g['key'] for g in wins], 'noWin': not wins}
        refs = [g for g in ref if g['oppId'] == tid]
        refs_w = [g for g in refs if g['outcome'] == 'W']
        refs_b = [g for g in refs if g['side'] == 'B']
        def rt(gs):
            return {'N': len(gs), 'W': sum(g['outcome'] == 'W' for g in gs),
                    'nat': [sum(g['A']['nat'][p] for g in gs) for p in range(5)],
                    'enemyNat': [sum(g['B']['nat'][p] for g in gs) for p in range(5)],
                    'u50': mean([g['A']['units'][5] for g in gs]), 'u100': mean([g['A']['units'][10] for g in gs]),
                    'enemy50': mean([g['B']['units'][5] for g in gs]),
                    'splitLate': mean([sum(g['A']['splitPhase'][2:]) for g in gs]),
                    'kingRamEvents': sum(g['B']['kingRams'] for g in gs),
                    'sprintKingEvents': sum(g['B']['kingSprint'] for g in gs),
                    'signature': {k: sum(g['signature'][k] for g in gs) for k in ['swarm50', 'homeRaid', 'kingRam', 'sprintKingRam', 'lateResupply', 'kingFeed']}}
        references[tid] = {'all': rt(refs), 'wins': rt(refs_w),
                           'seats': {t: rt([g for g in refs if g['side'] == t]) for t in ['A', 'B']},
                           'families': {kind: rt([g for g in refs if g['kind'] == kind]) for kind in ['elim', 'r500']},
                           'maps': {m: rt([g for g in refs if g['map'] == m]) for m in sorted({g['map'] for g in refs})},
                           'signatureExample': {k: next((g['key'] for g in sorted(refs_w, key=lambda g: g['gameId']) if g['signature'][k]), None)
                                                for k in ['swarm50', 'homeRaid', 'kingRam', 'sprintKingRam', 'lateResupply', 'kingFeed']}}
        maps_b = {m: rt([g for g in refs_b if g['map'] == m]) for m in sorted({g['map'] for g in p})}
        references[tid]['mapSeatB'] = maps_b
        references[tid]['mapStandardizedB'] = {k: mean([v['signature'][k] / v['N'] for v in maps_b.values() if v['N']])
                                              for k in ['swarm50', 'homeRaid', 'kingRam', 'sprintKingRam', 'lateResupply', 'kingFeed']}
    report = {'population': {'primary': len(primary), 'contrast': len(online) - len(primary),
                             'referenceBeforeExclusion': sum(t['src'] == 'top' for t in MAN['tasks']),
                             'referenceExcluded': len(excluded), 'referenceIncluded': len({g['key'] for g in ref}),
                             'referenceTeamGames': len(ref), 'missing': len(MAN['missing'])},
              'checks': dict(checks), 'recount': {k: dict(v) for k, v in recount_totals.items()}, 'recountDisagreements': dict(bad),
              'overall': table(primary), 'teams': team_tables, 'maps': map_tables, 'families': family_tables,
              'contrast': contrast_tables, 'reference': references, 'classNames': CLASS_NAMES,
              'sets': {s: table([g for g in online if g['set'] == s]) for s in MAN['primarySets'] + MAN['contrastSets']},
              'keyNumbers': {'primaryFirst': {'eliminated': sum(g['elim'] is not None for g in primary),
                                             'naturalUs': sum(sum(g['U']['nat']) for g in primary),
                                             'enemyOurTerritory': sum(sum(g['E']['natEnemy']) for g in primary),
                                             'kingRams': sum(g['U']['kingRams'] for g in primary),
                                             'kingSprint': sum(g['U']['kingSprint'] for g in primary)},
                             'primarySecond': dict(recount_totals['primary'])}}
    if preview:
        write('online-aggregate.json', report)
        print(json.dumps({'population': report['population'], 'keyNumbers': report['keyNumbers'],
                          'teams': {tid: {k: v[k] for k in ['N', 'W', 'L', 'eliminated', 'classes', 'kingRams', 'kingSprint', 'sig', 'intakeUs', 'intakeEnemy', 'enemyOur', 'usOwn', 'behavior']}
                                    for tid, v in team_tables.items()}}, ensure_ascii=False, indent=2))
        return
    write('aggregate.json', report)
    write('excluded-top.json', excluded)
    write('selection.json', {'rule': MAN['selectionRule'], 'classesPriority': CLASSES, 'teams': selection})
    # Compact enough for later film planning; preserve individual online death pointers.
    with (C / 'games.jsonl').open('w') as f:
        for g in online:
            f.write(json.dumps(g, ensure_ascii=False, separators=(',', ':')) + '\n')
    with (C / 'reference-games.jsonl').open('w') as f:
        for g in ref:
            f.write(json.dumps(g, ensure_ascii=False, separators=(',', ':')) + '\n')
    with (C / 'per-game.csv').open('w') as f:
        fields = ['key', 'era', 'opponent', 'map', 'variant', 'family', 'outcome', 'ourFinalLongest', 'theirFinalLongest', 'elimRound', 'lossClass',
                  *[f'{t}_nat_p{p}' for t in ['ours', 'theirs'] for p in range(5)],
                  'ourNatOwn', 'ourNatEnemy', 'enemyNatOur', 'enemyNatOwn', 'kingRams', 'kingSprint']
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for g in online:
            row = dict(key=g['key'], era=g['era'], opponent=g['oppId'], map=g['map'], variant=g['variant'], family=g['kind'],
                       outcome=g['outcome'], ourFinalLongest=g['U']['longest'][-1], theirFinalLongest=g['E']['longest'][-1],
                       elimRound=g['elim'], lossClass=g['class'], ourNatOwn=sum(g['U']['natOwn']), ourNatEnemy=sum(g['U']['natEnemy']),
                       enemyNatOur=sum(g['E']['natEnemy']), enemyNatOwn=sum(g['E']['natOwn']), kingRams=g['U']['kingRams'], kingSprint=g['U']['kingSprint'])
            for t, sidekey in [('ours', 'U'), ('theirs', 'E')]:
                for p in range(5): row[f'{t}_nat_p{p}'] = g[sidekey]['nat'][p]
            writer.writerow(row)
    with (C / 'our-deaths.csv').open('w') as f:
        fields = ['key', 'era', 'opponent', 'map', 'family', 'round', 'dragon', 'len', 'cause', 'coarse', 'engineReason', 'king',
                  'killer', 'killerLen', 'killerSteps', 'phase', 'a3', 'e3', 'a8', 'e8', 'd3', 'd8', 'x', 'y', 'indicator', 'indicatorRound']
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for g in online:
            for d in g['deaths']:
                writer.writerow(dict(key=g['key'], era=g['era'], opponent=g['oppId'], map=g['map'], family=g['kind'], round=d['r'],
                                     dragon=d['id'], len=d['len'], cause=d['cause'], coarse=d['coarse'], engineReason=d['reason'], king=int(d['king']),
                                     killer=d['killerId'], killerLen=d['killerLen'], killerSteps=d['killerSteps'], phase=d['phase'],
                                     **{k: d[k] for k in ['a3', 'e3', 'a8', 'e8', 'd3', 'd8']}, x=d['head']['x'], y=d['head']['y'],
                                     indicator=d['tag'], indicatorRound=d['tagRound']))
    print(json.dumps({'population': report['population'], 'overall': {k: report['overall'][k] for k in ['W', 'L', 'eliminated', 'kingRams', 'kingSprint']},
                      'selection': selection, 'recount': report['recount']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
