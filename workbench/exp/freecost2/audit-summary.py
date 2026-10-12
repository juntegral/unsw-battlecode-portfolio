from pathlib import Path
from collections import Counter
import json, re

task=Path(__file__).resolve().parent
first=json.loads((task/'firstdiv.json').read_text())
index=json.loads((task/'audit-index.json').read_text())
summary={'histories':len(index),'errors':[],'firstDecisions':[],'extraDecisions':[],'nativeDepth':Counter(),'uncertain':Counter(),'bodyDifferent':0,'postDifferent':0,'nativeActual':Counter(),'firstInputDifferent':[]}
for entry in index:
    row=next(r for r in first['rows'] if r['key']==entry['key'])
    prefix=task.parents[1]/entry['prefix']
    report=json.loads(Path(str(prefix)+'.json').read_text())
    if entry['exit'] or any(report['checks'].values()): summary['errors'].append(entry)
    summary['uncertain'].update(report['uncertain'])
    native={arm:[json.loads(l) for l in Path(str(prefix)+'.'+arm+'.jsonl').read_text().splitlines()] for arm in ['on','off']}
    snapshots=json.loads(Path(str(prefix)+'.snapshots.json').read_text())
    for s, n, o in zip(snapshots,native['on'],native['off']):
        summary['bodyDifferent']+=n['body']!=o['body']
        summary['postDifferent']+=n['post']!=o['post']
        chosen=n if entry['history']=='on' else o
        summary['nativeActual']['same' if chosen['choice']==s['actual'] else 'different']+=1
        depths=[re.search(r'\bd(\d+)\b',v['indicator']) for v in [n,o]]
        if all(depths):
            x,y=map(lambda m:int(m[1]),depths)
            summary['nativeDepth']['lower' if x<y else 'higher' if x>y else 'same']+=1
        else: summary['nativeDepth']['untagged']+=1
        changed=next((c for c in row['changed'] if c['id']==s['id'] and s['round']==row['R']),None)
        if not changed: continue
        expected={arm:changed[arm]['text'] for arm in ['on','off']}
        rec={'key':row['key'],'history':entry['history'],'R':row['R'],'id':s['id'],'on':n['choice'],'off':o['choice'],'expected':expected,'reproduced':{arm:native[arm][snapshots.index(s)]['choice']==expected[arm] for arm in ['on','off']},'bodySame':n['body']==o['body'],'bodyExact':n['body']==s['body'],'onScore':n['score'],'offScore':o['score'],'onIndicator':n['indicator'],'offIndicator':o['indicator'],'actualOracle':s['actualOracle']}
        summary['firstDecisions' if s['id']==row['id'] else 'extraDecisions'].append(rec)
for row in first['rows']:
    if row['status']!='matched': continue
    prefix=task/'audit'/row['key'].replace(':','_')
    inputs={}
    for history in ['on','off']:
        lines=Path(str(prefix)+'-'+history+'.input').read_text().splitlines()[1:]
        inputs[history]=[l.split()[:-4] for l in lines if l.split()[0]==str(row['id']) and int(l.split()[1])<=row['R']]
    if inputs['on']!=inputs['off']: summary['firstInputDifferent'].append(row['key'])
summary['firstReproduced']=sum(sum(r['reproduced'].values()) for r in summary['firstDecisions'])
summary['firstN']=2*len(summary['firstDecisions'])
summary['firstBodyExact']=sum(r['bodyExact'] for r in summary['firstDecisions'])
(task/'audit-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['firstDecisions','extraDecisions']},indent=2,ensure_ascii=False))
print('first mismatch',[r for r in summary['firstDecisions'] if not all(r['reproduced'].values())])
print('extra',json.dumps(summary['extraDecisions']))
