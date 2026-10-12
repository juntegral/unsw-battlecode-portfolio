import json,gzip,math,statistics
from pathlib import Path
from collections import defaultdict,Counter
O=Path(__file__).parent
def divide(a,b):return a/b if b else None
def roles(t,tm):
    if t['src']=='top':return ['elite-top10']
    if t['src']=='local':return ['local-v12','local-'+t['set'].split('-')[1]]
    return ['ours-online','ours-v1' if t['set'].startswith('v1-') else 'ours-W0-W12']
def main():
    T=json.loads((O/'tables.json').read_text());P={t['key']:t for t in json.loads((O/'population.json').read_text())['tasks']};groups=defaultdict(lambda:defaultdict(list));keys=set()
    for l in gzip.open(O/'supplement.jsonl.gz','rt'):
        s=json.loads(l);assert s['key'] not in keys;keys.add(s['key']);t=P[s['key']]
        for r,cp in s['cp'].items():
            eligible=[tm for tm in 'AB' if t.get('rank'+tm) is not None and t['rank'+tm]<=10] if t['src']=='top' else [t['us']]
            for tm in eligible:
                for role in roles(t,tm):
                    v={'rates':[],'geometry':[],'unionRates':None,'fullTeam':cp['fullSymmetry']['teams'][tm],'fullProcesses':[p for p in cp['fullSymmetry']['processes'] if p['team']==tm],'trueMask':cp['fullSymmetry'].get('trueMask',{'x':2,'y':1,'xy':4}[T['maps'][s['map']+'/'+s['layout']]['truth']['symmetry']]),'certificates':cp['teamCertificates'][tm]}
                    groups[('global',role)][r].append(v);groups[(s['map']+'/'+s['layout'],role)][r].append(v)
            for role in roles(t,t.get('us','A')):
                if t['src']=='local':groups[('global',role)][r].append({'rates':cp['rates'],'unionRates':cp['unionRates'],'geometry':[]});groups[(s['map']+'/'+s['layout'],role)][r].append({'rates':cp['rates'],'unionRates':cp['unionRates'],'geometry':[]})
            for v in cp['geometry']:
                for role in roles(t,v['team']):
                    groups[('global',role)][r].append({'rates':[],'geometry':[v],'unionRates':None});groups[(s['map']+'/'+s['layout'],role)][r].append({'rates':[],'geometry':[v],'unionRates':None})
    output={}
    for (m,role),rounds in groups.items():
        b={}
        for r,rs in rounds.items():
            a={'rates':{},'processGeometry':{},'unionRates':{}}
            rate=[v for s in rs for v in s['rates']]
            for mode in ['own','inherited','packet','legacy']:
                vals=[p[mode] for p in rate];ss={k:sum(v.get(k,0) for v in vals) for k in ['tp','fp','fountainN','classified','rateN','rateRelativeAbsoluteSum']};ss.update(N=len(vals),precision=divide(ss['tp'],ss['tp']+ss['fp']),recall=divide(ss['tp'],ss['fountainN']),rateRelativeMAE=divide(ss['rateRelativeAbsoluteSum'],ss['rateN']));a['rates'][mode]=ss
            for mode in ['raw','dynamicMirrored']:
                vals=[s['unionRates'][mode] for s in rs if s['unionRates']];ss={k:sum(v.get(k,0) for v in vals) for k in ['tp','fp','fountainN','classified','rateN','rateRelativeAbsoluteSum']};ss.update(N=len(vals),precision=divide(ss['tp'],ss['tp']+ss['fp']),recall=divide(ss['tp'],ss['fountainN']),rateRelativeMAE=divide(ss['rateRelativeAbsoluteSum'],ss['rateN']));a['unionRates'][mode]=ss
            pr=[v for s in rs for v in s['geometry']]
            for mode in ['own','inherited']:
                a['processGeometry'][mode]={}
                for region in ['raw','mirrored']:
                    vs=[(p[mode]['geometry'][region],p['weight']) for p in pr];a['processGeometry'][mode][region]={}
                    for pocket in ['optimistic','pessimistic','literalOptimistic','certified']:
                        ss={k:sum(v[pocket][k]*w for v,w in vs) for k in ['tp','fp','fn','predicted','evaluated']};ss.update(sampleProcessN=len(vs),weightedProcessN=sum(w for v,w in vs),precision=divide(ss['tp'],ss['tp']+ss['fp']),recall=divide(ss['tp'],ss['tp']+ss['fn']));a['processGeometry'][mode][region][pocket]=ss
                    ss={k:sum(v['frontier'][k]*w for v,w in vs) for k in ['correct','N','spawnCorrect','spawnN','fountainCorrect','fountainN']};ss.update(sampleProcessN=len(vs),weightedProcessN=sum(w for v,w in vs),accuracy=divide(ss['correct'],ss['N']),spawnAccuracy=divide(ss['spawnCorrect'],ss['spawnN']),fountainAccuracy=divide(ss['fountainCorrect'],ss['fountainN']));a['processGeometry'][mode][region]['frontier']=ss
                root={k:sum(p[mode]['ownRootOnlyFrontier'][k]*p['weight'] for p in pr) for k in ['correct','N']};root.update(sampleProcessN=len(pr),accuracy=divide(root['correct'],root['N']));a['processGeometry'][mode]['rootOnlyFrontier']=root
            full=[v for v in rs if 'fullTeam' in v];pp=[(p,v['trueMask']) for v in full for p in v['fullProcesses']]
            a['fullSymmetry']={'teamN':len(full),'teamDecidedN':sum(v['fullTeam']['mask'] in (1,2,4) for v in full),'teamDynamicN':sum(v['fullTeam']['dynamicMask'] is not None for v in full),'teamDynamicDecidedN':sum(v['fullTeam']['dynamicMask'] in (1,2,4) for v in full),'teamFirstRounds':[v['fullTeam']['first'] for v in full if v['fullTeam']['first'] is not None],'teamDynamicFirstRounds':[v['fullTeam']['dynamicFirst'] for v in full if v['fullTeam']['dynamicFirst'] is not None],'teamMirroredCoverageMean':statistics.fmean(v['fullTeam']['mirroredCoverage'] for v in full) if full else None,'teamDynamicMirroredCoverageMean':statistics.fmean(v['fullTeam']['dynamicMirroredCoverage'] for v in full if v['fullTeam']['dynamicMirroredCoverage'] is not None) if any(v['fullTeam']['dynamicMirroredCoverage'] is not None for v in full) else None,'truthNotSurvivingN':sum(not(v['fullTeam']['mask']&v['trueMask']) or v['fullTeam']['dynamicMask'] is not None and not(v['fullTeam']['dynamicMask']&v['trueMask']) for v in full),'processN':len(pp)}
            for mode in ['own','inherited','dynamic']:
                pr=[(p[mode],bit) for p,bit in pp if p[mode] is not None];a['fullSymmetry'][mode]={'N':len(pr),'decidedN':sum(q['mask'] in (1,2,4) for q,bit in pr),'truthNotSurvivingN':sum(not(q['mask']&bit) for q,bit in pr),'mirroredCoverageMean':statistics.fmean(q['mirroredCoverage'] for q,bit in pr) if pr else None,'firstRounds':[q['first'] for q,bit in pr if q['first'] is not None]}
            a['teamCertificates']={}
            for region in ['raw','mirrored']:
                vals=[v['certificates'][region] for v in full];ss={k:sum(v[k] for v in vals) for k in ['tp','fp','fn','predicted','evaluated']};ss.update(N=len(vals),precision=divide(ss['tp'],ss['tp']+ss['fp']),recall=divide(ss['tp'],ss['tp']+ss['fn']));a['teamCertificates'][region]=ss
            b[r]=a
        output.setdefault(m,{})[role]=b
    T['supplement']={'games':len(keys),'method':'rate packets chosen on actual send turns; replace strongest per-origin sample summary rather than add overlapping counters; one first-hash process per live seat/round, weighted by live population, conditional all-root seeds. Portal-pair symmetry and closed-component pocket certificates also measured. Pilot four-process records reduced to the same first-hash sample before pooling.','results':output};(O/'tables.json').write_text(json.dumps(T,ensure_ascii=False,indent=1)+'\n');print('supplement games',len(keys))
if __name__=='__main__':main()
