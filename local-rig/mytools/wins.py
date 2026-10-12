import json, sys
rows=[json.loads(l) for l in open('runs/eval-final/rows.jsonl')]
for r in rows:
    s=r['first_bot_side']
    if r['winner']==s:
        myq=r['a_queen'] if s==0 else r['b_queen']
        print('WIN', r['map_name'].replace('sqheld_',''), 'seed',r['seed'],'side',s, r['how'], r['verdict'], 'rounds',r['rounds'], 'myqueen',myq)
late=[r for r in rows if r['how']=='elimination' and r['rounds']>400]
print('late eliminations (r>400):', sum(r['winner']==r['first_bot_side'] for r in late),'won,',sum(r['winner']!=r['first_bot_side'] for r in late),'lost')
early=[r for r in rows if r['how']=='elimination' and r['rounds']<=400]
print('eliminations r<=400:', sum(r['winner']==r['first_bot_side'] for r in early),'won,',sum(r['winner']!=r['first_bot_side'] for r in early),'lost')
lim=[r for r in rows if r['how']=='round_limit']
print('round limit games:',len(lim),'both queens dead in',sum(r['a_queen']==0 and r['b_queen']==0 for r in lim),'| opp queen alive in',sum((r['b_queen'] if r['first_bot_side']==0 else r['a_queen'])>0 for r in lim))
print('opp longest at limit when it won:',sorted((r['b_longest'] if r['first_bot_side']==0 else r['a_longest']) for r in lim if r['winner']!=r['first_bot_side']))
print('opp dragons at limit:',sorted((r['b_dragons'] if r['first_bot_side']==0 else r['a_dragons']) for r in lim))
