#!/usr/bin/env python3
"""Candidate 2, attack A: my recount of the queen's turns in reach, her deaths by kind, cuts and own rams.
Reads x_out/c2/ (x_c2.py version 2). Output: x_out/c2a.txt

Two reach models side by side:  PEARL = pearl-paid steps count (what the engine allows; A4's model also has it),
PLAIN = pearls ignored (what the bot's existing spread_kill()/queen_margin() compute).
Per queen turn with an enemy head in her view:
  safe step     a free neighbouring cell that no enemy head in her view can reach this round
  start in      the cell she stands on is within such a reach
  ends in       measured on the real board right after her action
  A  start outside, a safe step exists, she ends in reach
  B  start inside,  a safe step exists, she ends in reach
  C  no safe step
Deaths: rammed by an enemy (killer in view at her turn or not; a safe step existed or not), boxed in (no free cell),
own ram, other."""
import sys
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c2a.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c2") if g["d"]]
P("games with data:", len(gs), " version:", Counter(g["d"].get("v", 1) for g in gs))

cols = defaultdict(list)
for g in gs:
    if not X.is_csv(g):
        continue
    for side in "AB":
        team = g[side]
        if not X.in_study(g, side):
            continue
        if team == X.ME:
            cols["meow all"].append((g, side))
            cols["meow live" if X.build(g) == "live" else "meow test"].append((g, side))
            cols["our opponents"].append((g, X.other(side)))
            if X.opp(g, side)[0] in (X.T4, X.WHQ):
                cols["meow vs t4/WHQ"].append((g, side))
            cols["meow >600 cells" if g["cells"] > 600 else "meow <=600 cells"].append((g, side))
        if team in X.TOP3:
            cols[X.NAMES[team]].append((g, side))
            cols["top three"].append((g, side))
            if X.opp(g, side)[0] in (X.T4, X.WHQ):
                cols["top3 vs t4/WHQ"].append((g, side))
order = ["meow all", "meow live", "meow test", "meow vs t4/WHQ", "meow >600 cells", "meow <=600 cells", "our opponents",
         "forgot", "SSS", "Vibing++", "top three", "top3 vs t4/WHQ"]
P("column sizes:", {k: len(cols[k]) for k in order})
W = 15

IDX = {"plain": 2, "pearl": 6}


def classify(t, model):
    """Return (start_in, n_safe, n_roomy_safe, ends_in, own_death)."""
    i = IDX[model]
    free = [o for o in t["opts"] if o[0] == "free"]
    safe = [o for o in free if o[i] == 0]
    roomy = [o for o in safe if o[4] >= 8 and not o[5]]
    start_in = t["start_seen" if model == "plain" else "startp_seen"] is not None
    own_death = bool(t["death"] and t["death"].get("own_move"))
    ends_in = (t.get("end_seen" if model == "plain" else "endp_seen") is not None) if not own_death else None
    return start_in, len(safe), len(roomy), ends_in, own_death


def death_kind(g, side, model):
    d = g["d"]
    qd = d["qdeath"].get(side)
    if qd is None:
        return "alive", None
    turn = None
    for t in d["turns"]:
        if t["side"] == side and t["r"] == qd["r"]:
            turn = t
    if qd.get("own_move"):
        if qd["reason"] == "headon":
            if turn is not None:
                i = IDX[model]
                free = [o for o in turn["opts"] if o[0] == "free"]
                safe = [o for o in free if o[i] == 0]
                return ("own ram, a free safe cell existed" if safe else "own ram, a free cell but none safe" if free else "own ram, boxed in"), turn
            return "own ram, ?", turn
        if turn is not None and turn["n_legal"] == 0:
            return "boxed in (no free cell)", turn
        return "own move into something with a free cell", turn
    if qd["reason"] != "headon":
        return "other", turn
    if qd.get("actor_team") == side:
        return "rammed by a team-mate", turn
    if turn is None or not qd.get("actor_seen"):
        return "rammed: killer not in her view", turn
    start_in, n_safe, n_roomy, ends_in, own = classify(turn, model)
    if n_safe == 0:
        return "rammed: cornered (no safe step)", turn
    if ends_in is False:
        return "rammed on a cell the model called safe", turn
    return ("rammed: stayed in reach, safe step existed" if start_in else "rammed: stepped into reach, safe step existed"), turn


