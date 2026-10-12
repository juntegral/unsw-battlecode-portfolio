import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['data/codex/astra/approach','data/analysis/ladder/dossier/local']
from scan import Board,replay
from scoreboard import load_replay
replay.load=load_replay
out=Path(__file__).resolve().parent
b=Board(Path('data/online/live-one1/b1479873/M1479875.replay'))
moments=json.loads((out/'moments.json').read_text())

def draw(c,x0,x1,y0,y1):
    bodies={int(i):list(map(tuple,bb)) for i,bb in c['bodies'].items()}
    def symbol(pt):
        for i,bb in bodies.items():
            if pt not in bb:continue
            if i==0:return 'Q' if pt==bb[0] else 'q'
            if i==8:return 'M' if pt==bb[0] else 'm'
            if i==181:return 'C' if pt==bb[0] else 'c'
            if i==1033:return 'L' if pt==bb[0] else 'l'
            if i==951:return 'E' if pt==bb[0] else 'e'
            return 'a' if c['teams'][str(i)]==1 else 'x'
        return '*' if list(pt) in c['pearls'] else '.'
    lines=['     '+''.join(f'{x:^4}' for x in range(x0,x1+1))]
    for y in range(y0,y1+1):
        lines.append('    '+''.join('+'+('---' if b.adj[x,y][0] is None else '   ') for x in range(x0,x1+1))+'+')
        line=f'{y:3} '
        for x in range(x0,x1+1):line+=('|' if b.adj[x,y][3] is None else ' ')+f' {symbol((x,y))} '
        line+='|' if b.adj[x1,y][1] is None else ' '
        lines.append(line)
    lines.append('    '+''.join('+'+('---' if b.adj[x,y1][2] is None else '   ') for x in range(x0,x1+1))+'+')
    return '\n'.join(lines)

text=['[M] 각 그림은 해당 드래곤 차례 시작. 좌표는 기보 좌표, 라운드는 0부터다. Q/q=여왕 #0 머리/몸, M/m=아군 #8, C/c=아군 #181, L/l=최장 #1033, E/e=적 #951, a=다른 아군, x=다른 적, *=진주, 선=벽.']
for r in (113,114,115,116):
    c=next(c for c in moments if c['id']==0 and c['r']==r)
    text+= [f"\n[M] r{r} #0, L{len(c['body'])}, 행동 {c.get('dirs')} (r114는 분열)", '```', draw(c,12,17,12,16),'```']
for r in (475,476,477):
    c=next(c for c in moments if c['id']==1033 and c['r']==r)
    text += [f"\n[M] r{r} #1033, L{len(c['body'])}, 행동 {c.get('dirs')}",'```',draw(c,2,7,6,10),'```']
(out/'boards.md').write_text('\n'.join(text)+'\n')

# Bounds use actual own-body order and only cells ever observed while connected to the head.
known=[];proof=[]
for c in moments:
    if c['id']!=1033:continue
    body=list(map(tuple,c['body']));view=set(map(tuple,c['window']));prior=set(known);n=0
    for z in body:
        if z in prior or z in view:n+=1
        else:break
    known=body[:n]
    proof.append(dict(round=c['r'],length=len(body),connected_known_upper_bound=n,tail=body[-1]))
c=next(c for c in moments if c['id']==1033 and c['r']==477)
body=tuple(map(tuple,c['body']));others={tuple(t) for i,bb in c['bodies'].items() if int(i)!=1033 for t in bb}
pearls=set(map(tuple,c['pearls']))
queue=deque([(body,(),frozenset())]);states=[]
while queue:
    bb,path,eaten=queue.popleft()
    if len(path)>=10:continue
    for d,n in enumerate(b.adj[bb[0]]):
        if n is None or n in bb or n in others:continue
        eat=n in pearls and n not in eaten
        nb=(n,)+(bb if eat else bb[:-1]);pp=path+(d,)
        states.append(dict(path=pp,end=n));queue.append((nb,pp,eaten|{n} if eat else eaten))
post_child=tuple(reversed(body[2:]));post_parent=body[:2]
child_legal=[dict(dir=d,dest=n) for d,n in enumerate(b.adj[post_child[0]]) if n is not None and n not in post_child and n not in post_parent and n not in others]
proof=dict(memory=proof,free_paths=states,hypothetical_split=dict(parent_length=2,child_length=37,child_head=post_child[0],legal_first_steps=child_legal),notes='Frozen other dragons; no new game and no future survival claim. Direction order N,E,S,W.')
(out/'geometry-proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
xs=json.loads((out/'samples.json').read_text());ls=json.loads((out/'longs.json').read_text());table=[]
for group in ('one6-w1-old','one6-c1-old','live'):
    a=[x for x in xs if x['group']==group];rams=[r for x in ls if x['src']==group for r in x['rams'] if r['s']==0 and not r['q'] and r['L']>=31]
    exact=[r for r in rams if r['last'] and r['last']['rammer_seen'] and r['last']['end_free'] and r['last']['clean_pay1']==0]
    qseq=[x for x in a if x['death'] and x['death']['reason'] in (0,1) and any(e['r']<x['death']['r']<=e['r']+2 for e in x['cage_entries']) and any(s['before']==4 and s['after']==2 and 0<x['death']['r']-s['r']<=3 for s in x['queen_splits'])]
    table.append(dict(group=group,games=len(a),long_rammed=len(rams),matching_visible_trap=len(exact),queen_split_cage_death=len(qseq),queen_games=[x['game'] for x in qseq]))
(out/'counts.json').write_text(json.dumps(table,indent=2));print(table)
checks=[]
for x in xs:
    checks.append(dict(game=x['game'],bot=x['bot'],final=x['final']))
(out/'verification.json').write_text(json.dumps(dict(games=len(xs),unique_games=len({x['game'] for x in xs}),final_state_checks='All 45 matched replay terminal alive/longest/total and metadata total in census.py',checks=checks),indent=2))
