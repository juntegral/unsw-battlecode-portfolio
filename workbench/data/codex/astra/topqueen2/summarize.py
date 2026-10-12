import json,statistics
from collections import Counter,defaultdict
from pathlib import Path
P=Path('data/codex/astra/topqueen2')
def mean(a):return round(statistics.mean(a),2) if a else None
def med(a):return statistics.median(a) if a else None
def pct(n,d):return round(100*n/d,1) if d else None
def summarise(rows):
 n=len(rows);out={'n':n};h=Counter(g['how'] for g,s in rows);out['end_counts']=dict(h);out['end_pct']={k:pct(h[k],n) for k in ['queen','longest','total','wipe','draw']};out['wins']=sum(g['winner']==s for g,s in rows)
 both=[(g,s) for g,s in rows if min(g['final'][0][0],g['final'][1][0])>0];out['both_alive_n']=len(both);out['both_alive_wins']=sum(g['winner']==s for g,s in both)
 qwin=[(g,s) for g,s in rows if g['how']=='queen' and g['winner']==s];out['queen_wins']=len(qwin);out['qwin_both_alive']=sum(g['final'][1-s][0]>0 for g,s in qwin)
 end=[g['final'][s][0] for g,s in rows if g['final'][s][0]>0];out['alive']=len(end);out['alive_pct']=pct(len(end),n);out['endL']=mean(end)
 survivors=[(g,s) for g,s in rows if g['final'][s][0]>0 and g['last']==499];out['full_survivors']=len(survivors);out['survivor_growth']=[mean([g['snaps'][str(r)][s][0] for g,s in survivors]) for r in [99,199,299,399,499]]
 out['growth_alive']=[dict(n=len(a:=[g['snaps'][str(r)][s][0] for g,s in rows if str(r) in g['snaps'] and g['snaps'][str(r)][s][0]>0]),L=mean(a)) for r in [99,199,299,399,499]]
 out['eating100']=[]
 for z in range(5):
  turns=[t for g,s in rows for t in g['turns'][s] if t['r']//100==z];e=[e for g,s in rows for e in g['eats'][s] if e['r']//100==z];c=Counter(e['origin'] for e in e)
  out['eating100'].append(dict(turns=len(turns),eats=dict(c),per100={k:round(c[k]*100/len(turns),2) if turns else None for k in ['natural','mate','enemy']}))
 eats=[e for g,s in rows for e in g['eats'][s]];mc=[e for e in eats if e['origin']=='mate'];out['all_eats']=dict(Counter(e['origin'] for e in eats));out['donors']={'pearls':len(mc),'length_med':med([e['donor_L'] for e in mc]),'causes':dict(Counter(e['cause'] for e in mc)),'within3':sum(e['qdist'] is not None and e['qdist']<=3 for e in mc),'distance_mean':mean([e['qdist'] for e in mc if e['qdist'] is not None]),'wait_med':med([e['lag'] for e in mc])}
 ts=[t for g,s in rows for t in g['turns'][s] if t['r']>=300];out['late']={'turns':len(ts),'mate':mean([t['mate'] for t in ts if t['mate'] is not None]),'enemy':mean([t['enemy'] for t in ts if t['enemy'] is not None]),'mates5':mean([t['mates5'] for t in ts]),'alone':pct(sum(t['mate'] is None for t in ts),len(ts)),'edge':mean([t['edge'] for t in ts]),'kelp':mean([t['kelp'] for t in ts]),'sealed16_pct':pct(sum(t['component']<=16 for t in ts),len(ts)),'L3_pct':pct(sum(t['L']<=3 for t in ts),len(ts))}
 ks=[k for g,s in rows for k in g['kills'] if k['side']==s];out['kill']={'n':len(ks),'Lmed':med([k['L'] for k in ks]),'Lmax':max([k['L'] for k in ks],default=None),'freeonly':sum(k['steps']<=k['free'] for k in ks),'paid_slot':sum(k['steps']>k['free'] for k in ks),'paid_actual':sum(k['paid_before']>0 for k in ks),'pearls_runs':sum(k['pearls']>0 for k in ks),'pearls':sum(k['pearls'] for k in ks),'outside':sum(k['view_at_last_qturn']==False for k in ks),'near5_med':med([k['near5'] for k in ks]),'near5_2plus':sum(k['near5']>=2 for k in ks),'rmed':med([k['r'] for k in ks]),'afterdead':sum(k['own_q_dead'] for k in ks)}
 out['defends']=sum(len(g['defends'][s]) for g,s in rows);out['fates']=dict(Counter('alive' if g['fates'][s] is None else 'rammed' if 'ram' in g['fates'][s] else g['fates'][s]['cause'] for g,s in rows))
 return out

def main():
 games=[json.loads(l) for l in (P/'games.jsonl').read_text().splitlines()];groups=defaultdict(list);ranks=json.loads((P/'inventory.json').read_text())['top']
 for g in games:
  if g['src'] in ('top3','top1'):
   for s,t in enumerate(g['teams']):groups[g['src']+'-'+str(t)].append((g,s))
   groups[g['src']+'-all'].extend((g,s) for s in (0,1))
  else:
   s=g['teams'].index(1119);o=g['teams'][1-s];v=g['version'];groups[f'one{v}'].append((g,s));groups[f'one{v}-opp{o}'].append((g,s));groups[f'opp{o}-one{v}'].append((g,1-s))
   if o==989:groups['kraken-all'].append((g,1-s))
   if g['gid'] in (1482056,1482057,1482058,1482059,1482060,1483343,1483344,1483345,1483346,1483347):groups['kraken-original10'].append((g,1-s))
 out={k:summarise(v) for k,v in groups.items()};(P/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print('games',len(games),Counter(g['src'] for g in games))
 for k,v in out.items():
  if k.startswith('top1-') or ('opp' in k and 'one9' not in k and 'one10' not in k):continue
  print(k,'n',v['n'],'ends',v['end_counts'],'alive',v['alive'],'L',v['endL'],'survivor_growth',v['survivor_growth'],'eats',v['all_eats'],'kills',v['kill'])
if __name__=='__main__':main()
