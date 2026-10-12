from pathlib import Path
p=Path('data/analysis/ladder/dossier/work')
s=(p/'at_scan.py').read_text().split('\ndef main():')[0]
s=s.replace("path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])", "path = Path(row['replay'])")
a=s.index('            en = 1 - s\n            if not g.ball')
b=s.index('        elif k == 3:',a)
s=s[:a]+'''            cur['open_start'] = sum(not occ[t] for t in g.adj[hd])
            cur['head_start'] = hd
'''+s[b:]
s=s.replace('    half = None\n','''    half = None
    history = defaultdict(lambda: deque(maxlen=2))
    turn_begin = None
    pending_net = []
    def finish_history():
        if actor is not None and actor in bodies and turn_begin is not None:
            history[actor].append((turn_begin, bodies[actor][0]))
    def distance(src, dst):
        if src == dst: return 0
        q = deque([src]); d = {src:0}
        while q:
            c=q.popleft()
            for t in g.adj[c]:
                if t in d: continue
                d[t]=d[c]+1
                if t==dst: return d[t]
                q.append(t)
        return None
    def reach(src, L, targets):
        budget=(L+3)//4+L-2
        d={src:0}; q=deque([src]); found=set()
        while q:
            c=q.popleft()
            for t in g.adj[c]:
                cost=d[c]+int(t not in present)
                if cost>budget: continue
                if t in targets: found.add(t)
                if occ[t]: continue
                if cost>=d.get(t,10**9): continue
                d[t]=cost
                if t in present:q.appendleft(t)
                else:q.append(t)
        return found
    def totals():
        out=[0,0]
        for i,b in bodies.items():out[side(i)]+=len(b)
        return out
''')
s=s.replace("            rnd, actor, cur = p.i32(0), None, None",'''            finish_history()
            next_r=p.i32(0)
            for ho in pending_net[:]:
                if next_r > ho['r']+15:
                    ho['net15']=[totals()[z]-ho['pre_total'][z] for z in (ho['ms'],1-ho['ms'])]
                    pending_net.remove(ho)
            rnd, actor, cur = next_r, None, None''')
s=s.replace("            actor = p.i32(0)","            finish_history()\n            actor = p.i32(0)")
s=s.replace("            hd = b[0]\n            turns", "            hd = b[0]\n            turn_begin = hd\n            turns")
s=s.replace("                hos.append(half)",'''                qbody=bodies.get(queen[ms])
                qhead=qbody[0] if qbody else None
                qdist=distance(hd,qhead) if qbody else None
                hist=list(history[i])
                towards=[distance(a,qhead)>distance(z,qhead) for a,z in hist] if qbody and all(distance(a,qhead) is not None and distance(z,qhead) is not None for a,z in hist) else []
                target_big={bb[0] for j,bb in bodies.items() if side(j)==ms and len(bb)>=8}
                target_q={qhead} if qbody else set()
                vr=reach(hd,L,target_big|target_q|{cur['head_start'],bodies[actor][0]})
                half.update(qalive=bool(qbody),qdist=qdist,history_n=len(hist),toward_any=any(towards),toward_both=len(towards)==2 and all(towards),
                    victim_big=bool(vr & target_big),victim_queen=bool(vr & target_q),
                    first_start=cur['head_start'] in vr,first_impact=bodies[actor][0] in vr,
                    open_start=cur['open_start'],open_impact=sum(not occ[t] for t in g.adj[bodies[actor][0]]),
                    sweep3=near(hd,ms,actor,3),pre_total=totals(),net15=None)
                pending_net.append(half)
                hos.append(half)''')
s=s.replace("    final = stand()",'''    for ho in pending_net:
        if rnd>=ho['r']+15:
            ho['net15']=[totals()[z]-ho['pre_total'][z] for z in (ho['ms'],1-ho['ms'])]
    final = stand()''')
(p/'lr_scan.py').write_text(s)
