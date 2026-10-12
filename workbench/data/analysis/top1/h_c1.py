#!/usr/bin/env python3
"""Candidate 1 ("take the queen"): counts and what-ifs from h_out/base.json.  Output: stdout -> h_out/c1.txt

A chance = a turn of a non-queen dragon (12 or shorter) that starts with a free path to the enemy queen's head no
longer than its reach; in view = her head inside the dragon's 7x7 square (lead's extract3.py, q3v2/).
Chance record: [round, side, id, length, steps, taken, her_length, is_longest, own_queen_alive, in_view].

A. Take-up of in-view chances: by group, attacker length, round band, own queen alive or dead, attacker = own longest.
B. Games: with an in-view chance / with a kill / chance but never a kill; how each kind of game ended.
C. What-if for meow (all 401 and live 275): the enemy queen dies on our first untaken in-view chance.
   Rule variants: any length (the candidate), 4 or shorter (the qh31 trial's hunters), 2-3 only.
   Readings: strict-lenient, strict-hard, strict minus "the rammer was our longest", realistic at our own rates.
D. Possible damage: round-500 wins in which the rule would have spent our longest dragon.
E. Vibing++ / SSS / forgot: win rate of games with and without a kill of the enemy queen (wins against losses).
"""
import json
from collections import Counter, defaultdict

rows = json.load(open("h_out/base.json"))
TOP = ("Vibing++", "SSS", "forgot")


def groups(r):
    g = list(r["groups"])
    if "meow" in g:
        g.append("meow live" if r["build"] == "live" else "meow cand")
        if r["battle"] == "qh31-test-new":
            g.append("meow qh31 build")
        if r["battle"] == "qh31-test-old":
            g.append("meow live, qh31 pair")
    if any(t in g for t in TOP):
        g.append("top3")
    return g


def lclass(n):
    return "2-3" if n <= 3 else "4" if n == 4 else "5-9" if n <= 9 else "10-12"


def rband(r):
    return "r0-99" if r < 100 else "r100-299" if r < 300 else "r300+"


ORDER = ["meow", "meow live", "meow cand", "meow qh31 build", "meow live, qh31 pair", "opp_of_meow", "Vibing++", "SSS", "forgot", "top3"]

