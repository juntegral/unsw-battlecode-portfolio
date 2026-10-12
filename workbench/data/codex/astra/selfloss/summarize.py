import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent

def readall():
    out={}
    for p in OUT.glob('m*--*.json'):
        try:g=json.loads(p.read_text())
        except ValueError:continue
        out.setdefault(g['src'],{})[g['folder']]=g
    return out

def first(a,b):
    if a.get('final_only') or b.get('final_only'):
        assert a.get('initial',a.get('signature',{}).get('initial'))==b.get('initial',b.get('signature',{}).get('initial'))
        return {'round':None,'not_checked':True}
    assert a['signature']['initial']==b['signature']['initial']
    ra,rb=a['signature']['rounds'],b['signature']['rounds']
    for r in sorted(set(ra)|set(rb),key=int):
        if ra.get(r)!=rb.get(r):
            aa=ra.get(r,{}).get('actions',[]);ab=rb.get(r,{}).get('actions',[])
            dif=next(([i,aa[i] if i<len(aa) else None,ab[i] if i<len(ab) else None] for i in range(max(len(aa),len(ab))) if i>=len(aa) or i>=len(ab) or aa[i]!=ab[i]),None)
            return dict(round=int(r),action=dif,physical=ra.get(r,{}).get('physical')!=rb.get(r,{}).get('physical'))
    return None

def flow(g,lo,hi,s):
    c=Counter()
    for r,side,role,origin,cause,L in g['eats']:
        if side==s and lo<r<=hi:c['eat_'+origin]+=1
    for d in g['deaths']:
        if d[1]==s and lo<d[0]<=hi:c['death_'+d[4]]+=d[2];c['n_'+d[4]]+=1;c['death']+=d[2];c['ndeath']+=1
    for r,side,L,paid,*rest in g['paids']:
        if side==s and lo<r<=hi:c['paid']+=paid
    for r,side,*rest in g['splits']:
        if side==s and lo<r<=hi:c['split']+=1
    return c

def write_tsv(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w') as f:
        w=csv.DictWriter(f,keys,delimiter='\t',restval=0);w.writeheader();w.writerows(rows)

def main():
    all=readall(); pairs=[]
    boundaries=json.loads((OUT/'boundary-states.json').read_text()) if (OUT/'boundary-states.json').exists() else {}
    for a,b in [('mJo5_vb','mDone8'),('mDone8','mR08_vb'),('mJo5_vb','mR05_vb'),('mDone7','mH62_vb'),('mDone7','mHzr_vb')]:
        keys=sorted(set(all.get(a,{}))&set(all.get(b,{})))
        winloss=Counter()
        for key in keys:
            x,y=all[a][key],all[b][key];f=first(x,y);winloss[x['result']+'/'+y['result']]+=1
            pairs.append(dict(a=a,b=b,key=key,result_a=x['result'],result_b=y['result'],how_a=x['how'],how_b=y['how'],ends_a=x['ends'],ends_b=y['ends'],first=f))
        print(a,b,len(keys),dict(winloss))
    (OUT/'pairs.json').write_text(json.dumps(pairs,indent=2))
    rows=[];leaderrows=[]
    for p in pairs:
        if p['a']!='mJo5_vb' or p['b']!='mDone8' or p['result_a']!='win' or p['result_b']!='loss':continue
        for arm in [p['a'],p['b']]:
            g=all[arm][p['key']];start=p['first']['round'];lo=((start-1)//25)*25
            snaps=dict(g['snaps'])
            if p['key'] in boundaries:
                bd=boundaries[p['key']];lo=bd['round'];snaps[str(lo)]=bd['snaps']
            for r in sorted(map(int,snaps)):
                if r<max(0,lo):continue
                for s in (0,1):
                    snap=snaps[str(r)][s];prev=max((int(z) for z in snaps if lo<=int(z)<r),default=r)
                    c=flow(g,prev,r,s)
                    before=snaps[str(prev)][s]
                    row=dict(arm=arm,key=p['key'],first=start,kind='state' if prev==r else 'interval',from_round=r if prev==r else prev+1,round=r,side=s,dragons=snap[0],total=snap[1],longest=snap[2],queen=snap[3],**c)
                    row['residual']=snap[1]-before[1]-sum(c['eat_'+z] for z in ['n','own','foe'])+c['death']+c['paid']
                    rows.append(row)
            d=g['detail'];ids=set()
            for r,sn in d['snapshots'].items():
                if int(r)>=350:
                    for s,z in enumerate(sn):
                        if z['id'] is not None:ids.add(z['id'])
            for i in sorted(ids):
                st=d['all_dragons'][str(i)];e=[e for e in d['eats'] if e['id']==i and e['round']>=350]
                src=Counter(e['source'] for e in e if e['source'] is not None)
                actions=[act for r,rs in g['signature']['rounds'].items() if int(r)>=350 for act in rs['actions'] if act[0]==i]
                leaderrows.append(dict(arm=arm,key=p['key'],id=i,side=st['side'],death=st['death'],natural=sum(z['origin']=='natural' for z in e),own_corpse=sum(z['origin']=='own_drop' for z in e),enemy_corpse=sum(z['origin']=='foe_drop' for z in e),sources=dict(src),stops=sum(z[1]!=1 and not z[2] for z in actions),turns=len(actions),splits=st['splits']))
    write_tsv(OUT/'ledger25.tsv',rows)
    (OUT/'longest350.json').write_text(json.dumps(leaderrows,indent=2))
    print('ledger rows',len(rows),'nonzero residual',sum(r['residual']!=0 for r in rows))
    for p in pairs:
        if p['a']=='mJo5_vb' and p['b']=='mDone8':print(p['key'],p['result_a'],p['result_b'],p['first'],p['ends_a'][0][:4],p['ends_b'][0][:4])

if __name__=='__main__':main()
