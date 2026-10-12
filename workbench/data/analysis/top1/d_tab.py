#!/usr/bin/env python3
"""d_tab.py: classification of every queen death (sub-session A4, question a).  Reads d_out/cls/*.json and games.csv.

  python3 d_tab.py            tables -> stdout (kept in d_out/tab.txt)
  python3 d_tab.py list WHO   one line per queen of group WHO (meow, opp, forgot, SSS, Vibing++) -> stdout

Groups: meow (all 401 games), meow live (ladder downloads and the "-old" halves of the smoke pairs), one group per
candidate run, opp = the 2000+ opponent's queen in meow's games, forgot / SSS / Vibing++ = their games against 2000+
teams.  Schooltime is left out everywhere.

Kinds (decided from the board at the start of the queen's LAST OWN TURN, see d_class.py for the reach model):
  alive
  boxed: ...            she died by her own order with no free cell next to her head.  Sub-kind by what stood on the
                        sides that were not kelp and not her own body:
      terrain dead end  her head stood on a "tree cell" (dead-end corridor or nook of the kelp/portal map)
      ally body         only team-mates' bodies (the list says whether it was her own split child)
      enemy body        only enemy bodies;   ally+enemy = both
      own body          nothing but kelp and her own body, on terrain that is not a dead end
  crash: portal         she had a free cell, stepped through a portal and hit a body there
  crash: stride         she had a free cell and hit something on the 2nd or later step of a multi-step move
  crash: other          she had a free cell and still stepped into kelp or a body with a one-step move
  no action             she had a free cell and died with reason noaction (no order, suicide order, illegal order)
  own ram               she moved her head into a head (enemy or ally)
  ally ram              a team-mate moved its head into hers
  ram: unseen           rammed by an enemy whose head was NOT in her view at the start of her last turn
                        (or that was born by a split after her turn)
  ram: stepped in       killer in view; at the start of her last turn she was outside the reach of every visible enemy
                        head, a step that stayed outside existed, and she ended her move inside reach
  ram: stayed in        killer in view; she began her last turn inside the reach of a visible enemy head, a step out of
                        reach existed, and she ended her move inside reach
  ram: cornered         killer in view; none of her one-step moves ended outside the reach of every visible enemy head
  ram: model miss       killer in view; she ended on a cell my reach model calls safe and was rammed anyway
"""
import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
CAND = {"stride-new": "cand stride", "passage2-test-new": "cand passage2", "qh31-test-new": "cand qh31",
        "tc30-test-new": "cand tc30", "tc30-dev1b-new": "cand tc30"}
ORDER = ["alive", "ram: unseen", "ram: stepped in", "ram: stayed in", "ram: cornered", "ram: model miss",
         "boxed: terrain dead end", "boxed: ally body", "boxed: ally+enemy", "boxed: enemy body", "boxed: own body",
         "crash: portal", "crash: stride", "crash: other", "no action", "own ram", "ally ram"]


def band(r):
    return "0-49" if r < 50 else "50-99" if r < 100 else "100-299" if r < 300 else "300+"


def classify(sd):
    """-> (kind, detail dict) for one side record of d_out/cls."""
    d = sd["death"]
    if d is None:
        return "alive", {}
    turns = sd["turns"]
    T = turns[-1] if turns else None
    det = dict(r=d["round"], len=d["len"], T=T)
    if d["own"]:
        if d["reason"] == "headon":
            hit = d.get("hit") or ["?"]
            det["hit"] = hit
            det["sub"] = "enemy head" if hit[0] == "E" else "ally head"
            return "own ram", det
        nfree = T["nfree"] if T and T["r"] == d["round"] else None
        det["nfree"] = nfree
        if nfree == 0:
            codes = [x[0] for x in T["sides"]]
            ally = any(c in "aA" for c in codes)
            enemy = any(c in "eE" for c in codes)
            det["blockers"] = [x for x in T["sides"] if x[0] in "aAeE"]
            det["codes"] = "".join(sorted(codes))
            if T["tree"]:
                return "boxed: terrain dead end", det
            if ally and enemy:
                return "boxed: ally+enemy", det
            if ally:
                return "boxed: ally body", det
            if enemy:
                return "boxed: enemy body", det
            return "boxed: own body", det
        if d["reason"] == "noaction":
            det["act"] = d.get("act")
            return "no action", det
        det["hit"] = d.get("hit")
        if d.get("portal"):
            return "crash: portal", det
        if d.get("step", 1) >= 2:
            return "crash: stride", det
        return "crash: other", det
    k = d.get("killer")
    if d["reason"] != "headon" or k is None:
        return "crash: other", det
    det["k"] = k
    side_team = None
    if T is None:
        return "ram: unseen", det
    # ally ram?
    if T.get("fate") == "ally":
        return "ally ram", det
    seen = k["seen_last"]
    det["seen"] = seen
    if not seen:
        det["nvis"] = T["nvis"]
        return "ram: unseen", det
    if T["kind"] != 0 or T["end"] is None:
        # she split (or gave no move) with the killer in view: she stayed where she was
        det["split"] = 1
    if T["nsafe"] == 0:
        return "ram: cornered", det
    if T.get("end_reach", 0) == 0:
        return "ram: model miss", det
    if T["reach0"] == 0:
        return "ram: stepped in", det
    return "ram: stayed in", det


