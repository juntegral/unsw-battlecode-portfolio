"""Reproducible census tables, with side-specific denominators and entrance annotations."""
import sys
sys.dont_write_bytecode=True
import json,csv
from collections import Counter
import scan

def load(name):return list(map(json.loads,(scan.OUT/name).read_text().splitlines()))

def metrics(gs,s,field='no_enemy3'):
    gr=[(g,c,ds) for g in gs for z,c,ds in scan.repeated(g,field) if z==s]
    ds=[d for g,c,dd in gr for d in dd]
    non=[d for g in gs for d in g['deaths'] if d['side']==s and d['cause'] in ('wall','own body','mate body','mate head','stop')]
    strict=[d for d in non if d['cause'] in ('wall','own body','mate body') and d[field]]
    return dict(games=len(gs),affected=len({g['gid'] for g,c,dd in gr}),cells=len(gr),deaths=len(ds),
                length=sum(d['length'] for d in ds),queens=sum(d['queen'] for d in ds),
                noncombat=len(non),noncombat_share=100*len(ds)/len(non) if non else None,
                eligible=len(strict),eligible_share=100*len(ds)/len(strict) if strict else None,
                split01=sum(d['split_age'] in (0,1) for d in ds),
                single_deaths=sum(d['component_size']==1 for d in ds),
                single_length=sum(d['length'] for d in ds if d['component_size']==1),
                single_games=len({g['gid'] for g,c,dd in gr if dd[0]['component_size']==1}),
                single_cells=sum(dd[0]['component_size']==1 for g,c,dd in gr),
                single_queens=sum(d['queen'] for d in ds if d['component_size']==1))

