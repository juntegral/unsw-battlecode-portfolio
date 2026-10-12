#!/usr/bin/env python3
"""Candidate 1, attack G (backfire). Own code on x_out/c1/.

1. Our WINS in which the rule would have fired (an untaken in-view strict chance, any attacker length): what would
   have been spent, and whether the win survives without that dragon.
2. Untaken chances whose attacker was our longest dragon, or 10+ long, or 13+ (the lengths B's files skip).
3. Chances whose shortest path leaves the attacker's own view (the bot would have to guess cells it cannot see).
4. Does an EARLIER death of her queen help? Round-500 games with both queens dead, by when hers died.
Output: x_out/c1g.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1g.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME) and X.in_study(g, X.side_of(g, X.ME))]


def inview(g, side, maxL=999):
    return [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3
            and c.get("dS") is not None and c["L"] <= maxL]


def endtype(g):
    d = g["d"]
    if d["end"]["rounds"] < 500:
        return "wipe-out"
    qa = d["end"]["qalive"]
    la, lb = d["end"]["st"]["A"][4], d["end"]["st"]["B"][4]
    if qa["A"] != qa["B"] or (qa["A"] and qa["B"] and la != lb):
        return "queen rule"
    return "longest"


P("== 1. Our wins in which the rule would have fired on the FIRST in-view chance (any attacker length)")
wins = [(g, s) for g, s in mine if X.won(g, s)]
n_fire = 0
risk = []
cnt = Counter()
for g, side in wins:
    d = g["d"]
    es = X.other(side)
    ch = inview(g, side)
    if not ch or ch[0]["taken"]:
        continue
    c = ch[0]
    n_fire += 1
    et = endtype(g)
    cnt[et] += 1
    end = d["end"]
    a = c["a"]
    our_tops = end["tops"][side]
    our_long = end["st"][side][2]
    her_long = end["st"][es][2]
    wo = max([L for L, did in our_tops if did != a] or [0])
    qid = d["q"][es]
    her_nonq = max([L for L, did in end["tops"][es] if did != qid] or [0])
    a_alive_end = "a_final" in c
    a_is_final_top = bool(our_tops) and our_tops[0][1] == a
    qd = d["qdeath"].get(es)
    # would the win survive? wipe-out wins: assumed yes. queen-rule wins: yes (our queen is not the attacker).
    # longest wins: needs our longest without the attacker to beat her longest (she is dead by the rule: non-queen best).
    survives = True
    why = ""
    if et == "longest":
        survives = wo > her_nonq
        why = "our longest without it %d vs her best non-queen %d (real margin %d vs %d)" % (wo, her_nonq, our_long, her_long)
    P("   game %d %-15s %-14s %-9s r%-3d attacker %2d long (longer own dragons: %d), her queen %2d; attacker %s; %s -> %s" % (
        g["gid"], g["map"], X.opp(g, side)[1][:14], et, c["r"], c["L"], c["longer"], c["qL"],
        ("alive at end, %d long%s" % (c["a_final"], ", OUR FINAL LONGEST" if a_is_final_top else "")) if a_alive_end
        else "died r%d (%s)" % (c["a_death"][0], c["a_death"][1]),
        why or ("her queen died r%d anyway" % qd["r"] if qd else "her queen lived"),
        "win kept" if survives else "WIN AT RISK"))
    if not survives:
        risk.append(g["gid"])
    cnt["attacker 5+"] += c["L"] >= 5
    cnt["attacker was our longest then"] += c["longer"] == 0
    cnt["attacker alive at end"] += a_alive_end
    cnt["attacker is our final longest"] += a_is_final_top
P("   wins: %d; the rule would have fired in %d: %s; at risk: %d %s" % (len(wins), n_fire, dict(cnt), len(risk), risk))

P("\n== 2. Untaken in-view chances by who the attacker was (all our 401 games, every turn)")
c2 = Counter()
games_long = defaultdict(set)
for g, side in mine:
    for c in inview(g, side):
        if c["taken"]:
            continue
        c2["untaken turns"] += 1
        if c["longer"] == 0:
            c2["attacker = our longest dragon"] += 1
            games_long["longest"].add(g["gid"])
            if c["L"] >= 8:
                c2["attacker = our longest dragon, 8+"] += 1
                games_long["longest8"].add(g["gid"])
        if c["L"] >= 10:
            c2["attacker 10+"] += 1
            games_long["10+"].add(g["gid"])
        if c["L"] >= 13:
            c2["attacker 13+"] += 1
            games_long["13+"].add(g["gid"])
        if c["L"] >= 5 and c["qL"] <= 3:
            c2["attacker 5+ on a queen of 2-3"] += 1
        if c["oq"] == 0:
            c2["own queen already dead"] += 1
        if c["own_h"] < c["en_h"] - 1:
            c2["attacker outnumbered by other enemies in view (2+ enemy heads more, the queen not counted)"] += 1
        paid = c["dS"] - (-(-c["L"] // 4))
        if paid >= 3:
            c2["3 or more paid steps"] += 1
for k, v in c2.most_common():
    P("   %-90s %d" % (k, v))
for k, v in games_long.items():
    res = Counter()
    for g, side in mine:
        if g["gid"] in v:
            res["won" if X.won(g, side) else "lost"] += 1
            res[endtype(g)] += 1
    P("   games with an untaken chance of kind %-9s: %d  %s" % (k, len(v), dict(res)))

P("\n-- first untaken chance per game: what the rule would spend")
seg = 0
n = 0
lens = Counter()
fate = Counter()
for g, side in mine:
    ch = inview(g, side)
    if not ch or ch[0]["taken"]:
        continue
    c = ch[0]
    n += 1
    seg += c["L"]
    lens["2-3" if c["L"] <= 3 else "4" if c["L"] == 4 else "5-9" if c["L"] <= 9 else "10-12" if c["L"] <= 12 else "13+"] += 1
    if "a_final" in c:
        fate["alive at the end"] += 1
        d = g["d"]
        if d["end"]["tops"][side] and d["end"]["tops"][side][0][1] == c["a"]:
            fate["... and our longest dragon at the end"] += 1
    else:
        fate["dead by the end"] += 1
        fate["... died by " + c["a_death"][1]] += 1
        if c["a_death"][0] - c["r"] <= 20:
            fate["... dead within 20 rounds of the chance"] += 1
P("   games %d, segments %d (%.1f a game); attacker length: %s; fate in the real game: %s" % (n, seg, seg / max(1, n), dict(lens), dict(fate)))

P("\n== 3. Chances whose every strict path leaves the attacker's 7x7 view (dV None), by team")
for name, pred in (("meow", lambda g, s: g[s] == X.ME), ("Vibing++", lambda g, s: g[s] == X.VIB), ("SSS", lambda g, s: g[s] == X.SSS),
                   ("forgot", lambda g, s: g[s] == X.FORGOT)):
    n = t = nv = tv = 0
    byL = Counter()
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            for c in inview(g, side):
                n += 1
                t += c["taken"]
                if c["dV"] is None:
                    nv += 1
                    tv += c["taken"]
                    byL["2-4" if c["L"] <= 4 else "5-12" if c["L"] <= 12 else "13+"] += 1
    P("   %-9s in-view chances %d (taken %d); path must leave the view: %d (taken %d) by attacker length %s" % (name, n, t, nv, tv, dict(byL)))

P("\n== 4. Round-500 games in which both queens ended dead: do we win more when HER queen died early?")
for name, pred in (("meow", lambda g, s: g[s] == X.ME), ("top three", lambda g, s: g[s] in X.TOP3)):
    tab = defaultdict(lambda: [0, 0])
    tab2 = defaultdict(lambda: [0, 0])
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            d = g["d"]
            es = X.other(side)
            if d["end"]["rounds"] < 500 or d["end"]["qalive"][side] or d["end"]["qalive"][es]:
                continue
            hr = d["qdeath"][es]["r"]
            orr = d["qdeath"][side]["r"]
            o4, e4 = X.stats_at(d, 400, side), X.stats_at(d, 400, es)
            b = X.band(o4[1] / max(1, e4[1])) if o4 and e4 else None
            k = "her queen died before r100" if hr < 100 else "r100-299" if hr < 300 else "r300+"
            tab[k][0] += X.won(g, side)
            tab[k][1] += 1
            tab2[(b, k)][0] += X.won(g, side)
            tab2[(b, k)][1] += 1
            k2 = "hers died first" if hr < orr else "ours died first"
            tab[k2][0] += X.won(g, side)
            tab[k2][1] += 1
            by = d["qdeath"][es]
            k3 = "hers was rammed by this team" if (by["reason"] == "headon" and by.get("actor_team") == side) else "hers died another way"
            tab[k3][0] += X.won(g, side)
            tab[k3][1] += 1
    P("-- %s: " % name + "; ".join("%s %s" % (k, X.frac(v[0], v[1])) for k, v in tab.items()))
    for b in range(4):
        P("     band at r400 %-7s: " % X.BAND_NAMES[b] + "; ".join(
            "%s %s" % (k, X.frac(tab2[(b, k)][0], tab2[(b, k)][1])) for k in ("her queen died before r100", "r100-299", "r300+")))
out.close()
