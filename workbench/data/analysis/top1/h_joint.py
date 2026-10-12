#!/usr/bin/env python3
"""Candidates 1 and 2 on one footing, alone and together.  Output: stdout -> h_out/joint.txt

C1 ("take the queen"): her queen dies on our first untaken in-view chance (any attacker length up to 12).
C2 ("our queen never ends a move in reach"): our queen does not die by a "stepped in" / "stayed in" ram.
C2+ : the same for all four families she controls herself (stepped/stayed in, boxed in by bodies, terrain dead end,
      her own ram), i.e. C2 plus A4's repairs.
Death kinds are A4's (d_tab.load(), d_haz.FAM).  Chances are the lead's q3v2.

For every meow game the script computes the probability of a win under each reading:
  strict     : the saved queen lives to the end; a killed enemy queen stays dead; nothing else changes.
               both dead at round 500 -> our final longest against her best non-queen dragon (lenient) or against her
               longest including the queen's own length (hard).  both alive -> queen lengths as they were (ours at
               the moment she would have died, hers at the end); a tie goes to the longest dragon as it was.
  realistic  : the saved queen then survives to the end as often as (a) a top-three queen alive at that round, on that
               map-size class and economy band (A4's reading 2), or (b) our own queen with only the other kinds of
               death left, at our own rates (A4's reading 3).  If she dies after all the game is what it was.
               A killed enemy queen stays dead; with both queens dead we win at OUR OWN rate for round-500 games
               with both queens dead in that economy band (band at round 300).  Both alive: our own rate (3 of 14).
Wipe-outs never change.  Reported: expected wins gained over the 401 games and over the live bot's 275.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
import d_tab  # noqa: E402
import h_c2  # noqa: E402
from d_haz import FAM, FAMS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS4 = [(0, 50), (50, 100), (100, 300), (300, 500)]
OWN4 = ("ram stepped/stayed in", "boxed bodies", "boxed terrain", "own ram")


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def eband(x):
    return "<0.67" if x < 0.67 else "0.67-1" if x < 1 else "1-1.5" if x < 1.5 else ">1.5"


def main():
    recs = d_tab.load()
    base = {(str(r["gid"]), r["side"]): r for r in json.load(open(os.path.join(HERE, "h_out", "base.json")))}
    qcache = {}

    def q(gid):
        if gid not in qcache:
            qcache[gid] = json.load(open(os.path.join(HERE, "q", gid + ".json")))
        return qcache[gid]

    # top-three survival to the end given alive at round r (A4's reading 2)
    surv = defaultdict(lambda: [0, 0])
    for x in recs:
        if "top three" not in x["groups"]:
            continue
        d = q(x["gid"])
        s = x["side"]
        o = "B" if s == "A" else "A"
        mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
        life = x["det"]["r"] if x["kind"] != "alive" else 10 ** 6
        alive_end = x["kind"] == "alive"
        for r in range(0, min(len(mine), len(theirs)), 25):
            if life <= r or not theirs[r] or not mine[r]:
                continue
            for key in ((size(x["cells"]), eband(mine[r] / theirs[r]), r), ("all", eband(mine[r] / theirs[r]), r), ("all", "all", r)):
                surv[key][0] += 1
                surv[key][1] += alive_end

    def p_top(cells, ratio, r):
        r0 = (r // 25) * 25
        for key in ((size(cells), eband(ratio), r0), ("all", eband(ratio), r0), ("all", "all", r0)):
            n, k = surv[key]
            if n >= 20:
                return k / n
        return 0.0

    expo = defaultdict(Counter)
    dead = defaultdict(Counter)
    for x in recs:
        if "meow" not in x["groups"]:
            continue
        sz = size(x["cells"])
        life = x["det"]["r"] if x["kind"] != "alive" else x["rounds"]
        for lo, hi in BANDS4:
            expo[sz][(lo, hi)] += max(0, min(life, hi) - lo)
        if x["kind"] != "alive":
            r = x["det"]["r"]
            for lo, hi in BANDS4:
                if lo <= r < hi:
                    dead[sz][(FAM[x["kind"]], (lo, hi))] += 1

    dead_part = defaultdict(Counter)
    for x in recs:
        if "meow" in x["groups"] and x["kind"] != "alive":
            r = x["det"]["r"]
            for lo, hi in BANDS4:
                if lo <= r < hi:
                    dead_part[size(x["cells"])][(h_c2.part_of(x) or "rest", (lo, hi))] += 1

    def p_own_rest_parts(cells, removed, r):
        sz = size(cells)
        tot = 0.0
        for lo, hi in BANDS4:
            left = max(0, hi - max(lo, r))
            if not left or not expo[sz][(lo, hi)]:
                continue
            rate = sum(v for (p, band), v in dead_part[sz].items() if band == (lo, hi) and p not in removed) / expo[sz][(lo, hi)]
            tot += rate * left
        return math.exp(-tot)

    def p_own_rest(cells, removed, r):
        """our queen's survival from round r to 500 with the families in `removed` gone, the others at our rates"""
        sz = size(cells)
        tot = 0.0
        for lo, hi in BANDS4:
            left = max(0, hi - max(lo, r))
            if not left or not expo[sz][(lo, hi)]:
                continue
            rate = sum(dead[sz][(f, (lo, hi))] for f in FAMS if f not in removed) / expo[sz][(lo, hi)]
            tot += rate * left
        return math.exp(-tot)

    # our own win rates by state (all 401 games)
    dd = defaultdict(lambda: [0, 0])
    aa = [0, 0]
    for x in recs:
        if "meow" not in x["groups"] or x["end"] == "wipe-out":
            continue
        b = base[(x["gid"], x["side"])]
        mq, oq = b["my_fin"]["queen"], b["op_fin"]["queen"]
        r300 = eband(b["my_tot300"] / b["op_tot300"]) if b.get("my_tot300") and b.get("op_tot300") else "<0.67"
        if not mq and not oq:
            dd[r300][0] += 1
            dd[r300][1] += x["won"]
        if mq and oq:
            aa[0] += 1
            aa[1] += x["won"]
    p_aa = aa[1] / aa[0]
    print("our own win rates used: both dead by band", {k: f"{v[1]}/{v[0]}" for k, v in dd.items()}, "; both alive", f"{aa[1]}/{aa[0]}")

    def evaluate(grp, c1, c2fam, hunters_max=12, parts=None):
        """returns dict of expected wins gained under each reading, and overlap counters"""
        res = Counter()
        n = 0
        for x in recs:
            if grp not in x["groups"]:
                continue
            n += 1
            b = base[(x["gid"], x["side"])]
            if x["end"] == "wipe-out" or x["won"]:
                continue
            mq, oq = b["my_fin"]["queen"], b["op_fin"]["queen"]
            # --- does C1 kill her queen?  (she was alive at the end and we had an untaken in-view chance)
            kill = False
            if c1 and oq:
                ch = sorted((c for c in b["my_ch"] if c[9] and c[3] <= hunters_max), key=lambda c: c[0])
                kill = bool(ch) and not ch[0][5]
                # (if the first chance was taken she would be dead; she is alive, so every in-view chance was untaken)
                kill = bool(ch)
            # --- does C2 save our queen?
            save = False
            p2 = p3 = 0.0
            qlen_then = 0
            hit = (parts is not None and x["kind"] != "alive" and h_c2.part_of(x) in parts) or \
                  (parts is None and c2fam and x["kind"] != "alive" and FAM[x["kind"]] in c2fam)
            if hit:
                save = True
                r = x["det"]["r"]
                d = q(x["gid"])
                s = x["side"]
                o = "B" if s == "A" else "A"
                mine, theirs = d["sides"][s]["per"]["total"], d["sides"][o]["per"]["total"]
                ratio = mine[r] / theirs[r] if r < len(theirs) and theirs[r] else 1.0
                p2 = p_top(x["cells"], ratio, r)
                p3 = p_own_rest_parts(x["cells"], parts, r) if parts is not None else p_own_rest(x["cells"], c2fam, r)
                qlen_then = d["sides"][s]["qdeath"]["len"]
            her_dead = (not oq) or kill
            own_alive_already = bool(mq)
            if not kill and not save:
                continue
            band = eband(b["my_tot300"] / b["op_tot300"]) if b.get("my_tot300") and b.get("op_tot300") else "<0.67"
            p_dd = dd[band][1] / dd[band][0] if dd[band][0] else 0.0
            op_long, op_second = b["op_fin"]["longest"], b["op_second_fin"]
            op_noq = op_second if (oq and oq == op_long) else op_long
            mine_long = b["my_fin"]["longest"]
            # ----- strict
            if own_alive_already or save:
                # our queen alive at the end
                if her_dead:
                    s_len = s_hard = 1.0
                else:
                    ql = mq if own_alive_already else qlen_then
                    s_len = s_hard = 1.0 if ql > oq else (1.0 if (ql == oq and mine_long > op_long) else 0.0)
            else:
                # our queen dead, hers killed
                s_len = 1.0 if mine_long > op_noq else 0.0
                s_hard = 1.0 if mine_long > op_long else 0.0
            res["strict lenient"] += s_len
            res["strict hard"] += s_hard
            # ----- realistic (a) top-three survival, (b) our own rest rates
            for tag, ps in (("realistic, saved queen survives like a top-three queen", p2), ("realistic, saved queen at our own other death rates", p3)):
                if own_alive_already:
                    val = 1.0 if her_dead else 0.0     # loss with both alive stays a loss unless she is killed
                elif save:
                    win_if_alive = 1.0 if her_dead else p_aa
                    win_if_dead = p_dd if (kill and not mq) else 0.0   # she dies after all: both dead only if C1 killed hers
                    if not oq:
                        win_if_dead = 0.0    # the game was a both-dead loss already
                    val = ps * win_if_alive + (1 - ps) * win_if_dead
                else:
                    val = p_dd
                res[tag] += val
            res["games touched"] += 1
            res["... her queen killed by C1"] += kill
            res["... our queen saved by C2"] += save
            res["... both in the same game"] += kill and save
        return n, res

    for grp in ("meow", "meow live"):
        print(f"\n===== {grp}")
        cases = [("C1 alone, any length", True, (), 12),
                 ("C2 as proposed alone (parts a+b+c1)", False, (), 12, ("a", "b", "c1")),
                 ("C1 + C2 as proposed (parts a+b+c1)", True, (), 12, ("a", "b", "c1")),
                 ("C1 alone, hunters 4 or shorter (qh31's limit)", True, (), 4),
                 ("C2 alone (stepped / stayed in)", False, ("ram stepped/stayed in",), 12),
                 ("C2+ alone (all four families she controls)", False, OWN4, 12),
                 ("C1 + C2", True, ("ram stepped/stayed in",), 12),
                 ("C1 + C2+", True, OWN4, 12)]
        out = {}
        for case in cases:
            name, c1, fam, hm = case[:4]
            n, res = evaluate(grp, c1, fam, hm, case[4] if len(case) > 4 else None)
            out[name] = res
            print(f"  {name}: touched {res['games touched']} losses (kill {res['... her queen killed by C1']}, save {res['... our queen saved by C2']}, both {res['... both in the same game']})")
            for k in ("strict lenient", "strict hard", "realistic, saved queen survives like a top-three queen", "realistic, saved queen at our own other death rates"):
                print(f"      {k}: +{res[k]:.1f} wins (+{100 * res[k] / n:.1f} points)")
        for a, b_, ab in (("C1 alone, any length", "C2 as proposed alone (parts a+b+c1)", "C1 + C2 as proposed (parts a+b+c1)"),
                          ("C1 alone, any length", "C2 alone (stepped / stayed in)", "C1 + C2"), ("C1 alone, any length", "C2+ alone (all four families she controls)", "C1 + C2+")):
            for k in ("strict lenient", "realistic, saved queen survives like a top-three queen", "realistic, saved queen at our own other death rates"):
                print(f"  together minus the sum of the two alone [{ab}; {k}]: {out[ab][k] - out[a][k] - out[b_][k]:+.1f}")


if __name__ == "__main__":
    main()
