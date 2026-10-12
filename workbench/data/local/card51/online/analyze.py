import sys, os, json, glob, pathlib
sys.dont_write_bytecode = True
CHECK='~/meow-cards/card-51/work/card_51_check.py'
sys.path.insert(0, str(pathlib.Path(CHECK).parent.parent))
source=pathlib.Path(CHECK).read_text()
source=source.replace("'pearls_60', 'pearls_100'", "'pearls_50', 'pearls_60', 'pearls_100'")
source=source.replace("stat['pearls_60'] += rnd <= 60", "stat['pearls_50'] += rnd <= 50\n                stat['pearls_60'] += rnd <= 60")
source=source.replace('units_100 = None', 'units_100 = None\n    queen_cause = None')
source=source.replace('queen_death = rnd', "queen_death = rnd\n                    queen_cause = REASONS[reason] if reason < len(REASONS) else str(reason)")
source=source.replace("'queen_death_round': queen_death", "'queen_death_cause': queen_cause, 'queen_death_round': queen_death")
ns={'__file__':CHECK,'__name__':'checker_reused'}
exec(compile(source,CHECK,'exec'),ns)
replay=ns['replay']
sets={'sr51':'sr51-bob1-new','main48':'qn48v1-bob1-new','main47':'qn48v1-bob1-old','um47':'um47c-bob1-new'}
out=pathlib.Path('data/local/card51/online')
rows=[]
for tag,folder in sets.items():
    files=sorted(glob.glob(f'data/online/smoke/{folder}/game-*.json'))
    assert len(files)==15,(tag,len(files))
    for file in files:
        meta=json.load(open(file)); side='A' if meta['teamAId']==1119 else 'B'
        assert 1119 in (meta['teamAId'],meta['teamBId'])
        path=str(pathlib.Path(file).parent/f"M{meta['id']}.replay")
        ours=ns['scan'](path,side); ours.pop('digests')
        root=replay.load(path).root(); result=root.pointer(4)
        row={'set':tag,'game_id':meta['id'],'map_id':meta['mapId'],'map':meta['mapName'],'seed':meta['seed'],'our_side':side,'result': 'draw' if meta['winner'] is None else 'win' if meta['winner'].upper()==side else 'loss','end': ['elimination','round limit'][result.u16(2)] if result.u16(2)<2 else str(result.u16(2)), 'terminated':result.bit(0),'ours':ours}
        if ours['judged']:
            opp=ns['scan'](path,'B' if side=='A' else 'A'); opp.pop('digests'); row['opponent']=opp
        rows.append(row)
    print(tag,'scanned',flush=True)
(out/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
qual=sorted({(r['map_id'],r['map']) for r in rows if r['ours']['judged']})
lines=['Table 1. Walled-start layouts (checker `judged`: centre map + walled + pinned): '+(', '.join(n for _,n in qual) or 'none')+'.', 'Each cell: game/side; result/end@last round; first out; outside turns r30–59; pearls r50/r100; dragons at start r100; visited head tiles through r100; wall/self deaths r0–100; queen; opponent first out/pearls r100.', '| Layout | sr51 | main48 | main47 | um47 |','|---|---|---|---|---|']
def first(v): return 'never' if v is None else str(v)
def cell(r):
    s=r['ours']; o=r['opponent']; den=s['turns_30_59']; num=s['out_30_59']; share=f'{num}/{den} ({num/den:.1%})' if den else '0/0 (n/a)'
    queen='alive' if s['queen_death_round'] is None else f"r{s['queen_death_round']} {s['queen_death_cause']}"
    return f"{r['game_id']}/{r['our_side']}; {r['result']}/{r['end']}@r{s['rounds']}; {first(s['first_exit'])}; {share}; {s['pearls_50']}/{s['pearls_100']}; {s['units_100']}; {s['tiles_visited_100']}; {s['deaths_0_100']['wall']}/{s['deaths_0_100']['self']}; {queen}; {first(o['first_exit'])}/{o['pearls_100']}"
for mid,name in qual:
    cells=[]
    for tag in sets:
        matches=[r for r in rows if r['set']==tag and r['map_id']==mid and r['ours']['judged']]
        cells.append('<br>'.join(cell(r) for r in matches) or 'none')
    lines.append('| '+name+' | '+' | '.join(cells)+' |')
order=sorted({(r['map_id'],r['map']) for r in rows})
lines+=['','Table 2. All 15 games per set; arrays follow this map order: '+', '.join(n for _,n in order)+'.','Wall/self counts and pearls include rounds 0–100; stall share uses all centre-rule turns and needs no paired base game.','| Set | Wall deaths/game (total/15) | Own-body deaths/game (total/15) | Pearls r100/game (total) | Stall/centre-rule turns |','|---|---|---|---|---|']
for tag in sets:
    group=sorted([r for r in rows if r['set']==tag], key=lambda r:(r['map_id'],r['map']))
    assert [(r['map_id'],r['map']) for r in group]==order
    w=[r['ours']['deaths_0_100']['wall'] for r in group]; b=[r['ours']['deaths_0_100']['self'] for r in group]; p=[r['ours']['pearls_100'] for r in group]
    st=sum(r['ours']['stalled_turns'] for r in group); rt=sum(r['ours']['rule_turns'] for r in group)
    share=f'{st}/{rt} ({st/rt:.1%})' if tag=='sr51' and rt else '—'
    lines.append(f'| {tag} | {w} ({sum(w)}/15) | {b} ({sum(b)}/15) | {p} ({sum(p)}) | {share} |')
keys={tag:{(r['map_id'],r['seed'],r['our_side']) for r in rows if r['set']==tag} for tag in sets}
paired=len(set.intersection(*keys.values()))
lines+=['',f'The four sets contain 60 games on 15 layouts, with {paired} shared map/seed/side pairs across all four sets; '+('all cross-set comparisons are unpaired.' if paired==0 else 'games without matching map/seed/side are unpaired.')]
groups={tag:[r for r in rows if r['set']==tag and r['ours']['judged']] for tag in sets}
lines.append('Walled-start first-out rounds are '+', '.join(tag+' '+str([first(r['ours']['first_exit']) for r in group]) for tag,group in groups.items())+'; pearls by r100 are '+', '.join(tag+' '+str([r['ours']['pearls_100'] for r in group]) for tag,group in groups.items())+'.')
assert len(lines)<=30
(out/'table.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
