import sys,json,statistics
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path('data/codex/astra/kraken')
games=[json.loads(p.read_text()) for p in sorted(OUT.glob('M*.json'))]
ranked=[g for g in games if g['ledger']['src'].startswith('b')]

def stats(gs):
    n=len(gs);out={}
    for s in (0,1):
        turns=[t for g in gs for t in g['detail']['turns'] if t['s']==s]
        deaths=[d for g in gs for d in g['ledger']['deaths'] if d[1]==s]
        rams=[d for d in deaths if d[4]=='rams']
        victim=[d for g in gs for d in g['ledger']['deaths'] if d[1]!=s and d[4]=='rammed']
        out[s]=dict(n=n,first=[g['detail']['first'][s] for g in gs],spread=round(sum(g['detail']['spread'][s] for g in gs)/n,2),
          splits30=sum(x['s']==s and x['r']<=30 for g in gs for x in g['detail']['splits']),
          pearls30=sum(x[1]==s and x[0]<=30 for g in gs for x in g['ledger']['eats']),
          natural100=sum(x[1]==s and x[0]<=100 and x[3]=='n' for g in gs for x in g['ledger']['eats']),
          head30=round(sum(g['detail']['snaps'].get('30',list(g['detail']['snaps'].values())[-1])[s][3] for g in gs)/n,2),
          rams=len(rams),rammed=sum(d[4]=='rammed' for d in deaths),
          ram_len=dict(Counter(x[18][0] for x in victim)),ram_steps=dict(Counter(x[18][1] for x in victim)),ram_paid=sum(x[18][2]>0 for x in victim),
          ram_queens=sum(x[6] for x in victim),late_stops=sum(d[0]>400 and d[4]=='stop' and d[5]>0 for d in deaths),
          late_splits=sum(x['s']==s and x['r']>400 for g in gs for x in g['detail']['splits']),
          late_nomove=sum(t['r']>400 and not t['steps'] and t['action']==1 for t in turns),
          final_heads=round(sum(g['ledger']['ends'][s][0] for g in gs)/n,2),
          q_alive=sum(g['ledger']['ends'][s][3]>0 for g in gs))
    return out

profiles={label:stats([g for g in games if g['ledger']['src']==label]) for label in sorted({g['ledger']['src'] for g in games})}
profiles['ranked10']=stats(ranked)
(OUT/'profiles.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2))
f=open(OUT/'moments.txt','w')
for g in ranked:
    d,l=g['detail'],g['ledger']; print('\nGAME',l['gid'],l['map'],l['result'],l['how'],'bot',l['bot'],file=f)
    sign=1 if l['result']=='win' else -1
    def lead(v):
        a,b=v
        return (a>b)-(a<b)
    # Lexicographic queen/longest/total at end of round; eliminated games still sort correctly.
    rr=[int(r) for r,v in d['snaps'].items() if lead([x[:3] for x in v])!=sign]
    print('final uninterrupted scoreboard lead',max(rr)+1 if rr else 0,'final',d['snaps'][str(l['last'])],file=f)
    print('queens',d['queens'],'final dragon lengths',{i:len(b) for i,b in d['final'].items()},file=f)
    print('r0-40 splits', [x for x in d['splits'] if x['r']<=40],file=f)
    print('r0-40 deaths',[{k:v for k,v in x.items() if k not in ('body','context')} for x in d['deaths'] if x['r']<=40],file=f)
    print('late big deaths',[{k:v for k,v in x.items() if k not in ('body','context')} for x in d['deaths'] if x['r']>=300 and x['L']>=10],file=f)
    for s in (0,1):
        death=next((x for x in d['deaths'] if x['id']==d['queens'][s]),None)
        if death is None:continue
        print('QUEEN DEATH', {k:v for k,v in death.items() if k not in ('body','context')},file=f)
        for t in d['qt'][s][-3:]:
            print('turn',{k:v for k,v in t.items() if k!='context'},file=f)
            if death['actor']!=death['id']:
                print('attacker body then',t['context'].get(str(death['actor'])),file=f)
        print('attacker turns', [{k:v for k,v in t.items() if k!='context'} for t in d['turns'] if t['id']==death['actor'] and death['r']-2<=t['r']<=death['r']],file=f)
f.close()

f=open(OUT/'queen-boards.md','w')
print('# 패한 6판 여왕 마지막 세 차례 [M]\n\nQ/q=우리 여왕 머리/몸, A/a=아군, E/e=적, 빈칸=미점유, 벽=─│, 포털=P. 관전자 전체 상태이며 진주 생략. 각 차례 시작 상태.',file=f)
for g in ranked:
    if g['ledger']['result']!='loss':continue
    d,l=g['detail'],g['ledger']; folder=Path('data/online/live-one1')/l['src'];root=lr.replay.load(folder/f"M{l['gid']}.replay").root()
    raw=[tuple(map(int,line.split()[1:4])) for line in root.text(0).splitlines() if line.startswith('EDGE ')]
    w,h=d['w'],d['h'];edges=lr.canonical_edges(w,h,raw)
    def edge(x,y,k):return edges.get(lr.edge_id(w,h,x%w,y%h,k),(0,-1))[0]
    print(f"\n## M{l['gid']} {l['map']} — #{d['queens'][0]}",file=f)
    for t in d['qt'][0][-3:]:
        x,y=t['body'][0];occ={}
        for i,b in t['context'].items():
            char='Q' if int(i)==d['queens'][0] else 'A' if d['teams'][i]==0 else 'E'
            for k,xy in enumerate(b):occ[tuple(xy)]=char if k==0 else char.lower()
        print(f"\nr{t['r']} L{t['L']} ({x},{y}) → {t['steps'] or ('split L'+str(len(t['end'])) if t['action']==1 else 'death')}; x={(x-3)%w}…{(x+3)%w}, y={(y-3)%h}…{(y+3)%h}\n```",file=f)
        for yy in range(y-3,y+4):
            print(''.join('+'+('──' if edge(xx,yy,0)==1 else 'PP' if edge(xx,yy,0)==2 else '  ') for xx in range(x-3,x+4))+'+',file=f)
            print(''.join(('│' if edge(xx,yy,3)==1 else 'P' if edge(xx,yy,3)==2 else ' ')+occ.get((xx%w,yy%h),'.')+' ' for xx in range(x-3,x+4)),file=f)
        print('```',file=f)
f.close()
