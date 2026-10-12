import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
sys.path.insert(0, 'tools')
from ladder_replay import replay
OUT=Path('data/analysis/ladder/dossier')
ROWS=[json.loads(s) for s in (OUT/'per-game.jsonl').read_text().splitlines()]
US=[r for r in ROWS if r['relation']=='us']
LAYOUTS=sorted({r['layout_key'] for r in US})
WINDOWS={'0-100':(0,100),'101-300':(101,300)}
assert len(ROWS)==1000 and len(US)==500 and len(LAYOUTS)==19
assert Counter(r['relation'] for r in ROWS)=={'us':500,'them':500}
assert len({(r['game'],r['relation']) for r in ROWS})==1000
EXTRA={}
cache=OUT/'work/fp_recount.json'
source_hash=hashlib.sha256((OUT/'per-game.jsonl').read_bytes()).hexdigest()
if cache.exists():
    saved=json.loads(cache.read_text())
    if saved['source_sha256']==source_hash: EXTRA=saved['games']
if not EXTRA:
    for ix,r in enumerate(US,1):
        root=replay.load(Path(r['replay'])).root()
        teams={}
        for line in root.text(0).splitlines():
            q=line.split()
            if q and q[0]=='DRAGON': teams[len(teams)]='AB'[int(q[1])]
        present={}; rnd=0; actor=None
        c={s:{w:Counter() for w in [*WINDOWS,'game']} for s in ('us','them')}
        for ev in root.pointer(3):
            k=ev.u16(0)
            if k not in (0,1,3,10): continue
            p=ev.pointer(0)
            if k==0: rnd,actor=p.i32(0),None
            elif k==1:
                actor=p.i32(0)
                s='us' if teams[actor]==r['our_side'] else 'them'
                for w in ['game']+[w for w,(lo,hi) in WINDOWS.items() if lo<=rnd<=hi]: c[s][w]['turns']+=1
            elif k==10: teams[p.i32(4)]='AB'[p.u16(8)]
            else:
                tile=tuple(replay.point(p.pointer(0)))
                if p.u32(0):
                    assert tile not in present
                    present[tile]=actor is not None
                else:
                    dropped=present.pop(tile)
                    s='us' if teams[actor]==r['our_side'] else 'them'
                    for w in ['game']+[w for w,(lo,hi) in WINDOWS.items() if lo<=rnd<=hi]:
                        c[s][w]['eaten']+=1;c[s][w]['drop_eaten']+=int(dropped)
        for s in ('us','them'):
            row=next(x for x in ROWS if x['game']==r['game'] and x['relation']==s)
            assert c[s]['game']['eaten']==row['game_counts']['pearls_eaten']
            for w in WINDOWS:
                assert c[s][w]['turns']==row['ranges'][w]['turns']
                assert c[s][w]['eaten']==row['ranges'][w]['pearls_eaten']
        EXTRA[str(r['game'])]=c
        if ix%100==0: print('Recount validated',ix,flush=True)
    cache.write_text(json.dumps({'source_sha256':source_hash,'games':EXTRA})+'\n')
METRICS=[]
def add(name,w,unit,fields,fn,description,status='open',context=False):
    METRICS.append(dict(name=name,window=w,unit=unit,fields=fields,fn=fn,description=description,status=status,context=context))
def simple(name,n,d,unit='%',scale=100,description=None,status='open'):
    for w in WINDOWS:
        add(name,w,unit,[f'ranges.{w}.{n}',f'ranges.{w}.{d}'],lambda r,w=w,n=n,d=d,scale=scale:(r['ranges'][w][n]*scale,r['ranges'][w][d]),description or name,status)
CAUSES=list(ROWS[0]['ranges']['0-100']['deaths'])
for cause in CAUSES:
    for w in WINDOWS:
        add('Death: '+cause,w,'/1k turns',[f'ranges.{w}.deaths.{cause}',f'ranges.{w}.turns'],lambda r,w=w,cause=cause:(1000*r['ranges'][w]['deaths'][cause],r['ranges'][w]['turns']), 'dies as '+cause, 'explained' if cause.startswith('head-on') else 'open')
