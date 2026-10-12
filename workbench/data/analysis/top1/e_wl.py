#!/usr/bin/env python3
"""Winners against losers of LEVEL races. A level race = a round-500 game with both queens dead in which own potential /
enemy potential at round 350 is between 0.8 and 1.25 (potential = longest + the pearls every other own dragon would
drop). One row per side of each such game in the study (a game between two study teams gives two rows). For winners
and losers: start of leader feeding, longest at 350 / 400 / 450 / end, share of potential in the longest at the end,
units at the end, cuts of the final lineage from round 400 (all / with a free cell), deaths by choice in rounds
300-499: number, pearls, share next to the longest, share next to nothing, share of the pearls eaten by the final
lineage. Groups: meow, our opponents (the other side of our races), the top three.
Reads e_out/w4 through e_data. Output: e_out/wl.txt"""
import e_data as D
import e_cutcost as C  # noqa: F401  (lineage_cuts)

P = D.Out("wl.txt")


def feed_start(rec):
    DI = {k: i for i, k in enumerate(rec.d["dcol"])}
    rs = sorted(x[0] for x in rec.s["deaths"] if x[DI["cls"]] == 2 and 1 <= x[DI["tdist"]] <= 3 and not x[DI["tq"]] and x[0] >= 150)
    for i in range(len(rs) - 2):
        if rs[i + 2] - rs[i] <= 15:
            return rs[i]
    return None


def pot(rec, r, own=True):
    t = rec.tl(r, own)
    return (t[3] + t[12]) if t else None


def main():
    rows = D.rows()
    agg = {}
    for r in rows:
        if not r.bd:
            continue
        a, b = pot(r, 350), pot(r, 350, False)
        if not a or not b or not (0.8 <= a / b <= 1.25):
            continue
        gs = [g for g in D.groups(r) if g in ("meow", "opp", "top3")]
        if not gs:
            continue
        DI = {k: i for i, k in enumerate(r.d["dcol"])}
        dd = [x for x in r.s["deaths"] if x[0] >= 300 and x[DI["cls"]] == 2]
        n = len(dd)
        drop = sum(x[DI["drop"]] for x in dd)
        lin = sum(x[DI["e_lin"]] for x in dd)
        nl = sum(1 for x in dd if 0 <= x[DI["lpath"]] <= 3)
        nn = sum(1 for x in dd if not (0 <= x[DI["lpath"]] <= 3) and x[DI["tdist"]] < 0)
        cuts = [c for c in C.lineage_cuts(r.s) if c[0] >= 400]
        f = r.s["final"]
        fl = f["top"][0][0] if f["top"] else 0
        fp = fl + f["pot"]
        t350, t400, t450 = r.tl(350), r.tl(400), r.tl(450)
        for g in gs:
            x = agg.setdefault((g, r.won), dict(n=0, start=[], l350=[], l400=[], l450=[], end=[], c=[], units=[], cuts=0, vol=0,
                                                dn=0, drop=0, lin=0, nl=0, nn=0, p350=[], grow=[]))
            x["n"] += 1
            x["start"].append(feed_start(r))
            x["l350"].append(t350[3])
            x["l400"].append(t400[3])
            x["l450"].append(t450[3])
            x["end"].append(fl)
            x["c"].append(fl / fp if fp else None)
            x["units"].append(f["units"])
            x["cuts"] += len(cuts)
            x["vol"] += sum(1 for c in cuts if c[2])
            x["dn"] += n
            x["drop"] += drop
            x["lin"] += lin
            x["nl"] += nl
            x["nn"] += nn
            x["p350"].append(a)
            x["grow"].append(fl - t400[3])
    P("WINNERS AGAINST LOSERS OF LEVEL RACES (round-500 games with both queens dead; own potential / enemy potential at round 350")
    P("between 0.8 and 1.25). Medians unless marked; one row per side.")
    P("%-22s %5s | start of leader feeding (median; sides with none) | longest at 350 / 400 / 450 / end | growth 400->end | share of potential in the longest at the end | "
      "units at the end | cuts of the final lineage from 400: all, with a free cell (mean) | deaths by choice 300-499 (mean) | pearls (mean) | next to the longest | next to nothing | pearls eaten by the final lineage" % ("group", "sides"))
    for g in ("meow", "opp", "top3"):
        for won in (True, False):
            x = agg.get((g, won))
            if not x:
                continue
            none = sum(1 for v in x["start"] if v is None)
            P("%-22s %5d | %s (%d) | %s / %s / %s / %s | %s | %s | %s | %.1f, %.1f | %.1f | %.1f | %2.0f%% | %2.0f%% | %2.0f%%" % (
                g + (" winners" if won else " losers"), x["n"], D.med(x["start"]), none, D.med(x["l350"]), D.med(x["l400"]), D.med(x["l450"]),
                D.med(x["end"]), D.med(x["grow"]), D.med(x["c"], 2), D.med(x["units"]), x["cuts"] / x["n"], x["vol"] / x["n"], x["dn"] / x["n"],
                x["drop"] / x["n"], 100.0 * x["nl"] / max(1, x["dn"]), 100.0 * x["nn"] / max(1, x["dn"]), 100.0 * x["lin"] / max(1, x["drop"])))
    P.f.close()


main()
