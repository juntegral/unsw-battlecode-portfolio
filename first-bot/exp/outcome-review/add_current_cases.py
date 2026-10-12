#!/usr/bin/env python3
import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
old=json.load(open(C/'selection.json'));G=[json.loads(l)for l in open(C/'games.jsonl')if l.strip()]
selected={x['key']:{**x,'reasons':x['reasons'][:]}for x in old['games']}
latest=max((r['waveOrder']for r in G if r['era']=='waves'))
groups=collections.defaultdict(list)
for r in G:
    if r['waveOrder']!=latest:continue
    for p,f in [('win','winClass'),('near','nearClass'),('lead','leadClass')]:
        if r.get(f):groups[p+':'+r[f]].append(r)
addedwins=[]
for k,rr in sorted(groups.items()):
    for r in sorted(rr,key=lambda x:x['id'])[:2]:
        selected.setdefault(r['key'],{'key':r['key'],'id':r['id'],'file':r['file'],'reasons':[]})['reasons'].append('latest-W12:'+k)
        if r['outcome']=='W':addedwins.append(r)
for r in addedwins:
    candidates=[z for z in G if z['era']=='waves' and z['waveOrder']<latest and z['outcome']=='L' and z['map']==r['map'] and z['opponent']==r['opponent']]
    if candidates:
        t=max(z['waveOrder']for z in candidates);z=min((z for z in candidates if z['waveOrder']==t),key=lambda x:x['id'])
        selected.setdefault(z['key'],{'key':z['key'],'id':z['id'],'file':z['file'],'reasons':[]})['reasons'].append('latest-cell-loss-for:'+r['key'])
out={'method':['METHOD.md','METHOD-APPENDIX.md','METHOD-CURRENT-CASES.md'],'classes':old['classes'],'originalSelectedN':len(old['games']),'latestClassSizes':{k:len(v)for k,v in groups.items()},'games':sorted(selected.values(),key=lambda x:x['id'])}
with open(C/'selection-v2.json','x')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'originalN':len(old['games']),'combinedN':len(selected),'latestClasses':out['latestClassSizes']}))
