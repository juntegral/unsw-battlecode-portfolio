import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,csv
from collections import Counter,defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyze import HERE,ARMS,RUNS,MAPS,firstdiv,sha,ledger_scan

def loadall():return [json.loads(p.read_text()) for v in ARMS.values() for p in sorted(HERE.glob(v+'-*.json'))]
def writecsv(name,rows):
    if not rows:return
    keys=list(rows[0]);
    with (HERE/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(c) for c in r)+' |' for r in rows])
def label(g):return g['version']+'/'+g['folder']
def basicturn(t):return {k:t[k] for k in ('r','id','s','L','head','count','action','eaten','natural','drop','paid','split','deaths','free')}
def main():
 gs=loadall();by={(g['version'],g['folder']):g for g in gs};summary=json.loads((HERE/'summary.json').read_text());sm={(x['version'],x['folder']):x for x in summary}
 # Independent imported ledger counter, cross-check all completed games.
 checks=[]
 for g in gs:
    j=dict(id=0,teamAId=1119 if g['side']==0 else 1,teamBId=1 if g['side']==0 else 1119,mapName=g['folder'],teamAName='A',teamBName='B')
    z=ledger_scan(g['arm'],Path(g['path']),j)
    assert z['result']==g['result'] and z['last']==g['last']
    assert len(z['eats'])==len(g['eats']) and len(z['deaths'])==len(g['deaths']) and len(z['splits'])==len(g['splits'])
    for r,sn in z['snaps'].items():assert [[x[0],x[1],x[3]] for x in sn]==g['snapshots'][r]
    assert sum(x[3] for x in z['paids'])==sum(t['paid'] for t in g['turns'])
    checks.append(dict(game=label(g),replay_sha256=g['sha256'],turns=len(g['turns']),deaths=len(g['deaths']),pearls=len(g['eats']),splits=len(g['splits']),logs=len(g['logs']),ledger_match=True))
    print('validated',label(g),flush=True)
 writecsv('validation.csv',checks)
 lossrows=[];timerows=[];deathrows=[];switchrows=[];allwindow=[]
 for g in gs:
    for lo,hi in ((0,20),(21,40),(41,60),(61,100),(101,g['last'])):
        if lo>hi:continue
        for side in (0,1):
            ts=[t for t in g['turns'] if t['s']==side and lo<=t['r']<=hi];ds=[d for d in g['deaths'] if d['s']==side and lo<=d['r']<=hi]
            allwindow.append(dict(game=label(g),side=side,lo=lo,hi=min(hi,g['last']),turns=len(ts),natural=sum(t['natural'] for t in ts),drops=sum(t['drop'] for t in ts),paid=sum(t['paid'] for t in ts),splits=sum(t['split'] is not None for t in ts),deaths=len(ds),rammed=sum(d['cause']=='rammed' for d in ds),rams=sum(d['cause']=='rams' for d in ds),other_deaths=sum(d['cause'] not in ('rams','rammed') for d in ds)))
    if g['result']!='loss':continue
    b=by['one5',g['folder']];s=sm[g['version'],g['folder']];r0=s['firstdiv']['a'][0]
    div=s['lastwindiv'];ourdiv=next(t for t in g['turns'] if t['r']==div['a'][0] and t['id']==div['a'][1])
    lb=by[s['lastwin'],g['folder']];bt=next(t for t in lb['turns'] if t['r']==div['b'][0] and t['id']==div['b'][1])
    lossrows.append(dict(game=label(g),firstdiv_one5=r0,lastwin=s['lastwin'],firstdiv_lastwin=div['a'][0],actor=div['a'][1],before_same=ourdiv['state']==bt['state'],action=ourdiv['action'],lastwin_action=bt['action'],permanent_behind=g['behind'],elimination=g['last']))
    prev=r0-1
    intervals=list(range(r0,g['last']+1,10))
    if intervals[-1]!=g['last']:intervals.append(g['last'])
    md=[f'# [M] {label(g)}',f'좌석 {g["side"]}; replay r은 0부터. 엔진 result의 rounds는 마지막 r+1. 첫 갈림 r{r0}; 수가 끝까지 적어지는 최초 종료 라운드 r{g["behind"]}.',
        '표의 진주·사망은 직전 표 행 다음부터 해당 행까지 누계(첫 행은 갈림 라운드만). N/T/Q = 개체/총길이/여왕길이. one5가 이미 끝났으면 —.']
    rows=[]
    for r in intervals:
        sn=g['snapshots'][str(r)];bs=b['snapshots'].get(str(r));ds=[d for d in g['deaths'] if prev<d['r']<=r];es=[e for e in g['eats'] if prev<e['r']<=r]
        row=dict(game=label(g),round=r,ours=sn[0],theirs=sn[1],one5_ours=bs[0] if bs else None,one5_theirs=bs[1] if bs else None,pearls_ours=sum(e['s']==0 for e in es),pearls_theirs=sum(e['s']==1 for e in es),our_deaths=dict(Counter(d['cause'] for d in ds if d['s']==0)),their_deaths=dict(Counter(d['cause'] for d in ds if d['s']==1)))
        timerows.append(row);rows.append([r,'/'.join(map(str,sn[0])),'/'.join(map(str,sn[1])), '/'.join(map(str,bs[0])) if bs else '—','/'.join(map(str,bs[1])) if bs else '—',str(row['pearls_ours'])+'/'+str(row['pearls_theirs']),str(row['our_deaths']),str(row['their_deaths'])]);prev=r
    md.append(table(['r','우리 N/T/Q','상대 N/T/Q','one5 우리','one5 상대','진주 우리/상대','우리 사인','상대 사인'],rows))
    rows=[]
    for d in g['deaths']:
        row=dict(game=label(g),**d);deathrows.append(row)
        rows.append([d['r'],'우리' if d['s']==0 else '상대',d['id'],d['L'],d['cause'],d['actor'],d['target'],d['activity'],d['parent'],d['age'],d['last_r'],d['last_action'],d['head'],d['free']])
    md+=['\n## [M] 모든 사망', 'activity는 관측 범주다. move/unresolved의 의도(회피·공격·탐색)는 기록만으로 구별 불가. wait-split은 여왕의 마지막 차례가 분열이었다는 뜻이며 QUEEN_WAIT 실행을 확정하지 않는다. boxed는 사망 이벤트 순간 즉시 빈 출구 0; ram 직전 상대 머리가 드롭으로 바뀌면 출구 수가 늘 수 있으므로 last_free도 JSON에 보존했다.',table(['r','팀','id','L','사인','행동자','맞은 id','마지막 활동','부모','출생후 r','마지막 차례','행동(0이동/1분열)','머리','빈 출구'],rows)]
    (HERE/('timeline-'+g['version']+'-'+g['folder']+'.md')).write_text('\n\n'.join(md)+'\n')
    ts=[t for t in g['turns'] if t['s']==0]
    # Observable gates only; these are explicitly not counterfactual action-change counts.
    switchrows.append(dict(game=label(g),queen_L4_split_low_units=sum(bool(t['q'] and t['L']==4 and t['split'] and t['count'][0][0]<(2 if g['version']=='one8' else 6)) for t in ts),queen_L4_low_split_no_enemy=sum(bool(t['q'] and t['L']==4 and t['split'] and t['count'][0][0]<(2 if g['version']=='one8' else 6) and not any(n['s']==1 for n in t['near'])) for t in ts),portal_adjacent_split=sum(bool(t['split'] and not t['q'] and t['tail_portal'] and t['L']==4 and t['r']<=100) for t in ts),short_evade_outer_eligible=sum(t['id']>1 and t['L']<=4 and t['split'] is None and t['action'][0]==0 and 1+sum(n['s']==0 for n in t['near'])<=sum(n['s']==1 for n in t['near']) for t in ts),queen_portal_adjacent=sum(t['q'] and any(o['edge']==2 for o in t['opts']) for t in ts),ram_enemy_queen=sum(d['s']==0 and d['activity']=='ram-enemy-queen' for d in g['deaths']),rounds_above400=sum(t['r']>400 for t in ts)))
 writecsv('losses.csv',lossrows);writecsv('timeline-10.csv',timerows);writecsv('deaths.csv',deathrows);writecsv('windows.csv',allwindow);writecsv('observable-gates.csv',switchrows)
 # Early rates, including a common-support panel stopping each map/seat at earliest finish across available versions.
 erows=[]
 for mode in ('available','common7','common7_equal_time'):
    for v in ARMS.values():
        vg=[g for g in gs if g['version']==v and (mode=='available' or not g['folder'].startswith('sqheld_portals_small_90029-seed1-side1'))]
        for side in (0,1):
            ts=[]
            for g in vg:
                end=min([100]+[p['last'] for p in gs if p['folder']==g['folder']]) if mode=='common7_equal_time' else 100
                ts.extend(t for t in g['turns'] if t['s']==side and t['r']<=end)
            erows.append(dict(panel=mode,version=v,side=side,games=len(vg),turns=len(ts),natural=sum(t['natural'] for t in ts),drops=sum(t['drop'] for t in ts),all_pearls=sum(t['eaten'] for t in ts),natural_per_turn=sum(t['natural'] for t in ts)/len(ts),all_per_turn=sum(t['eaten'] for t in ts)/len(ts),splits=sum(t['split'] is not None for t in ts),paid=sum(t['paid'] for t in ts)))
 writecsv('early-rates.csv',erows)
 provenance=[]
 for arm,v in ARMS.items():
    src=RUNS.parent/'bots'/arm/'main.cpp';d=dict(__import__('re').findall(r'constexpr\s+(?:bool|int|double)\s+(\w+)\s*=\s*([^;]+);',src.read_text()))
    provenance.append(dict(arm=arm,version=v,source=str(src),sha256=sha(src),constants=d))
 (HERE/'sources.json').write_text(json.dumps(provenance,indent=2))
 (HERE/'tables.json').write_text(json.dumps(dict(losses=lossrows,gates=switchrows,early=erows),indent=2))
if __name__=='__main__':main()
