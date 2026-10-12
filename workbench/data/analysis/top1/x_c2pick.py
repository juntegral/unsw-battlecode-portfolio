#!/usr/bin/env python3
"""Pick queen turns of ours to look at by eye for candidate 2 (from x_out/c2/, pearl-paid reach model):
fatal turns on which a safe step existed (stepped in / stayed in), turns the plain model calls safe but the pearl
model does not, cuts of a boxed-in queen, own rams with a free safe cell. Output: x_out/c2_eye.json"""
import json
import random

import x_load as X

random.seed(5)
I = 6
gs = [g for g in X.games("c2") if g["d"] and X.is_csv(g)]
picks = {"stepped": [], "stayed": [], "pearl_only": [], "cut": [], "ownram": [], "cornered": []}
for g in gs:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side):
        continue
    d = g["d"]
    qid = d["q"][side]
    qd = d["qdeath"].get(side)
    for t in d["turns"]:
        if t["side"] != side:
            continue
        free = [o for o in t["opts"] if o[0] == "free"]
        safe = [o for o in free if o[I] == 0]
        safe_plain = [o for o in free if o[2] == 0]
        dth = t["death"]
        if dth and not dth.get("own_move") and dth["reason"] == "headon" and dth.get("actor_team") != side and dth.get("actor_seen"):
            opts = " ".join("%s:%s" % ("NESW"[i], ("free%s thr%d room%d" % ("*" if o[1] else "", o[I], o[4])) if o[0] == "free" else o[0])
                            for i, o in enumerate(t["opts"]))
            note = "queen L%d moved %s; options %s; killer #%s L%s" % (t["L"], "".join("NESW"[x] for x in t["dirs"]) or "split", opts,
                                                                       dth["actor"], dth.get("actor_L"))
            if safe:
                key = "stayed" if t["startp_seen"] is not None else "stepped"
                picks[key].append([g["gid"], t["r"], qid, "C2 %s into reach, safe step existed: %s" % (key, note)])
            else:
                if safe_plain:
                    picks["pearl_only"].append([g["gid"], t["r"], qid, "C2 cornered only when pearl-paid steps count (the plain model sees a safe step): " + note])
                else:
                    picks["cornered"].append([g["gid"], t["r"], qid, "C2 cornered: " + note])
        if dth and dth.get("own_move") and dth["reason"] == "headon" and safe:
            picks["ownram"].append([g["gid"], t["r"], qid, "C2 own ram with a free safe cell, queen L%d" % t["L"]])
    for s in d["splits"]:
        if s["side"] == side and s["n_legal"] == 0 and s["L"] >= 6 and s["keep"] <= 3 and s["child"] > 2:
            picks["cut"].append([g["gid"], s["r"], qid, "C2 cut: boxed-in queen L%d keeps %d, child gets %d" % (s["L"], s["keep"], s["child"])])
out = []
for key, n in (("stepped", 7), ("stayed", 3), ("pearl_only", 3), ("cornered", 2), ("cut", 2), ("ownram", 2)):
    v = picks[key]
    random.shuffle(v)
    out += v[:n]
    print(key, len(v))
json.dump(out, open("x_out/c2_eye.json", "w"))
print(len(out), "picked")
