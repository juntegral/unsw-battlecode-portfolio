import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter, defaultdict

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'tools'))
import ladder_replay as lr

OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'data/online/live-one1/b1495464'

def scan(gid):
    path = SOURCE / f'M{gid}.replay'
    meta = json.loads((SOURCE / f'game-{gid}.json').read_text())
    base = lr.scan(path, meta, 'b1495464', set())
    root = lr.replay.load(path).root()
    w, h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, edges_raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            bodies[len(bodies)] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
            teams[len(teams)] = int(q[1])
        elif q and q[0] == 'EDGE':
            edges_raw.append(tuple(map(int, q[1:4])))
    edges = lr.canonical_edges(w, h, edges_raw)
    portals = defaultdict(list)
    for edge, (kind, pid) in edges.items():
        if kind == 2:
            portals[pid].append(edge)
    def dest(cell, direction):
        edge = lr.edge_id(w, h, *cell, direction)
        kind, pid = edges.get(edge, (0, -1))
        if kind == 1:
            return None
        if kind == 2:
            other = next(e for e in portals[pid] if e != edge)
            row, x = divmod(other, w+1)
            return ((x-(direction == 3)) % w, (row//2-(direction == 0)) % h)
        dx, dy = ((0,-1),(1,0),(0,1),(-1,0))[direction]
        return ((cell[0]+dx) % w, (cell[1]+dy) % h)
    def man(a,b):
        dx,dy = abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    def seen(a,b):
        dx,dy = abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def within3(a,b):
        visited={a}
        todo=deque([(a,0)])
        while todo:
            c,distance=todo.popleft()
            if c==b:
                return True
            if distance==3:
                continue
            for direction in range(4):
                n=dest(c,direction)
                if n is not None and n not in visited:
                    visited.add(n)
                    todo.append((n,distance+1))
        return False
    us = 1
    queen = base['queens']['us']
    enemy_queen = base['queens']['them']
    rnd, actor, turn = -1, None, None
    pearls = set()
    turns = []
    def finish():
        if turn is None:
            return
        turn['end'] = list(bodies[actor][0]) if actor in bodies else None
        turn['end_length'] = len(bodies.get(actor, ()))
        if actor == queen and actor in bodies:
            occ = {c for b in bodies.values() for c in b}
            turn['end_exits'] = [list(n) for d in range(4) if (n:=dest(bodies[actor][0],d)) is not None and n not in occ]
        turns.append(turn)
    for index, ev in enumerate(root.pointer(3)):
        kind = ev.u16(0)
        p = ev.pointer(0)
        if kind == 0:
            finish()
            turn = None
            rnd, actor = p.i32(0), None
        elif kind == 1:
            finish()
            actor = p.i32(0)
            occ = {c for b in bodies.values() for c in b}
            head = bodies[actor][0]
            nexts = [dest(head,d) for d in range(4)]
            adjacent = [list(n) for n in nexts if n is not None and n not in occ and n in pearls]
            same = [(i,b) for i,b in bodies.items() if teams[i] == teams[actor]]
            foes = [(i,b) for i,b in bodies.items() if teams[i] != teams[actor]]
            turn = dict(round=rnd,event=index,id=actor,ours=teams[actor]==us,length=len(bodies[actor]),
                        head=list(head),steps=[],eats=[],action=None,split=None,deaths=[],
                        nearby_pearls=adjacent,free=[list(n) for n in nexts if n is not None and n not in occ],
                        own_count=len(same),own_longest=max(map(lambda z:len(z[1]),same)),
                        qhead=list(bodies[queen][0]) if queen in bodies else None,
                        foe_qhead=list(bodies[enemy_queen][0]) if enemy_queen in bodies else None,
                        foe_q_length=len(bodies.get(enemy_queen,())),
                        visible_foes=[[i,len(b),list(b[0])] for i,b in foes if seen(head,b[0])])
            turn['heading'] = next((d for d in range(4) if dest(bodies[actor][1],d)==head),None)
            if actor == queen:
                turn['body'] = list(map(list,bodies[actor]))
                turn['adjacent_cells'] = [list(n) if n is not None else None for n in nexts]
                turn['blocking'] = [[i, list(n)] for n in nexts if n is not None for i,b in bodies.items() if n in b]
                turn['near_mates'] = [[i,len(b),list(b[0]),man(head,b[0])] for i,b in same if i!=actor and man(head,b[0])<=6]
                turn['nearest_foe'] = min([[man(head,b[0]),i,len(b),list(b[0])] for i,b in foes], default=None)
        elif kind == 3:
            c = lr.replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.remove(c)
                turn['eats'].append(list(c))
        elif kind == 4:
            a=p.pointer(0)
            turn['action'] = a.u16(0) if a else None
            turn['dirs'] = list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif kind == 9:
            i=p.i32(0)
            head,tail=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1))
            b=bodies[i]
            if b[0]!=head:
                if i==actor:
                    turn['steps'].append(list(head))
                b.appendleft(head)
            while len(b)>1 and b[-1]!=tail:
                b.pop()
            assert b[-1]==tail
        elif kind == 10:
            parent,child=p.i32(0),p.i32(4)
            turn['split']=[parent,child,len(bodies[parent])]
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z))
                teams[i]=p.u16(8)
            turn['split'].extend([len(bodies[parent]),len(bodies[child])])
        elif kind == 11:
            i=p.i32(0)
            turn['deaths'].append([i,p.u16(4),teams[i],len(bodies[i])])
            bodies.pop(i)
    finish()
    def key(s):
        return (s['queen_length'],s['longest'],s['total'])
    leads={int(r):key(st['us'])>key(st['them']) for r,st in base['snapshots'].items()}
    last_nonlead=max((r for r,lead in leads.items() if not lead), default=-1)
    base['ahead_for_good']=last_nonlead+1
    base['dimensions']=[w,h]
    base['turns']=turns
    base['round_leads']=leads
    base['intervals']={f'{x},{y}':v for (x,y),v in base['intervals'].items()}
    (OUT/f'game-{gid}.json').write_text(json.dumps(base,ensure_ascii=False,separators=(',',':'))+'\n')
    counters=Counter()
    moments=defaultdict(list)
    def count(name,t):
        counters[name]+=1
        if len(moments[name])<5:
            moments[name].append([t['round'],t['id'],t['length'],t['head'],t['steps'],t['eats']])
    for t in turns:
        if not t['ours']:
            continue
        count('turns',t)
        if t['split']:
            count('splits',t)
        if not t['steps'] and not t['split']:
            count('no_step_no_split',t)
        if t['nearby_pearls']:
            count('adjacent_pearl_turn',t)
            if t['steps'] and t['steps'][0] in t['nearby_pearls']:
                count('adjacent_pearl_taken_first',t)
            else:
                count('adjacent_pearl_passed',t)
        if t['round']<12 and t['id']!=queen and t['length']<=3 and t['steps']:
            count('early_short_moving',t)
        if t['id']==queen:
            count('queen_turns',t)
            if t['split']:
                count('queen_splits',t)
            if t['nearest_foe'] and t['nearest_foe'][0]<=1:
                count('queen_foe_head_adjacent',t)
            if not t['free']:
                count('queen_no_exit',t)
            if t['length']==4 and t['own_count']>=2 and not t['split']:
                count('queen_L4_nonsplit_units2',t)
        for i,reason,team,length in t['deaths']:
            if i==enemy_queen:
                count('enemy_queen_ram',t)
            if reason==3 and team!=us and i!=enemy_queen and t['length']<=4 and t['qhead'] is not None:
                dead=next(d for d in base['deaths'] if d['id']==i)
                if within3(tuple(t['qhead']),tuple(dead['body'][0])):
                    count('queen_near3_ram',t)
    summary=dict(gid=gid,map=base['map'],dimensions=[w,h],bot=base['bots']['B'],queens=base['queens'],
                 end=base['last_round'],ahead_for_good=base['ahead_for_good'],final=base['final'],eats=base['eats'],
                 queen_deaths=[d for d in base['deaths'] if d['id'] in base['queens'].values()],
                 counts=dict(counters),moments=dict(moments))
    print(json.dumps(summary,ensure_ascii=False))
    return summary

if __name__=='__main__':
    rows=[scan(gid) for gid in range(1495464,1495468)]
    (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