print("== A. In-view chances on the enemy queen: taken / all ==")
tab = defaultdict(lambda: [0, 0])
for r in rows:
    for c in r["my_ch"]:
        if not c[9]:
            continue
        for g in groups(r):
            for key in (("len", lclass(c[3])), ("round", rband(c[0])), ("ownq", "own queen alive" if c[8] else "own queen dead"),
                        ("longest", "attacker is own longest" if c[7] else "attacker not own longest"), ("all", "all"),
                        ("paid", min(3, max(0, c[4] - (-(-c[3] // 4)))))):
                tab[(g, key)][0] += 1
                tab[(g, key)][1] += c[5]
for sec, keys in (("by attacker length", [("len", k) for k in ("2-3", "4", "5-9", "10-12")]),
                  ("by round", [("round", k) for k in ("r0-99", "r100-299", "r300+")]),
                  ("by own queen", [("ownq", "own queen alive"), ("ownq", "own queen dead")]),
                  ("by attacker role", [("longest", "attacker is own longest"), ("longest", "attacker not own longest")]),
                  ("by paid steps (0, 1, 2, 3+)", [("paid", k) for k in (0, 1, 2, 3)]),
                  ("all", [("all", "all")])):
    print(f"\n-- {sec}: " + " | ".join(str(k[1]) for k in keys))
    for g in ORDER:
        cells = []
        for k in keys:
            n, t = tab[(g, k)]
            cells.append(f"{t}/{n}" + (f" {100 * t / n:.0f}%" if n else ""))
        print(f"   {g:22s} " + " | ".join(f"{c:>14s}" for c in cells))

print("\n== B. Games by chance and kill ==")
for g in ORDER:
    n = Counter()
    res = defaultdict(Counter)
    for r in rows:
        if g not in groups(r):
            continue
        ch = [c for c in r["my_ch"] if c[9]]
        qd = r["op_qd"]
        killed = bool(qd and qd["by_enemy"])
        kind = ("we rammed her" if killed else "in-view chance, never rammed her" if ch else "no in-view chance, her queen dead another way"
                if qd else "no in-view chance, her queen alive at the end")
        n[kind] += 1
        if r["end_type"] == "wipe-out":
            res[kind]["wipe W" if r["win"] else "wipe L"] += 1
        else:
            res[kind][("r500 W" if r["win"] else "r500 L") + (" her alive" if r["op_fin"]["queen"] else " her dead")] += 1
    tot = sum(n.values())
    print(f"\n{g}: {tot} games")
    for kind in ("we rammed her", "in-view chance, never rammed her", "no in-view chance, her queen dead another way",
                 "no in-view chance, her queen alive at the end"):
        w = res[kind]["wipe W"] + sum(v for k, v in res[kind].items() if k.startswith("r500 W"))
        print(f"   {kind:48s} {n[kind]:4d} ({100 * n[kind] / tot:4.1f}%)  won {w:4d} ({100 * w / max(1, n[kind]):.0f}%)  {dict(res[kind])}")

# ---------- C. what-if for meow
print("\n== C. What-if: her queen dies on our first untaken in-view chance (meow) ==")
BANDS = [("<0.67", 0, 0.67), ("0.67-1", 0.67, 1.0), ("1-1.5", 1.0, 1.5), (">1.5", 1.5, 1e9)]


def band(r):
    a, b = r.get("my_tot300"), r.get("op_tot300")
    if a is None or b is None or not b:
        return None
    x = a / b
    for name, lo, hi in BANDS:
        if lo <= x < hi:
            return name


# our own win rate in round-500 games in which both queens ended dead, by band (all 401 games)
dd = defaultdict(lambda: [0, 0])
dd_ram = [0, 0]
for r in rows:
    if "meow" not in r["groups"] or r["end_type"] == "wipe-out":
        continue
    if r["my_fin"]["queen"] == 0 and r["op_fin"]["queen"] == 0:
        dd[band(r)][0] += 1
        dd[band(r)][1] += r["win"]
        dd["all"][0] += 1
        dd["all"][1] += r["win"]
        if r["op_qd"] and r["op_qd"]["by_enemy"]:
            dd_ram[0] += 1
            dd_ram[1] += r["win"]
print("our win rate, round-500 games with both queens dead at the end, by band at round 300: "
      + ", ".join(f"{k}: {v[1]}/{v[0]}" for k, v in dd.items()) + f"; of those in which we rammed her: {dd_ram[1]}/{dd_ram[0]}")


def whatif(scope, maxlen, minlen=2):
    out = Counter()
    games = []
    exp_band = exp_flat = exp_ram = 0.0
    for r in rows:
        gs = groups(r)
        if scope not in gs:
            continue
        ch = sorted((c for c in r["my_ch"] if c[9] and minlen <= c[3] <= maxlen), key=lambda c: c[0])
        if not ch:
            continue
        out["games with such a chance"] += 1
        first = ch[0]
        qd = r["op_qd"]
        if first[5]:
            out["first such chance taken (no change)"] += 1
            continue
        untaken_first = first
        t1 = untaken_first[0]
        if qd and qd["round"] <= t1:
            continue
        # she dies at t1 instead of later / never
        if qd:
            out["she died later anyway (kill only earlier)"] += 1
            out["... rounds earlier, sum"] += qd["round"] - t1
            if qd["by_enemy"]:
                out["... later rammed by us"] += 1
        else:
            out["she was alive at the end (kill gained)"] += 1
        if r["end_type"] == "wipe-out":
            out["  wipe-out " + ("W" if r["win"] else "L") + (" (kill gained)" if not qd else " (earlier)")] += 1
            continue
        if qd:
            out["  round 500, she died later anyway: " + ("W" if r["win"] else "L")] += 1
            # possible damage: a win by longest in which the rule spends our longest dragon
            if r["win"] and untaken_first[7]:
                out["  DAMAGE? round-500 win, first chance was by our longest"] += 1
            continue
        # she was alive at the end, round 500
        if r["win"]:
            out["  round 500 win with her alive (no change)"] += 1
            continue
        out["  round-500 LOSS with her alive: can flip"] += 1
        mq = r["my_fin"]["queen"]
        oq = r["op_fin"]["queen"]
        op_long, op_second = r["op_fin"]["longest"], r["op_second_fin"]
        op_noq = op_second if oq == op_long else op_long
        mine = r["my_fin"]["longest"]
        lenient = bool(mq) or mine > op_noq
        hard = bool(mq) or mine > op_long
        out["    strict, lenient (our longest > her best non-queen dragon)"] += lenient
        out["    strict, hard (our longest > her longest incl. the queen's length)"] += hard
        out["    strict lenient, and the rammer was not our longest then"] += lenient and not untaken_first[7]
        out["    of the lenient flips: our queen alive at the end"] += bool(mq)
        b = band(r)
        p_band = 1.0 if mq else dd[b][1] / dd[b][0]
        p_flat = 1.0 if mq else dd["all"][1] / dd["all"][0]
        p_ram = 1.0 if mq else dd_ram[1] / dd_ram[0]
        exp_band += p_band
        exp_flat += p_flat
        exp_ram += p_ram
        games.append((r["gid"], r["map"], r["opp"][:10], t1, untaken_first[3], untaken_first[4], "longest" if untaken_first[7] else "",
                      f"ours {mine} q{mq} / hers {op_long} q{oq} second {op_second}", "LEN" if lenient else "", "HARD" if hard else "",
                      b, r["build"], r["battle"]))
    n = sum(1 for r in rows if scope in groups(r))
    print(f"\n-- {scope} ({n} games), attackers {minlen}-{maxlen} long")
    for k, v in out.items():
        print(f"   {k}: {v}")
    print(f"   realistic: expected wins among the round-500 losses with her alive: at our own both-dead rate of the band {exp_band:.1f}"
          f" (+{100 * exp_band / n:.1f} points); at our flat both-dead rate {exp_flat:.1f}; at our rate when we did ram her {exp_ram:.1f}")
    return games


for scope in ("meow", "meow live"):
    g_any = whatif(scope, 12)
    g_4 = whatif(scope, 4)
    g_3 = whatif(scope, 3)
    g_long = whatif(scope, 12, 5)
    if scope == "meow":
        print("\n   the round-500 losses with her alive and an untaken in-view chance (any length):")
        for g in sorted(g_any):
            print("     ", *g)

print("\n== E. Top teams: games with and without a ram on the enemy queen ==")
for g in ("Vibing++", "SSS", "forgot", "opp_of_meow", "meow"):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if g not in r["groups"]:
            continue
        qd = r["op_qd"]
        killed = bool(qd and qd["by_enemy"])
        own_dead_before = None
        k = "rammed her queen" if killed else "did not"
        c[k][0] += 1
        c[k][1] += r["win"]
        if killed:
            early = "rammed her before round 150" if qd["round"] < 150 else "rammed her at round 150 or later"
            c[early][0] += 1
            c[early][1] += r["win"]
        # round-500 games with own queen dead at the end
        if r["end_type"] != "wipe-out" and r["my_fin"]["queen"] == 0:
            kk = "r500, own queen dead: " + ("she was rammed by us" if killed else "she died another way" if qd else "she lived")
            c[kk][0] += 1
            c[kk][1] += r["win"]
    print(g, "; ".join(f"{k}: {v[1]}/{v[0]} = {100 * v[1] / v[0]:.0f}%" for k, v in sorted(c.items())))
    # share of wins / losses with a kill
    w = [r for r in rows if g in r["groups"] and r["win"]]
    l = [r for r in rows if g in r["groups"] and not r["win"]]
    kw = sum(1 for r in w if r["op_qd"] and r["op_qd"]["by_enemy"])
    kl = sum(1 for r in l if r["op_qd"] and r["op_qd"]["by_enemy"])
    cw = sum(1 for r in w if any(c[9] for c in r["my_ch"]))
    cl = sum(1 for r in l if any(c[9] for c in r["my_ch"]))
    print(f"    wins with a ram on her queen {kw}/{len(w)} = {100 * kw / len(w):.0f}%, losses {kl}/{len(l)} = {100 * kl / len(l):.0f}%;"
          f" wins with an in-view chance {cw}/{len(w)} = {100 * cw / len(w):.0f}%, losses {cl}/{len(l)} = {100 * cl / len(l):.0f}%")