def story(sd):
    """How a boxed-in queen got there, from her last turns: (code string, entry index, detail)."""
    turns = sd["turns"]
    n = len(turns)
    i = n - 1
    while i > 0 and turns[i - 1].get("froom", 99) < 12:
        i -= 1
    j = n - 1
    while j > 0 and turns[j - 1].get("tree", 0):
        j -= 1
    lo = max(0, min(i, j) - 2)
    ate = sum(t["ate"] for t in turns[lo:])
    split = [t["split"] for t in turns[lo:] if "split" in t]
    vis = any(t["nvis"] > 0 for t in turns[lo:])
    near = any(t.get("reach0_all", 0) > 0 for t in turns[lo:])
    code = ("P" if ate else "") + ("S" if split else "") + ("E" if vis else "") or "-"
    return code, n - 1 - i, n - 1 - j, dict(ate=ate, split=split, vis=vis, near=near)


def load():
    games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "d_out", "cls", "*.json"))):
        d = json.load(open(f))
        g = games[str(d["game_id"])]
        for s in "AB":
            o = "B" if s == "A" else "A"
            team, opp = g[f"team{s}Id"], g[f"team{o}Id"]
            elo_o = float(g[f"team{o}Elo"] or 0)
            elo_s = float(g[f"team{s}Elo"] or 0)
            groups = []
            if team in TOP and elo_o >= 2000:
                groups.append(TOP[team])
                groups.append("top three")
                if opp in ("19", "87"):
                    groups.append("top three vs test4/WHQ")
            if team == "1119" and opp in ("19", "87"):
                groups.append("meow vs test4/WHQ")
                if g["battle_id"] in LIVE:
                    groups.append("meow live vs test4/WHQ")
            if team == "1119" and elo_o >= 2000:
                groups.append("meow")
                groups.append("meow live" if g["battle_id"] in LIVE else CAND.get(g["battle_id"], "meow other"))
                groups.append("run " + g["battle_id"])
            if opp == "1119" and elo_s >= 2000:
                groups.append("opp")
            if not groups:
                continue
            sd = d["sides"][s]
            kind, det = classify(sd)
            won = g["winner"] == s
            oq_alive = int(g[f"final_queen_length_{o}"] or 0) > 0
            out.append(dict(gid=str(d["game_id"]), side=s, groups=groups, map=g["map"], cells=int(g["cells"]),
                            run=g["battle_id"], opp=g[f"team{o}Name"], won=won, end=g["end_type"], rounds=int(g["rounds"]),
                            oq_alive=oq_alive, kind=kind, det=det, sd=sd, g=g))
    return out


