import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import replay_format as rp
from unswbc.engine import EngineModule
OUT=Path(__file__).resolve().parent

def probe(reply_value=b'MOVE E\n',sym=False):
    tiles=[(3,3,5,5),(1,1,5,5),(2,2,2,4),(0,0,1,1),(4,4,0,0)]
    if sym:tiles=[(1,1,2,4),(6,6,2,4)]
    text='MAP 8 8\n'+('SYMMETRY xy\n' if sym else '')+'MAP_NAME Probe\nTILE_COUNT '+str(len(tiles))+'\n'+''.join('TILE %d %d %d %d\n'%t for t in tiles)+'EDGE_COUNT 0\nDRAGON_COUNT 2\nDRAGON 0 2 1 1 1 2\nDRAGON 1 2 6 6 6 5\nEND\n'
    e=EngineModule();deaths=[]
    result=e.run(text.encode(),lambda i,b:reply_value,on_death=lambda *a:deaths.append(a),debug=0,seed=1)
    blob=e.replay('probe','probe');(OUT/('probe-sym.replay' if sym else 'probe-move.replay' if reply_value!=b'MOVE\n' else 'probe-noop.replay')).write_bytes(blob)
    root=rp.Message(rp.unpack_packed(blob)).root(); rnd=-1;actor=None;events=[]
    for v in root.pointer(3):
        k=v.u16(0);p=v.pointer(0)
        if k==0:rnd=p.i32(0);actor=None
        elif k==1:actor=p.i32(0)
        elif k in (2,3):events.append(dict(round=rnd,kind=k,value=p.i32(0),tile=rp.point(p.pointer(0)),natural=actor is None))
    return dict(rounds=result.rounds,deaths=deaths,events=events)

if __name__=='__main__':
    output=dict(noop=probe(b'MOVE\n'),move=probe(),symmetry=probe(sym=True))
    (OUT/'semantics.json').write_text(json.dumps(output,indent=2)+'\n')
    for name,row in output.items():
        print(name,'rounds',row['rounds'],'deaths',row['deaths'])
        print(row['events'][:30])
