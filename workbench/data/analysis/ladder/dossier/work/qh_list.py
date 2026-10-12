"""Scratch (diag-queenhit): one block per queen death from qh_fates.json + qh_turns.jsonl (her last own turn)."""
import sys
import json
sys.dont_write_bytecode = True
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
DN = 'NESW'
fates = json.loads((WORK / 'qh_fates.json').read_text())
last = {}
prev = {}
with (WORK / 'qh_turns.jsonl').open() as fh:
    for line in fh:
        t = json.loads(line)
        if t['game'] in last:
            prev[t['game']] = last[t['game']]
        last[t['game']] = t
for f in fates:
    d = f['fate']
    if d is None:
        print(f['game'], f['label'], f['map'], f['cells'], f['result'], 'queen alive at end L', f['final']['L'])
        continue
    t = last[f['game']]
    Wd, H = f['W'], f['H']
    hx, hy = t['head'] % Wd, t['head'] // Wd
    rel = lambda c: (((c % Wd - hx + Wd // 2) % Wd) - Wd // 2, ((c // Wd - hy + H // 2) % H) - H // 2)
    print('=' * 8, f['game'], f['label'], f['map'], f['cells'], f['result'], 'Q', f['Q'], '| death r', d['round'], d['cause'], 'MOVER' if d['mover'] else 'hit', 'L', d['L'], '| last turn r', t['round'])
    for e in t['enemies']:
        print('    in view:', e['id'], rel(e['head']), 'L', e['L'], 'seen', e['seen'], 'ENEMY QUEEN' if e['queen'] else 'parts %d cut %d free %d reach %d true %d' % (e['parts'], e['cut'], e['free'], e['reach'], e['treach']))
    print('    cands:', ' | '.join(DN[c['d']] + ':' + ('kelp' if c['kind'] == 'kelp' else c['occ'] if not c['enterable'] else ('P' if c['kind'] == 'portal' else '') + 'risk%d%s%s true%s' % (c['risk'], ' closed' if c['closed'] else '', ' pearl' if c['pearl'] else '', [tuple(x) for x in c['danger']])) for c in t['cands']))
    a = t.get('action') or {}
    print('    open0', t['open0'], 'open1', t['open1'], 'hit_head', t['hit_head'], 'pay_head', t['pay_head'], '| action', a.get('kind'), ''.join(DN[x] for x in a.get('dirs', [])), 'end', None if t.get('end') is None else rel(t['end']), 'split', t.get('split_child'), '| own tile true danger', [tuple(x) for x in t['own_danger']])
    r = d.get('rammer')
    if r:
        inview = any(e['id'] == r['id'] for e in t['enemies'])
        print('    RAMMER', r['id'], 'L', r['L'], 'from', rel(r['start']), 'steps', r['steps'], ''.join(DN[x] for x in r['dirs']), 'existed', r['existed'], 'head at her turn', None if r['then_head'] is None else rel(r['then_head']), 'len then', r['then_len'], 'IN VIEW' if inview else 'not a visible head', 'ENEMY QUEEN' if r['is_enemy_queen'] else '', '' if r['enemy'] else 'OWN TEAM')
    else:
        print('    mover dirs', ''.join(DN[x] for x in d.get('dirs', [])), 'used', d.get('used'))
