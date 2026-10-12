#!/usr/bin/env python3
"""d_box.py [list]: the boxed-in queen deaths in detail (sub-session A4, questions a and d).

For every queen that died by her own order with no free cell next to her head (kinds 'boxed: ...' of d_tab.py):
  sides    what stood on her four sides: K kelp, o her own body, a / A a team-mate's body / head, e / E an enemy's
  blocker  for team-mates: is it her own split child (born in her last 13 turns), was it born by a "cut" (she kept
           2-3 and gave the rest away), is it a head (two own dragons nose to nose) or a body segment
  entry    how many turns before her death the free region around her became smaller than 12 cells, and what she
           did on the turn before that: ate, split, had an enemy head in view, had a roomier option (a free side
           whose region was 12 or more while the one she took was smaller)
  portal   one of her sides was a portal edge (the exit cell lies outside her view)
Sub-kinds printed for the report:
  cut and stuck     she split so that she kept 2-3 of 6 or more, and died inside what had been her own body
  own child on the exit   her own recent split child (not a cut) stood on her last exit
  nose to nose      a team-mate's HEAD stood on her last exit (two own dragons met head-on in a one-cell-wide way)
  team-mate's body  another team-mate's body segment stood on her last exit
  terrain dead end  tree cell; with whether she ate or split on the way in
Reads d_out/cls through d_tab.load().
"""
import sys
from collections import Counter, defaultdict

import d_tab

GROUPS = ["meow", "meow live", "meow live rules on", "meow live rules off", "opp", "forgot", "SSS", "Vibing++"]


def sub(x):
    sd, det = x["sd"], x["det"]
    turns = sd["turns"]
    T = det["T"]
    kids = {}
    for t in turns:
        if "split" in t:
            b, p, c, ch = t["split"]
            kids[ch] = (t["r"], b, p, c)
    cut = [v for v in kids.values() if v[1] >= 6 and v[2] <= 3]
    bl = det["blockers"]
    ally = [b for b in bl if b[0] in "aA"]
    portal = any(len(s) > 3 and s[0] != "K" and s[3] for s in T["sides"])
    info = dict(portal=portal, cut=bool(cut), len=T["len"], kids=kids)
    if x["kind"] == "boxed: terrain dead end":
        return "terrain dead end", info
    if cut and any(b[4] in kids for b in bl if b[0] in "aA") or (cut and not ally and x["kind"] != "boxed: own body"):
        return "cut and stuck", info
    if x["kind"] in ("boxed: enemy body", "boxed: ally+enemy"):
        return "enemy body on the exit", info
    if x["kind"] == "boxed: own body":
        return "own body", info
    if any(b[4] in kids for b in ally):
        return "own child on the exit", info
    if any(b[0] == "A" for b in ally):
        return "nose to nose", info
    return "team-mate's body", info


def entry(x):
    turns = x["sd"]["turns"]
    n = len(turns)
    i = n - 1
    while i > 0 and turns[i - 1].get("froom", 99) < 12:
        i -= 1
    back = n - 1 - i
    dec = turns[i - 1] if i > 0 else None
    out = dict(back=back)
    if dec is not None:
        opts = [s for s in dec["sides"] if s[0] in "FP"]
        end = dec["end"]
        took = [s for s in opts if end and [s[1], s[2]] == end]
        best = max((s[8] for s in opts), default=0)
        out.update(ate=dec["ate"] > 0, split="split" in dec, vis=dec["nvis"] > 0,
                   took_room=took[0][8] if took else None, best_room=best,
                   roomier=bool(took) and took[0][8] < 12 <= best, pearl=bool(took) and took[0][0] == "P",
                   reach=dec["reach0"] > 0 or any(s[4] > 0 for s in opts))
    ate = sum(t["ate"] for t in turns[max(0, i - 1):])
    out["ate_in"] = ate
    out["split_in"] = sum(1 for t in turns[max(0, i - 1):] if "split" in t)
    out["vis_in"] = any(t["nvis"] > 0 for t in turns[max(0, i - 1):])
    return out


def main():
    want = len(sys.argv) > 1 and sys.argv[1] == "list"
    recs = [x for x in d_tab.load() if x["kind"].startswith("boxed")]
    by = defaultdict(list)
    for x in recs:
        gs = [g for g in x["groups"] if not g.startswith("run ")]
        if "meow live" in gs:
            gs.append("meow live rules on" if x["cells"] > 600 else "meow live rules off")
        x["sub"], x["info"] = sub(x)
        x["entry"] = entry(x)
        for g in gs:
            by[g].append(x)
    subs = ["cut and stuck", "own child on the exit", "nose to nose", "team-mate's body", "enemy body on the exit", "own body", "terrain dead end"]
    print("sub-kind | " + " | ".join(GROUPS))
    for s in subs:
        print(f"{s} | " + " | ".join(str(sum(1 for x in by[g] if x["sub"] == s)) for g in GROUPS))
    print("all boxed-in deaths | " + " | ".join(str(len(by[g])) for g in GROUPS))
    print("... one of her sides was a portal edge | " + " | ".join(str(sum(1 for x in by[g] if x["info"]["portal"])) for g in GROUPS))
    print("... her length 2 / 3 / 4+ | " + " | ".join("/".join(str(sum(1 for x in by[g] if (x["info"]["len"] if x["info"]["len"] < 4 else 4) == k)) for k in (2, 3, 4)) for g in GROUPS))
    print("\nhow she got into the small region (the turn before the free region around her fell under 12 cells)")
    for s in subs:
        print(f"  {s}")
        for g in GROUPS:
            xs = [x for x in by[g] if x["sub"] == s]
            if not xs:
                continue
            e = [x["entry"] for x in xs]
            known = [v for v in e if "ate" in v]
            back = Counter(min(v["back"], 6) for v in e)
            print(f"    {g:20s} n={len(xs):3d} | small region for 0/1/2/3/4/5/6+ turns before death: " + "/".join(str(back[k]) for k in range(7))
                  + f" | on the entry turn (n={len(known)}): stepped onto a pearl {sum(v['pearl'] for v in known)}, split {sum(v['split'] for v in known)}, "
                  f"enemy head in view {sum(v['vis'] for v in known)}, a roomier free side existed {sum(v['roomier'] for v in known)}, an option was inside enemy reach {sum(v['reach'] for v in known)}"
                  + f" | ate in the small region {sum(v['ate_in'] > 0 for v in e)}, split there {sum(v['split_in'] > 0 for v in e)}, enemy in view there {sum(v['vis_in'] for v in e)}")
    if want:
        for g in ("meow",):
            print(f"\n{g}: one line per boxed-in death")
            for x in sorted(by[g], key=lambda x: (x["sub"], x["map"], x["det"]["r"])):
                e = x["entry"]
                bl = [f"{b[0]}#{b[4]}L{b[5]}s{b[6]}" for b in x["det"]["blockers"]]
                print(f"  {x['sub']:22s} | {x['gid']} {x['map'][:14]:14s} {x['run'][:16]:16s} vs {x['opp'][:8]:8s} {d_tab.outcome(x):16s} r{x['det']['r']:3d} L{x['det']['len']} at {x['sd']['death']['pos']} "
                      f"sides {x['det']['codes']} {bl} portal {int(x['info']['portal'])} | small for {e['back']} turns; entry: took room {e.get('took_room')} best {e.get('best_room')} pearl {e.get('pearl')} "
                      f"vis {e.get('vis')} | ate in {e['ate_in']} splits in {e['split_in']} | kids {dict(x['info']['kids'])}")


if __name__ == "__main__":
    main()
