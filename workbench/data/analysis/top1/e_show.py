#!/usr/bin/env python3
"""Print the two leaders' story of one game from e_out/w4/<gid>.json (made by e_walk.py).
Usage: python3 e_show.py <game_id> [from_round=250] [--step N] [--deaths] [--brief]
  per --step rounds (default 25) for both sides: units / total / longest (leader id) / second / third / "potential" (the
  longest plus the pearls every other own dragon would drop if it died now) / the lineage of the final longest; feeders
  that died in the window (deaths by choice within 3 path steps of an own dragon twice as long; for meow also its
  `noaction` deaths) and what the fed dragon got; the leader's place; for meow, when its sonar is readable, what its dragons
  believed. Then handovers and big splits, deaths of dragons of 8+, and a per-50-round feeding summary.
  --deaths lists every death by choice from from_round on (one line each). --brief leaves out the split list."""
import json
import sys

import e_lib as E

RE = ("wall", "self", "body", "headon", "noaction", "other")
CL = ("rammed", "it rammed", "by choice", "boxed", "rammed by own")


def load(gid):
    return json.load(open("%s/e_out/w4/%s.json" % (E.HERE, gid)))


def is_feed(x, DI, me):
    if x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= 3:
        return True
    return me and x[DI["reason"]] == 4 and x[DI["akind"]] == 2


