from pathlib import Path
import json
from collections import Counter

task = Path(__file__).resolve().parent
a = json.loads((task / 'analysis.json').read_text())
f = json.loads((task / 'firstdiv.json').read_text())
summary = {'inventory': {k: a[k] for k in ['expectedGames', 'missing', 'historyErrors', 'duplicates', 'unexpected', 'errors']}, 'arms': {}, 'groups': {}, 'firstdiv': f['summary']}
for arm in ['on', 'off', 'id-on', 'id-off', 'id-base']:
    if arm not in a['sets']:
        continue
    games = a['sets'][arm]
    out = {'games': len(games)}
    for k in ['turns', 'turnsL5', 'freeMulti', 'completedFreeMulti', 'multi', 'completedMulti', 'oversprint', 'tle', 'missingAction', 'turnActionGap', 'bodyxTags', 'missingBodyxTags', 'unknownInput', 'unseenPath']:
        out[k] = sum(g[k] for g in games.values())
    out['rate'] = out['freeMulti'] / out['turnsL5'] if out['turnsL5'] else None
    for k in ['raw', 'causes', 'checks']:
        c = Counter()
        for g in games.values():
            c.update(g[k])
        out[k] = dict(c)
    for k in ['startHashDrift', 'endHashDrift']:
        out[k] = sum(len(g[k]) for g in games.values())
    out['endDriftStartExact'] = sum(sum(not any(z['round'] == x['round'] and z['id'] == x['id'] for z in g['startHashDrift']) for x in g['endHashDrift']) for g in games.values())
    out['cpuMissing'] = sum(g['cpuMaxM'] is None for g in games.values())
    out['cpuMaxM'] = max((g['cpuMaxM'] for g in games.values() if g['cpuMaxM'] is not None), default=None)
    out['depthTagged'] = sum(len(g['depth']) for g in games.values())
    out['depthUntagged'] = out['actions'] - out['depthTagged'] if 'actions' in out else sum(g['actions'] for g in games.values()) - out['depthTagged']
    out['bands'] = {}
    for g in games.values():
        for b, counts in g['bands'].items():
            out['bands'].setdefault(b, Counter()).update(counts)
    summary['arms'][arm] = out
    if arm not in ['on', 'off']:
        continue
    for dim, idx in [('opponent', 0), ('map', 1), ('side', 2), ('key', None)]:
        groups = summary['groups'].setdefault(dim, {})
        for key, g in games.items():
            label = key if idx is None else key.split(':')[idx]
            counts = groups.setdefault(label, {}).setdefault(arm, Counter())
            counts.update({k: g[k] for k in ['turnsL5', 'freeMulti', 'completedFreeMulti', 'multi', 'completedMulti']})
for dim in summary['groups'].values():
    for group in dim.values():
        for counts in group.values():
            counts['rate'] = counts['freeMulti'] / counts['turnsL5'] if counts['turnsL5'] else None
summary['queens'] = {'directions': dict(Counter(p['queenDirection'] for p in a['pairs'])), 'deltaSum': sum(p['queenDelta'] for p in a['pairs']), 'deltaMin': min(p['queenDelta'] for p in a['pairs']), 'deltaMax': max(p['queenDelta'] for p in a['pairs']), 'censoredOn': sum(p['queenCensoredOn'] for p in a['pairs']), 'censoredOff': sum(p['queenCensoredOff'] for p in a['pairs'])}
summary['identity'] = {'N': len(a['identity']), 'same': sum(p['same'] for p in a['identity'])}
summary['rawA'] = [{'arm': arm, 'key': key, **d} for arm in ['on', 'off'] for key, g in a['sets'][arm].items() for d in g['deaths'] if d['reason'] == 'A']
summary['instant'] = []
summary['extraChanged'] = []
summary['prefixFailures'] = []
depth = {s: Counter() for s in ['beforeR', 'atR', 'afterR', 'noDivergence']}
for r in f['rows']:
    if r['status'] == 'matched':
        c = r['changed'][0]
        summary['instant'].append({'key': r['key'], 'R': r['R'], 'id': r['id'], 'length': len(c['turn']['on']['body']), 'on': c['on']['text'], 'off': c['off']['text'], 'onFate': c['turn']['on']['fate'], 'offFate': c['turn']['off']['fate'], 'onAfter': c['turn']['on']['after'], 'offAfter': c['turn']['off']['after'], 'onIndicator': c['on']['indicator'], 'offIndicator': c['off']['indicator']})
        for c in r['changed'][1:]:
            summary['extraChanged'].append({'key': r['key'], 'R': r['R'], 'id': c['id'], 'on': c['on'], 'off': c['off'], 'turnBoardIdentical': c['turnBoardIdentical'], 'classification': c['classification']})
        p = r['prefixDifference']
        if p and any(p.get(arm, {}).get('event', {}).get('type') != 'dragonAction' or p.get(arm, {}).get('event', {}).get('id') != r['id'] or p.get(arm, {}).get('round') != r['R'] for arm in ['on', 'off']):
            summary['prefixFailures'].append({'key': r['key'], 'prefixDifference': p})
    key = r['key']
    on, off = a['sets']['on'][key]['depth'], a['sets']['off'][key]['depth']
    for k in on.keys() & off.keys():
        rr = int(k.split(':')[0])
        scope = 'noDivergence' if r['status'] == 'no_divergence' else 'beforeR' if rr < r['R'] else 'atR' if rr == r['R'] else 'afterR'
        depth[scope]['lower' if on[k] < off[k] else 'higher' if on[k] > off[k] else 'same'] += 1
summary['depth'] = depth
summary['newOnlyImmediateDeath'] = [r for r in summary['instant'] if r['onFate'] and not r['offFate']]
summary['harms'] = [{'key': r['key'], 'R': r['R'], 'id': r['id'], 'classification': r['classification'], 'queen': r['queen']} for r in f['rows'] if r['status'] == 'matched' and ('harm' in r['classification'].values() or 'harm' in r['queen']['classification'].values())]
(task / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k not in ['groups', 'instant', 'extraChanged', 'harms']}, indent=2, ensure_ascii=False))
print('HARMS', json.dumps(summary['harms'], ensure_ascii=False))
