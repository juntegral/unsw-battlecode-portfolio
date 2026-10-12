import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/early-opus')
from summ import games
label=sys.argv[1];maps=sys.argv[2:]
for g in games(label):
    if g['map'] not in maps:continue
    print('==',label,g['gid'],g['map'],g['size'],'initial heads',g['initial'],'initial length',g['initialL'])
    for s in (0,1):
        ids=sorted({t['id'] for t in g['turns'] if t['side']==s and t['r']<=1})
        for i in ids[:3]:
            tr=[t for t in g['turns'] if t['id']==i and t['r']<=70]
            print('  side',s,'id',i,'queen' if tr and tr[0]['queen'] else '',' '.join('%d:%d,%d%s%s'%(t['r'],t['h'][0],t['h'][1],'*' if sum(t['eats'].values()) else '','S' if t['split'] else '') for t in tr[::3]), '| d0:',[t['d0'] for t in tr[::6]])
        print('  side',s,'splits',[(x['r'],x['L']) for x in g['splits'] if x['side']==s][:8],'deaths',[(d['r'],d['cause'],d['L']) for d in g['deaths'] if d['side']==s][:8],'first eats',[(e['r'],tuple(e['xy'])) for e in g['eats'] if e['side']==s][:6])