def show(gid, r0=250, step=25, deaths=False, brief=False):
    d = load(gid)
    DI = {k: i for i, k in enumerate(d["dcol"])}
    readable = d["nping"] > 0 and d["badping"] / d["nping"] < 0.05
    print("game %s | %s %dx%d = %d cells | %s | A = %s (%d, elo %d) B = %s (%d, elo %d) | winner %s by %s | meow is %s%s" % (
        gid, d["map"], d["w"], d["h"], d["cells"], d["set"], d["An"], d["A"], d["Ae"], d["Bn"], d["B"], d["Be"], d["winner"], d["end_type"], d["me"],
        "" if not d["me"] else (" (sonar readable)" if readable else " (sonar sealed: no belief data)")))
    for S in "AB":
        s = d["sides"][S]
        me = d["me"] == S
        lin = s["lin"]
        f = s["final"]
        print("\n=== side %s = %s | queen #%d %s | final: %d units, total %d, top %s, potential %d" % (
            S, d[S + "n"], s["queen"], ("died r%d (%s, len %d)" % (s["qdeath"][0], s["qdeath"][1], s["qdeath"][3])) if s["qdeath"] else "alive",
            f["units"], f["total"], [x[0] for x in f["top"][:3]], f["top"][0][0] + f["pot"] if f["top"] else 0))
        if lin:
            print("    final longest #%d (%d long); its lineage was first 8/15/25/40 long at rounds %s; the team's longest of the time first 8/15/25/40: %s" % (
                lin["id"], lin["len"], [lin["first"].get(str(t), "-") for t in (8, 15, 25, 40)], [s["longfirst"].get(str(t), "-") for t in (8, 15, 25, 40)]))
        lead = {row[0]: row for row in s["lead"]}
        bel = {row[0]: row for row in s.get("bel", [])} if (me and readable) else {}
        print("    round units total long(id)     2nd 3rd  pot. | lineage | feeders since last row: n, length -> fed dragon ate | leader at (x,y), nearest enemy head (cells/its length), own heads within 15 (their length), median path distance of the team to it"
              + (" | belief: senders, believe true leader, a dead one, a small one; top id x n; could feed now n (len)" if bel else ""))
        prev = r0 - step
        for row in s["tl"]:
            r = row[0]
            if r < r0 or r % step:
                continue
            i = r // 5
            ll = lin["curve"][i] if lin and i < len(lin["curve"]) else 0
            fd = [x for x in s["deaths"] if prev <= x[0] < r and is_feed(x, DI, me)]
            txt = "%5d %5d %5d %4d(#%-4d) %3d %3d %5d | %4d | %2d, %3d -> %3d" % (
                r, row[1], row[2], row[3], row[4], row[5], row[6], row[3] + row[12], ll, len(fd), sum(x[2] for x in fd),
                sum(x[DI["e_t"]] + x[DI["e_l"]] for x in fd))
            ld = lead.get(r)
            if ld:
                txt += " | (%2d,%2d) %3d/L%-2d  %2d (%3d)  %3d" % (ld[3], ld[4], ld[6], ld[7], ld[21], ld[22], ld[27])
            b = bel.get(r)
            if b:
                txt += " | %2d %2d %2d %2d; #%d x%d (believed %d, true %d); %d (%d)" % (b[1], b[2], b[3], b[13], b[6], b[7], b[8], b[9], b[14], b[15])
            print("    " + txt)
            prev = r
        if lin:
            hs = [h for h in lin["hand"] if h[0] >= r0 - 50]
            print("    lineage handovers (parent -> split child, length before -> child gets):", ", ".join("r%d #%d->#%d %d->%d" % tuple(h) for h in hs))
        if not brief:
            big = [x for x in s["splits"] if x[0] >= r0 and x[3] >= 8]
            print("    splits of dragons of 8+ from r%d: " % r0 + "; ".join(
                "r%d #%d %d->%d+%d%s%s" % (x[0], x[1], x[3], x[4], x[5], " (no free cell)" if x[6] == 0 else "", " LEADER" if x[7] else "") for x in big[:60]))
        print("    deaths of dragons of 8+ from r%d:" % r0)
        for x in s["deaths"]:
            if x[0] >= r0 and x[2] >= 8:
                print("       r%d #%d L%d %s (%s) rank %d at (%d,%d)%s | nearest enemy head %d cells (L%d) | pearls %d: fed dragon / leader %d, other own %d, enemy %d" % (
                    x[0], x[1], x[2], CL[x[DI["cls"]]], RE[x[DI["reason"]]], x[DI["rank"]], x[DI["x"]], x[DI["y"]],
                    (" by #%d L%d in %d steps" % (x[DI["kid"]], x[DI["klen"]], x[DI["ksteps"]])) if x[DI["cls"]] in (0, 4) else
                    (" victim #%d L%d" % (x[DI["kid"]], x[DI["klen"]])) if x[DI["cls"]] == 1 else "",
                    x[DI["emanh"]], x[DI["elen"]], x[DI["drop"]], x[DI["e_t"]] + x[DI["e_l"]], x[DI["e_o"]] + x[DI["e_q"]], x[DI["e_e"]]))
        print("    per 50 rounds: deaths by choice n, length | feeders n, length, pearls dropped -> eaten by the fed dragon / the leader otherwise / other own / enemy / nobody | rammed by the enemy n, length")
        for bin_ in range(r0 // 50, 10):
            v = [x for x in s["deaths"] if x[DI["cls"]] == 2 and x[0] // 50 == bin_]
            nr = [x for x in s["deaths"] if is_feed(x, DI, me) and x[0] // 50 == bin_]
            dr = sum(x[DI["drop"]] for x in nr)
            et, el, eo, ee = (sum(x[DI[k]] for x in nr) for k in ("e_t", "e_l", "e_o", "e_e"))
            eo += sum(x[DI["e_q"]] for x in nr)
            rm = [v2 for k, v2 in s["dagg"].items() if k.split("|")[0] == str(bin_) and k.split("|")[1] == "0"]
            bx = [v2 for k, v2 in s["dagg"].items() if k.split("|")[0] == str(bin_) and k.split("|")[1] == "3"]
            at = [v2 for k, v2 in s["dagg"].items() if k.split("|")[0] == str(bin_) and k.split("|")[1] == "1"]
            nat = s["eats"].get("T|%d|0" % bin_, 0)
            natl = s["eats"].get("L|%d|0" % bin_, 0)
            print("       r%d-%d: %3d, %4d | %3d, %4d, %4d -> %d / %d / %d / %d / %d | %d, %d | boxed in %d, %d | it rammed %d, %d | natural pearls: team %d, leader %d" % (
                bin_ * 50, bin_ * 50 + 49, len(v), sum(x[2] for x in v), len(nr), sum(x[2] for x in nr), dr, et, el, eo, ee, dr - et - el - eo - ee,
                sum(x[0] for x in rm), sum(x[1] for x in rm), sum(x[0] for x in bx), sum(x[1] for x in bx), sum(x[0] for x in at), sum(x[1] for x in at), nat, natl))
        if deaths:
            print("    every feeder / death by choice from r%d: round #id L reason | fed dragon (own >=2x within 8 path steps): id L dist | leader: id L manhattan | enemy cells"
                  + (" | belief the turn before: id L age alive trueL isLeader" if bel else "") + " | pearls: fed/leader/queen/other/enemy")
            for x in s["deaths"]:
                if x[0] >= r0 and (x[DI["cls"]] == 2 or is_feed(x, DI, me)):
                    txt = "       r%d #%d L%d %s%s | #%d L%d d%d | #%d L%d m%d | e%d" % (
                        x[0], x[1], x[2], RE[x[DI["reason"]]], " (boxed)" if x[DI["cls"]] == 3 else "", x[DI["tid"]], x[DI["tlen"]], x[DI["tdist"]],
                        x[DI["lid"]], x[DI["llen"]], x[DI["lmanh"]], x[DI["emanh"]])
                    if bel:
                        txt += " | #%d L%d age %d alive %d true %d lead %d" % (x[DI["bid"]], x[DI["blen"]], x[DI["bage"]], x[DI["balive"]], x[DI["btrue"]], x[DI["blong"]])
                    txt += " | %d: %d/%d/%d/%d/%d" % (x[DI["drop"]], x[DI["e_t"]], x[DI["e_l"]], x[DI["e_q"]], x[DI["e_o"]], x[DI["e_e"]])
                    print(txt)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    step = 25
    if "--step" in sys.argv:
        step = int(sys.argv[sys.argv.index("--step") + 1])
        args.remove(str(step))
    show(args[0], int(args[1]) if len(args) > 1 else 250, step, "--deaths" in sys.argv, "--brief" in sys.argv)
