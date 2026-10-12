import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent

def windows(d,unit,end=499):
    all=d['all_dragons'];out=[]
    while unit is not None:
        st=all[str(unit)];out.append((unit,max(350,st['born']),end));parent=st['parent']
        if parent is None:break
        sp=next(x for x in all[str(parent)]['splits'] if x[3]==unit)
        if 2*st['start']<sp[1]:break
        end=sp[0];unit=parent
    return out

def main():
    pairs=json.loads((P/'pairs.json').read_text());rows=[]
    for pair in pairs:
        if pair['a']!='mJo5_vb' or pair['b']!='mDone8' or pair['result_a']!='win' or pair['result_b']!='loss':continue
        for arm in ['mJo5_vb','mDone8']:
            g=json.loads((P/f"{arm}--{pair['key']}.json").read_text());d=g['detail']
            ids={x['id'] for r,snap in d['snapshots'].items() if int(r)>=350 for x in snap if x['id'] is not None}
            ids|={x['id'] for x in d['deaths'] if x['round']>=350 and x['top']}
            for i in sorted(ids):
                st=d['all_dragons'][str(i)];end=st['death']['round'] if st['death'] else 499;win=windows(d,i,end)
                eligible={u:(lo,hi) for u,lo,hi in win if hi>=lo}
                es=[e for e in d['eats'] if e['id'] in eligible and eligible[e['id']][0]<=e['round']<=eligible[e['id']][1]]
                donors=Counter((e['source'],e['origin'],e['stop']) for e in es if e['source'] is not None)
                acts=[(int(r),a) for r,v in g['signature']['rounds'].items() for a in v['actions'] if a[0] in eligible and eligible[a[0]][0]<=int(r)<=eligible[a[0]][1]]
                rows.append(dict(arm=arm,key=pair['key'],id=i,side=st['side'],death=st['death'],windows=win,natural=sum(e['origin']=='natural' for e in es),own_corpse=sum(e['origin']=='own_drop' for e in es),enemy_corpse=sum(e['origin']=='foe_drop' for e in es),stopped_mate_pearls=sum(e['origin']=='own_drop' and e['stop'] for e in es),donors=[dict(id=u,origin=o,stopped=stop,pearls=n) for (u,o,stop),n in donors.most_common()],no_move_turns=[[r,a[0],a[1]] for r,a in acts if a[1]!=1 and not a[2]],splits=sum(a[1]==1 for r,a in acts),turns=len(acts)))
    (P/'longest-lineages350.json').write_text(json.dumps(rows,indent=2))
    print('longest lineages',len(rows))

if __name__=='__main__':main()
