"""Load maps through installed engine; abort before the first bot turn."""
import json
from pathlib import Path
from unswbc.engine import EngineModule

class Loaded(Exception):
    pass

engine = None

def load(text):
    global engine
    if engine is None:
        engine = EngineModule()
    notices = []
    initial = []
    def stop_spawn(dragon_id, data):
        initial.append(data.decode())
        raise Loaded()
    def no_turn(*args):
        raise AssertionError("No bot turns are authorized")
    try:
        engine.run(text.encode(), no_turn, bot_spawn=stop_spawn, on_notice=notices.append, debug=0)
    except Loaded:
        return dict(loaded=True, notices=notices, initial=initial[0])
    except Exception as error:
        return dict(loaded=False, notices=notices, error=str(error))
    return dict(loaded=False, error="Returned without a spawn", notices=notices)

def minimal(w=16,h=16,extras="", symmetry="xy", dragons=None):
    if dragons is None:
        dragons = ["DRAGON 0 2 2 2 1 2", "DRAGON 1 2 %d %d %d %d" % (w-3,h-3,w-2,h-3)]
    rows=[f"MAP {w} {h}"]
    if symmetry is not None:
        rows.append(f"SYMMETRY {symmetry}")
    rows += ["TILE_COUNT " + str(sum(line.startswith("TILE ") for line in extras.splitlines())), "EDGE_COUNT " + str(sum(line.startswith("EDGE ") for line in extras.splitlines())), extras,f"DRAGON_COUNT {len(dragons)}",*dragons,"END"]
    return "\n".join(rows)+"\n"

if __name__ == "__main__":
    cases={}
    for w,h in [(6,16),(7,16),(8,8),(64,64),(65,64),(128,128),(129,32),(4097,1),(32,129),(256,256),(257,16),(1024,16),(65536,16),(16,6),(16,7),(16,8)]:
        cases[f"dimensions-{w}x{h}"]=minimal(w,h)
    for sym in [None,"x","y","xy","none","rot90","diagonal"]:
        cases[f"symmetry-{sym}"]=minimal(symmetry=sym)
    for gap in [(0,0),(0,1),(1,1),(1,500),(500,500),(501,501),(1000000,1000000),(-1,10),(5,4)]:
        cases[f"gap-{gap}"]=minimal(extras=f"TILE 8 8 {gap[0]} {gap[1]}")
    for limit in [0,1,2,64,128,4096,2147483647]:
        cases[f"unit-limit-{limit}"]=minimal(extras=f"UNIT_LIMIT {limit}")
    for edges in ["EDGE 0 1 -1", "EDGE 0 2 0\nEDGE 1 2 0", "EDGE 0 2 0\nEDGE 16 2 0", "EDGE 0 2 1000000\nEDGE 1 2 1000000", "EDGE 0 2 0"]:
        cases[f"edges-{edges}"]=minimal(extras=edges)
    for teams in [(0,1),(1,0),(0,0),(0,1,0),(0,1,1,0)]:
        d=[f"DRAGON {team} 2 {2+i*3} 2 {1+i*3} 2" for i,team in enumerate(teams)]
        cases[f"team-order-{teams}"]=minimal(dragons=d)
    out={key:load(value) for key,value in cases.items()}
    Path(__file__).with_name("loader_probes.json").write_text(json.dumps(out,indent=2)+"\n")
    for key,value in out.items():
        print(key, "OK" if value["loaded"] else value.get("error"),value["notices"])
    print("Initial protocol:",next(value["initial"] for value in out.values() if value["loaded"]))
