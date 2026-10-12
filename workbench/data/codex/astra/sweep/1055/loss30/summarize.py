import sys,json
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from count_local import Geo
OUT=Path(__file__).resolve().parent
summary={}
boards=[]
for gid in (1507922,1507923,1507925):
    g=json.loads((OUT/f'{gid}.json').read_text())
    w,h=g['width'],g['height']
    raw=[tuple(map(int,l.split()[1:4])) for l in g['text'].splitlines() if l.startswith('EDGE ')]
    geo=Geo(w,h,raw)
    xy=lambda c:[c%w,c//w]
    key=lambda s:(s['queen_length'],s['longest'],s['total'])
    last=max((int(r) for r,s in g['snapshots'].items() if key(s['us'])>=key(s['them'])),default=-1)
    row=dict(final=g['final'],bots=g['bots'],queens=g['queens'],end_round=g['last_round'],end_reason=g['end_reason'],permanent_score_deficit=last+1,crossings={},queen_shortening=[])
    for side in (0,1):
        cross=[]
        for t in g['turns']:
            if t['side']!=side:continue
            pos=t['body'][0]
            for d,nxt in zip(t['dirs'],t['path']):
                if geo.moves[pos][d][0]==2:cross.append(dict(r=t['r'],id=t['id'],start=xy(pos),end=xy(nxt)))
                pos=nxt
        row['crossings'][side]=dict(total=len(cross),through100=sum(c['r']<=100 for c in cross),first=cross[:1])
    row['queen_shortening']=[dict(r=t['r'],before=len(t['body']),after=len(t['end']),dirs=t['dirs']) for t in g['queen_turns'] if len(t['body'])>=3 and len(t['end'])==2]
    enemy_turns=[t for t in g['turns'] if t['id']==g['queens']['them']]
    row['enemy_queen_final_head']=xy(enemy_turns[-1]['end'][0])
    row['our_deaths']=[d for d in g['deaths'] if d['side']=='us']
    row['our_long_deaths']=[d for d in row['our_deaths'] if d['length']>=5]
    if gid!=1507922:
        qdeath=next(d for d in row['our_deaths'] if d['id']==g['queens']['us'])
        assert qdeath['round']==g['last_round'] and g['final']['us']['alive']==0
        row['post_queen_death_own_survivors']=0
        row['post_queen_death_within5']=0
        panels=g['queen_turns'][-3:]
        boards.append(f'| {g["map"]} [M] | '+ ' | '.join(f'r{t["r"]}, 머리 {tuple(xy(t["body"][0]))}' for t in panels)+' |')
        boards.append('| 7×7 | '+' | '.join('<pre>'+'<br>'.join(t['board'])+'</pre>' for t in panels)+' |')
        boards.append('| 벽 마스크 | '+' | '.join('<pre>'+'<br>'.join(''.join(format(sum(1<<d for d,k in enumerate(e) if k==1),'x') for e in t['edges'][r*7:r*7+7]) for r in range(7))+'</pre>' for t in panels)+' |')
    summary[gid]=row
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(OUT/'boards.txt').write_text('\n'.join(boards)+'\n')
print('summary.json and boards.txt written')
