#!/usr/bin/env python3
"""The pair of candidates 1 and 2: alone and together, game by game on our 401 games. Own code on x_out/c1/ and
x_out/c2/ (pearl-paid reach model). Output: x_out/pair.txt

Candidate 1 event: the first untaken in-view chance on her queen (attacker <= 12) at round r1, and she was alive
                   at the end or died later than r1.
Candidate 2 event: our queen's death was one the candidate touches (ended in a visible reach although a safe step
                   existed; own ram with a free safe cell; boxed in or rammed within 5 rounds of a cut) at round r2.
Readings for a round-500 loss:
  strict       the changed queen states hold to the end. Ours alive / hers dead = win. Both dead: lenient = our
               longest beats her best non-queen dragon; hard = it beats her longest dragon, queen's length included.
               Both alive = no win (our queen is 2-3 long).
  realistic    a saved queen of ours lives to the end with the chance S(r2) of (a) our own queen alive at that
               round, (b) a top-three queen alive at that round; a both-dead game we did not win is won at our own
               rate for both-dead games in that economy band at round 300 (lowest band: 0 of 49 / 4 of 23 by whether
               her queen died before round 300).
"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/pair.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


g1 = {g["gid"]: g for g in X.games("c1") if g["d"]}
g2 = {g["gid"]: g for g in X.games("c2") if g["d"]}
I = 6


def c2_event(g, side):
    d = g["d"]
    qd = d["qdeath"].get(side)
    if qd is None:
        return None
    turn = None
    for t in d["turns"]:
        if t["side"] == side and t["r"] == qd["r"]:
            turn = t
    cut = any(s["side"] == side and s["n_legal"] == 0 and s["keep"] <= 3 and s["child"] > 2 and 0 <= qd["r"] - s["r"] <= 5
              for s in d["splits"])
    if qd.get("own_move"):
        if qd["reason"] == "headon" and turn is not None:
            free = [o for o in turn["opts"] if o[0] == "free"]
            if any(o[I] == 0 for o in free):
                return "ram"
            return None
        if turn is not None and turn["n_legal"] == 0 and cut:
            return "cut"
        return None
    if qd["reason"] != "headon" or qd.get("actor_team") == side:
        return None
    if turn is None or not qd.get("actor_seen"):
        return "cut" if cut else None
    free = [o for o in turn["opts"] if o[0] == "free"]
    safe = [o for o in free if o[I] == 0]
    if safe and turn.get("endp_seen") is not None:
        return "reach"
    return None


def surv_table(pred):
    tab = {}
    for R in range(0, 500, 25):
        a = e = 0
        for g in g2.values():
            if not X.is_csv(g):
                continue
            for side in "AB":
                if not X.in_study(g, side) or not pred(g, side):
                    continue
                d = g["d"]
                qd = d["qdeath"].get(side)
                if d["final"]["rounds"] <= R:
                    continue
                if qd is None or qd["r"] >= R:
                    a += 1
                    e += qd is None
        tab[R] = (e / a) if a else 0.0
    return tab


S_me = surv_table(lambda g, s: g[s] == X.ME)
S_top = surv_table(lambda g, s: g[s] in X.TOP3)


def S(tab, r):
    return tab[min(475, (r // 25) * 25 + 25)]


# our own both-dead win rates by band at round 300 (and timing in the lowest band)
dd = defaultdict(lambda: [0, 0])
for g in g1.values():
    if not X.is_csv(g):
        continue
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side):
        continue
    d = g["d"]
    es = X.other(side)
    e = d["end"]
    if e["rounds"] < 500 or e["qalive"][side] or e["qalive"][es]:
        continue
    o, en = X.stats_at(d, 300, side), X.stats_at(d, 300, es)
    b = X.band(o[1] / max(1, en[1]))
    late = d["qdeath"][es]["r"] >= 300
    key = (b, late) if b == 0 else (b, None)
    dd[key][0] += X.won(g, side)
    dd[key][1] += 1
P("our both-dead win rates used below (band at round 300; lowest band split by whether her queen died from round 300 on):",
  {str(k): "%d of %d" % tuple(v) for k, v in sorted(dd.items(), key=str)})


def dd_rate(b, late):
    v = dd[(b, late) if b == 0 else (b, None)]
    return v[0] / v[1] if v[1] else 0.0


for label, pred in (("meow, all 401 games", lambda g: True), ("meow, live bot (275)", lambda g: X.build(g) == "live")):
    tot = Counter()
    n_both = 0
    rows = []
    for gid, g in g1.items():
        if not X.is_csv(g) or gid not in g2:
            continue
        side = X.side_of(g, X.ME)
        if side is None or not X.in_study(g, side) or not pred(g):
            continue
        d = g["d"]
        es = X.other(side)
        e = d["end"]
        if e["rounds"] < 500 or X.won(g, side):
            continue
        ours, hers = e["qalive"][side], e["qalive"][es]
        # candidate 1 event
        ch = [c for c in d["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3 and c.get("dS") is not None and c["L"] <= 12]
        c1 = bool(ch) and not ch[0]["taken"] and hers
        r1 = ch[0]["r"] if c1 else None
        ev2 = c2_event(g2[gid], side) if not ours else None
        r2 = g2[gid]["d"]["qdeath"][side]["r"] if ev2 else None
        if not c1 and not ev2:
            continue
        qid = d["q"][es]
        her_nonq = max([L for L, did in e["tops"][es] if did != qid] or [0])
        her_q = e["st"][es][4]
        our_long = e["st"][side][2]
        o3, e3 = X.stats_at(d, 300, side), X.stats_at(d, 300, es)
        band = X.band(o3[1] / max(1, e3[1])) if o3 and e3 else 0
        len_l = our_long > her_nonq
        len_h = our_long > max(her_nonq, her_q)

        def strict(k1, k2, hard):
            o = ours or k2
            h = hers and not k1
            if o and not h:
                return 1.0
            if o and h:
                return 0.0
            if not o and h:
                return 0.0
            # both dead: was it already both dead (then it was lost on length: stays lost)?
            if not ours and not hers:
                return 0.0
            return 1.0 if (len_h if hard else len_l) else 0.0

        def real(k1, k2, tab):
            p_o = (S(tab, r2) if k2 else 0.0) if not ours else 1.0
            h_dead = (not hers) or k1
            late = (r1 is not None and r1 >= 300) if (hers and k1) else (d["qdeath"][es]["r"] >= 300 if not hers else False)
            if h_dead:
                # ours alive -> win; ours dead -> both dead: already-lost games stay lost, new both-dead games at our rate
                p_dd = 0.0 if not hers else dd_rate(band, late)
                return p_o * 1.0 + (1 - p_o) * p_dd
            return 0.0  # her queen alive: ours 2-3 long loses on queen length

        for nm, k1, k2 in (("c1", True, False), ("c2", False, True), ("both", True, True)):
            if (k1 and not c1) and (k2 and not ev2):
                continue
            a1, a2 = (k1 and c1), (k2 and bool(ev2))
            tot[nm, "strict lenient"] += strict(a1, a2, False)
            tot[nm, "strict hard"] += strict(a1, a2, True)
            tot[nm, "realistic, our own survival"] += real(a1, a2, S_me)
            tot[nm, "realistic, top-three survival"] += real(a1, a2, S_top)
        n_both += bool(c1 and ev2)
        tot["games with a c1 event"] += c1
        tot["games with a c2 event"] += bool(ev2)
    P("\n== %s: round-500 losses with a candidate-1 event %d, with a candidate-2 event %d, with both %d" % (
        label, tot["games with a c1 event"], tot["games with a c2 event"], n_both))
    for rd in ("strict lenient", "strict hard", "realistic, our own survival", "realistic, top-three survival"):
        a, b, c = tot["c1", rd], tot["c2", rd], tot["both", rd]
        P("   %-32s candidate 1 alone %5.1f | candidate 2 alone %5.1f | sum %5.1f | together %5.1f | extra from doing both %+.1f" % (rd, a, b, a + b, c, c - a - b))
out.close()
