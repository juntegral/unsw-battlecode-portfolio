"""Scratch: per-layout head-on and growth table from dossier/per-game.jsonl (no replay reads)."""
import json
from collections import defaultdict

PATH = "data/analysis/ladder/dossier/per-game.jsonl"
rows = defaultdict(dict)
with open(PATH) as f:
    for line in f:
        r = json.loads(line)
        slim = dict(layout=r["layout_key"], cells=r["cells"], res=r["our_result"], ended=r["ended_by"], rating=r["opponent_rating"],
                    half100=(r["heads_enemy_half"]["100"] or {}).get("share"), nstart=len(r["starting_dragons"]),
                    contact=r["first_enemy_head_in_view"], q=r["queen"], rg={})
        for name in ("0-100", "101-300", "101-200", "201-300"):
            c = r["ranges"][name]
            slim["rg"][name] = dict(mover=c["deaths"]["head-on mover"], hit=c["deaths"]["head-on hit"], trades=c["cross_head_on_trades"],
                                    lost=c["head_on_length_lost"], pearls=c["pearls_eaten"], splits=c["splits"], es=c["end_state"],
                                    deaths=sum(c["deaths"].values()), turns=c["turns"])
        rows[r["game"]][r["relation"]] = slim

by = defaultdict(list)
for g, d in rows.items():
    by[d["us"]["layout"]].append(d)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


print("layout | cells | start | games won | r0-100: trades, their mover share | r101-300: trades, their mover share, trades per 100 of our turns | total r100 us/them | total r300 us/them | longest r300 us/them | enemy-half100 us")
out = []
for lay, ds in by.items():
    n = len(ds)
    won = sum(d["us"]["res"] == "win" for d in ds)
    line = [lay, ds[0]["us"]["cells"], ds[0]["us"]["nstart"], n, won]
    for name in ("0-100", "101-300"):
        tr = sum(d["us"]["rg"][name]["trades"] for d in ds)
        tm = sum(d["them"]["rg"][name]["mover"] for d in ds)
        um = sum(d["us"]["rg"][name]["mover"] for d in ds)
        turns = sum(d["us"]["rg"][name]["turns"] for d in ds)
        line += [round(tr / n, 1), round(tm / max(1, tm + um), 2), round(100.0 * tr / max(1, turns), 2)]
    for name, key in (("0-100", "total"), ("101-300", "total"), ("101-300", "longest"), ("101-300", "alive")):
        line.append("%.0f/%.0f" % (mean([(d["us"]["rg"][name]["es"] or {}).get(key) for d in ds]),
                                   mean([(d["them"]["rg"][name]["es"] or {}).get(key) for d in ds])))
    line.append(round(100 * mean([d["us"]["half100"] for d in ds]), 0))
    line.append(round(mean([d["us"]["contact"] for d in ds]), 0))
    out.append(line)
out.sort(key=lambda l: -l[9])
for l in out:
    print(" | ".join(str(x) for x in l))
