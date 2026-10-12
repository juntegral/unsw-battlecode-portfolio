#!/usr/bin/env python3
"""Read-only card 38 counts; run from repository root. Writes only beside this file."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import statistics as stats
from pathlib import Path
from collections import Counter, deque
from datetime import datetime

OUT = Path(__file__).resolve().parent
H = OUT.parent
spec = importlib.util.spec_from_file_location('card38', H/'harness/work/card_38_check.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
R = C.replay
MARKS = (100,200,250,300,350,400,450,500)
CLASSES = ('forced','only risky','had a safe move')


def one(path, dataset, meta):
    arm, stem = path.stem.split('_',1)
    mapname, seed, side = stem.rsplit('_',2)
    ours = ('A','B')[int(side)]
    root = R.load(str(path)).root()
    text = root.text(0)
    W, B, step, _ = C.load_map(text)
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0]=='DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i] = ('A','B')[int(q[1])]
    queen = next(i for i in (0,1) if teams[i]==ours)
    enemy = next(i for i in (0,1) if teams[i]!=ours)
    spawn = bodies[queen][0]
    far = lambda a,b: C.gap(a[0],b[0],W)+C.gap(a[1],b[1],B)
    trail, singles, laps = [spawn], [], []
    counts, snapshots, lengths, deaths = Counter(), {}, {}, []
    pending, action_state, mover, rnd = None, None, None, 0

    def snapshot():
        return {i:tuple(b) for i,b in bodies.items() if b}

    def blocked(state):
        own = set(state[queen])
        own.discard(state[queen][-1])
        others = {p for i,b in state.items() if i!=queen for p in b}
        return own, others

    def room(state):
        if queen not in state:
            return None
        own,others = blocked(state)
        occupied = own|others
        head = state[queen][0]
        seen, queue = {head}, deque([head])
        while queue and len(seen)<30:
            for d in C.DIRS:
                hop = step(queue[0],d)
                if hop and hop[0] not in occupied and hop[0] not in seen:
                    seen.add(hop[0])
                    queue.append(hop[0])
                    if len(seen)==30:
                        break
            queue.popleft()
        return len(seen)

    def pressure(state):
        if queen not in state:
            return None
        return sum(teams[i]!=ours and far(b[0],state[queen][0])<=6 for i,b in state.items())

    def close():
        nonlocal pending
        p,pending = pending,None
        if p is None:
            return
        singles.append(p['kind']=='move' and not p['dead'] and p['n']==1 and p['seen']==1)
        trail.append(p['end'])
        lap = (len(singles)>=4 and all(singles[-4:]) and trail[-5]==trail[-1]
               and C.square_of(trail[-4:],W,B) is not None)
        laps.append((p['round'],lap))
        period = 'early' if p['round']<300 else 'late'
        counts['decisions_'+period] += 1
        counts['laps_'+period] += lap

    for ev in root.pointer(3):
        kind = R.EVENT_NAMES[ev.u16(0)]
        pl = ev.pointer(0)
        if kind=='roundStart':
            close()
            rnd = pl.i32(0)
            mover,action_state = None,None
            state = snapshot()
            snapshots[rnd] = dict(room=room(state),pressure=pressure(state))
            if rnd in MARKS:
                lengths[str(rnd)] = [len(bodies.get(i,())) for i in (queen,enemy)]
        elif kind=='dragonAction':
            close()
            mover = pl.i32(0)
            a = pl.pointer(0)
            action_state = snapshot() if queen in bodies else None
            if mover==queen and a is not None and bodies.get(queen):
                what = a.u16(0)
                try:
                    n = max(1,len(a.pointer(0))) if what==0 else 0
                except Exception:
                    n = 1
                pending = dict(round=rnd,kind='move' if what==0 else 'split' if what==1 else 'other',
                               n=n,seen=0,end=bodies[queen][0],dead=False)
                snapshots[rnd] = dict(room=room(action_state),pressure=pressure(action_state))
        elif kind=='dragonUpdate':
            i = pl.i32(0)
            head,tail = R.point(pl.pointer(0)),R.point(pl.pointer(1))
            b = bodies.setdefault(i,deque())
            before = len(b)
            hopped = bool(b) and b[0]!=head
            if not b or b[0]!=head:
                b.appendleft(head)
                if pending and i==queen:
                    pending['seen'] += 1
                    pending['end'] = head
            while len(b)>1 and b[-1]!=tail:
                b.pop()
            if hopped and len(b)>before and i in (queen,enemy):
                counts[('ours' if i==queen else 'theirs')+'_pearls_'+('early' if rnd<300 else 'late')] += 1
        elif kind=='dragonSplit':
            pa,ch = pl.i32(0),pl.i32(4)
            bodies[pa] = deque(R.point(x) for x in pl.pointer(0))
            bodies[ch] = deque(R.point(x) for x in pl.pointer(1))
            teams[pa] = teams[ch] = ('A','B')[pl.u16(8)]
            if pa in (queen,enemy):
                counts[('ours' if pa==queen else 'theirs')+'_splits_'+('early' if rnd<300 else 'late')] += 1
        elif kind=='dragonDeath':
            i = pl.i32(0)
            if i==queen:
                state = action_state or snapshot()
                head = state[queen][0]
                own,others = blocked(state)
                foes = [dict(id=j,at=b[0],true=C.full_reach(len(b))) for j,b in state.items() if teams[j]!=ours]
                low = C.margins(step,foes,'true',others,own)
                legal,safe = [],[]
                for d in C.DIRS:
                    hop = step(head,d)
                    if hop and hop[0] not in own|others:
                        legal.append(d)
                        if low.get(hop[0],(1,))[0]>0:
                            safe.append(d)
                cause = C.CAUSE[pl.u16(4)] if pl.u16(4)<5 else 'other'
                deaths.append(dict(type='death',dataset=dataset,replay=str(path),arm=arm,map=mapname,
                    seed=int(seed),side=int(side),queen_id=queen,round=rnd,cause=cause,
                    length_just_before=len(bodies[queen]),decision_length=len(state[queen]),
                    spawn_distance=far(bodies[queen][0],spawn),decision_spawn_distance=far(head,spawn),
                    legal_moves=legal,safe_moves=safe,legal_count=len(legal),safe_count=len(safe),
                    classification=CLASSES[0] if not legal else CLASSES[1] if not safe else CLASSES[2],
                    room={str(offset):snapshots.get(rnd+offset,{}).get('room') for offset in (-10,-5)},
                    enemy_heads_within_6={'-5':snapshots.get(rnd-5,{}).get('pressure'),'0':pressure(snapshot())},
                    decision_actor=mover,decision_is_ours=mover==queen,
                    fatal_move_steps=pending['n'] if pending else None,
                    fatal_action=('multi-step' if pending['n']>1 else 'single-step')
                    if pending and pending['kind']=='move' else 'no move action',
                    lap_in_previous_4_rounds=any(rnd-4<=r<rnd and lap for r,lap in laps)))
                deaths[-1]['room']['0'] = room(snapshot())
                deaths[-1]['decision_room'] = room(state)
                if pending:
                    pending['dead'] = True
            bodies.pop(i,None)
    close()
    if rnd>=499:
        lengths['500'] = [len(bodies.get(i,())) for i in (queen,enemy)]
    return deaths,dict(type='game',dataset=dataset,replay=str(path),arm=arm,map=mapname,seed=int(seed),
                      side=int(side),end_round=rnd,lengths=lengths,counts=dict(counts),
                      final_lengths=[len(bodies.get(i,())) for i in (queen,enemy)],**meta)


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,r))+' |' for r in rows])


def report(deaths,games,selected):
    lines = []
    for dataset in ('hunter','normal'):
        for cause in ('wall','self'):
            ds = [d for d in deaths if d['dataset']==dataset and d['cause']==cause]
            f = sum(d['classification']=='forced' for d in ds)
            early = sum(d['round']<50 for d in ds)
            lines.append(f'{dataset.capitalize()} {cause}: {f}/{len(ds)} forced ({100*f/len(ds):.1f}%); {early}/{len(ds)} before r50 (both arms).')
    lines += ['TIMING_QUEEN','TIMING_TRAUMA','',
        f'Counted {len(games)} games and {len(deaths)} queen deaths; {datetime.now().astimezone().isoformat(timespec="seconds")}.',
        'Safety, room, pressure and distance use replay true state, including what she cannot see. Safety is at the start of the fatal action; for an enemy-caused death this is the enemy action start, not a new queen decision. Reach is full_reach(real length), through the check margins walker (walls/portals, other bodies block, her body is an endpoint); distance <= reach is risky. Her tail is excluded as in the check; other tails stay blocked.',
        'Room counts the starting head and caps at 30, with static bodies and her tail excluded. -5/-10 use that round’s queen action start, or roundStart if no queen action; room 0 and pressure 0 use the state immediately before the death event. Missing negative rounds are excluded from medians. Shrinking room does not by itself prove she walked into a pocket.',
        'r100–450 lengths are roundStart, as in the check; r500 is terminal after actions (these replays label their 500 rounds 0–499). Dead queens count as zero. Early = replay r0–299, late = replay r300–499. Pearls/splits concern original ids 0/1, not descendants. Lap uses the check definition (first three loop steps excluded).','']
    for dataset in ('hunter','normal'):
        for arm in ('base','candidate'):
            ds = [d for d in deaths if d['dataset']==dataset and d['arm']==arm]
            ng = sum(g['dataset']==dataset and g['arm']==arm for g in games)
            lines += [f'### {dataset}, {arm}: {ng} games, {len(ds)} deaths','']
            causes = {c:[d for d in ds if d['cause']==c] for c in C.CAUSE}
            lines += [table(['cause','deaths',*CLASSES],
                [[c,len(cs)]+[sum(d['classification']==k for d in cs) for k in CLASSES] for c,cs in causes.items()]),'']
            lines += [table(['cause','deaths','<50','50–99','100–199','200–299','300+'],
                [[c,len(cs)]+[sum(lo<=d['round']<hi for d in cs) for lo,hi in
                [(0,50),(50,100),(100,200),(200,300),(300,100000)]] for c,cs in causes.items()]),'']
            rows = []
            for c,cs in causes.items():
                cells = []
                for off in ('-10','-5','0'):
                    vals = [d['room'][off] for d in cs if d['room'][off] is not None]
                    cells.append(f'{stats.median(vals):g} (n={len(vals)})' if vals else '— (n=0)')
                rows.append([c,len(cs),*cells])
            lines += [table(['cause','deaths','room -10','room -5','room 0'],rows),'']
            lines += [table(['cause','deaths','multi-step','single-step','no move','lap in prior 4 rounds'],
                [[c,len(causes[c])]+[sum(d['fatal_action']==k for d in causes[c]) for k in
                ('multi-step','single-step','no move action')]+[sum(d['lap_in_previous_4_rounds'] for d in causes[c])]
                for c in ('wall','self')]),'']
    lines += ['### Examples (up to five each)','']
    for cause,cls in [('wall',CLASSES[2]),('self',CLASSES[2]),('wall',CLASSES[0])]:
        ex = [d for d in deaths if d['cause']==cause and d['classification']==cls][:5]
        lines += [f'{cause}, {cls}: '+'; '.join(f"{d['dataset']}/{Path(d['replay']).name} r{d['round']}" for d in ex),'']
    lines += ['### Part B: lengths and events','']
    agg = {}
    union = {(g['map'],g['seed'],g['side']) for g in selected if g.get('how')=='queen'}
    for group in ('queen endings','all trauma','paired union of queen endings'):
        for arm in ('base','candidate'):
            gs = [g for g in games if g['dataset']=='hunter' and g['arm']==arm and
                (g.get('how')=='queen' if group=='queen endings' else g['map']=='trauma' if group=='all trauma'
                 else (g['map'],g['seed'],g['side']) in union)]
            lines += [f'{group}, {arm}: {len(gs)} games. Means include dead queens as 0.','']
            rows,means = [],{}
            for mark in MARKS:
                vals = [g['lengths'][str(mark)] for g in gs if str(mark) in g['lengths']]
                mean = [stats.mean(v[i] for v in vals) if vals else None for i in (0,1)]
                means[mark] = mean
                rows.append([mark,len(vals)]+[f'{x:.2f}' if x is not None else '—' for x in mean]+
                            [sum(v[i]>0 for v in vals) for i in (0,1)])
            lines += [table(['round','games','our mean length','their mean length','ours alive','theirs alive'],rows),'']
            c = Counter()
            for g in gs:
                c.update(g['counts'])
            lines += [table(['period','games','our pearls','their pearls','our splits','their splits','our lap/decisions'],
                [[period,len(gs),c[f'ours_pearls_{p}'],c[f'theirs_pearls_{p}'],c[f'ours_splits_{p}'],c[f'theirs_splits_{p}'],
                  f"{c[f'laps_{p}']}/{c[f'decisions_{p}']} ({100*c[f'laps_{p}']/max(1,c[f'decisions_{p}']):.1f}%)"]
                 for period,p in [('r0–299','early'),('r300–500','late')]]),'']
            agg[group,arm] = (gs,means,c)
    lines += ['### Timing interpretation','']
    for group in ('queen endings','all trauma','paired union of queen endings'):
        bg,bm,bc = agg[group,'base']
        cg,cm,cc = agg[group,'candidate']
        first = next((m for m in MARKS if m<=300 and cm[m][0] is not None and bm[m][0] is not None and cm[m][0]<bm[m][0]),None)
        text = f'{group} ({len(bg)} off/{len(cg)} on games): '
        text += f'on is already shorter at r{first}. ' if first else 'on is not shorter at sampled rounds through r300. '
        for p in ('early','late'):
            text += f"{p}: our pearls {bc[f'ours_pearls_{p}']}→{cc[f'ours_pearls_{p}']}, splits {bc[f'ours_splits_{p}']}→{cc[f'ours_splits_{p}']}. "
        text += f"Final surviving queens {sum(g['final_lengths'][0]>0 for g in bg)}→{sum(g['final_lengths'][0]>0 for g in cg)}."
        alive100 = [sum(g['lengths'].get('100',[0])[0]>0 for g in gs) for gs in (bg,cg)]
        text += f' At r100, alive {alive100[0]}/{len(bg)} off and {alive100[1]}/{len(cg)} on.'
        if group in ('queen endings','all trauma'):
            text += ' The early deficit accompanies less eating, with fewer splits; all queens are alive at r100, so death does not explain that first deficit.'
        if group=='queen endings':
            text += ' Later, on has lost 2/6 queens by r350 versus 0/5 off, and also eats less after r300; both reduce its late mean.'
        if group=='all trauma':
            text += ' On loses no queen here; its r300-on pearls are nearly equal, and neither arm splits then, so late paid movement/damage or timing remains unallocated.'
        lines += [text,'']
        if group=='queen endings':
            lines[4] = text
        elif group=='all trauma':
            lines[5] = text
    lines += ['Queen-ending groups select different games in each arm; the paired union additionally compares the same map/seed/side games, including the other arm even if its ending differs.',
        'Could not measure: exact internal bot view/reasons, future survival after a safe alternative, dynamic multi-step escape, causal attribution of length loss to food/splits alone (paid steps and incoming damage also change length). Room is static. Fatal step count is requested steps, including unexecuted ones; free/paid allocation at the fatal step is not inferred. No new games were run.']
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n')


def main():
    meta = {}
    for p in sorted((H/'rows').glob('*.rows.jsonl')):
        for line in p.read_text().splitlines():
            r = json.loads(line)
            meta[f"{r['tag']}_{r['map']}_{r['seed']}_{r['side']}"] = {k:r[k] for k in ('how','win','us','them')}
    deaths,games = [],[]
    for dataset,directory,expected in [('hunter',H/'replays',136),
        ('normal',Path('~/meow-loop-out/card-38/attempt-1/replays'),32)]:
        paths = sorted(p for p in directory.glob('*.replay') if p.name.startswith(('base_','candidate_')))
        if len(paths)!=expected:
            sys.exit(f'STOP: {dataset}: expected {expected}, found {len(paths)} games')
        keys = {arm:{p.stem.split('_',1)[1] for p in paths if p.stem.startswith(arm+'_')}
                for arm in ('base','candidate')}
        if keys['base']!=keys['candidate'] or len(keys['base'])!=expected//2:
            sys.exit(f'STOP: {dataset}: arms are not paired')
        for n,p in enumerate(paths,1):
            d,g = one(p,dataset,meta.get(p.stem,{}) if dataset=='hunter' else {})
            deaths.extend(d)
            games.append(g)
            if n%8==0:
                print(f'{dataset}: {n}/{len(paths)}',flush=True)
        original_path = H/'check.json' if dataset=='hunter' else directory.parent/'check.json'
        if original_path.exists():
            original = json.loads(original_path.read_text())
            for arm in ('base','candidate'):
                actual = dict(Counter(d['cause'] for d in deaths if d['dataset']==dataset and d['arm']==arm))
                target = original[arm]['queen_deaths_by_cause']
                if actual!=target:
                    sys.exit(f'STOP: {arm} deaths {actual} != {target}')
                gs = [g for g in games if g['dataset']==dataset and g['arm']==arm]
                for own,key in [('laps_early','lap_steps_before_r300'),('laps_late','lap_steps_from_r300'),
                    ('decisions_early','queen_decisions_before_r300'),('ours_pearls_early','queen_pearls_eaten_before_r300'),
                    ('ours_splits_early','queen_splits_before_r300')]:
                    value = sum(g['counts'].get(own,0) for g in gs)
                    if value!=original[arm][key]:
                        sys.exit(f'STOP: {arm} {key}: {value} != {original[arm][key]}')
            print(f'{dataset}: death/lap/decision/pearl/split totals match check.json.',flush=True)
    union = {(g['map'],g['seed'],g['side']) for g in games if g['dataset']=='hunter' and g.get('how')=='queen'}
    selected = [g for g in games if g['dataset']=='hunter' and
                (g['map']=='trauma' or (g['map'],g['seed'],g['side']) in union)]
    for g in selected:
        g['part_b_groups'] = (['queen endings'] if g.get('how')=='queen' else []) + \
            (['all trauma'] if g['map']=='trauma' else []) + \
            (['paired union of queen endings'] if (g['map'],g['seed'],g['side']) in union else [])
    (OUT/'rows.json').write_text(json.dumps({'deaths':deaths,'games':selected},indent=2)+'\n')
    report(deaths,games,selected)
    print(f'Wrote {len(deaths)} deaths and {len(selected)} Part B games.',flush=True)


if __name__=='__main__':
    main()
