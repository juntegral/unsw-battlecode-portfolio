import json
from pathlib import Path
from probe_loader import load, minimal
cases={}
for sym in [None,"x","y","xy"]:
    cases[f"asymmetric-{sym}"]=minimal(symmetry=sym,extras="TILE 8 8 1 501")
for gap in [1,501,1000000,2147483647]:
    cases[f"timer-{gap}"]=minimal(symmetry=None,extras=f"TILE 8 8 {gap} {gap}")
for pid in [-2,-1,0,8000000,2147483647]:
    cases[f"portal-id-{pid}"]=minimal(symmetry=None,extras=f"EDGE 0 2 {pid}\nEDGE 1 2 {pid}")
for edges in ["EDGE 0 2 0\nEDGE 17 2 0", "EDGE 0 2 0\nEDGE 1 2 0\nEDGE 2 2 0", "EDGE 0 1 -1\nEDGE 544 1 -1", "EDGE 0 1 -1"]:
    cases[f"edge-case-{edges}"]=minimal(symmetry=None,extras=edges)
for n in [0,1,2,3,65,128]:
    dragons=[]
    for i in range(n):
        x=(i%8)*2;y=i//8
        dragons.append(f"DRAGON {i%2} 2 {x} {y} {x+1} {y}")
    cases[f"starters-{n}"]=minimal(dragons=dragons,symmetry=None)
for length in [1,2,4,25,128]:
    body=[(x,y) for y in range(8) for x in (range(16) if y%2==0 else range(15,-1,-1))][:length]
    dragons=["DRAGON 0 "+str(length)+" "+" ".join(f"{x} {y}" for x,y in body),"DRAGON 1 2 13 13 14 13"]
    cases[f"length-{length}"]=minimal(dragons=dragons,symmetry=None)
for line in ["ROUND_LIMIT 17", "MAX_ROUNDS 17", "TORUS 0"]:
    cases[line]=minimal(extras=line)
out={key:load(value) for key,value in cases.items()}
Path(__file__).with_name("loader_more.json").write_text(json.dumps(out,indent=2)+"\n")
for key,value in out.items():
    print(key, "OK" if value["loaded"] else value.get("error"),value["notices"])
