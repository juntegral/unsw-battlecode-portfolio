#!/usr/bin/env python3
"""Summary of x_out/c2vis.json: would a veto built from the bot's existing pieces (visible parts, no pearls) see the
turns the study counts as "ended in reach although a safe step existed"? Output: x_out/c2vis.txt"""
import json
from collections import Counter

import x_load as X

out = open("x_out/c2vis.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


T = json.load(open("x_out/c2vis.json"))
P("our queen's turns with an enemy head in view:", len(T))
M = {"bot": 0, "bot+1": 1, "true": 2, "pearl": 3}


def by_choice(t, m):
    """She moved onto a cell in reach although a free cell out of reach existed, under model m."""
    f = t["first"]
    if f is None or not t["free"][f]:
        return False
    i = M[m]
    return t["thr"][f][i] and any(t["free"][d] and not t["thr"][d][i] for d in range(4))


def safe_opts(t, m):
    i = M[m]
    return [d for d in range(4) if t["free"][d] and not t["thr"][d][i]]


for label, sel in (("all 401 games", T), ("live bot", [t for t in T if t["live"]]), ("maps over 600 cells", [t for t in T if t["cells"] > 600]),
                   ("maps of 600 cells or fewer", [t for t in T if t["cells"] <= 600])):
    P("\n== %s: %d turns" % (label, len(sel)))
    truth = [t for t in sel if by_choice(t, "pearl")]
    rammed = [t for t in truth if t["rammed"]]
    P("   moved into reach although a free cell out of reach existed (true length, pearl-paid steps): %d turns, rammed that round on %d" % (len(truth), len(rammed)))
    for m in ("true", "bot+1", "bot"):
        c = Counter()
        for t in truth:
            fires = by_choice(t, m)
            c["veto fires"] += fires
            if fires:
                so = safe_opts(t, m)
                tso = set(safe_opts(t, "pearl"))
                c["... every cell it then allows is truly safe"] += all(d in tso for d in so)
                c["... at least one cell it allows is truly safe"] += any(d in tso for d in so)
                c["... none of the cells it allows is truly safe"] += not any(d in tso for d in so)
            else:
                f = t["first"]
                c["no veto: the model calls her cell safe"] += not t["thr"][f][M[m]]
                c["no veto: the model sees no safe cell at all"] += t["thr"][f][M[m]]
            if t["rammed"]:
                c["rammed turns: veto fires"] += fires
                if fires:
                    so = safe_opts(t, m)
                    tso = set(safe_opts(t, "pearl"))
                    c["rammed turns: veto fires and every allowed cell is truly safe"] += all(d in tso for d in so)
        P("   model %-6s %s" % (m, dict(c)))
    # what the coded rule would change in all, and its false alarms
    for m in ("bot", "bot+1"):
        ch = [t for t in sel if by_choice(t, m)]
        fa = [t for t in ch if not t["thr"][t["first"]][M["pearl"]]]
        ate = [t for t in ch if t["pearl"][t["first"]]]
        P("   the rule coded with model %-6s would change %d turns (%d of them she was not truly in reach; she took a pearl on %d)" % (m, len(ch), len(fa), len(ate)))
    kv = [t for t in sel if t["rammed"] and t.get("killer_L")]
    part = [t for t in kv if t["killer_vis"] < t["killer_L"]]
    P("   rammed by an enemy in view: %d; the killer was only partly inside her view on %d (its visible parts / true length: %s)" % (
        len(kv), len(part), Counter("%d/%d" % (t["killer_vis"], t["killer_L"]) for t in part).most_common(8)))
out.close()