# The mover death is exactly one initiating dragon per head-on meeting (either team).
for w in WINDOWS:
    add('Head-on meetings started',w,'/1k turns',[f'ranges.{w}.deaths.head-on mover',f'ranges.{w}.turns'],lambda r,w=w:(1000*r['ranges'][w]['deaths']['head-on mover'],r['ranges'][w]['turns']),'starts head-on meetings','explained')
simple('Same-team head-on meetings','same_team_head_on_trades','turns','/1k turns',1000,'starts a head-on meeting with a teammate')
simple('Cross-team head-on involvement','cross_head_on_trades','turns','/1k turns',1000,'takes part in a cross-team head-on meeting','explained')
simple('Split frequency','splits','turns','/1k turns',1000,'splits on its turn')
simple('Splits per eaten pearl','splits','pearls_eaten','/pearl',1,'splits per pearl eaten')
simple('Blind turns','no_view_pearl_turns','turns',description='starts its turn with no pearl in view')
simple('Blind successful movement','no_view_pearl_moved','no_view_pearl_turns',description='makes at least one successful step when no pearl is in view')
simple('Blind direction kept','keeps','keeps_eligible',description='keeps its previous successful direction when no pearl is in view')
simple('Blind re-tread','dither','no_view_pearl_moved',description='steps onto one of its own last 12 visited tiles when no pearl is in view')
simple('Adjacent pearl missed','adjacent_pearl_missed','adjacent_pearl_turns',description='eats none of the pearls adjacent at the start of its turn')
simple('Adjacent pearl opportunity','adjacent_pearl_turns','turns',description='starts beside at least one pearl')
simple('Repeated-spawn tile nearby','hot_turns','turns',description='starts on or beside a tile with at least two prior pearl spawns')
simple('Portal steps','portal_steps','turns','/1k turns',1000,'takes portal steps')
for w,(lo,hi) in WINDOWS.items():
    for name,key in [('Tiles visited per 20-round dragon block','distinct_per_dragon_20'),('Blind tiles visited per 20-round dragon block','no_view_pearl_distinct_per_dragon_20')]:
        add(name,w,'tiles/block',[f'ranges.{w}.{key}.sum',f'ranges.{w}.{key}.n'],lambda r,w=w,key=key:(r['ranges'][w][key]['sum'],r['ranges'][w][key]['n']),'visits distinct tiles in a complete 20-round dragon block'+(' during blind turns' if key.startswith('no_') else ''))
    add('Board seen by endpoint',w,'%', [f'ranges.{w}.seen_share_end'],lambda r,w=w:(100*r['ranges'][w]['seen_share_end'],1) if r['ranges'][w]['seen_share_end'] is not None else (0,0),'has seen a larger share of the board by the endpoint')
    for name,n,d in [('Births within six steps','near6_births','births'),('Natural births within six steps','natural_near6','natural_births')]:
        add(name,w,'%', [f'ranges.{w}.{n}',f'ranges.{w}.{d}'],lambda r,w=w,n=n,d=d:(100*r['ranges'][w][n],r['ranges'][w][d]),'has a head within six steps of '+('natural ' if n.startswith('natural') else '')+'pearl births')
    for name,n,d in [('Birth-cohort harvest','cohort_eaten','births'),('Natural birth-cohort harvest','natural_eaten','natural_births'),('Portal-room birth-cohort harvest','portal_room_eaten','portal_room_births'),('Portal-required birth-cohort harvest','portal_required_eaten','portal_required_births')]:
        add(name,w,'%', [f'ranges.{w}.{n}.relation',f'ranges.{w}.{d}'],lambda r,w=w,n=n,d=d:(100*r['ranges'][w][n][r['relation']],r['ranges'][w][d]),'eventually eats pearls born in this window'+(' behind portals' if n.startswith('portal') else ''),'explained' if n.startswith('portal') else 'open')
    add('Birth-cohort wait until eaten',w,'rounds/eaten',[f'ranges.{w}.cohort_wait.sum',f'ranges.{w}.cohort_wait.n'],lambda r,w=w:(r['ranges'][w]['cohort_wait']['sum'],r['ranges'][w]['cohort_wait']['n']),'waits longer between a pearl birth and eating it (eaten birth cohorts only)')
    add('Dead-dropped share of eaten pearls',w,'%', ['recount.drop_eaten',f'ranges.{w}.pearls_eaten'],lambda r,w=w:(100*EXTRA[str(r['game'])][r['relation']][w].get('drop_eaten',0),r['ranges'][w]['pearls_eaten']),'eats a larger share of its pearls from dead dragons')
    def death(r):return r['queen']['death']
    def risk(r,lo=lo,hi=hi):
        d=death(r)
        return (d is None or d['round']>=lo) and (r['last_round']>=hi or d is not None and lo<=d['round']<=hi)
    add('Queen dies in window',w,'%', ['queen.death.round','last_round'],lambda r,lo=lo,hi=hi,risk=risk:(100*int(death(r) is not None and lo<=death(r)['round']<=hi),1) if risk(r) else (0,0),'loses its queen during the window (queens alive at its start; complete follow-up or death)')
    for cause in CAUSES:
        add('Queen death: '+cause,w,'%', ['queen.death.cause','queen.death.round','last_round'],lambda r,lo=lo,hi=hi,cause=cause,risk=risk:(100*int(death(r) is not None and lo<=death(r)['round']<=hi and death(r)['cause']==cause),1) if risk(r) else (0,0),'loses its queen as '+cause, 'explained' if cause.startswith('head-on') else 'open')
    add('Queen death round',w,'rounds/death',['queen.death.round'],lambda r,lo=lo,hi=hi:(death(r)['round'],1) if death(r) is not None and lo<=death(r)['round']<=hi else (0,0),'loses its queen later among deaths observed in the window')
    add('First contact round',w,'rounds/contact',['first_enemy_head_in_view'],lambda r,lo=lo,hi=hi:(r['first_enemy_head_in_view'],1) if r['first_enemy_head_in_view'] is not None and lo<=r['first_enemy_head_in_view']<=hi else (0,0),'first sees an enemy head later among first contacts in the window')
    add('First contact in window',w,'%', ['first_enemy_head_in_view','first_contact_observed_through'],lambda r,lo=lo,hi=hi:(100*int(r['first_enemy_head_in_view'] is not None and lo<=r['first_enemy_head_in_view']<=hi),1) if r['first_contact_observed_through']>=hi or r['first_enemy_head_in_view'] is not None and r['first_enemy_head_in_view']<=hi else (0,0),'first sees an enemy head in this window')
