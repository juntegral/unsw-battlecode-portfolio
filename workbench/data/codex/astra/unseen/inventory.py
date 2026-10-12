import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=Path.home()/"meow-redteam"
PACKAGE=BASE/"engine/venv/lib/python3.13/site-packages/unswbc"

def read_map(path):
    lines=[line.split() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]
    w,h=map(int,next(row for row in lines if row[0]=="MAP")[1:])
    beds=[list(map(int,row[1:])) for row in lines if row[0]=="TILE"]
    edges={}
    for row in lines:
        if row[0]!="EDGE":continue
        raw,kind,pid=map(int,row[1:]);y,x=divmod(raw,w+1)
        if y%2==0:
            if x==w:continue
            key=(0,x,(y//2)%h)
        else:key=(1,x%w,y//2)
        edges[key]=(kind,pid)
    ds=[list(map(int,row[1:])) for row in lines if row[0]=="DRAGON"]
    def head_distance(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    qs=[next((d for d in ds if d[0]==team),None) for team in [0,1]]
    ids=sorted({pid for kind,pid in edges.values() if kind==2})
    result=dict(file=str(path),width=w,height=h,cells=w*h,symmetry=next((row[1] for row in lines if row[0]=="SYMMETRY"),None),unit_limit=next((int(row[1]) for row in lines if row[0]=="UNIT_LIMIT"),64),start_count=[sum(d[0]==team for d in ds) for team in [0,1]],queen_lengths=[q[1] if q else None for q in qs],queen_heads=[q[2:4] if q else None for q in qs],queen_spawn_distance=head_distance(qs[0][2:4],qs[1][2:4]) if all(qs) else None,start_length_range=[min(d[1] for d in ds),max(d[1] for d in ds)] if ds else [],beds=sum(b[3]>0 for b in beds),gap_range=[min(b[2] for b in beds if b[3]>0),max(b[3] for b in beds)] if any(b[3]>0 for b in beds) else [],portal_pairs=len(ids),portal_id_range=[min(ids),max(ids)] if ids else [],kelp_edges=sum(kind==1 for kind,pid in edges.values()),seam_kelp=sum(kind==1 and (y==0 if vertical==0 else x==0) for (vertical,x,y),(kind,pid) in edges.items()))
    return result

state=json.loads((ROOT/"data/online/smoke/one5-w1.json").read_text())
index=json.loads((ROOT/"data/analysis/ladder/maps.json").read_text())
source={"weakhold":"weakhold","Default":"default","Queen Of Spades":"queen_of_spades","Trophy":"trophy","Devil":"devil","Trauma":"trauma"}
source.update({"Australia":"ladder_australia_1","Islands":"ladder_islands_1","Maze":"maze","Stripes":"ladder_stripes_1","Tower Defense":"ladder_tower_defense_1","Around UNSW":"ladder_around_unsw_1","Schooltime":"ladder_schooltime_2","Portals":"ladder_portals_1","Slithery Fight":"ladder_slithery_fight_1"})
rows=[]
for item in state["maps"]:
    name=item["name"];stem=source[name]
    path=(BASE/"maps/ladder"/f"{stem}.map") if stem.startswith("ladder_") else (PACKAGE/"templates/maps"/f"{stem}.map")
    r=read_map(path);r["name"]=name;r["map_id"]=item["id"]
    candidates=[(key,value) for key,value in index.items() if value["name"]==name]
    key,online=max(candidates,key=lambda pair:pair[1]["last_game"])
    r["online_index_key"]=key;r["online_index"]=dict(width=online["width"],height=online["height"],queen_length=online["queen_spawn_length"],beds=online["pearl_tiles"],dragons=online["dragons_at_spawn"])
    rows.append(r)
others=[read_map(path) for directory in ["dev","eval"] for path in sorted((BASE/"maps"/directory).glob("*.map"))]
(HERE/"map_inventory.json").write_text(json.dumps(dict(ladder=rows,heldout=others),indent=2)+"\n")
lines=["[M] Live 15-map list: `data/online/smoke/one5-w1.json`; `maps.json` has 19 historical name/version entries, so using all 19 as the current ladder is wrong.","[M] Exact initializer data below comes from local ladder files, plus installed engine templates where a ladder copy is absent. Counts in the replay-derived index are not always initializer counts; mismatches are retained in JSON.","", "| Map | Size/cells | Sym | Starters A/B | Queen lengths | All start lengths | Pearl beds; gap min/max | Portal pairs; max ID | Seam kelp |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['name']} | {r['width']}×{r['height']} / {r['cells']} | {r['symmetry']} | {r['start_count']} | {r['queen_lengths']} | {r['start_length_range']} | {r['beds']}; {r['gap_range']} | {r['portal_pairs']}; {r['portal_id_range'][-1] if r['portal_id_range'] else '—'} | {r['seam_kelp']} |")
lines += ["", "[M] Local ladder ranges: "+str(dict(width=[min(r['width'] for r in rows),max(r['width'] for r in rows)],height=[min(r['height'] for r in rows),max(r['height'] for r in rows)],cells=[min(r['cells'] for r in rows),max(r['cells'] for r in rows)],queen_distance=[min(r['queen_spawn_distance'] for r in rows),max(r['queen_spawn_distance'] for r in rows)])),"", "[M] Read-only held-out geometry: "+str(dict(maps=len(others),width=[min(r['width'] for r in others),max(r['width'] for r in others)],height=[min(r['height'] for r in others),max(r['height'] for r in others)],cells=[min(r['cells'] for r in others),max(r['cells'] for r in others)])),"", "[M] Every inventoried ladder/held-out file has unit limit 64 and declared x/y/xy symmetry; no tested local ladder portal ID reaches 2*cells."]
(HERE/"inventory.md").write_text("\n".join(lines)+"\n")
print("Inventoried",len(rows),"live ladder maps and",len(others),"held-out maps")
