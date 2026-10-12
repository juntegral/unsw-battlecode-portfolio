#!/usr/bin/env python3
"""Who is fed to the leader: small feeders or whole dragons? Every death by choice in a race (round-500 game with both
queens dead), rounds 300-499, by the length of the dragon that died: 2-4, 5-7, 8-14, 15 or more. Per group and map
class: deaths per race, pearls dropped per race, the share of those pearls eaten by the lineage of the team's final
longest, and for the last 50 rounds alone the same for dragons of 8+. Same test for every team.
Reads e_out/w4 through e_data. Output: e_out/merge.txt"""
import e_data as D

P = D.Out("merge.txt")
GROUPS = D.ORDER + ("test4 (vs us)", "WHQ (vs us)")
CLS = ((2, 4, "2-4"), (5, 7, "5-7"), (8, 14, "8-14"), (15, 9999, "15+"))


def main():
    rows = D.rows()
    P("WHO IS FED: deaths by choice in races, rounds 300-499, by the length of the dragon that died (same test for every team)")
    for big, name in ((False, "SMALL MAPS (<= 1,200 cells)"), (True, "BIG MAPS (> 1,200 cells)")):
        P("")
        P(name)
        P("%-16s %5s | per race: deaths of 2-4 / 5-7 / 8-14 / 15+ | pearls per race from 2-4 / 5-7 / 8-14 / 15+ | final lineage's share of those pearls: 2-4 / 5-7 / 8-14 / 15+ | "
          "rounds 450-499, dragons of 8+: deaths per race, pearls per race, lineage's share | races with at least one death by choice of a dragon of 15+" % ("group", "races"))
        agg = {}
        for r in rows:
            if (r.cells > 1200) != big or not r.bd:
                continue
            DI = {k: i for i, k in enumerate(r.d["dcol"])}
            dd = [x for x in r.s["deaths"] if x[0] >= 300 and x[DI["cls"]] == 2]
            for g in D.groups(r):
                a = agg.setdefault(g, dict(n=0, c=[0] * 4, p=[0] * 4, l=[0] * 4, ln=0, lp=0, ll=0, any15=0))
                a["n"] += 1
                any15 = False
                for x in dd:
                    L = x[2]
                    k = next(i for i, (lo, hi, _) in enumerate(CLS) if lo <= L <= hi)
                    a["c"][k] += 1
                    a["p"][k] += x[DI["drop"]]
                    a["l"][k] += x[DI["e_lin"]]
                    if L >= 15:
                        any15 = True
                    if L >= 8 and x[0] >= 450:
                        a["ln"] += 1
                        a["lp"] += x[DI["drop"]]
                        a["ll"] += x[DI["e_lin"]]
                a["any15"] += int(any15)
        for g in GROUPS:
            a = agg.get(g)
            if not a:
                continue
            n = a["n"]
            P("%-16s %5d | %5.1f / %4.1f / %4.2f / %4.2f | %5.1f / %4.1f / %4.1f / %5.1f | %3.0f%% / %3.0f%% / %3.0f%% / %3.0f%% | %4.2f, %4.1f, %3.0f%% | %3d of %d" % (
                g, n, a["c"][0] / n, a["c"][1] / n, a["c"][2] / n, a["c"][3] / n, a["p"][0] / n, a["p"][1] / n, a["p"][2] / n, a["p"][3] / n,
                100.0 * a["l"][0] / max(1, a["p"][0]), 100.0 * a["l"][1] / max(1, a["p"][1]), 100.0 * a["l"][2] / max(1, a["p"][2]),
                100.0 * a["l"][3] / max(1, a["p"][3]), a["ln"] / n, a["lp"] / n, 100.0 * a["ll"] / max(1, a["lp"]), a["any15"], n))
    P.f.close()


main()
