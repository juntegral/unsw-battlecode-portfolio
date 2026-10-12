import sys
sys.dont_write_bytecode = True
import importlib.util, json, types
from pathlib import Path
from collections import Counter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
CHECK = Path('~/meow-cards/card-47/work/card_47_check.py')
sys.path.insert(0, str(CHECK.parent.parent))
spec = importlib.util.spec_from_file_location('card47', CHECK)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
# Keep the strict pearl, collision, and final-result assertions in the shared reconstruction.
source = (ROOT / 'tools/ladder_replay.py').read_text()
source = source.replace('rnd=0;actor=None;', 'action_rows=[];rnd=0;actor=None;')
needle = "        elif k=='tileChange':"
insert = """            if side(actor)=='us':
                timeout=p.bit(32) or (used_up is not None and used_up.bit(64))
                no_action=a is None or a.u16(0)>=2
                exists=None
                if timeout or no_action:
                    head=bodies[actor][0]; occupied={xy for bb in bodies.values() for xy in bb}
                    exists=any(edges.get(edge_id(W,H,*head,d),(0,-1))[0]!=1 and destination(head,d) not in occupied for d in range(4))
                action_rows.append(dict(round=rnd,id=actor,timeout=bool(timeout),no_action=no_action,empty_destination_move_exists=exists))
"""
source = source.replace(needle, insert + needle)
source = source.replace('return dict(text=text,', 'return dict(action_rows=action_rows,text=text,')
lr = types.ModuleType('ladder_online')
lr.__file__ = str(ROOT / 'tools/ladder_replay.py')
exec(compile(source, lr.__file__, 'exec'), lr.__dict__)
CAUSES = ['wall','own body','another body','head-on mover','head-on hit','no action','timeout','unpaid sprint','illegal split']
FOLDERS = {'new':'um47d-bob1-new','main51':'sr51-bob1-new','main48':'qn48v1-bob1-new','main47':'qn48v1-bob1-old'}

def analyze(label, folder, p):
    j = json.loads(p.read_text())
    ours = 'A' if j['teamAId']==1119 else 'B'
    assert j['team'+ours+'Id']==1119 and j['team'+('B' if ours=='A' else 'A')+'Id']==946
    path = p.parent / ('M'+str(j['id'])+'.replay')
    mech = c.scan(str(path), ours)
    g = lr.scan(path,j,folder,set())
    assert g['winner'] is None or g['winner'].lower()==j['winner']
    counts = Counter()
    for d in g['deaths']:
        if d['side']!='us': continue
        reason=d['reason']
        cause=CAUSES[reason] if reason<3 else ('head-on mover' if d['id']==d['actor'] else 'head-on hit') if reason==3 else d['other']
        counts[cause]+=1
    assert set(counts)<=set(CAUSES),counts
    assert sum(counts.values())==mech['deaths']
    assert len(g['action_rows'])==mech['turns']
    children=mech['children']
    babies=[r for r in children if r['trapped'] and r['spots'] and r['gap0']!=0]
    death_inside=c.stay_counts(mech['stays'],mech['turns'])
    # Count actual pearl removals by each baby on any named tile during the watch window.
    root=c.replay.load(str(path)).root(); rnd=0; actor=None; baby_map={r['child']:r for r in babies}; refill_eats=0
    for ev in root.pointer(3):
        kind=c.replay.EVENT_NAMES[ev.u16(0)]; pl=ev.pointer(0)
        if kind=='roundStart':rnd=pl.i32(0)
        elif kind=='turnStart':actor=pl.i32(0)
        elif kind=='tileChange' and pl.u32(0)==0:
            b=baby_map.get(actor)
            if b and b['told'] and rnd-b['round']<=c.WATCH and c.replay.point(pl.pointer(0)) in b['spots']:refill_eats+=1
    row=dict(set=label,game_id=j['id'],map_id=j['mapId'],map=j['mapName'],side=ours,seed=j['seed'],replay=str(path.relative_to(ROOT)),
        result='D' if g['winner'] is None else 'W' if g['winner']==ours else 'L',end_reason=['elimination','round limit'][g['end_reason']],last_round=g['last_round'],
        turns=mech['turns'],pearls={str(r):sum(rr<=r and s=='us' for rr,s in g['eaten_rounds']) for r in (100,300)},
        alive={str(r):(g['snapshots'][r]['us']['alive'] if r in g['snapshots'] else None) for r in (100,200,300)},
        deaths={k:counts[k] for k in CAUSES},death_rates={k:1000*counts[k]/mech['turns'] for k in CAUSES},
        timeout_turns=sum(a['timeout'] for a in g['action_rows']),no_action_turns=sum(a['no_action'] for a in g['action_rows']),
        failed_turns_move_exists=sum((a['timeout'] or a['no_action']) and a['empty_destination_move_exists'] for a in g['action_rows']),
        sonar={k:mech[k] for k in ('leader','new_rays','mouth','queen','other','unreadable')},final=g['final']['us'],
        stays=death_inside,arrivals=c.arrival_counts(mech['arrivals']),splits=c.split_counts(children),
        babies={name:c.baby_counts([r for r in babies if r['told']==told]) for name,told in [('told',True),('untold',False)]},
        refill_pearls_eaten=refill_eats,mechanism={k:mech[k] for k in c.STATS},
        stay_rows=mech['stays'],arrival_rows=mech['arrivals'],baby_rows=babies,anomalies=g['anomalies'])
    assert not row['anomalies'],row['anomalies']
    row['dead_end_babies'] = watch_babies(path, ours, children)
    for checkpoint in row['alive']:
        if row['alive'][checkpoint] is None:
            assert row['last_round'] < int(checkpoint)
            row['alive'][checkpoint] = row['final']['alive']
    return row

