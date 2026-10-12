import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
rows=json.loads((HERE/'analysis.json').read_text())
c=Counter();examples={};games=[]
def add(key, game, turn):
    c[key]+=1
    examples.setdefault(key,[]).append(dict(game=game,round=turn['r'],dragon=turn['id']))
for row in rows:
    gid=row['gid'];ts=[t for t in row['trace']['turns'] if t['s']==0]
    assert row['botId']==21126
    c['games']+=1;c['turns']+=len(ts)
    c['our_natural']+=row['base']['eats']['us']['spawn'];c['their_natural']+=row['base']['eats']['them']['spawn']
    # Adjacent means a currently empty cell across a non-kelp edge, including a known physical portal.
    for t in ts:
        if t['adj_pearls']:
            c['adjacent_pearl_turns']+=1
            if not t['adj_pass']:add('adjacent_eaten',gid,t)
            else:
                add('adjacent_passed',gid,t)
                c['adjacent_passed_split' if t['split'] else 'adjacent_passed_non_split']+=1
        if t['r']<12 and not t['q'] and t['L']<=4 and t['heading'] is not None and t['dirs']:
            c['early_nonqueen_moving']+=1
            if t['dirs'][0]==t['heading']:add('early_straight',gid,t)
        # This is a behavioural match, not a full reconstruction of the bot's remembered herd field.
        if t['q'] and t['ownN']>=12 and t['own_square']<3 and t['mate_gap'] and t['mate_gap']>3 and t.get('mate_gap_end',999)<t['mate_gap']:
            add('herd_nearer_match',gid,t)
        if t['action']==0 and not t['dirs'] and not t['split']:add('empty_move',gid,t)
        if t['logs']:c['log_events']+=len(t['logs'])
        if t['L']<=4 and not t['q'] and t['ownQ']==0 and t['foeQ']>0 and t.get('foe_queen_visible'):
            add('avenge_visible_opportunity',gid,t)
    for sp in row['trace']['splits']:
        if sp['s']==0 and sp['q']:
            c['queen_splits']+=1;c['queen_splits_L5']+=sp['L']==5
    for d in row['trace']['deaths']:
        if d['reason']==3 and d['s']==1 and 'ram_start' in d and d['ram_start']['s']==0:
            t=d['ram_start'];c['our_rams']+=1
            if d['q'] and t['L']<=4 and not t['q'] and len(t['dirs'])<=3:add('queen_sure_match',gid,t)
            if not d['q'] and not t['q'] and t['L']<=4 and d.get('target_queen_dist',99) is not None and d.get('target_queen_dist',99)<=3 and d.get('guard_visible'):add('queen_defend_match',gid,t)
    portal_ids=[int(l.split()[3]) for l in row['base']['text'].splitlines() if l.startswith('EDGE ') and l.split()[2]=='2']
    c['guard_rejected_portal_ids']+=sum(pid>=2*row['old']['cells'] for pid in set(portal_ids))
    c['cap_round_eligible_turns']+=sum(t['r']>350 for t in ts)
    behind=[int(n) for n,s in row['base']['snapshots'].items() if s['us']['queen_length']<s['them']['queen_length']]
    qdeath=[d for d in row['base']['deaths'] if d['id']==row['base']['queens']['us']]
    games.append(dict(gid=gid,map=row['map'],side=row['side'],botId=row['botId'],end=row['last'],decision=row['how'],final=row['final'],permanent_lead=row['permanent_lead'],queen_death=qdeath,queen_behind_rounds=behind))
# No action logs are retained in these replays; match counts must never be called counterfactual benefits.
for key in ['log_events','empty_move','guard_rejected_portal_ids','cap_round_eligible_turns']:c[key]+=0
out=dict(counts=dict(c),examples=examples,games=games,definitions=dict(permanent_lead='First end-of-round scoreboard strictly ahead, with no later tie or deficit; elimination overrides the queen/longest/total tuple.',herd_nearer_match='Queen, 12+ allied heads, fewer than two other allied heads in 7x7, nearest global mate starts >3 away and becomes nearer during queen action. No memory/pocket/risk terms recreated.',queen_sure_match='Our nonqueen of <=4 rams their queen with at most 3 issued directions; observational match.',queen_defend_match='Our nonqueen of <=4 rams a nonqueen enemy, both heads visible, enemy within 3 static terrain steps of our queen. Overlaps ordinary trading.',adjacent_pearl_turns='Turn start has an unoccupied adjacent pearl across non-kelp edge, including portals; no safety veto is assumed.',empty_move='Move action with zero directions, excluding split actions.',risk='Static occupied-cell BFS with terrain and portals; ignores moving tails and pearls gained along approach. Not a proof of safety.'))
(HERE/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(dict(c))
