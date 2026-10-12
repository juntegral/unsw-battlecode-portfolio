"""Print the structure of one per-game row and list the games of one layout."""
import json
import sys

PATH = "data/analysis/ladder/dossier/per-game.jsonl"
LAYOUT = sys.argv[1] if len(sys.argv) > 1 else "Australia #1"


def shape(v, depth=0, maxd=3):
    if isinstance(v, dict):
        if depth >= maxd:
            return "{%d keys}" % len(v)
        return {k: shape(x, depth + 1, maxd) for k, x in v.items()}
    if isinstance(v, list):
        return "[%d] %s" % (len(v), shape(v[0], depth + 1, maxd) if v else "")
    return type(v).__name__


first = True
with open(PATH) as f:
    for line in f:
        r = json.loads(line)
        if r["layout_key"] != LAYOUT:
            continue
        if first:
            top = {k: v for k, v in r.items() if k != "ranges"}
            print(json.dumps(shape(top), indent=1, ensure_ascii=False)[:3000])
            print("ranges:", list(r["ranges"].keys()))
            k0 = list(r["ranges"].keys())[0]
            print(json.dumps(shape(r["ranges"][k0], 0, 2), indent=1)[:5000])
            first = False
        if r["relation"] == "us":
            print(r["game"], r["battle"], r["opponent_rating"], r["our_result"], r["ended_by"],
                  r["last_round"], r["replay"], r["cells"], r["width"], r["height"])
