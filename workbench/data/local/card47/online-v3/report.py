import analyze as a
import json
from collections import Counter
from statistics import mean

def supplement(r):
    root=a.c.replay.load(str(a.ROOT/r['replay'])).root()
    board=a.c.board_for(root.text(0));W,H=board.W,board.H
    _,_,bodies,teams,_=a.c.read_map(root.text(0))
    key=a.c.make_key(W,H,a.c.team_tag(r['side']));streams={};opened={};heard=set();first=0
    rnd=0;split_round={};counted_splits=set();tiles_on_split=0
    _,_,_,teams,_=a.c.read_map(root.text(0))
    for ev in root.pointer(3):
        kind=a.c.replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
        if kind=='roundStart':rnd=p.i32(0)
        elif kind=='dragonSplit':
            teams[p.i32(0)]=teams[p.i32(4)]='AB'[p.u16(8)]
            split_round[p.i32(0)]=rnd
        elif kind=='sonarPing' and teams.get(p.i32(0))==r['side']:
            wire=p.u64(16)
            if wire not in opened:
                plain=a.c.unseal(key,wire,streams)
                opened[wire]=a.c.parse(plain,W,H) if plain is not None else None
            msg=opened[wire]
            if msg is None or msg['kind']!='split':continue
            sk=(p.i32(0),rnd)
            if msg['spots'] and split_round.get(p.i32(0))==rnd and sk not in counted_splits:
                counted_splits.add(sk);tiles_on_split+=sum(refill for _,refill in msg['spots'])
            if msg['end'] is None:continue
            end=board.told(msg['end'])
            if end is None or not p.u16(6):continue
            hit=p.i32(12)
            if hit==p.i32(0) or teams.get(hit)!=r['side']:continue
            k=(hit,end['id'])
            if k not in heard:heard.add(k);first+=1
    r['first_dead_end_receptions']=first
    r['refill_tiles_on_split']=tiles_on_split
    for rnd in r['alive']:
        if r['alive'][rnd] is None:
            assert r['last_round']<int(rnd)
            r['alive'][rnd]=r['final']['alive']
    return r

