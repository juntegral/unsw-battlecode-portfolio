import sys
sys.dont_write_bytecode = True
import json, gzip, hashlib, re, math, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from collections import Counter, defaultdict, deque
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[5]
sys.path.insert(0,str(OUT.parent))
import replay_format as rp
import ctypes
native=ctypes.CDLL(str(OUT/'unpack-fast.dylib'))
native.unpack.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p]
native.unpack.restype=ctypes.c_size_t

def fast_unpack(data):
    n=native.unpack_size(data,len(data))
    out=ctypes.create_string_buffer(n)
    size=native.unpack(data,len(data),out)
    assert size==n
    return out.raw
rp.unpack_packed=fast_unpack
native.unpack_size.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
native.unpack_size.restype=ctypes.c_size_t
native.extract_events.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
native.extract_events.restype=ctypes.c_size_t

def event_list(raw):
    out=(ctypes.c_int32*(len(raw)//4))()
    n=native.extract_events(raw,out)
    events=[];i=0
    widths={0:1,1:1,3:3,9:5,11:1}
    while i<n:
        k=out[i];i+=1
        if k!=10:
            nn=widths[k];events.append((k,tuple(out[i:i+nn])));i+=nn
        else:
            values=list(out[i:i+2]);i+=2
            for j in range(2):
                nn=out[i];i+=1;values.append(tuple(out[i:i+2*nn]));i+=2*nn
            events.append((k,values))
    return events

TARGETS=['islands_1','australia_1','around_unsw_1','slithery_fight_1','schooltime_1','schooltime_2']

def layout(text):
    lines=text.splitlines(); w,h=map(int,lines[0].split()[1:3]);edges=[];bodies=[];sym=''
    for l in lines:
        q=l.split()
        if not q:continue
        if q[0]=='EDGE':edges.append(tuple(map(int,q[1:])))
        elif q[0]=='DRAGON':bodies.append(tuple(map(int,q[3:])))
        elif q[0]=='SYMMETRY':sym=q[1]
    return (w,h,sym,tuple(sorted(edges)),tuple(sorted(bodies)))

def orbit(c,w,h,sym):
    x,y=c%w,c//w
    # xy denotes 180-degree rotation, not independent x and y mirrors.
    d=(h-1-y)*w+(w-1-x) if sym=='xy' else y*w+(w-1-x) if sym=='y' else (h-1-y)*w+x
    return min(c,d)

def partial(path):
    f=path.open('rb');magic=f.read(2);f.seek(0)
    if magic==b'\x1f\x8b':f=gzip.GzipFile(fileobj=f)
    data=f.read(350000);f.close();out=bytearray();i=0
    while i<len(data) and len(out)<220000:
        tag=data[i];i+=1
        if tag==0:
            if i>=len(data):break
            out+=bytes(8*(data[i]+1));i+=1;continue
        word=bytearray(8)
        for bit in range(8):
            if tag&(1<<bit):word[bit]=data[i];i+=1
        out+=word
        if tag==255:
            count=data[i];i+=1;out+=data[i:i+8*count];i+=8*count
    return rp.Message(bytes(out)).root().text(0)

def inventory():
    signatures={layout((OUT.parent/'maps'/('ladder_'+s+'.map')).read_text()):s for s in TARGETS}
    main={json.loads(l)['replay'] for l in (OUT.parents[1]/'per-game.jsonl').read_text().splitlines()}
    rows=[];seen={};errors=[]
    for p in sorted((ROOT/'data/online').rglob('*.replay')):
        try:slug=signatures.get(layout(partial(p)))
        except Exception as e:errors.append([str(p.relative_to(ROOT)),str(e)]);continue
        if slug:
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            rel=str(p.relative_to(ROOT)); duplicate=seen.get(digest);seen[digest]=rel
            rows.append(dict(path=rel,slug=slug,sha256=digest,duplicate_of=duplicate,main=rel in main))
    (OUT/'inventory.json').write_text(json.dumps(dict(rows=rows,errors=errors),indent=2)+'\n')
    print('inventory',Counter(r['slug'] for r in rows),'unique',Counter(r['slug'] for r in rows if not r['duplicate_of']),'errors',len(errors),flush=True)


def scan(row):
    blob=(ROOT/row['path']).read_bytes()
    if blob[:2]==b'\x1f\x8b':blob=gzip.decompress(blob)
    raw=fast_unpack(blob);root=rp.Message(raw).root();events=event_list(raw)
    text=root.text(0);w,h,sym,*_=layout(text)
    orb=[orbit(c,w,h,sym) for c in range(w*h)];members=defaultdict(list)
    for c,o in enumerate(orb):members[o].append(c)
    bodies={};occupied=Counter();pearls=set()
    for l in text.splitlines():
        q=l.split()
        if q and q[0]=='DRAGON':
            b=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            bodies[len(bodies)]=b;occupied.update(b)
    active=set(json.loads((OUT/'active-orbits.json').read_text())[row['slug']])
    members={o:cs for o,cs in members.items() if o in active}
    virgin_end={c:0 for b in bodies.values() for c in b}
    freehist=defaultdict(list);births=defaultdict(set);tilebirths=Counter();firstbirth={};phasebirths=[0,0];rnd=-1;actor=None
    for k,p in events:
        if k==0:
            rnd=p[0];actor=None
            for o,cs in members.items():freehist[o].append(any(c not in pearls and not occupied[c] for c in cs))
        elif k==1:actor=p[0]
        elif k==3:
            x,y=p[1:3];c=y*w+x
            if p[0]:
                pearls.add(c)
                if actor is None:
                    births[orb[c]].add(rnd);tilebirths[c]+=1;firstbirth.setdefault(c,rnd)
                    if rnd<=300:phasebirths[int(rnd>100)]+=1
                else:virgin_end.setdefault(c,rnd)
            else:pearls.discard(c)
        elif k==9:
            i=p[0];b=bodies[i];head=p[2]*w+p[1];tail=p[4]*w+p[3]
            occupied.subtract(b)
            if b[0]!=head:b.appendleft(head)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            occupied.update(b)
            for c in b:virgin_end.setdefault(c,rnd+1)
        elif k==10:
            par,child=p[0],p[1];occupied.subtract(bodies[par])
            for z,i in enumerate((par,child)):
                bodies[i]=deque(p[z+2][i+1]*w+p[z+2][i] for i in range(0,len(p[z+2]),2));occupied.update(bodies[i])
        elif k==11:occupied.subtract(bodies.pop(p[0]))
    # Successful birth at an available start must be the shared orbit's attempt.
    samples={};records={}
    for o in active:
        bs=births[o]
        bs=sorted(bs);free=freehist[o];first=[];exact=[];residual=[]
        if bs:
            b=bs[0]
            if all(free[:b+1]):first=[b+1]
        for a,b in zip(bs,bs[1:]):
            if all(free[a+1:b+1]):exact.append(b-a)
        for b in bs:
            a=b
            while a>0 and free[a-1] and a-1 not in births[o]:a-=1
            if a>0 and not free[a-1]:residual.append(b-a+1)
        samples[str(o)]=dict(first=first,exact=exact,residual=residual)
        records[str(o)]=dict(births=bs,free_bits=hex(sum(1<<i for i,b in enumerate(free) if b)))
    return dict(**row,last_round=rnd,tile_births=dict(tilebirths),samples=samples,records=records,firstbirth=firstbirth,virgin_end=virgin_end,phasebirths=phasebirths)


def extract():
    inv=json.loads((OUT/'inventory.json').read_text())['rows'];rows=[r for r in inv if not r['duplicate_of']]
    existing=set()
    if (OUT/'observations-complete.jsonl').exists():
        existing={json.loads(l)['path'] for l in (OUT/'observations-complete.jsonl').read_text().splitlines()}
    with (OUT/'observations-complete.jsonl').open('a') as f:
        todo=[r for r in rows if r['path'] not in existing]
        with ProcessPoolExecutor(max_workers=3) as pool:
            for idx,result in enumerate(pool.map(scan,todo,chunksize=1)):
                f.write(json.dumps(result,separators=(',',':'))+'\n');f.flush()
                if idx%20==0:print(idx+1,len(todo),result['slug'],flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
