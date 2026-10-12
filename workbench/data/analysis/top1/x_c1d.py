#!/usr/bin/env python3
"""Candidate 1, attack D (sample size) and the recount of B's game-level what-if. Own code on x_out/c1/.

1. Our 401 games by what happened at the first in-view chance; the round-500 losses with her queen alive and an
   untaken chance, one line each, with the strict readings (lenient, hard) recomputed from the final board.
2. Where those games sit: by run, map, opponent. Intervals.
3. Take-up by opponent (test4, WeHaveQuizzes, dev test 1, the stronger teams).
4. How often a queen OFFERS an in-view chance, by the team she belongs to and by who is attacking.
Output: x_out/c1d.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1d.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME) and X.in_study(g, X.side_of(g, X.ME))]
P("our games in the study:", len(mine), "won", sum(X.won(g, s) for g, s in mine))


def inview(g, side, maxL=12, key="dS"):
    return [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3
            and c.get(key) is not None and c["L"] <= maxL]


for label, sel in (("meow, all builds", mine), ("meow, live bot", [(g, s) for g, s in mine if X.build(g) == "live"])):
    P("\n== 1. %s (%d games)" % (label, len(sel)))
    cat = Counter()
    flips = []
    later = []
    for g, side in sel:
        d = g["d"]
        es = X.other(side)
        ch = inview(g, side)
        if not ch:
            cat["no in-view chance"] += 1
            continue
        c = ch[0]
        if c["taken"]:
            cat["first chance taken"] += 1
            continue
        qd = d["qdeath"].get(es)
        if qd is not None and qd["r"] == c["r"]:
            cat["not taken, she died in that same round"] += 1
            continue
        if qd is not None:
            cat["not taken, she died later"] += 1
            later.append(qd["r"] - c["r"])
            continue
        end = d["end"]
        if end["rounds"] < 500:
            cat["not taken, she lived: wipe-out " + ("win" if X.won(g, side) else "loss")] += 1
            continue
        if X.won(g, side):
            cat["not taken, she lived: round-500 win"] += 1
            continue
        cat["not taken, she lived: round-500 loss"] += 1
        qid = d["q"][es]
        her_nonq = [L for L, did in end["tops"][es] if did != qid]
        her_best_nonq = her_nonq[0] if her_nonq else 0
        her_q = end["st"][es][4]
        our_q_alive = end["qalive"][side]
        our_long = end["st"][side][2]
        our_tops = end["tops"][side]
        a = c["a"]
        our_long_wo = max([L for L, did in our_tops if did != a] or [0])
        lenient = our_q_alive or our_long > her_best_nonq
        hard = our_q_alive or our_long > max(her_best_nonq, her_q)
        # the "share" reading: her longest becomes max(real non-queen best, share of total) is B's; here a simpler
        # middle reading: her best non-queen dragon gets HALF of the queen's length on top
        mid = our_q_alive or our_long > her_best_nonq + her_q // 2
        ratio300 = None
        o3, e3 = X.stats_at(d, 300, side), X.stats_at(d, 300, es)
        if o3 and e3 and e3[1]:
            ratio300 = o3[1] / e3[1]
        flips.append(dict(gid=g["gid"], map=g["map"], opp=X.opp(g, side)[1], set=g["set"], r=c["r"], L=c["L"], qL=c["qL"],
                          our_long=our_long, her_nonq=her_best_nonq, her_q=her_q, oq=our_q_alive, lenient=lenient,
                          hard=hard, mid=mid, longer=c["longer"], a_dead=("a_death" in c), our_long_wo=our_long_wo,
                          ratio300=ratio300, cells=g["cells"], n_untaken=sum(1 for x in ch if not x["taken"]),
                          ratio_now=c["own"][1] / max(1, c["en"][1]), units=c["own"][0]))
    for k, v in sorted(cat.items(), key=lambda kv: -kv[1]):
        P("   %-48s %d" % (k, v))
    if later:
        P("   she died later: mean %.0f rounds later, median %d" % (sum(later) / len(later), sorted(later)[len(later) // 2]))
    n = len(flips)
    P("   round-500 losses with her alive and an untaken chance: %d; strict lenient %d, middle %d, hard %d" % (
        n, sum(f["lenient"] for f in flips), sum(f["mid"] for f in flips), sum(f["hard"] for f in flips)))
    P("   ... flips that need an attacker of 5+: lenient %d, hard %d; attacker was our longest dragon: %d" % (
        sum(f["lenient"] and f["L"] >= 5 for f in flips), sum(f["hard"] and f["L"] >= 5 for f in flips),
        sum(f["lenient"] and f["longer"] == 0 for f in flips)))
    P("   ... lenient flips that survive taking the attacker out of our final lengths: %d" % sum(
        (f["oq"] or f["our_long_wo"] > f["her_nonq"]) for f in flips if f["lenient"]))
    for key in ("opp", "map", "set"):
        cn = Counter(f[key] for f in flips)
        cl = Counter(f[key] for f in flips if f["lenient"])
        ch_ = Counter(f[key] for f in flips if f["hard"])
        P("   by %-4s: " % key + "; ".join("%s %d (lenient %d, hard %d)" % (k, v, cl[k], ch_[k]) for k, v in cn.most_common()))
    P("   by map size: over 1,200 cells %d (lenient %d, hard %d); smaller %d (lenient %d, hard %d)" % (
        sum(f["cells"] > 1200 for f in flips), sum(f["lenient"] and f["cells"] > 1200 for f in flips),
        sum(f["hard"] and f["cells"] > 1200 for f in flips), sum(f["cells"] <= 1200 for f in flips),
        sum(f["lenient"] and f["cells"] <= 1200 for f in flips), sum(f["hard"] and f["cells"] <= 1200 for f in flips)))
    if label.startswith("meow, all"):
        P("   the games, one line each:")
        P("   %-8s %-16s %-14s %-18s %4s %3s %3s  %-9s %-8s %-6s %-5s %s" % (
            "game", "map", "opponent", "run", "rnd", "L", "qL", "our long", "her best", "her q", "ourQ", "lenient/mid/hard  ratio@300  untaken turns"))
        for f in sorted(flips, key=lambda f: (not f["lenient"], not f["hard"], f["gid"])):
            P("   %-8d %-16s %-14s %-18s %4d %3d %3d  %-9d %-8d %-6d %-5s %s/%s/%s   %s   %d" % (
                f["gid"], f["map"], f["opp"][:14], f["set"], f["r"], f["L"], f["qL"], f["our_long"], f["her_nonq"], f["her_q"],
                "alive" if f["oq"] else "dead", "Y" if f["lenient"] else "-", "Y" if f["mid"] else "-", "Y" if f["hard"] else "-",
                ("%.2f" % f["ratio300"]) if f["ratio300"] else "-", f["n_untaken"]))

P("\n== 2. Intervals (80% Wilson) for the shares the case rests on, our 401 games")
tot = Counter()
for g, side in mine:
    for c in inview(g, side):
        k = "2-3" if c["L"] <= 3 else "4" if c["L"] == 4 else "5-12"
        tot[k, "n"] += 1
        tot[k, "t"] += c["taken"]
        tot["all", "n"] += 1
        tot["all", "t"] += c["taken"]
for k in ("2-3", "4", "5-12", "all"):
    lo, hi = X.wilson(tot[k, "t"], tot[k, "n"])
    P("   attacker %-5s taken %-18s 80%% interval %.0f-%.0f%%" % (k, X.frac(tot[k, "t"], tot[k, "n"]), 100 * lo, 100 * hi))

P("\n== 3. Our take-up by opponent (in-view strict chances, attackers <= 12) and what those games became")
byopp = defaultdict(Counter)
for g, side in mine:
    oid, oname, oelo = X.opp(g, side)
    key = oname if oid in (X.T4, X.WHQ, X.DEV1) else ("top three" if oid in X.TOP3 else "other 2000+ teams")
    d = g["d"]
    es = X.other(side)
    ch = inview(g, side)
    c = byopp[key]
    c["games"] += 1
    c["won"] += X.won(g, side)
    c["has"] += bool(ch)
    c["n"] += len(ch)
    c["t"] += sum(x["taken"] for x in ch)
    c["n23"] += sum(1 for x in ch if x["L"] <= 3)
    c["t23"] += sum(x["taken"] for x in ch if x["L"] <= 3)
    qd = d["qdeath"].get(es)
    c["rammed"] += bool(qd and qd["reason"] == "headon" and qd.get("actor_team") == side)
    c["her_alive_end"] += d["end"]["qalive"][es]
    c["r500loss_her_alive_untaken"] += (d["end"]["rounds"] >= 500 and not X.won(g, side) and d["end"]["qalive"][es]
                                         and bool(ch) and not any(x["taken"] for x in ch))
    c["qrounds"] += (qd["r"] if qd else d["end"]["rounds"])
    c["chance_rounds"] += len({x["r"] for x in ch})
for key, c in sorted(byopp.items(), key=lambda kv: -kv[1]["games"]):
    P("   %-18s games %-4d won %-14s | games with a chance %-14s | chances taken %-16s (2-3-long %-14s) | we rammed her %-14s | her queen alive at end %-14s | r500 losses, her alive, chance untaken: %d | rounds with a chance per 1,000 of her queen-rounds %.1f"
      % (key[:18], c["games"], X.frac(c["won"], c["games"]), X.frac(c["has"], c["games"]), X.frac(c["t"], c["n"]),
         X.frac(c["t23"], c["n23"]), X.frac(c["rammed"], c["games"]), X.frac(c["her_alive_end"], c["games"]),
         c["r500loss_her_alive_untaken"], 1000.0 * c["chance_rounds"] / max(1, c["qrounds"])))

P("\n== 4. How often a queen offers an in-view chance (rounds with at least one in-view strict chance on her, any attacker length, per 1,000 of her queen-rounds), and how often she is rammed (per 1,000)")
P("   rows: the queen's team; columns: who attacks her")
off = defaultdict(Counter)


def grp(tid, elo):
    if tid == X.ME:
        return "meow"
    if tid in X.TOP3:
        return X.NAMES[tid]
    if tid in (X.T4, X.WHQ, X.DEV1):
        return X.NAMES[tid]
    return "other 2000+" if elo >= 2000 else "under 2000"


def agrp(tid, elo):
    if tid == X.ME:
        return "meow"
    if tid in X.TOP3:
        return "top three"
    return "other 2000+" if elo >= 2000 else "under 2000"


for g in gs:
    if g["map"] == "Schooltime":
        continue
    d = g["d"]
    for dside in "AB":  # the defending queen's side
        aside = X.other(dside)
        dkey = grp(g[dside], g[dside + "e"])
        akey = agrp(g[aside], g[aside + "e"])
        qd = d["qdeath"].get(dside)
        c = off[dkey, akey]
        c["games"] += 1
        c["qrounds"] += (qd["r"] if qd else d["end"]["rounds"])
        ch = [x for x in d["chances"] if x["side"] == aside and not x.get("far") and x["cheb"] <= 3 and x.get("dS") is not None]
        c["rounds"] += len({x["r"] for x in ch})
        c["turns"] += len(ch)
        c["taken"] += sum(x["taken"] for x in ch)
        c["rammed"] += bool(qd and qd["reason"] == "headon" and qd.get("actor_team") == aside)
        c["has"] += bool(ch)
dkeys = ["test4", "WeHaveQuizzes", "dev test 1", "other 2000+", "Vibing++", "SSS", "forgot", "meow", "under 2000"]
akeys = ["meow", "top three", "other 2000+"]
for dk in dkeys:
    line = "   %-14s" % dk
    for ak in akeys:
        c = off.get((dk, ak))
        if not c or c["games"] < 3:
            line += " | %-9s: -%s" % (ak, " " * 58)
            continue
        line += " | %-9s: %3d games, %4.1f chance-rounds/1000, rammed %4.1f/1000, games with a chance %3.0f%%" % (
            ak, c["games"], 1000.0 * c["rounds"] / max(1, c["qrounds"]), 1000.0 * c["rammed"] / max(1, c["qrounds"]),
            100.0 * c["has"] / c["games"])
    P(line)
out.close()