def outcome(x):
    if x["end"] == "wipe-out":
        return "wipe W" if x["won"] else "wipe L"
    oq = "her alive" if x["oq_alive"] else "her dead"
    return f"r500 {'W' if x['won'] else 'L'} {oq}"


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def main():
    recs = load()
    by = defaultdict(list)
    for x in recs:
        for grp in x["groups"]:
            by[grp].append(x)
    cols = ["meow", "meow live", "cand stride", "cand passage2", "cand qh31", "cand tc30", "opp", "forgot", "SSS", "Vibing++"]
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        who = sys.argv[2]
        for x in sorted(by[who], key=lambda x: (x["kind"], x["map"], x["det"].get("r", 0))):
            d = x["det"]
            extra = ""
            if x["kind"].startswith("ram"):
                k = d["k"]
                T = d["T"]
                extra = (f"killer #{k['id']} L{k['len']} {k['steps']}st from {k['start']} born {k['born']} seen3 {k['seen_last3']} | last turn r{T['r']} "
                         f"{'move ' + T['dirs'] if T['kind'] == 0 else 'SPLIT' if T['kind'] == 1 else 'none'} free {T['nfree']} safe {T['nsafe']} paid-safe {T['nsafe_paid']} "
                         f"vis {T['nvis']} reach0 {T['reach0']} end_reach {T.get('end_reach')} ate {T['ate']} a3 {T['a3']}")
            elif x["kind"].startswith("boxed"):
                code, i, j, st = story(x["sd"])
                bl = [f"{b[0]}#{b[4]}L{b[5]}s{b[6]}" for b in d["blockers"]]
                extra = f"sides {d['codes']} blockers {bl} story {code} small-region for {i} turns, tree for {j}; ate {st['ate']} split {st['split']}"
            elif x["kind"] != "alive":
                extra = f"hit {d.get('hit')} act {d.get('act')} nfree {d.get('nfree')} step {x['sd']['death'].get('step')}/{x['sd']['death'].get('nsteps')} dir {x['sd']['death'].get('dir')}"
            print(f"{x['kind']:24s} | {x['gid']} {x['side']} | {x['map'][:15]:15s} {x['cells']:4d} | {x['run'][:17]:17s} | vs {x['opp'][:10]:10s} | {outcome(x):16s} | "
                  f"r{d.get('r', 0):3d} L{d.get('len', 0)} at {x['sd']['death']['pos'] if x['sd']['death'] else '-'} | {extra}")
        return

    print("=== 1. kind of queen death, count and share of games, by group")
    print("kind | " + " | ".join(cols))
    for k in ORDER:
        row = []
        for c in cols:
            n = len(by[c])
            v = sum(1 for x in by[c] if x["kind"] == k)
            row.append(f"{v} ({pct(v, n)})")
        print(f"{k} | " + " | ".join(row))
    print("games | " + " | ".join(str(len(by[c])) for c in cols))
    fam = lambda k: "alive" if k == "alive" else "rammed" if k.startswith("ram") else "boxed" if k.startswith("boxed") else "own crash / ram / no action"
    print("\nfamilies:")
    for f in ("alive", "rammed", "boxed", "own crash / ram / no action"):
        print(f"{f} | " + " | ".join(f"{sum(1 for x in by[c] if fam(x['kind']) == f)} ({pct(sum(1 for x in by[c] if fam(x['kind']) == f), len(by[c]))})" for c in cols))

    print("\n=== 1b. the same, live bot by run")
    runs = sorted({g for x in recs for g in x["groups"] if g.startswith("run ")})
    print("kind | " + " | ".join(r[4:] for r in runs))
    for k in ORDER:
        print(f"{k} | " + " | ".join(str(sum(1 for x in by[r] if x["kind"] == k)) for r in runs))
    print("games | " + " | ".join(str(len(by[r])) for r in runs))

    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        print(f"\n=== 2. {grp}: kind by round band (0-49 / 50-99 / 100-299 / 300+), games {len(by[grp])}")
        for k in ORDER[1:]:
            c = Counter(band(x["det"]["r"]) for x in by[grp] if x["kind"] == k)
            if sum(c.values()):
                print(f"  {k:24s} {sum(c.values()):4d} | " + " / ".join(str(c[b]) for b in ("0-49", "50-99", "100-299", "300+")))
        tot = Counter(band(x["det"]["r"]) for x in by[grp] if x["kind"] != "alive")
        print(f"  {'all deaths':24s} {sum(tot.values()):4d} | " + " / ".join(str(tot[b]) for b in ("0-49", "50-99", "100-299", "300+")))

    print("\n=== 3. meow: kind by queen rules (map over 600 cells = rules on), all runs and live bot")
    for grp in ("meow", "meow live"):
        on = [x for x in by[grp] if x["cells"] > 600]
        off = [x for x in by[grp] if x["cells"] <= 600]
        print(f"  {grp}: rules on {len(on)} games, off {len(off)} games")
        for k in ORDER:
            a, b = sum(1 for x in on if x["kind"] == k), sum(1 for x in off if x["kind"] == k)
            if a + b:
                print(f"    {k:24s} on {a:3d} ({pct(a, len(on))})  off {b:3d} ({pct(b, len(off))})")
    print("  by map size class (600 or fewer / 601-1500 / over 1500), meow all runs:")
    for k in ORDER:
        v = [sum(1 for x in by["meow"] if x["kind"] == k and lo < x["cells"] <= hi) for lo, hi in ((0, 600), (600, 1500), (1500, 99999))]
        if sum(v):
            print(f"    {k:24s} {v[0]:3d} / {v[1]:3d} / {v[2]:3d}")

    print("\n=== 4. her length at death, the killer's length and steps (rammed kinds)")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        print(f"  {grp}")
        for k in ORDER[1:]:
            xs = [x for x in by[grp] if x["kind"] == k]
            if not xs:
                continue
            ql = Counter(min(x["det"]["len"], 6) for x in xs)
            line = f"    {k:24s} n={len(xs):3d} her length 2/3/4/5/6+: " + "/".join(str(ql[i]) for i in range(2, 7))
            if k.startswith("ram"):
                kl = Counter("2" if x["det"]["k"]["len"] <= 2 else "3" if x["det"]["k"]["len"] == 3 else "4" if x["det"]["k"]["len"] == 4 else "5-9" if x["det"]["k"]["len"] <= 9 else "10+" for x in xs)
                ks = Counter(min(x["det"]["k"]["steps"], 5) for x in xs)
                born = sum(x["det"]["k"]["born"] for x in xs)
                line += " | killer length 2/3/4/5-9/10+: " + "/".join(str(kl[i]) for i in ("2", "3", "4", "5-9", "10+"))
                line += " | killer steps 1/2/3/4/5+: " + "/".join(str(ks[i]) for i in range(1, 6)) + f" | killer born that round {born}"
            print(line)

    print("\n=== 5. what the game became, by kind (wipe W / wipe L / r500 W her dead / r500 W her alive / r500 L her dead / r500 L her alive)")
    keys = ("wipe W", "wipe L", "r500 W her dead", "r500 W her alive", "r500 L her dead", "r500 L her alive")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        print(f"  {grp}")
        for k in ORDER:
            xs = [x for x in by[grp] if x["kind"] == k]
            if not xs:
                continue
            c = Counter(outcome(x) for x in xs)
            print(f"    {k:24s} n={len(xs):3d} | " + " / ".join(str(c[q]) for q in keys))

    print("\n=== 6. boxed-in deaths: what stood around her, and how she got there (P ate in the last turns, S split, E enemy head in view)")
    for grp in ("meow", "meow live", "opp", "forgot", "SSS", "Vibing++"):
        xs = [x for x in by[grp] if x["kind"].startswith("boxed")]
        if not xs:
            continue
        print(f"  {grp}: {len(xs)} boxed-in deaths")
        st = Counter()
        child = Counter()
        for x in xs:
            code, i, j, det = story(x["sd"])
            st[(x["kind"], code)] += 1
            # was a blocking team-mate her own split child?
            kids = set()
            for t in x["sd"]["turns"]:
                if "split" in t:
                    kids.add(t["split"][3])
            bl = x["det"]["blockers"]
            if any(b[0] in "aA" for b in bl):
                child[(x["kind"], "own recent child" if any(b[0] in "aA" and b[4] in kids for b in bl) else "other team-mate")] += 1
        for (k, code), v in sorted(st.items()):
            print(f"    {k:24s} story {code:4s} {v}")
        for (k, w), v in sorted(child.items()):
            print(f"    {k:24s} blocking team-mate: {w} {v}")
        print("    her length:", dict(sorted(Counter(x["det"]["len"] for x in xs).items())))

    print("\n=== 7. per map, meow (all runs): kinds")
    maps = sorted({x["map"] for x in by["meow"]}, key=lambda m: min(x["cells"] for x in by["meow"] if x["map"] == m))
    for m in maps:
        xs = [x for x in by["meow"] if x["map"] == m]
        c = Counter(x["kind"] for x in xs)
        print(f"  {m:18s} {xs[0]['cells']:4d} n={len(xs):2d} | " + ", ".join(f"{k} {c[k]}" for k in ORDER if c[k]))
    for grp in ("opp", "top three"):
        print(f"  --- {grp}")
        for m in maps:
            xs = [x for x in by[grp] if x["map"] == m]
            c = Counter(x["kind"] for x in xs)
            print(f"  {m:18s} n={len(xs):3d} | " + ", ".join(f"{k} {c[k]}" for k in ORDER if c[k]))


if __name__ == "__main__":
    main()
