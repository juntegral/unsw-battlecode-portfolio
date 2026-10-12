import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,deque,Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[6]/'tools'))
from ladder_replay import canonical_edges,edge_id
STEP=((0,-1),(1,0),(0,1),(-1,0))
class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                    row.append((kind, dest))
                self.moves.append(row)
        # components without portals (kelp-bounded), the bot's "pocket"
        self.comp = [-1] * (w * h)
        self.size = []
        for c0 in range(w * h):
            if self.comp[c0] >= 0:
                continue
            n = len(self.size)
            self.comp[c0] = n
            q = deque([c0])
            k = 0
            while q:
                c = q.popleft()
                k += 1
                for kind, dest in self.moves[c]:
                    if kind == 0 and self.comp[dest] < 0:
                        self.comp[dest] = n
                        q.append(dest)
            self.size.append(k)
        # a component is a "loop" pocket when some portal edge has both of its tiles inside it and leads outside
        self.loop = [0] * len(self.size)
        for c in range(w * h):
            y, x = divmod(c, w)
            for d in range(4):
                kind, dest = self.moves[c][d]
                if kind != 2:
                    continue
                plain = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                if self.comp[plain] == self.comp[c] and self.comp[dest] != self.comp[c]:
                    self.loop[self.comp[c]] = 1


def inspect():
    out=Path(__file__).resolve().parent
    text=(out/'ladder_stripes_1.map').read_text();w,h=map(int,text.splitlines()[0].split()[1:3]);raw=[];tiles={};starts=set()
    for l in text.splitlines():
        q=l.split()
        if q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:])))
        elif q and q[0]=='TILE':tiles[int(q[2])*w+int(q[1])]=list(map(int,q[3:5]))
        elif q and q[0]=='DRAGON':starts.add(int(q[4])*w+int(q[3]))
    g=Geo(w,h,raw);startcomps={g.comp[c] for c in starts};rows=[]
    for i,size in enumerate(g.size):
        cs=[c for c in range(w*h) if g.comp[c]==i]
        if i in startcomps or not any(kind==2 for c in cs for kind,t in g.moves[c]):continue
        rows.append(dict(id=i,size=size,kind='loop' if g.loop[i] else 'dead end',tiles=[dict(x=c%w,y=c//w,interval=tiles[c],moves=[['NESW'[d],kind,[t%w,t//w]] for d,(kind,t) in enumerate(g.moves[c])]) for c in cs]))
    (out/'stripes-rooms.json').write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:print(r['id'],r['size'],r['kind'],[(t['x'],t['y'],t['interval']) for t in r['tiles']])
if __name__=='__main__':inspect()
