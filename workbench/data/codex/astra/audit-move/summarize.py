import sys
sys.dont_write_bytecode=True
import json, statistics
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent

def stats(gs):
    c=Counter()
    for g in gs:
        c.update(g['counts'])
        byparent=defaultdict(list)
        for sp in g['splits']:byparent[sp['parent']].append(sp)
        for d in g['deaths']:
            recent_parent=any(sp['head']==d['head'] and 0<=d['r']-sp['r']<=1 for sp in byparent[d['id']])
            entered=d['last'] is not None and d['head']!=d['last']['head'] and not recent_parent
            c['neck_recent_parent']+=d['neck_only'] and recent_parent
            c['neck_entry_deaths']+=d['neck_only'] and entered
            c['pinned_entry_deaths']+=d['pinned'] and entered
            c['reason4_deaths']+=d['reason']==4
    out=dict(games=len(gs),counts=dict(c),per1000={k:round(1000*v/c['turns'],5) for k,v in c.items()} if c['turns'] else {})
    out['queen_L2_share']=c['queen_L2_turns']/c['queen_turns'] if c['queen_turns'] else None
    gs2=[g for g in gs if g['start_units']==2]
    out['two_starters']=dict(games=len(gs2),first_split=[g['first_split'] for g in gs2],first_queen_split=[g['first_queen_split'] for g in gs2])
    for k in ('first_split','first_queen_split'):
        vals=[g[k] for g in gs2 if g[k] is not None]
        out['two_starters'][k+'_median']=statistics.median(vals) if vals else None
        out['two_starters'][k+'_missing']=sum(g[k] is None for g in gs2)
    for r in ('50','100'):
        vals=[g['snapshots'][r]['units'] for g in gs2 if r in g['snapshots']]
        out['two_starters']['units'+r+'_mean']=statistics.mean(vals) if vals else None
        out['two_starters']['units'+r+'_n']=len(vals)
    return out

def main():
    gs=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')]
    summary={v:stats([g for g in gs if g['version']==v]) for v in ('one5','one7','one8','one9','one10')}
    summary['before']=stats([g for g in gs if g['version'] in ('one5','one7')])
    summary['after']=stats([g for g in gs if g['version'] in ('one8','one9','one10')])
    summary['strata']={str(opp):{v:stats([g for g in gs if g['version']==v and g['oppid']==opp]) for v in ('one5','one7','one8','one9','one10')} for opp in sorted({g['oppid'] for g in gs})}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    keys=['pinned_deaths','neck_only_deaths','self_shut_deaths','portal_noeat','portal_splits','portal_child_died3','early_portal_splits','early_portal_child_died3','pearls','stationary_alive','empty_move','queen_L2_deaths']
    for v in ('one5','one7','one8','one9','one10','before','after'):
        s=summary[v];print(v,s['games'],'games',s['counts'].get('turns',0),'turns')
        print({k:(s['counts'].get(k,0),round(s['per1000'].get(k,0),3)) for k in keys})
        print('two starters',s['two_starters'],'q2share',s['queen_L2_share'])

if __name__=='__main__':main()
