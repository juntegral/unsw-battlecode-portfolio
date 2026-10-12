import sys
sys.dont_write_bytecode = True
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'data/analysis/ladder/dossier/local'),
                str(ROOT / 'data/analysis/ladder/dossier/work')]
import scoreboard as sb
import ladder_replay as lr
import o1_scan

JOBS = [(1512560, 'one13-p2-old'), (1512564, 'one13-p2-old'),
        (1512567, 'one13-p2-old'), (1512571, 'one13-p2-old'),
        (1512572, 'one13-p2-old'), (1513122, None),
        (1515657, 'one13-q1-old'), (1515659, 'one13-q1-old'),
        (1515663, 'one13-q1-old'), (1515665, 'one13-q1-old'),
        (1515666, 'one13-q1-old'), (1515668, 'one13-q1-old')]
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def scan(gid, label):
    folder = ROOT / ('data/online/smoke/' + label if label else 'data/online/live-one1/b1513119')
    path = folder / f'M{gid}.replay'
    meta = json.loads((folder / f'game-{gid}.json').read_text())
    root = sb.load_replay(path).root()
    assert root.pointer(4).bit(0)
    own = int(meta['teamAId'] != 1119)
    assert root.text(1 + own) == '21377'
    lr.replay.load = lambda _: type('Loaded', (), {'root': lambda _: root})()
    base = lr.scan(path, meta, str(folder.relative_to(ROOT)), set())
    ledger = o1_scan.scan(label or 'ranked', path, meta)
    assert base['final']['us']['total'] == ledger['ends'][0][1]
    assert base['winner'] == 'AB'[own] and meta['winner'].upper() == 'AB'[own]
    w, h = map(int, base['text'].splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in base['text'].splitlines():
        p = line.split()
        if p[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(p[3 + 2*k]), int(p[4 + 2*k])) for k in range(int(p[2])))
            teams[i] = int(p[1])
        elif p[0] == 'EDGE':
            raw.append(tuple(map(int, p[1:4])))
    edges = lr.canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, (k, pid) in edges.items():
        if k == 2:
            portals[pid].append(e)
    qid = base['queens']['us']
    enemy_qid = base['queens']['them']
    side = lambda i: int(teams[i] != own)
    def dest(c, d):
        x, y = c
        e = lr.edge_id(w, h, x, y, d)
        k, pid = edges.get(e, (0, -1))
        if k == 1:
            return None
        if k == 2:
            other = next(z for z in portals[pid] if z != e)
            row, x = divmod(other, w+1)
            return ((x-(d == 3)) % w, (row//2-(d == 0)) % h)
        return ((x+STEP[d][0]) % w, (y+STEP[d][1]) % h)
    def visible(a, b):
        dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        return min(dx,w-dx) <= 3 and min(dy,h-dy) <= 3
    def man(a, b):
        dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    turns, splits, logs, far, opportunities = [], [], [], [], []
    present, seen, visited = set(), defaultdict(set), defaultdict(set)
    rnd, actor, turn = -1, None, None
    counts = Counter()
    def close():
        nonlocal turn
        if turn is None:
            return
        i = turn['id']
        turn['end'] = list(bodies[i][0]) if i in bodies else None
        turn['L1'] = len(bodies.get(i, ()))
        turn['steps'] = len(turn['path'])
        turn['miss_adjacent'] = bool(turn['adj_pearls']) and not turn['eats'] and not turn['split']
        turn['idle_split'] = turn['split'] and turn['end'] == turn['head']
        if side(i) == 0:
            for k, val in [('turns',1),('adj_pearl_turns',bool(turn['adj_pearls'])),
                           ('miss_adjacent',turn['miss_adjacent']),('idle_split',turn['idle_split']),
                           ('multistep_L8',turn['L0'] >= 8 and turn['steps'] >= 2),
                           ('queen_turns',i == qid),('queen_L2',i == qid and turn['L0'] == 2)]:
                counts[k] += val
        turns.append(turn)
        turn = None
    for index, ev in enumerate(root.pointer(3)):
        k, p = ev.u16(0), ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close()
            actor = p.i32(0)
            b = bodies[actor]
            seen[actor].update(((b[0][0]+dx)%w, (b[0][1]+dy)%h) for dx in range(-3,4) for dy in range(-3,4))
            visited[actor].add(b[0])
            occ = {c:i for i, bb in bodies.items() for c in bb}
            adj = [(d, dest(b[0],d)) for d in range(4)]
            pearls = [(d, c) for d,c in adj if c in present and c not in occ and visible(b[0],c)]
            enemies = [(i,len(bb),list(bb[0]),man(b[0],bb[0])) for i,bb in bodies.items() if side(i) != side(actor)]
            turn = dict(round=rnd, event=index, id=actor, side=side(actor), L0=len(b), head=list(b[0]),
                        count=sum(side(i)==side(actor) for i in bodies),
                        queen_length=len(bodies.get(qid,())), enemy_queen_length=len(bodies.get(enemy_qid,())),
                        adj_pearls=pearls, free_exits=[(d,c) for d,c in adj if c is not None and c not in occ],
                        enemies=enemies if actor == qid else [], path=[], eats=[], split=False,
                        action=None, dirs=[], logs=[], portal_steps=[], far_messages=[])
            if actor == qid:
                for eid,bb in bodies.items():
                    if side(eid) == 1:
                        for d in range(4):
                            if dest(bb[0],d) == b[0]:
                                opportunities.append(dict(round=rnd,event=index,queen=actor,queen_length=len(b),
                                                          queen_head=list(b[0]),enemy=eid,enemy_length=len(bb),
                                                          enemy_head=list(bb[0]),enemy_queen=eid==enemy_qid,
                                                          direction=d,visible=visible(b[0],bb[0]),later=eid>actor))
        elif k == 3:
            c = lr.replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                assert c in present
                present.remove(c)
                turn['eats'].append(list(c))
        elif k == 4:
            assert turn is not None and p.i32(0) == actor
            a = p.pointer(0)
            turn['action'] = a.u16(0) if a else None
            turn['dirs'] = list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k == 6:
            i, msg = p.i32(0), p.text(0)
            logs.append(dict(round=rnd,id=i,side=side(i),text=msg))
            if turn is not None and i == actor:
                turn['logs'].append(msg)
        elif k == 9:
            i = p.i32(0)
            hd, tl = lr.replay.point(p.pointer(0)), lr.replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if i == actor:
                    d = turn['dirs'][len(turn['path'])]
                    ek = edges.get(lr.edge_id(w,h,b[0][0],b[0][1],d),(0,-1))[0]
                    if ek == 2:
                        turn['portal_steps'].append(dict(before=list(b[0]),after=list(hd),unseen=hd not in seen[i]))
                    turn['path'].append(list(hd))
                b.appendleft(hd)
            while len(b)>1 and b[-1] != tl:
                b.pop()
            assert b[-1] == tl
        elif k == 10:
            i, child = p.i32(0), p.i32(4)
            turn['split'] = True
            old = len(bodies[i])
            for z,j in enumerate((i,child)):
                bodies[j] = deque(lr.replay.point(c) for c in p.pointer(z))
                teams[j] = p.u16(8)
            splits.append(dict(round=rnd,id=i,child=child,side=side(i),before=old,
                               kept=len(bodies[i]),child_length=len(bodies[child]),count_before=turn['count'],
                               queen=i == qid,head=list(bodies[i][0])))
        elif k == 11:
            bodies.pop(p.i32(0))
        elif k == 12:
            msg = p.u64(16)
            if (msg>>63) and ((msg>>38)&0x7fff)==0x5b and actor is not None and side(actor)==0:
                cell, parts, when = msg&0x3fff, ((msg>>14)&0x3fff)+1, (msg>>28)&0x1ff
                end = lr.replay.point(p.pointer(1))
                recipients = [i for i,bb in bodies.items() if bb[0]==end]
                far.append(dict(round=rnd,id=actor,cell=cell,parts=parts,when=when,
                                end=end,hit=p.u16(24),recipients=recipients,queen_receives=qid in recipients))
    close()
    snaps = base['snapshots']
    def cmp(st):
        a,b=st['us'],st['them']
        av=(int(a['alive']>0),a['queen_length'],a['longest'],a['total'])
        bv=(int(b['alive']>0),b['queen_length'],b['longest'],b['total'])
        return (av>bv)-(av<bv)
    last_not_ahead = max((int(r) for r,st in snaps.items() if cmp(st)<=0),default=-1)
    ahead = min((int(r) for r,st in snaps.items() if int(r)>last_not_ahead and cmp(st)>0),default=None)
    for t in turns:
        for p in t['portal_steps']:
            if t['side']==0:
                counts['portal_crossings']+=1
                counts['portal_blind_crossings']+=p['unseen']
    row = dict(gid=gid,map=meta['mapName'],source=label or 'ranked',side='AB'[own],bot_id=21377,
               opponent=meta['team'+'AB'[1-own]+'Name'],last_round=base['last_round'],how=ledger['how'],
               final=base['final'],ahead_for_good=ahead,snapshots=snaps,
               queen_death=next((d for d in base['deaths'] if d['id']==qid),None),
               enemy_queen_death=next((d for d in base['deaths'] if d['id']==enemy_qid),None),
               qid=qid,enemy_qid=enemy_qid,queens=base['queens'],eats=base['eats'],counts=dict(counts),
               death_counts=dict(Counter((d['side']+':'+d['cause']) for d in base['deaths'])),
               anomalies=base['anomalies'],logs=logs,far=far,splits=splits,
               queen_one_step_opportunities=opportunities,deaths=base['deaths'],ledger=ledger)
    (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':'))+'\n')
    (OUT/f'{gid}.json').write_text(json.dumps(row,separators=(',',':'))+'\n')
    print(json.dumps({k:row[k] for k in ('gid','map','side','last_round','how','final','ahead_for_good','queen_death','enemy_queen_death','counts','anomalies')},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    for gid,label in JOBS:
        scan(gid,label)
