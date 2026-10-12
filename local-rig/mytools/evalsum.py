import json, sys, collections
rows=[json.loads(l) for l in open(sys.argv[1])]
selfplay = len(sys.argv) > 2
def cls(n): return 'small' if '_small_' in n else 'medium' if '_medium_' in n else 'large'
tab=collections.defaultdict(lambda: collections.Counter())
ends=collections.Counter(); qalive=0; perm=collections.defaultdict(lambda: [0,0])
for r in rows:
    side=r['first_bot_side']; c=cls(r['map_name'])
    if selfplay:
        res='side0' if r['winner']==0 else 'side1' if r['winner']==1 else 'draw'
        tab[c][res]+=1
        continue
    win = r['winner']==side; draw = r['winner']=='draw'
    tab[(c,side)]['win' if win else 'draw' if draw else 'loss']+=1
    rule = r['verdict'].split(',')[0].split(' each')[0]
    rule = 'equal' if rule.startswith('equal') else rule
    ends[('WIN ' if win else 'draw ' if draw else 'loss ')+r['how']+': '+rule]+=1
    myq = r['a_queen'] if side==0 else r['b_queen']
    qalive += myq>0
    perm[r['map_name']][0]+=win; perm[r['map_name']][1]+=1
if selfplay:
    for c in ('small','medium','large'): print(c, dict(tab[c]))
    print('total', dict(sum((tab[c] for c in tab), collections.Counter())), 'games', len(rows))
else:
    tw=0
    for c in ('small','medium','large'):
        for s in (0,1):
            t=tab[(c,s)]; n=sum(t.values()); tw+=t['win']
            print(f'{c:6} side{s}: {t["win"]}/{n} wins, {t["draw"]} draws')
    print('TOTAL wins', tw, 'of', len(rows), '| my queen alive at end in', qalive, 'games')
    for k,v in sorted(ends.items()): print('  ',v,k)
    print('maps with at least one win:', sum(1 for m,v in perm.items() if v[0]>0), 'of', len(perm))
    for m,v in sorted(perm.items()): print('   ',m.replace('sqheld_',''),f'{v[0]}/{v[1]}')