def main():
    games=load('games.jsonl');tests=load('test20905.jsonl');access={a['gid']:a['deaths'] for a in load('access.jsonl')}
    narrow={a['gid']:a for a in load('audit-narrow.jsonl')};all_metrics={str(s):metrics(games,s) for s in (0,1)}
    summary=dict(core=all_metrics,sensitivity_man3={str(s):metrics(games,s,'no_enemy_man3') for s in (0,1)},
                 test20905={str(s):metrics(tests,s) for s in (0,1)},
                 versions={v:{str(s):metrics([g for g in games if g['version']==v],s) for s in (0,1)} for v in scan.BOTS.values()},
                 opponents={o:{str(s):metrics([g for g in games if g['opp']==o],s) for s in (0,1)} for o in sorted({g['opp'] for g in games})})
    groups=[];per=[];eligible_keys=set()
    for g in games:
        for s,c,ds in scan.repeated(g):
            eligible_keys.update((g['gid'],d['event']) for d in ds if s==0)
            companions=[d for d in g['deaths'] if d['side']==s and tuple(d['cell'])==c and d['cause'] in ('wall','own body','mate body') and not d['no_enemy3']]
            facts=[]
            for d in ds:
                ent=d['entry'] or {};way=access[g['gid']][str(d['event'])]['component_entrance'] or {}
                facts.append(dict(r=d['r'],id=d['id'],length=d['length'],queen=d['queen'],cause=d['cause'],
                    last_step_portal=ent.get('portal'),last_step_r=ent.get('r'),last_step_pearl=ent.get('pearl'),
                    entry_src=ent.get('src'),entry_dest=ent.get('dest'),component_entrance_portal=way.get('portal',False),
                    component_entrance_r=way.get('r'),pearls_remaining_at_component_entry=way.get('pearls_remaining'),
                    component_pearls_at_death=d['component_pearls'],split_age=d['split_age'],birth_head=ent.get('birth')))
            groups.append(dict(gid=g['gid'],version=g['version'],map=g['map'],opponent=g['opp'],side=s,x=c[0],y=c[1],
                count=len(ds),gross_length=sum(d['length'] for d in ds),queen_any=any(d['queen'] for d in ds),
                component_size=ds[0]['component_size'],deaths=facts,near_enemy_companions=[dict(r=d['r'],id=d['id'],length=d['length'],queen=d['queen']) for d in companions]))
        per.append(dict(gid=g['gid'],version=g['version'],map=g['map'],opponent=g['opp'],ours=metrics([g],0),theirs=metrics([g],1)))
    summary['card']={}
    for s in (0,1):
        entries=[r for a in narrow.values() for r in a['records'] if r['side']==s and r['narrow_reject']]
        links=[(gid,d) for gid,a in narrow.items() for d in a['links'] if d['side']==s and d['narrow_reject']]
        cov=[d for gid,d in links if (gid,d['event']) in eligible_keys] if s==0 else []
        summary['card'][str(s)]=dict(entries=len(entries),pearls=sum(r['pearl'] for r in entries),queen_entries=sum(r['queen'] for r in entries),
                portal_entries=sum(r['portal'] for r in entries),linked_deaths=len(links),linked_length=sum(d['length'] for gid,d in links),
                queen_deaths=sum(d['queen'] for gid,d in links),repeated_covered=len(cov),repeated_length=sum(d['length'] for d in cov),repeated_queens=sum(d['queen'] for d in cov),
                qualified_linked=sum(d['no_enemy3'] and d['cause'] in ('wall','own body','mate body') for gid,d in links))
    summary['card_without_alternative']=summary.pop('card')
    final=load('audit-card.jsonl');summary['card']={}
    for s in (0,1):
        entries=[r for a in final for r in a['records'] if r['side']==s and r.get('card_reject')]
        links=[(a['gid'],d) for a in final for d in a['links'] if d['side']==s and d['card_reject']]
        keys={(g['gid'],d['event']) for g in games for side,c,ds in scan.repeated(g) if side==s for d in ds}
        cov=[d for gid,d in links if (gid,d['event']) in keys]
        summary['card'][str(s)]=dict(entries=len(entries),pearls=sum(r['pearl'] for r in entries),
            queen_entries=sum(r['queen'] for r in entries),portal_entries=sum(r['portal'] for r in entries),
            deaths=len(links),gross_length=sum(d['length'] for gid,d in links),queen_deaths=sum(d['queen'] for gid,d in links),
            repeated_deaths=len(cov),repeated_queens=sum(d['queen'] for d in cov),repeated_length=sum(d['length'] for d in cov),
            qualified_deaths=sum(d['no_enemy3'] and d['cause'] in ('wall','own body','mate body') for gid,d in links))
    (scan.OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    (scan.OUT/'card-summary.json').write_text(json.dumps(summary['card'],ensure_ascii=False,indent=2))
    (scan.OUT/'cells.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in groups))
    with (scan.OUT/'cells.csv').open('w',newline='') as f:
        keys=list(groups[0]);w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for r in groups:w.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,list) else v for k,v in r.items()})
    md=['# 판별 반복 사망 [M]\n',
        '[M] 머리의 마지막 유효 좌표를 사망 칸으로 센다. 벽 충돌 시도 도착 칸은 별개다. 적 머리에서 그 칸까지 실제 벽·포털을 반영한 최단 경로가 3걸음 이내이면 제외한다. 몸은 거리 계산에서 무시한다.\n',
        '[M] 비전투 분모=벽/자기몸/아군몸/아군머리/무행동. 비전투가 지형 탓이라는 뜻은 아니다. lost는 사망 직전 길이 합이며 낙하 재섭취를 빼지 않은 총량이다.\n',
        '[M] 세부 칸/라운드/각 L/여왕/포털 진입/진주: [cells.csv](cells.csv), [cells.jsonl](cells.jsonl). 각 death record의 component_entrance는 열린 변 성분에 들어온 사건이고 last_step은 사망 칸의 마지막 진입이다. 초기 배치/출생으로 들어온 경우는 별도로 표기한다.\n',
        '|[M] 판|버전|지도|상대|우리 반복 칸/사망/총 L/Q|우리 비전투 분모|상대 반복 칸/사망/총 L/Q|상대 비전투 분모|',
        '|---|---|---|---|---:|---:|---:|---:|']
    for r in per:
        a,b=r['ours'],r['theirs'];md.append(f"|{r['gid']}|{r['version']}|{r['map']}|{r['opponent']}|{a['cells']}/{a['deaths']}/{a['length']}/{a['queens']}|{a['noncombat']}|{b['cells']}/{b['deaths']}/{b['length']}/{b['queens']}|{b['noncombat']}|")
    (scan.OUT/'per-game.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(dict(core=summary['core'],card=summary['card'],man=summary['sensitivity_man3']),indent=2))

if __name__=='__main__':main()
