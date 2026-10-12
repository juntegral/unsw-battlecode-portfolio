#!/usr/bin/env python3
"""The direct cost of leader cuts, counted on the lineage of the final longest dragon. For every race (round-500 game
with both queens dead): the segments the lineage left behind in its own cuts (a handover where the parent keeps 2-3)
from round R on, all cuts and only the cuts made with a free cell next to the head (voluntary: the first cut of a
same-round chain decides, the children born in that round have no free-cell count of their own). Then, for the lost
races: in how many is that number at least the losing margin + 1 (a strict what-if: the stubs' pearls are ignored, the
enemy unchanged). Per group. Reads e_out/w4 through e_data. Output: e_out/cutcost.txt"""
import e_data as D

P = D.Out("cutcost.txt")
GROUPS = D.ORDER + ("test4 (vs us)", "WHQ (vs us)")


def lineage_cuts(s):
    """[(round, left behind, voluntary)] for the final lineage's handovers that are cuts (parent keeps 2-3)."""
    lin = s["lin"]
    if not lin:
        return []
    free = {}
    for x in s["splits"]:
        free[(x[0], x[1], x[2])] = x[6]
    out = []
    chain_free = {}
    for h in lin["hand"]:
        r, parent, child, before, gets = h
        keep = before - gets
        if keep > 3 or before < 8:
            continue
        f = free.get((r, parent, child), -1)
        if f < 0 or r in chain_free and parent in chain_free[r]:
            # born this round in a chain: inherit the chain's first verdict
            vol = chain_free[r].get(parent, False) if r in chain_free else False
        else:
            vol = f >= 1
        chain_free.setdefault(r, {})[child] = vol
        out.append((r, keep, vol))
    return out


def main():
    rows = D.rows()
    P("DIRECT COST OF THE FINAL LINEAGE'S OWN CUTS (races = round-500 games with both queens dead; a cut = handover in which")
    P("the parent keeps 2-3; 'voluntary' = the dragon that started the cut (or the chain of cuts of that round) had a free cell)")
    for R in (350, 400, 440):
        P("")
        P("cuts from round %d on" % R)
        P("%-16s %5s | cuts per race: all, voluntary | segments left behind per race: all, voluntary | lost races | ... in which all cuts' segments >= margin+1 | ... voluntary cuts' segments >= margin+1 | races with a same-round chain of 3+ cuts" % ("group", "races"))
        agg = {}
        for r in rows:
            if not r.bd:
                continue
            cuts = [c for c in lineage_cuts(r.s) if c[0] >= R]
            n_all, n_vol = len(cuts), sum(1 for c in cuts if c[2])
            s_all, s_vol = sum(c[1] for c in cuts), sum(c[1] for c in cuts if c[2])
            byround = {}
            for c in cuts:
                byround[c[0]] = byround.get(c[0], 0) + 1
            chain = any(v >= 3 for v in byround.values())
            fs, fo = r.s["final"], r.o["final"]
            mine = fs["top"][0][0] if fs["top"] else 0
            theirs = fo["top"][0][0] if fo["top"] else 0
            margin = theirs - mine
            for g in D.groups(r):
                a = agg.setdefault(g, dict(n=0, c=0, cv=0, s=0, sv=0, lost=0, t_all=0, t_vol=0, chain=0))
                a["n"] += 1
                a["c"] += n_all
                a["cv"] += n_vol
                a["s"] += s_all
                a["sv"] += s_vol
                a["chain"] += int(chain)
                if not r.won:
                    a["lost"] += 1
                    if s_all >= margin + 1:
                        a["t_all"] += 1
                    if s_vol >= margin + 1:
                        a["t_vol"] += 1
        for g in GROUPS:
            a = agg.get(g)
            if not a:
                continue
            P("%-16s %5d |      %4.1f  %4.1f           |        %4.1f  %4.1f                          | %5d      | %5d                                      | %5d                                   | %5d" % (
                g, a["n"], a["c"] / a["n"], a["cv"] / a["n"], a["s"] / a["n"], a["sv"] / a["n"], a["lost"], a["t_all"], a["t_vol"], a["chain"]))
    P("")
    P("our lost races in which the cuts from round 400 alone cover the margin (game, map, set, opponent, result, cuts, segments left, voluntary segments):")
    for r in rows:
        if not r.bd or r.won or r.team != D.E.ME or not r.study:
            continue
        cuts = [c for c in lineage_cuts(r.s) if c[0] >= 400]
        s_all, s_vol = sum(c[1] for c in cuts), sum(c[1] for c in cuts if c[2])
        fs, fo = r.s["final"], r.o["final"]
        margin = fo["top"][0][0] - fs["top"][0][0]
        if s_all >= margin + 1:
            P("   %d %-14s %-22s vs %-5d %3d : %-3d  cuts %2d  left %2d  voluntary %2d  (rounds %s)" % (
                r.gid, r.map, r.set, r.opp, fs["top"][0][0], fo["top"][0][0], len(cuts), s_all, s_vol, " ".join(str(c[0]) + ("v" if c[2] else "") for c in cuts)))
    P.f.close()


main()
