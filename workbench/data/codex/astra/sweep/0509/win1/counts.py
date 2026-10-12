import sys
sys.dont_write_bytecode = True
import gzip
import json
from collections import Counter, defaultdict
from analyze import OUT, IDS
from mechanisms import module

def main():
    counts, games = Counter(), Counter()
    examples = defaultdict(list)
    details = []
    def add(key, rows, gid):
        counts[key] += len(rows)
        games[key] += bool(rows)
        for r in rows[:3]:
            if len(examples[key]) < 6:
                examples[key].append(dict(gid=gid, **r))
    for gid in IDS:
        d = json.loads((OUT/f'{gid}.json').read_text())
        h = json.loads((OUT/f'hunt-{gid}.json').read_text())
        g = json.loads((OUT/f'g{gid}.json').read_text())
        ts = [json.loads(x) for x in (OUT/f'{gid}-turns.jsonl').read_text().splitlines()]
        own = [t for t in ts if t['s'] == 0]
        rows = json.load(gzip.open(OUT/f'turns-{gid}.json.gz', 'rt'))
        own_by_turn = {(t['r'], t['id']):t for t in own}
        floor_over = [t for t in rows if t['q'] and any(s['edge'] and s['parts']<4 and s['L']<4 and int(i)!=g['enemyqueen'] for i,s in t['seen'].items())]
        floor_miss = []
        for t in floor_over:
            b = own_by_turn[t['r'],t['id']]
            if b['adjp'] and b['alive'] and not b['split'] and not any(c in b['adjp'] for c in b['eaten']):
                floor_miss.append(t)
        groups = {
            'eat_adj': [t for t in own if t['adjp'] and any(c in t['adjp'] for c in t['eaten'])],
            'heading': [t for t in own if t['r']<12 and t['id']>1 and t['directions'] and t['directions'][0]==t['prior_dir']],
            'queen_exit_kept': [t for t in own if t['steps'] and any(z['queen'] and z['cell'] not in t['steps'] for z in t['last_exit_choices'])],
            'mate_exit_kept': [t for t in own if t['steps'] and any(not z['queen'] and z['cell'] not in t['steps'] for z in t['last_exit_choices'])],
            'pocket_short_avoid': [t for t in own if t['L']<4 and t['pocket_pearl_choices'] and t['steps'] and not t['split'] and not any(c in t['steps'] for c in t['pocket_pearl_choices'])],
            'qs_relax_split': [t for t in own if t['id']==d['queenIds'][0] and t['split'] and t['L']==4 and t['ownN']<6],
            'miss_adj_survived': [t for t in own if t['adjp'] and t['alive'] and not t['split'] and not any(c in t['adjp'] for c in t['eaten'])],
            'idle_survived': [t for t in own if not t['split'] and not t['steps'] and t['alive'] and t.get('actionKind')==0],
            'cap_stops_free': [t for t in own if 350<t['r']<400 and t['ownN']>=56 and t['death']==4 and t['free']>0],
            'sure_queen_ram': [t for t in h['deaths'] if 'rammer' in t],
            'expanded_queen_ram': [t for t in h['deaths'] if 'rammer' in t and t['rammer']['L']>4],
            'boot_stop_donor_eaten': [t for t in h['transfers'] if t['queen'] and t['side']==0 and t['source_side']==0 and t['cause']=='stop' and t['r']>300 and t['sourceL'] in (2,3) and t['eaterL']<6 and t['sourceL']*2>t['eaterL']],
            'boot_phase_low_queen_no_split': [t for t in rows if t['q'] and t['r']>400 and t['L']<6 and not t['split']],
            'queen_cut_floor_gate': [t for t in rows if t['q'] and any(s['edge'] and s['parts']<4 and int(i)!=g['enemyqueen'] for i,s in t['seen'].items())],
            'queen_floor_above_true': floor_over,
            'queen_floor_missed_pearl': floor_miss,
            'queen_unknown_portal_avoid': [t for t in rows if t['q'] and t.get('unseen_portal_options') and not t.get('portals')],
            'queen_unknown_portal_entry': [t for t in rows if t['q'] and any(not z['exit_seen'] for z in t.get('portals',[]))],
            'small_sprint_gate': [t for t in rows if not t['q'] and t['L']<=4 and any(s['parts'] in (3,4) for s in t['seen'].values())],
            'short_evade_gate_proxy': [t for t in rows if not t['q'] and t['L']<=4 and t['dirs'] and not t['split'] and t['ally_heads']+1<=t['enemy_heads'] and t['id']>1],
            'miss_sure_visible': [t for t in h['reach'] if t['visible'] and not t['hitqueen'] and not t['is_leader_proxy'] and t['id']!=h['queens'][0]],
        }
        for key, value in groups.items():
            add(key, value, gid)
        counts['herd_nearer'] += d['signatureCounts']['herd_nearer']
        games['herd_nearer'] += bool(d['signatureCounts']['herd_nearer'])
        if len(examples['herd_nearer'])<6:
            examples['herd_nearer'] += [dict(gid=gid, **t) for t in d['signatureExamples']['herd_nearer'][:1]]
        counts['sonar_dead_claims'] += int(h['states'].get('1',0))+int(h['states'].get('3',0))
        games['sonar_dead_claims'] += bool(int(h['states'].get('1',0))+int(h['states'].get('3',0)))
        details.append(dict(gid=gid, queen_rams=[r for r in g['rams'] if r['q']], counts={k:len(v) for k,v in groups.items()},
                            queen_transfer_stop=[t for t in h['transfers'] if t['queen'] and t['side']==0 and t['source_side']==0 and t['cause']=='stop'],
                            expanded_rammer_recovery=[dict(rammer=t['rammer'],r=t['r'],recovered=sum(e['side']==0 for e in h['transfers'] if e['source']==t['rammer']['id']),
                                                        donor_initial=t['rammer']['L']) for t in groups['expanded_queen_ram']],
                            rally_proxy=h['candidates']))
    # Existing read-only defense and split counters; redirect their output globals only.
    guard = module('guard_reader', 'data/analysis/ladder/dossier/work/o1_qdef.py')
    saved_analyze = sys.modules.get('analyze')
    sys.modules['analyze'] = module('move_geometry', 'data/codex/astra/evade/analyze.py')
    try:
        move = module('move_reader', 'data/codex/astra/audit-move/audit.py')
    finally:
        sys.modules['analyze'] = saved_analyze
    for gid in IDS:
        d=json.loads((OUT/f'{gid}.json').read_text())
        from pathlib import Path
        path=Path(d['path'])
        gd=guard.scan('0509',path,d['meta'])
        candidates=[t for t in gd['guard'] if t[1]<=4 and t[5]<=3 and t[7]<=t[6]]
        add('defend_candidate', [dict(r=t[0],L=t[1],id=t[2],target=t[3],ram=bool(t[8])) for t in candidates],gid)
        add('defend_ram', [dict(r=t[0],id=t[2],target=t[3]) for t in candidates if t[8]],gid)
        move_path=OUT/f'move-{gid}.json'
        if move_path.exists():
            mc=json.loads(move_path.read_text())
        else:
            root=move.lr.agg.sb.load_replay(path).root()
            mc=move.census(path.resolve(),d['meta'],root)
            move_path.write_text(json.dumps(mc,ensure_ascii=False,separators=(',',':'))+'\n')
        realized=[t for t in mc['splits'] if t['portal'] and t['r']<=100 and t['L']==4 and not t['queen']]
        add('split_portal_observed',realized,gid)
    output=dict(counts=dict(counts),games=dict(games),examples=dict(examples),details=details)
    (OUT/'counts.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=dict(counts),games=dict(games)),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