for model in ("pearl", "plain"):
    P("\n" + "=" * 30, "REACH MODEL:", model.upper(), "=" * 30)
    P("\n== 1. Turns with an enemy head in view")
    P("%-62s" % "" + "".join("%-*s" % (W, k[:W - 1]) for k in order))
    stat = {k: Counter() for k in order}
    for k in order:
        c = stat[k]
        for g, side in cols[k]:
            d = g["d"]
            c["qrounds"] += d["qrounds"][side]
            c["view"] += d["view_rounds"][side]
            for t in d["turns"]:
                if t["side"] != side or t["seen"] == 0:
                    continue
                start_in, n_safe, n_roomy, ends_in, own = classify(t, model)
                rammed = bool(t["death"] and not t["death"].get("own_move") and t["death"]["reason"] == "headon"
                              and t["death"].get("actor_team") != side)
                c["turns"] += 1
                if own:
                    c["own death on the turn"] += 1
                    continue
                if n_safe > 0 and not start_in:
                    c["A_n"] += 1
                    c["A"] += bool(ends_in)
                if n_safe > 0 and start_in:
                    c["B_n"] += 1
                    c["B"] += bool(ends_in)
                if n_safe == 0:
                    c["C"] += 1
                if ends_in:
                    c["ends_in"] += 1
                    c["ends_in_rammed"] += rammed
                    if n_safe > 0:
                        c["choice"] += 1
                        c["choice_rammed"] += rammed
                        c["choice_ate"] += t["ate"] > 0
                        c["choice_split"] += t["kind"] == 1
                        c["choice_roomy"] += n_roomy > 0

    def row(label, f):
        P("%-62s" % label + "".join("%-*s" % (W, f(stat[k])) for k in order))

    row("share of her rounds with an enemy head in view", lambda c: X.pct(c["view"], c["qrounds"], 1))
    row("A. outside reach, safe step exists: ends in reach", lambda c: "%s" % X.pct(c["A"], c["A_n"], 2))
    row("A. per 1,000 queen-rounds", lambda c: "%.2f" % (1000.0 * c["A"] / max(1, c["qrounds"])))
    row("B. inside reach, safe step exists: ends in reach again", lambda c: "%s" % X.pct(c["B"], c["B_n"], 0))
    row("B. per 1,000 queen-rounds", lambda c: "%.2f" % (1000.0 * c["B"] / max(1, c["qrounds"])))
    row("C. no safe step, per 1,000 queen-rounds", lambda c: "%.2f" % (1000.0 * c["C"] / max(1, c["qrounds"])))
    row("all turns that end in reach, per 1,000", lambda c: "%.2f" % (1000.0 * c["ends_in"] / max(1, c["qrounds"])))
    row("... by her own choice (A + B), per 1,000", lambda c: "%.2f" % (1000.0 * c["choice"] / max(1, c["qrounds"])))
    row("... by choice: number of turns", lambda c: c["choice"])
    row("... by choice: a roomy safe step existed", lambda c: c["choice_roomy"])
    row("... by choice: she ate a pearl / it was a split", lambda c: "%d / %d" % (c["choice_ate"], c["choice_split"]))
    row("a turn that ends in reach is punished by a ram that round", lambda c: X.pct(c["ends_in_rammed"], c["ends_in"]))
    row("... by choice, punished", lambda c: "%d of %d" % (c["choice_rammed"], c["choice"]))

    P("\n== 2. How each queen ended (games)")
    kinds = {k: Counter() for k in order}
    for k in order:
        for g, side in cols[k]:
            kd, turn = death_kind(g, side, model)
            kinds[k][kd] += 1
            kinds[k]["n"] += 1
            kinds[k]["qrounds"] += g["d"]["qrounds"][side]
    allk = sorted({kd for k in order for kd in kinds[k] if kd not in ("n", "qrounds")}, key=lambda s: -kinds["meow all"][s])
    P("%-48s" % "" + "".join("%-*s" % (W, k[:W - 1]) for k in order))
    for kd in allk:
        P("%-48s" % kd + "".join("%-*s" % (W, "%d (%.0f%%)" % (kinds[k][kd], 100.0 * kinds[k][kd] / max(1, kinds[k]["n"]))) for k in order))
    P("%-48s" % "all deaths per 1,000 queen-rounds" + "".join(
        "%-*s" % (W, "%.1f" % (1000.0 * (kinds[k]["n"] - kinds[k]["alive"]) / max(1, kinds[k]["qrounds"]))) for k in order))
    avoid = ("rammed: stayed in reach, safe step existed", "rammed: stepped into reach, safe step existed")
    P("%-48s" % "avoidable rams (the two kinds), games" + "".join(
        "%-*s" % (W, "%d of %d" % (sum(kinds[k][a] for a in avoid), kinds[k]["n"])) for k in order))

P("\n== 3. Splits of a queen with no free cell (boxed in), by her length; cut = she keeps 2-3 and gives more than 2, shed = the child gets 2")
P("%-48s" % "" + "".join("%-*s" % (W, k[:W - 1]) for k in order))
sp = {k: Counter() for k in order}
for k in order:
    for g, side in cols[k]:
        for s in g["d"]["splits"]:
            if s["side"] != side:
                continue
            boxed = s["n_legal"] == 0
            big = s["L"] >= 6
            kind = "cut" if s["keep"] <= 3 and s["child"] > 2 else "shed" if s["child"] == 2 else "other"
            sp[k][("boxed" if boxed else "free", "6+" if big else "4-5", kind)] += 1
for key in sorted({kk for k in order for kk in sp[k]}):
    P("%-48s" % ("%s, length %s: %s" % key) + "".join("%-*s" % (W, sp[k][key]) for k in order))
out.close()
