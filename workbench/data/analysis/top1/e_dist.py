#!/usr/bin/env python3
"""How close to the dragon it feeds does a feeder die, and does the distance matter? Feeders here = deaths by choice
from round 250 on within 3 path steps of an own dragon at least twice as long (the same test for every team). Per
group and map class: number at 1 / 2 / 3 steps, share of their pearls the dragon fed eats at each distance, share
eaten by the enemy, and the same split by whether the dragon fed was the team's longest.
Reads e_out/w4 through e_data. Output: e_out/dist.txt"""
import e_data as D

P = D.Out("dist.txt")
GROUPS = D.ORDER + ("test4 (vs us)", "WHQ (vs us)")


def main():
    rows = D.rows()
    P("HOW CLOSE A FEEDER DIES TO THE DRAGON IT FEEDS (deaths by choice from round 250, within 3 path steps of an own dragon")
    P("at least twice as long; all study games of the group)")
    for big, name in ((False, "SMALL MAPS (<= 1,200 cells)"), (True, "BIG MAPS (> 1,200 cells)")):
        P("")
        P(name)
        P("%-16s %7s | at 1 / 2 / 3 steps: n (share) | pearls eaten by the dragon fed at 1 / 2 / 3 steps | by the enemy at 1 / 2 / 3 | dragon fed is the team's longest: n (share), its share of the pearls | not the longest: n, share of pearls it eats" % ("group", "feeders"))
        agg = {}
        for r in rows:
            if (r.cells > 1200) != big:
                continue
            DI = {k: i for i, k in enumerate(r.d["dcol"])}
            fd = [x for x in r.s["deaths"] if x[0] >= 250 and x[DI["cls"]] == 2 and 1 <= x[DI["tdist"]] <= 3]
            for g in D.groups(r):
                a = agg.setdefault(g, dict(n=[0, 0, 0], drop=[0, 0, 0], fed=[0, 0, 0], en=[0, 0, 0], ln=0, ldrop=0, lfed=0, on=0, odrop=0, ofed=0))
                for x in fd:
                    i = x[DI["tdist"]] - 1
                    a["n"][i] += 1
                    a["drop"][i] += x[DI["drop"]]
                    a["fed"][i] += x[DI["e_t"]]
                    a["en"][i] += x[DI["e_e"]]
                    if x[DI["tid"]] == x[DI["lid"]]:
                        a["ln"] += 1
                        a["ldrop"] += x[DI["drop"]]
                        a["lfed"] += x[DI["e_t"]]
                    else:
                        a["on"] += 1
                        a["odrop"] += x[DI["drop"]]
                        a["ofed"] += x[DI["e_t"]]
        for g in GROUPS:
            a = agg.get(g)
            if not a:
                continue
            n = sum(a["n"])
            if not n:
                continue
            P("%-16s %7d | %5d (%2.0f%%) %5d (%2.0f%%) %5d (%2.0f%%) | %3.0f%% %3.0f%% %3.0f%% | %4.1f%% %4.1f%% %4.1f%% | %5d (%2.0f%%) %3.0f%% | %5d %3.0f%%" % (
                g, n, a["n"][0], 100.0 * a["n"][0] / n, a["n"][1], 100.0 * a["n"][1] / n, a["n"][2], 100.0 * a["n"][2] / n,
                100.0 * a["fed"][0] / max(1, a["drop"][0]), 100.0 * a["fed"][1] / max(1, a["drop"][1]), 100.0 * a["fed"][2] / max(1, a["drop"][2]),
                100.0 * a["en"][0] / max(1, a["drop"][0]), 100.0 * a["en"][1] / max(1, a["drop"][1]), 100.0 * a["en"][2] / max(1, a["drop"][2]),
                a["ln"], 100.0 * a["ln"] / n, 100.0 * a["lfed"] / max(1, a["ldrop"]), a["on"], 100.0 * a["ofed"] / max(1, a["odrop"])))
    where()
    P.f.close()


def where():
    """Same footing for every team: every death by choice from round 300 on in a race, by what was near."""
    rows = D.rows()
    P("")
    P("WHERE A DRAGON DIES BY CHOICE, RACES ONLY (round-500 games with both queens dead), ROUNDS 300-499, the same test for every team")
    P("near = within 3 path steps of the head of: the team's longest dragon of the moment / else another own dragon at least twice")
    P("as long / else such a dragon at 4-8 steps / else nothing. Pearls: share eaten by the lineage of the team's final longest")
    for big, name in ((False, "SMALL MAPS (<= 1,200 cells)"), (True, "BIG MAPS (> 1,200 cells)")):
        P("")
        P(name)
        P("%-16s %5s %8s | the longest  another 2x  2x at 4-8  nothing | pearls per race | eaten by: final lineage  other own  enemy  nobody | lineage's share when the death was next to: the longest / another 2x / 4-8 / nothing" % ("group", "races", "per race"))
        agg = {}
        for r in rows:
            if (r.cells > 1200) != big or not r.bd:
                continue
            DI = {k: i for i, k in enumerate(r.d["dcol"])}
            dd = [x for x in r.s["deaths"] if x[0] >= 300 and x[DI["cls"]] == 2]
            for g in D.groups(r):
                a = agg.setdefault(g, dict(games=0, n=[0, 0, 0, 0], drop=[0, 0, 0, 0], lin=[0, 0, 0, 0], own=0, en=0))
                a["games"] += 1
                for x in dd:
                    lp, td = x[DI["lpath"]], x[DI["tdist"]]
                    k = 0 if 0 <= lp <= 3 else 1 if 1 <= td <= 3 else 2 if td > 3 else 3
                    a["n"][k] += 1
                    a["drop"][k] += x[DI["drop"]]
                    a["lin"][k] += x[DI["e_lin"]]
                    a["own"] += x[DI["e_t"]] + x[DI["e_l"]] + x[DI["e_q"]] + x[DI["e_o"]]
                    a["en"] += x[DI["e_e"]]
        for g in GROUPS:
            a = agg.get(g)
            if not a or not sum(a["n"]):
                continue
            n, dr, li = sum(a["n"]), sum(a["drop"]), sum(a["lin"])
            P("%-16s %5d %8.1f |   %4.0f%%       %4.0f%%      %4.0f%%    %4.0f%%  | %8.1f        |      %4.0f%%            %4.0f%%     %4.1f%%   %4.0f%%  |   %3.0f%% / %3.0f%% / %3.0f%% / %3.0f%%" % (
                g, a["games"], n / a["games"], 100.0 * a["n"][0] / n, 100.0 * a["n"][1] / n, 100.0 * a["n"][2] / n, 100.0 * a["n"][3] / n,
                dr / a["games"], 100.0 * li / dr, 100.0 * (a["own"] - li) / dr, 100.0 * a["en"] / dr, 100.0 * (dr - a["own"] - a["en"]) / dr,
                100.0 * a["lin"][0] / max(1, a["drop"][0]), 100.0 * a["lin"][1] / max(1, a["drop"][1]),
                100.0 * a["lin"][2] / max(1, a["drop"][2]), 100.0 * a["lin"][3] / max(1, a["drop"][3])))


main()