for endpoint in (50,100):
    add('Heads in enemy half',f'r{endpoint}','%', [f'heads_enemy_half.{endpoint}.n',f'heads_enemy_half.{endpoint}.d'],lambda r,e=str(endpoint):(100*r['heads_enemy_half'][e]['n'],r['heads_enemy_half'][e]['d']) if r['heads_enemy_half'][e] else (0,0),'places a head on the half closer to enemy starting heads')
for kind in ('room','required'):
    add('Portal-'+kind+' whole-game harvest','game','%', [f'portal_births_game.{kind}_eaten.relation', 'portal_births_game.'+('rooms' if kind=='room' else 'required')],lambda r,kind=kind:(100*r['portal_births_game'][kind+'_eaten'][r['relation']],r['portal_births_game']['rooms' if kind=='room' else 'required']),'eats pearls born behind portals','explained')
add('Portal steps','game','/1k turns',['portal_steps_game','recount.game.turns'],lambda r:(1000*r['portal_steps_game'],EXTRA[str(r['game'])][r['relation']]['game']['turns']),'takes portal steps')
add('Dead-dropped share of eaten pearls','game','%',['recount.game.drop_eaten','game_counts.pearls_eaten'],lambda r:(100*EXTRA[str(r['game'])][r['relation']]['game'].get('drop_eaten',0),r['game_counts']['pearls_eaten']),'eats a larger share of its pearls from dead dragons')
add('Split frequency','game','/1k turns',['game_counts.splits','recount.game.turns'],lambda r:(1000*r['game_counts']['splits'],EXTRA[str(r['game'])][r['relation']]['game']['turns']),'splits on its turn')
add('Splits per eaten pearl','game','/pearl',['game_counts.splits','game_counts.pearls_eaten'],lambda r:(r['game_counts']['splits'],r['game_counts']['pearls_eaten']),'splits per pearl eaten')
add('All deaths','game','/1k turns',['game_counts.deaths','recount.game.turns'],lambda r:(1000*r['game_counts']['deaths'],EXTRA[str(r['game'])][r['relation']]['game']['turns']),'dies')
add('First contact round','game','rounds/contact',['first_enemy_head_in_view'],lambda r:(r['first_enemy_head_in_view'],1) if r['first_enemy_head_in_view'] is not None else (0,0),'first sees an enemy head later among observed first contacts')
add('First contact observed','game','%',['first_enemy_head_in_view'],lambda r:(100*int(r['first_enemy_head_in_view'] is not None),1),'sees an enemy head before the game ends')
add('Queen death round','game','rounds/death',['queen.death.round'],lambda r:(r['queen']['death']['round'],1) if r['queen']['death'] else (0,0),'loses its queen later among observed deaths')
add('Queen dies before game end','game','%',['queen.death'],lambda r:(100*int(r['queen']['death'] is not None),1),'loses its queen before the game ends')
add('Queen final length','game','length/game',['final_reconstructed.queen_length'],lambda r:(r['final_reconstructed']['queen_length'],1),'queen final length',context=True)
for w in WINDOWS:
    add('Dead-drop births within six steps',w,'%', [f'ranges.{w}.near6_births',f'ranges.{w}.natural_near6',f'ranges.{w}.births',f'ranges.{w}.natural_births'],lambda r,w=w:(100*(r['ranges'][w]['near6_births']-r['ranges'][w]['natural_near6']),r['ranges'][w]['births']-r['ranges'][w]['natural_births']),'has a head within six steps of dead-dropped pearl births')
    add('Dead-drop birth-cohort harvest',w,'%', [f'ranges.{w}.cohort_eaten.relation',f'ranges.{w}.natural_eaten.relation',f'ranges.{w}.births',f'ranges.{w}.natural_births'],lambda r,w=w:(100*(r['ranges'][w]['cohort_eaten'][r['relation']]-r['ranges'][w]['natural_eaten'][r['relation']]),r['ranges'][w]['births']-r['ranges'][w]['natural_births']),'eventually eats pearls dropped by dead dragons in this birth window')