def watch_babies(path, ours, children):
    root = c.replay.load(str(path)).root()
    board = c.board_for(root.text(0))
    _, _, bodies, teams, _ = c.read_map(root.text(0))
    candidates = {r['child']: r for r in children if r['in_dead_end']}
    watches = {}; rnd = 0
    for ev in root.pointer(3):
        kind = c.replay.EVENT_NAMES[ev.u16(0)]; p = ev.pointer(0)
        if kind == 'roundStart': rnd = p.i32(0)
        elif kind == 'dragonUpdate':
            did = p.i32(0); head = c.replay.point(p.pointer(0)); tail = c.replay.point(p.pointer(1))
            body = bodies.setdefault(did, c.deque()); moved = not body or body[0] != head
            if moved: body.appendleft(head)
            while len(body) > 1 and body[-1] != tail: body.pop()
            w = watches.get(did)
            if w and moved and rnd - w['round'] <= c.WATCH:
                inside = head in w['_cells']
                if inside and not w['_inside']:
                    if w['returned_after'] is None: w['returned_after'] = rnd - w['round']
                    w['return_entries'] += 1
                if not inside: w['left'] = True
                w['_inside'] = inside
        elif kind == 'dragonSplit':
            parent, child = p.i32(0), p.i32(4)
            old = bodies[parent]
            end = board.dead_end(old[0], old[1]) if len(old) > 1 else None
            w = watches.get(parent)
            if w and rnd - w['round'] <= c.WATCH and old[0] in w['_cells'] and w['returned_after'] is not None:
                w['split_inside_after_return'] = True
            bodies[parent] = c.deque(c.replay.point(q) for q in p.pointer(0))
            bodies[child] = c.deque(c.replay.point(q) for q in p.pointer(1))
            teams[parent] = teams[child] = 'AB'[p.u16(8)]
            if child in candidates:
                r = candidates[child]; assert end is not None and teams[child] == ours
                born_inside = bodies[child][0] in end['cells']
                watches[child] = dict(round=rnd, parent=parent, child=child, told=bool(r['own_end_sent'] and r['told']),
                    own_end_sent=r['own_end_sent'], born_inside=born_inside, gate=end['gate'], direction=end['dir'],
                    room=len(end['cells']), returned_after=None, return_entries=0, left=not born_inside,
                    died_inside_after_return=False, split_inside_after_return=False, died_after=None,
                    _inside=born_inside, _cells=end['cells'])
        elif kind == 'dragonDeath':
            did = p.i32(0); w = watches.get(did)
            if w and rnd - w['round'] <= c.WATCH:
                w['died_after'] = rnd - w['round']
                if bodies[did][0] in w['_cells'] and w['returned_after'] is not None:
                    w['died_inside_after_return'] = True
            bodies.pop(did, None)
    assert set(watches) == set(candidates)
    for w in watches.values():
        w['observed_rounds'] = min(c.WATCH, rnd - w['round'])
        w['censored'] = w['observed_rounds'] < c.WATCH and w['died_after'] is None
        del w['_inside']; del w['_cells']
    return list(watches.values())

if __name__=='__main__':
    rows=[]
    with (OUT/'rows.jsonl').open('w') as f:
        for label,folder in FOLDERS.items():
            paths=sorted((ROOT/'data/online/smoke'/folder).glob('game-*.json'))
            assert len(paths)==15,(label,len(paths))
            for p in paths:
                row=analyze(label,folder,p);rows.append(row)
                f.write(json.dumps(row)+'\n');f.flush()
                print(label,row['game_id'],row['map'],row['turns'],flush=True)
    assert len(rows)==60
