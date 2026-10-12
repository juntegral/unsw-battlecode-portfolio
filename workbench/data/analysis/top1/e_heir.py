#!/usr/bin/env python3
"""What happens to the heir of a leader cut. A leader cut = the team's longest dragon (8+) splits and keeps 2-3; the
heir is the child. For every cut from round 250 on: does the heir die within the next 1, 3, 10 rounds, how (rammed, it
rammed, by choice, boxed in), and does it cut again within 3 rounds. Per group, small and big maps.
Reads e_out/w4/*.json through e_data. Output: e_out/heir.txt"""
import e_data as D
import e_lib as E

P = D.Out("heir.txt")
CL = ("rammed", "it rammed", "by choice", "boxed in", "own ram")


def main():
    rows = D.rows()
    P("WHAT HAPPENS TO THE HEIR OF A LEADER CUT (cuts from round 250 on; all study games of the group, not only races)")
    P("a leader cut = the team's longest dragon (8+) splits and keeps 2-3; heir = the child that gets the rest")
    P("")
    for big, name in ((False, "SMALL MAPS (<= 1,200 cells)"), (True, "BIG MAPS (> 1,200 cells)")):
        P(name)
        P("%-22s %6s %6s | heir dies within 1 round: n (%%)  how | within 3 rounds | within 10 rounds | heir of 25+: cuts, dies within 1 / 3 rounds, by choice or boxed | heir cuts again within 3 rounds" % ("group", "games", "cuts"))
        agg = {}
        for r in rows:
            if (r.cells > 1200) != big:
                continue
            for g in D.groups(r):
                a = agg.setdefault(g, dict(games=0, cuts=0, d1=0, d3=0, d10=0, how={}, c25=0, d25_1=0, d25_3=0, own25=0, again=0))
                a["games"] += 1
                s = r.s
                DI = {k: i for i, k in enumerate(r.d["dcol"])}
                dead = {}
                for x in s["deaths"]:
                    dead[x[1]] = x
                cuts = [x for x in s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= 250]
                bychild = {}
                for x in s["splits"]:
                    bychild.setdefault(x[1], []).append(x)
                for x in cuts:
                    a["cuts"] += 1
                    child = x[2]
                    dd = dead.get(child)
                    dt = (dd[0] - x[0]) if dd else 999
                    if dt <= 1:
                        a["d1"] += 1
                        k = CL[dd[DI["cls"]]]
                        a["how"][k] = a["how"].get(k, 0) + 1
                    if dt <= 3:
                        a["d3"] += 1
                    if dt <= 10:
                        a["d10"] += 1
                    if x[5] >= 25:
                        a["c25"] += 1
                        if dt <= 1:
                            a["d25_1"] += 1
                        if dt <= 3:
                            a["d25_3"] += 1
                            if dd[DI["cls"]] in (2, 3):
                                a["own25"] += 1
                    if any(y[7] and y[4] <= 3 and 0 <= y[0] - x[0] <= 3 for y in bychild.get(child, [])):
                        a["again"] += 1
        for g in D.ORDER + ("test4 (vs us)", "WHQ (vs us)", "test4 (vs top3)", "WHQ (vs top3)"):
            a = agg.get(g)
            if not a or not a["cuts"]:
                continue
            P("%-22s %6d %6d | %4d (%4.1f%%)  %-44s | %4d (%4.1f%%) | %4d (%4.1f%%) | %4d, %3d / %3d, %3d | %4d (%4.1f%%)" % (
                g, a["games"], a["cuts"], a["d1"], 100.0 * a["d1"] / a["cuts"], ", ".join("%s %d" % kv for kv in sorted(a["how"].items())),
                a["d3"], 100.0 * a["d3"] / a["cuts"], a["d10"], 100.0 * a["d10"] / a["cuts"], a["c25"], a["d25_1"], a["d25_3"], a["own25"],
                a["again"], 100.0 * a["again"] / a["cuts"]))
        P("")
    P.f.close()


main()