for endpoint in (50,100,200,300):
    add('Queen length',f'r{endpoint}','length/game',[f'queen.length.{endpoint}'],lambda r,e=str(endpoint):(r['queen']['length'][e],1) if r['queen']['length'][e] is not None else (0,0),'queen length',context=True)
for w in WINDOWS:
    add('Queen length immediately before death',w,'length/death',['queen.death.length','queen.death.round'],lambda r,w=w:(r['queen']['death']['length'],1) if r['queen']['death'] and WINDOWS[w][0]<=r['queen']['death']['round']<=WINDOWS[w][1] else (0,0),'queen length before death',context=True)
    for key in ('head_on_length_lost','head_on_other_length_lost','head_on_net_length_lost'):
        add(key,w,'length/meeting',[f'ranges.{w}.{key}',f'ranges.{w}.cross_head_on_trades'],lambda r,w=w,key=key:(r['ranges'][w][key],r['ranges'][w]['cross_head_on_trades']),'head-on lengths',context=True)

def pool(rs,fn):
    pairs=[fn(r) for r in rs]; pairs=[(n,d) for n,d in pairs if d>0]
    n=sum(a for a,b in pairs);d=sum(b for a,b in pairs)
    return dict(value=n/d if d else None,numerator_scaled=n,denominator=d,valid_games=len(pairs))
def band(r):
    v=r['opponent_rating'];return '<1900' if v<1900 else '2100+' if v>=2100 else '1900-2099'
