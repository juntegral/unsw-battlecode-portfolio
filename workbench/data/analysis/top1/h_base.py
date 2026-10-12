#!/usr/bin/env python3
"""Base table for hypotheses.md: one row per (game, side) for meow, the three top teams and meow's opponents.

Reads q/<gid>.json (lead's extract.py), q3v2/<gid>.json (extract3.py), games.csv (battle_id = run/build),
d_out/tab-style death kinds are NOT read here (see h_c2.py).
Filter: opponent elo >= 2000, map Schooltime left out.
Writes h_out/base.json: list of dict rows. Usage: python3 h_base.py
"""
import csv
import json
import os

TEAMS = {1119: "meow", 306: "Vibing++", 91: "SSS", 264: "forgot"}
CK = (50, 100, 150, 200, 250, 300, 350, 400, 450)
LIVE_PREFIX = ("dl-",)


def build_of(bid):
    if bid.startswith("dl-"):
        return "live"
    if bid.endswith("-old"):
        return "live"
    return "cand"


def main():
    rows = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
    out = []
    for gid, row in rows.items():
        if row["map"] == "Schooltime":
            continue
        p = f"q/{gid}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        ch = json.load(open(f"q3v2/{gid}.json"))["chances"] if os.path.exists(f"q3v2/{gid}.json") else []
        for s in "AB":
            o = "B" if s == "A" else "A"
            me, op = d["sides"][s], d["sides"][o]
            groups = []
            if me["team"] in TEAMS and (op["elo"] or 0) >= 2000:
                groups.append(TEAMS[me["team"]])
            if op["team"] == 1119 and (me["elo"] or 0) >= 2000:
                groups.append("opp_of_meow")
            if not groups:
                continue
            rounds = d["rounds"]
            rec = dict(gid=int(gid), side=s, groups=groups, team=me["team"], opp=op["name"], opp_team=op["team"],
                       opp_elo=op["elo"], map=d["map"], cells=d["w"] * d["h"], rounds=rounds,
                       win=int(d["winner"] == s), end_type=d["end_type"], battle=row["battle_id"],
                       build=build_of(row["battle_id"]))
            for tag, side in (("my", me), ("op", op)):
                per = side["per"]
                for r in CK:
                    if r < len(per["total"]):
                        rec[f"{tag}_tot{r}"] = per["total"][r]
                        rec[f"{tag}_lon{r}"] = per["longest"][r]
                        rec[f"{tag}_uni{r}"] = per["units"][r]
                        q = per["q"][r]
                        rec[f"{tag}_q{r}"] = q[2] if q else 0
                    else:
                        rec[f"{tag}_tot{r}"] = rec[f"{tag}_lon{r}"] = rec[f"{tag}_uni{r}"] = rec[f"{tag}_q{r}"] = None
                rec[f"{tag}_fin"] = side["final"]
                rec[f"{tag}_second_fin"] = per["second"][-1] if per["second"] else 0
                qd = side["qdeath"]
                if qd:
                    k = qd.get("killer")
                    rec[f"{tag}_qd"] = dict(round=qd["round"], reason=qd["reason"], len=qd["len"],
                                            by_enemy=int(bool(qd["reason"] == "headon" and k and k["team"] != (s if tag == "my" else o))),
                                            klen=k["len"] if k else None, ksteps=k["steps_used"] if k else None)
                else:
                    rec[f"{tag}_qd"] = None
            # chances this side had on the enemy queen / the enemy had on this side's queen
            rec["my_ch"] = [c for c in ch if c[1] == s]
            rec["op_ch"] = [c for c in ch if c[1] == o]
            out.append(rec)
    json.dump(out, open("h_out/base.json", "w"), separators=(",", ":"))
    from collections import Counter
    c = Counter(g for r in out for g in r["groups"])
    print("rows", len(out), dict(c))
    m = [r for r in out if "meow" in r["groups"]]
    print("meow games", len(m), "wins", sum(r["win"] for r in m), "live", sum(r["build"] == "live" for r in m),
          "live wins", sum(r["win"] for r in m if r["build"] == "live"))
    print("battles", dict(Counter(r["battle"] for r in m)))


if __name__ == "__main__":
    main()