def report(rows):
    groups={s:[r for r in rows if r['set']==s] for s in a.FOLDERS}
    assert all(len(rs)==15 for rs in groups.values())
    assert len({r['map_id'] for r in rows})==15
    def total(rs,*ks):
        return sum(value(r,ks) for r in rs)
    def value(r,ks):
        for k in ks:r=r[k]
        return r
    def sums(*ks):return [total(rs,*ks) for rs in groups.values()]
    def avg(*ks):return [total(rs,*ks)/15 for rs in groups.values()]
    def rate(*ks):return [1000*total(rs,*ks)/total(rs,'turns') for rs in groups.values()]
    def cells(nums):return ' | '.join(f'{x:.2f}' if isinstance(x,float) else str(x) for x in nums)
    lines=['# Card 47 third build: 45 online games, 7 Oct 2026',
        'Each set has 15 maps against Big Bobs Bots (946); our side is read from team 1119 in each game. These are unpaired games: build effects and opponent variation/luck are mixed.',
        'Definitions reuse card_47_check.py: room ≤31, no portal, one gate; wasted = <2 growth-counted pearls then split/died inside; charged uses its 25-round pearl-count proxy, not bot-state inspection; enemy near = wrapped 3-tile square. Ray hits proxy hearing; receptions count first dragon/end pairs; babies born on a named tile are excluded. Alive checkpoints after an early finish carry the final state; safe move means a non-kelp step to an unoccupied tile, including portals; no action includes explicit suicide.',
        '## A. Job (totals unless labelled)', '| Measure | new | main48 | main47 |','|---|---:|---:|---:|']
    def add(name,nums):lines.append('| '+name+' | '+cells(nums)+' |')
    add('Dragon turns',sums('turns'))
    add('Dead-end stays / with alert (incl. split ping)',[f"{total(rs,'stays','stays')} / {total(rs,'stays','with_alert_or_split_ping')}" for rs in groups.values()])
    add('Inside turns / alerted; non-split alerts / own-end split pings',[f"{total(rs,'mechanism','inside_turns')} / {total(rs,'mechanism','inside_turns_alert')}; {total(rs,'mechanism','alert_turns')} / {total(rs,'mechanism','split_turns_own_end')}" for rs in groups.values()])
    add('End packets / true; end rays / teammate hits',[f"{total(rs,'mechanism','msgs_with_end')} / {total(rs,'mechanism','msgs_end_true')}; {total(rs,'mechanism','end_rays')} / {total(rs,'mechanism','end_rays_hit_teammate')}" for rs in groups.values()])
    add('Passed on: relay turns / relay rays heard',[f"{total(rs,'mechanism','relay_turns')} / {total(rs,'mechanism','relay_rays_hit_teammate')}" for rs in groups.values()])
    add('First dead-end receptions (dragon/end pairs)',sums('first_dead_end_receptions'))
    for cut in ('told','untold','told_charged'):
        add(cut.replace('_','-')+' arrivals / entered / share',[f"{total(rs,'arrivals',cut,'arrivals')} / {total(rs,'arrivals',cut,'walked_in')} / {100*total(rs,'arrivals',cut,'walked_in')/max(1,total(rs,'arrivals',cut,'arrivals')):.1f}%" if total(rs,'arrivals',cut,'arrivals') else '0 / 0 / —' for rs in groups.values()])
    add('Charged entries with enemy head within 3',sums('arrivals','told_charged','walked_in_with_enemy_near'))
    add('Wasted stays / per 1,000 dragon turns',[f"{total(rs,'stays','wasted')} / {1000*total(rs,'stays','wasted')/total(rs,'turns'):.3f}" for rs in groups.values()])
    add('Pearls eaten on stays / length lost at deaths inside',[f"{total(rs,'stays','pearls_eaten')} / {total(rs,'stays','length_lost_inside')}" for rs in groups.values()])
    add('Trapped mother splits / those naming refill tiles',[f"{total(rs,'splits','trapped')} / {total(rs,'splits','trapped_with_spots')}" for rs in groups.values()])
    add('Refill tiles named at split / split+resends / told to babies',[f"{total(rs,'refill_tiles_on_split')} / {total(rs,'mechanism','spots_sent')} / {total(rs,'mechanism','spots_told_refill')}" for rs in groups.values()])
    add('Babies told / reached ≤30 rounds / pearls there',[f"{total(rs,'babies','told','babies')} / {total(rs,'babies','told','reached')} / {total(rs,'refill_pearls_eaten')}" for rs in groups.values()])
    add('Refill message turns from trapped mothers / all; unflagged tiles',[f"{total(rs,'mechanism','spot_turns_trapped')} / {total(rs,'mechanism','spot_turns')}; {total(rs,'mechanism','spots_sent_not_refill')}" for rs in groups.values()])
    lines+=['## B. Downsides (per-game means; death cells = mean / pooled per 1,000 turns)', '| Measure | new | main48 | main47 |','|---|---:|---:|---:|']
    add('Results W/D/L (counts)',[f"{sum(r['result']=='W' for r in rs)}/{sum(r['result']=='D' for r in rs)}/{sum(r['result']=='L' for r in rs)}" for rs in groups.values()])
    add('Endings elimination / round limit (counts)',[f"{sum(r['end_reason']=='elimination' for r in rs)} / {sum(r['end_reason']=='round limit' for r in rs)}" for rs in groups.values()])
    add('Pearls by r100 / r300',[f"{total(rs,'pearls','100')/15:.2f} / {total(rs,'pearls','300')/15:.2f}" for rs in groups.values()])
    add('Alive at r100 / r200 / r300',[f"{total(rs,'alive','100')/15:.2f} / {total(rs,'alive','200')/15:.2f} / {total(rs,'alive','300')/15:.2f}" for rs in groups.values()])
    for k in a.CAUSES[:6]:
        add('Death: '+k,[f"{total(rs,'deaths',k)/15:.2f} / {1000*total(rs,'deaths',k)/total(rs,'turns'):.3f}" for rs in groups.values()])
    add('Deaths: timeout; unpaid sprint; illegal split',[ '; '.join(f"{total(rs,'deaths',k)/15:.2f} / {1000*total(rs,'deaths',k)/total(rs,'turns'):.3f}" for k in a.CAUSES[6:]) for rs in groups.values()])
    add('Timeout turns / no-action turns / either with safe move',[f"{total(rs,'timeout_turns')/15:.2f} / {total(rs,'no_action_turns')/15:.2f} / {total(rs,'failed_turns_move_exists')/15:.2f}" for rs in groups.values()])
    add('Sonar rays: leader / new kind',[f"{total(rs,'sonar','leader')/15:.2f} / {total(rs,'sonar','new_rays')/15:.2f}" for rs in groups.values()])
    add('Other rays: mouth / queen / other / unreadable',[f"{total(rs,'sonar','mouth')/15:.2f} / {total(rs,'sonar','queen')/15:.2f} / {total(rs,'sonar','other')/15:.2f} / {total(rs,'sonar','unreadable')/15:.2f}" for rs in groups.values()])
    add('Queen alive at end (mean indicator) / longest at end',[f"{total(rs,'final','queen_alive')/15:.3f} / {total(rs,'final','longest')/15:.2f}" for rs in groups.values()])
    lines+=['## C. Per map (new / main48)', '| Map | Result | Pearls r100 | Wasted stays | Deaths in dead ends |','|---|---|---:|---:|---:|']
    old={r['map_id']:r for r in groups['main48']}
    for r in groups['new']:
        b=old[r['map_id']]
        lines.append(f"| {r['map']} | {r['result']} / {b['result']} | {r['pearls']['100']} / {b['pearls']['100']} | {r['stays']['wasted']} / {b['stays']['wasted']} | {r['stays']['died_inside']} / {b['stays']['died_inside']} |")
    lines+=['## What the counts say']
    sentences=[
        'Alerts appear on 529 of 557 stays, all 3,901 dead-end packets describe real dead ends, 3,277 rays hit teammates, and 1,113 relay turns show passing on.',
        'Charged dragons enter on 57 of 495 arrivals (11.5%), against 284 of 2,944 untold arrivals (9.6%), so lower entry by charged dragons does not show, while wasted stays per 1,000 turns are 0.623 versus 0.755 and 0.828 in the two earlier sets.',
        'All 144 refill-message turns come from trapped splits, 102 told babies produce four reaches and seven pearls on named tiles, and one reach starts 13 tiles away, but the replay cannot establish the baby’s motive or whether nothing else was in reach.',
        'Using |new − main48| > |main48 − main47| as the requested luck scale, the per-game measures beyond it are pearls by r300 (down 63.87 versus spread 9.87), alive at r200 (down 1.67 versus 1.53), wall deaths (down 8.00 versus 1.80), own-body deaths (down 7.67 versus 2.53), mover head-on deaths (down 0.53 versus 0.27), queen rays (down 1,388.67 versus 720.80), new-kind rays (up 1,022.13 versus zero), and elimination endings (five versus four and four, with round-limit endings falling from eleven to ten).',
        'For pooled deaths per 1,000 turns, only own-body deaths (down 0.603 versus spread 0.362) and no-action deaths (down 0.407 versus 0.205) move beyond that scale.',
        'Results, pearls by r100, alive at r100 and r300, queen survival, final longest, leader and mouth rays, no-action and safe-move failure turns, and all other listed death measures stay within the reference spread; unpaired opponent behavior prevents attributing these differences to the build.'
    ]
    formatted=[]
    for line in lines:
        formatted.append(line)
        if line.startswith('#'):formatted.append('')
    formatted+=sentences
    assert len(formatted)<=70,len(formatted)
    (a.OUT/'table.md').write_text('\n'.join(formatted)+'\n')
    print('table lines',len(formatted))
    measures={}
    for name,ks in [('pearls r100',('pearls','100')),('pearls r300',('pearls','300')),*[(f'alive r{r}',('alive',str(r))) for r in (100,200,300)],*[(f'death {k}',('deaths',k)) for k in a.CAUSES],('leader rays',('sonar','leader')),('new rays',('sonar','new_rays')),('queen alive',('final','queen_alive')),('longest',('final','longest')),('timeouts',('timeout_turns',)),('no action',('no_action_turns',)),('failed with move',('failed_turns_move_exists',))]:
        n,b,o=avg(*ks);measures[name]=dict(new=n,main48=b,main47=o,delta=n-b,spread=abs(b-o),exceeds=abs(n-b)>abs(b-o)+1e-9)
    for k in a.CAUSES:
        n,b,o=rate('deaths',k);measures[f'death {k} /1000']=dict(new=n,main48=b,main47=o,delta=n-b,spread=abs(b-o),exceeds=abs(n-b)>abs(b-o)+1e-9)
    for k in ('mouth','queen','other','unreadable'):
        n,b,o=avg('sonar',k);measures[f'{k} rays']=dict(new=n,main48=b,main47=o,delta=n-b,spread=abs(b-o),exceeds=abs(n-b)>abs(b-o)+1e-9)
    for name,key,target in [('wins','result','W'),('draws','result','D'),('losses','result','L'),('elimination','end_reason','elimination'),('round limit','end_reason','round limit')]:
        n,b,o=[sum(r[key]==target for r in rs)/15 for rs in groups.values()];measures[name]=dict(new=n,main48=b,main47=o,delta=n-b,spread=abs(b-o),exceeds=abs(n-b)>abs(b-o)+1e-9)
    (a.OUT/'spread.json').write_text(json.dumps(measures,indent=2)+'\n')
    print(json.dumps(measures,indent=2))

if __name__=='__main__':
    rows=[supplement(json.loads(line)) for line in (a.OUT/'rows.jsonl').read_text().splitlines()]
    (a.OUT/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    report(rows)