def pair(rs,fn):return {s:pool([r for r in rs if r['relation']==s],fn) for s in ('us','them')}
def sign(a,b):return None if a is None or b is None else (b>a)-(b<a)
RESULTS=[]
for m in METRICS:
    fn=m['fn']; res={k:v for k,v in m.items() if k!='fn'}
    res['pooled']=pair(ROWS,fn)
    res['rating_bands']={b:pair([r for r in ROWS if band(r)==b],fn) for b in ('<1900','1900-2099','2100+')}
    res['layouts']={l:pair([r for r in ROWS if r['layout_key']==l],fn) for l in LAYOUTS}
    a,b=[res['pooled'][s]['value'] for s in ('us','them')];sgn=sign(a,b)
    signs=[sign(v['us']['value'],v['them']['value']) for v in res['layouts'].values()]
    res['layouts_theirs_higher']=signs.count(1);res['layouts_theirs_lower']=signs.count(-1);res['layouts_tied']=signs.count(0);res['layouts_missing']=signs.count(None)
    res['consistent']=bool(sgn and signs.count(sgn)>=15 and all(sign(v['us']['value'],v['them']['value'])==sgn for v in res['rating_bands'].values()))
    res['relative_gap']=abs(a-b)/max(abs(a),abs(b)) if a is not None and b is not None and max(abs(a),abs(b)) else 0
    eligible=[]
    for r in US:
        n,d=fn(r)
        if d>0 and r['our_result'] in ('win','loss'):eligible.append((r,n/d))
    means={l:sum(v for r,v in eligible if r['layout_key']==l)/sum(r['layout_key']==l for r,v in eligible) for l in LAYOUTS if any(r['layout_key']==l for r,v in eligible)}
    res['won_lost_layout_demeaned']={z:dict(mean=sum(v-means[r['layout_key']] for r,v in eligible if r['our_result']==z)/sum(r['our_result']==z for r,v in eligible) if any(r['our_result']==z for r,v in eligible) else None,valid_games=sum(r['our_result']==z for r,v in eligible)) for z in ('win','loss')}
    RESULTS.append(res)
ranked=sorted([r for r in RESULTS if not r['context']],key=lambda r:(not r['consistent'],-r['relative_gap'],r['name'],r['window']))
for i,r in enumerate(ranked,1):r['rank']=i

def fmt(x):return 'NA' if x is None else f'{x:.3f}'
def both(p):return '/'.join(fmt(p[s]['value']) for s in ('us','them'))
lines=['# Behaviour fingerprint','',f'500 games; 19 layouts; 1000 side rows. Rating bands: <1900 (215), 1900–2099 (215), 2100+ (70).',
'Rates pool numerators/denominators; percentages use 0–100; W/L percentage residuals are points. Ties/missing layouts do not count as higher.',
'W/L = mean game rate minus its layout mean, then mean within wins/losses; draws excluded; negative values are residuals.',
'Order: ≥15/19 layouts agree with pooled sign and all three bands, then others; each group by |ours−theirs|/max(|ours|,|theirs|).',
f"The first {sum(r['consistent'] for r in ranked)} table rows meet the consistency threshold; the remaining rows do not.",
'Windows include endpoints; counts use observed turns only. Seen is cumulative at r100/r300; early endpoints are missing.',
'Blind keep: successful blind turns with a preceding successful direction; re-tread: successful blind turns. Partial 20-round blocks excluded.',
'Harvest/wait use birth-window cohorts eaten by game end, not eating-window counts; wait excludes uneaten pearls.',
'Queen incidence: alive at window start and observed through endpoint or death; death/contact rounds are conditional event means.',
'First-contact incidence excludes still-uncontacted games ending before endpoint. Queen lengths and head-on lengths are JSON context.',
'Recount: all 500 replays, only pearl origin at eating time (rows lack it) and whole-game turns (portal denominator absent); counts matched rows.',
'Explained labels apply to traced head-on mover/hit and portal-cohort harvest; mixed-window splitting/harvest stay open (r151 leader regime not isolated).','',
'| Rate (unit) | Window | Ours | Theirs | Higher /19 | 2100+ O/T | <1900 O/T | W/L residual | Status |',
'|---|---|---:|---:|---:|---|---|---|---|']
for r in ranked[:30]:
    wl='/'.join(fmt(r['won_lost_layout_demeaned'][s]['mean']) for s in ('win','loss'))
    lines.append(f"| {r['name']} ({r['unit']}) | {r['window']} | {fmt(r['pooled']['us']['value'])} | {fmt(r['pooled']['them']['value'])} | {r['layouts_theirs_higher']} | {both(r['rating_bands']['2100+'])} | {both(r['rating_bands']['<1900'])} | {wl} | {r['status']} |")
