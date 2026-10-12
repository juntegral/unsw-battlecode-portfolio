#!/usr/bin/env python3
"""Candidate 3, backfire: our wins on maps over 1,200 cells one by one. Units (the early-feeding rule needs 56 from
round 200), total length and the longest dragon at rounds 150-400 against the enemy's; how much of the final leader
was there at round 300. Own code on x_out/c1/. Output: x_out/c3wins.txt"""
import x_load as X
out = open("x_out/c3wins.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
rows = []
for g in gs:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side) or g["cells"] <= 1200:
        continue
    d = g["d"]; es = X.other(side); e = d["end"]
    st = {R: (X.stats_at(d, R, side), X.stats_at(d, R, es)) for R in (150, 200, 250, 300, 400)}
    if any(v[0] is None for v in st.values()):
        continue
    rows.append(dict(g=g, won=X.won(g, side), st=st, ole=e["st"][side][2], ele=e["st"][es][2], live=X.build(g) == "live",
                     dd=(e["rounds"] >= 500 and not e["qalive"][side] and not e["qalive"][es])))
def med(v):
    v = sorted(v); return v[len(v) // 2] if v else 0
for lab, sel in (("our 12 wins", [r for r in rows if r["won"]]), ("our losses that ended at round 500 with both queens dead", [r for r in rows if not r["won"] and r["dd"]]),
                 ("all our other losses that reached round 400", [r for r in rows if not r["won"] and not r["dd"]])):
    P("\n== %s (%d games), medians" % (lab, len(sel)))
    for R in (150, 200, 250, 300, 400):
        P("   round %d: units %d : %d | total %d : %d | longest %d : %d | games with 56 or more own units: %d | games with the longer leader: %d" % (
            R, med([r["st"][R][0][0] for r in sel]), med([r["st"][R][1][0] for r in sel]), med([r["st"][R][0][1] for r in sel]),
            med([r["st"][R][1][1] for r in sel]), med([r["st"][R][0][2] for r in sel]), med([r["st"][R][1][2] for r in sel]),
            sum(r["st"][R][0][0] >= 56 for r in sel), sum(r["st"][R][0][2] > r["st"][R][1][2] for r in sel)))
    P("   end: longest %d : %d" % (med([r["ole"] for r in sel]), med([r["ele"] for r in sel])))
P("\n== the wins one by one")
for r in rows:
    if not r["won"]:
        continue
    g = r["g"]; st = r["st"]
    P("   %d %-15s %-18s units r200 %d r250 %d | longest r150 %d r300 %d r400 %d end %d vs enemy %d %d %d %d | total r300 %d vs %d | margin at the end %+d | behind in total at r300: %s; longer leader at r300: %s" % (
        g["gid"], g["map"], g["set"], st[200][0][0], st[250][0][0], st[150][0][2], st[300][0][2], st[400][0][2], r["ole"],
        st[150][1][2], st[300][1][2], st[400][1][2], r["ele"], st[300][0][1], st[300][1][1], r["ole"] - r["ele"],
        "yes" if st[300][0][1] < st[300][1][1] else "no", "yes" if st[300][0][2] > st[300][1][2] else "no"))
