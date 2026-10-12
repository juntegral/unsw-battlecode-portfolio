#!/usr/bin/env python3
"""Candidate 1: what does the enemy build when its queen is dead?  (Between the "lenient" and the "hard" strict count.)

The lenient strict count assumes that the pearls her queen ate would not have gone to another dragon; the hard count
assumes all of them would.  Measured here on our opponents in our own games (round-500 games only):
  share = their longest dragon at the end / their total length at round 400
for games in which their queen was alive at the end and for games in which she was dead before round 300, by their
total length at round 400.  Then a third, empirical strict count for the 25 flippable losses: if her queen had died
at our first chance, their longest at the end = max(their best non-queen dragon as it was,
median share of the queen-dead games x their total at round 400); we flip if our longest beats that.
Output: stdout -> h_out/c1enemy.txt
"""
import json
import statistics

rows = json.load(open("h_out/base.json"))
opp = [r for r in rows if "opp_of_meow" in r["groups"] and r["end_type"] != "wipe-out" and r.get("my_tot400")]
print("our opponents in round-500 games:", len(opp))


def desc(xs, label):
    if not xs:
        print(f"  {label}: none")
        return None
    sh = [r["my_fin"]["longest"] / max(1, r["my_tot400"]) for r in xs]
    lon = [r["my_fin"]["longest"] for r in xs]
    print(f"  {label}: n={len(xs):3d}  final longest median {statistics.median(lon):5.1f} mean {sum(lon) / len(lon):5.1f};"
          f" longest at the end / total at round 400: median {statistics.median(sh):.2f}, quartiles {statistics.quantiles(sh, n=4)[0]:.2f}-{statistics.quantiles(sh, n=4)[2]:.2f}")
    return statistics.median(sh)


med = {}
for name, test in (("all", lambda r: True), ("test4", lambda r: r["team"] == 19), ("WeHaveQuizzes", lambda r: r["team"] == 87)):
    print(f"\n{name}")
    sub = [r for r in opp if test(r)]
    alive = [r for r in sub if r["my_fin"]["queen"]]
    dead_early = [r for r in sub if not r["my_fin"]["queen"] and r["my_qd"] and r["my_qd"]["round"] < 300]
    dead_late = [r for r in sub if not r["my_fin"]["queen"] and r["my_qd"] and r["my_qd"]["round"] >= 300]
    desc(alive, "their queen alive at the end")
    m = desc(dead_early, "their queen dead before round 300")
    desc(dead_late, "their queen dead at round 300 or later")
    med[name] = m
    for lo, hi in ((0, 150), (150, 300), (300, 10 ** 6)):
        a = [r for r in alive if lo <= r["my_tot400"] < hi]
        d = [r for r in dead_early if lo <= r["my_tot400"] < hi]
        if a:
            desc(a, f"   total at r400 {lo}-{hi if hi < 10 ** 6 else ''}: queen alive")
        if d:
            desc(d, f"   total at r400 {lo}-{hi if hi < 10 ** 6 else ''}: queen dead before r300")

print("\n== empirical strict count for the 25 flippable losses ==")
mine = {r["gid"]: r for r in rows if "meow" in r["groups"]}
theirs = {r["gid"]: r for r in rows if "opp_of_meow" in r["groups"]}
n = flips = 0
for gid, r in sorted(mine.items()):
    if r["end_type"] == "wipe-out" or r["win"] or not r["op_fin"]["queen"]:
        continue
    if not any(c[9] for c in r["my_ch"]):
        continue
    n += 1
    o = theirs[gid]
    key = "test4" if o["team"] == 19 else "WeHaveQuizzes" if o["team"] == 87 else "all"
    share = med.get(key) or med["all"]
    oq = r["op_fin"]["queen"]
    op_long, op_second = r["op_fin"]["longest"], r["op_second_fin"]
    op_noq = op_second if oq == op_long else op_long
    predicted = max(op_noq, share * (o["my_tot400"] or 0))
    predicted = min(predicted, max(op_long, op_noq))      # never more than what they actually had in one dragon
    flip = bool(r["my_fin"]["queen"]) or r["my_fin"]["longest"] > predicted
    flips += flip
    print(f"  {gid} {r['map']:16s} ours {r['my_fin']['longest']:3d} (queen {r['my_fin']['queen']}) | hers: queen {oq}, best non-queen {op_noq}, total r400 {o['my_tot400']}, "
          f"expected longest without the queen {predicted:5.1f} | {'FLIP' if flip else 'no'}")
print(f"{n} games; flips under the empirical reading: {flips}")