lines+=['','## Open gaps, largest first','']
# List all top-30 open lines, ordered by the same relative gap used in the table.
for r in sorted([r for r in ranked[:30] if r['status']=='open'],key=lambda r:-r['relative_gap']):
    direction='more often' if r['pooled']['them']['value']>r['pooled']['us']['value'] else 'less often'
    if r['unit'].startswith('rounds'):direction='later' if r['pooled']['them']['value']>r['pooled']['us']['value'] else 'earlier'
    phrase=r['description']
    if r['unit']=='tiles/block': phrase='visits tiles in a complete 20-round dragon block'+(' during blind turns' if r['name'].startswith('Blind') else '')
    if r['name'].startswith('Death: '):
        cause=r['name'].split(': ',1)[1]
        phrases={'no action':'dies after failing to provide a move or split','illegal split':'dies after an illegal split','timeout':'dies after an action timeout','unpaid sprint':'dies after a sprint it cannot pay for','wall':'dies by hitting a wall','own body':'dies by hitting its own body','another body':"dies by hitting another dragon's body"}
        phrase=phrases.get(cause,phrase)
    if r['name'].startswith('Queen death: '):
        cause=r['name'].split(': ',1)[1]
        phrases={'no action':'dies after failing to provide a move or split','illegal split':'dies after an illegal split','wall':'dies by hitting a wall','own body':'dies by hitting its own body','another body':"dies by hitting another dragon's body"}
        subject='Their queen';phrase=phrases.get(cause,phrase)
    else: subject='A dragon of theirs'
    if r['unit']=='tiles/block':
        direction='with more distinct tiles' if r['pooled']['them']['value']>r['pooled']['us']['value'] else 'with fewer distinct tiles'
    lines.append(f"- {r['window']}: {subject} {phrase} {direction} than ours; fields: `{'`, `'.join(r['fields'])}`.")
assert len(lines)<=80,len(lines)
meta={'created_at':datetime.now().astimezone().isoformat(timespec='seconds'),'source_sha256':source_hash,'games':500,'layouts':LAYOUTS,'rating_band_games':dict(Counter(band(r) for r in US)),'recount':'500 replays: drop-origin eat counts for each window and game, whole-game turns; eating/turn totals checked against rows. No other replay measures recounted.','pooled_definition':'sum of scaled numerator / sum denominator over valid games; field numerator_scaled contains scaling already','relative_gap_definition':'abs(ours-theirs)/max(abs(ours),abs(theirs)); zero if both zero or missing','won_lost_definition':'unweighted per-game rate, subtract layout mean over valid win/loss games; mean residual within result; draws excluded','ranking':'consistent sign >=15/19 layouts and each of 3 bands, then remaining; relative gap descending within tiers','omitted_nonbehaviour_fields':['end_state alive/total/longest','game_counts pearls_eaten/deaths/splits as raw outcomes','births and natural_births as raw environment counts','cohort_not_eaten as global uneaten environmental count','portal room/required cells and components as layout geometry','observed_rounds and visit active_rounds as observation exposure','head_on length fields retained only as context'],'rates':RESULTS,'top30':[{'name':r['name'],'window':r['window']} for r in ranked[:30]]}
(OUT/'fingerprint.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(OUT/'fingerprint.md').write_text('\n'.join(lines)+'\n')
print('Wrote',len(RESULTS),'rates/context entries;',len(lines),'markdown lines;',sum(r['consistent'] for r in ranked),'consistent rates',flush=True)
