#!/usr/bin/env python3
"""Common footing for the candidates: where our games end up, by state, next to the top three.

Reads h_out/base.json (h_base.py). Prints to stdout (redirect to h_out/states.txt).

1. How games end, by queen state at the end (own / her queen alive or dead), per group.
2. The same inside each economy band (own / enemy total length at round 300), games that reach round 300.
3. Decomposition: our wins if ONE factor were at the top three's level and everything else stayed ours.
   Factors: (a) share of games in each end state, (b) win rate inside "both queens dead", (c) win rate inside
   "both queens alive". Done inside economy bands, so that the economy is held fixed.
4. Live bot only (275 games) for the headline rows.
"""
import json
import sys
from collections import Counter, defaultdict

rows = json.load(open("h_out/base.json"))
GROUPS = ["meow", "meow_live", "opp_of_meow", "Vibing++", "SSS", "forgot", "top3"]
BANDS = [("<0.67", 0, 0.67), ("0.67-1", 0.67, 1.0), ("1-1.5", 1.0, 1.5), (">1.5", 1.5, 1e9)]


def members(g):
    for r in rows:
        gs = r["groups"]
        if g == "top3":
            if any(x in gs for x in ("Vibing++", "SSS", "forgot")):
                yield r
        elif g == "meow_live":
            if "meow" in gs and r["build"] == "live":
                yield r
        elif g in gs:
            yield r


def end_state(r):
    """wipeW / wipeL / r500 + queen states"""
    if r["end_type"] == "wipe-out":
        return "wipe W" if r["win"] else "wipe L"
    a = "alive" if r["my_fin"]["queen"] else "dead"
    b = "alive" if r["op_fin"]["queen"] else "dead"
    return f"r500 own {a} / her {b}"


def band(r):
    a, b = r.get("my_tot300"), r.get("op_tot300")
    if a is None or b is None or b == 0:
        return None
    x = a / b
    for name, lo, hi in BANDS:
        if lo <= x < hi:
            return name
    return None


STATES = ["wipe W", "wipe L", "r500 own alive / her dead", "r500 own alive / her alive", "r500 own dead / her dead",
          "r500 own dead / her alive"]

print("== 1. How games end (all games of the group; opponents rated 2000+, Schooltime left out) ==")
tab = {}
for g in GROUPS:
    c, w = Counter(), Counter()
    n = 0
    for r in members(g):
        st = end_state(r)
        c[st] += 1
        w[st] += r["win"]
        n += 1
    tab[g] = (n, c, w)
    print(f"\n{g}: {n} games, {sum(w.values())} wins ({100 * sum(w.values()) / n:.1f}%)")
    for st in STATES:
        if c[st]:
            print(f"   {st:28s} {c[st]:4d} games ({100 * c[st] / n:4.1f}%)  won {w[st]:4d} ({100 * w[st] / c[st]:.0f}%)")
    r5 = sum(c[s] for s in STATES[2:])
    w5 = sum(w[s] for s in STATES[2:])
    print(f"   round-500 games {r5}, won {w5}; queen-rule wins (own alive) {w[STATES[2]] + w[STATES[3]]}, longest-rule wins {w[STATES[4]]}")

print("\n== 2. Inside economy bands (own / enemy total length at round 300; games that reach round 300) ==")
bt = {}
for g in GROUPS:
    for r in members(g):
        b = band(r)
        if b is None:
            continue
        k = (g, b)
        bt.setdefault(k, [0, 0, Counter(), Counter()])
        bt[k][0] += 1
        bt[k][1] += r["win"]
        st = end_state(r)
        bt[k][2][st] += 1
        bt[k][3][st] += r["win"]
for g in GROUPS:
    print(f"\n{g}")
    for name, _, _ in BANDS:
        v = bt.get((g, name))
        if not v:
            continue
        n, w, c, cw = v
        parts = "; ".join(f"{st.replace('r500 ', '')} {c[st]}/{cw[st]}w" for st in STATES if c[st])
        print(f"   {name:7s} n={n:4d} won {w:4d} ({100 * w / n:4.1f}%) | {parts}")

print("\n== 3. Decomposition inside bands: our games, one factor at the top three's level ==")
for who in ("meow", "meow_live"):
    base_w = 0
    alt = Counter()
    tot_n = 0
    for name, _, _ in BANDS:
        mine = bt.get((who, name))
        top = bt.get(("top3", name))
        if not mine or not top:
            continue
        n, w, c, cw = mine
        tn, tw, tc, tcw = top
        tot_n += n
        base_w += w
        # (0) everything top three: n * top win rate
        alt["all at top-three level (same band mix)"] += n * tw / tn
        # helper: our win rate per state (0 if no games)
        def rate(cc, ww, st, fallback):
            return ww[st] / cc[st] if cc[st] else fallback
        # (a) end-state mix of the top three, our win rate inside each state (top's rate where we have no games)
        exp = 0.0
        for st in STATES:
            share = tc[st] / tn
            pr = rate(c, cw, st, rate(tc, tcw, st, 0.0))
            exp += n * share * pr
        alt["end-state mix of the top three, our win rate inside each state"] += exp
        # (b) our mix, top three's win rate inside 'both dead'
        exp = 0.0
        for st in STATES:
            pr = rate(c, cw, st, 0.0)
            if st == "r500 own dead / her dead":
                pr = rate(tc, tcw, st, pr)
            exp += c[st] * pr
        alt["our mix, top three's win rate when both queens are dead (longest rule)"] += exp
        # (c) our mix, top three's win rate inside 'both alive'
        exp = 0.0
        for st in STATES:
            pr = rate(c, cw, st, 0.0)
            if st == "r500 own alive / her alive":
                pr = rate(tc, tcw, st, pr)
            exp += c[st] * pr
        alt["our mix, top three's win rate when both queens are alive (queen length)"] += exp
        # (d) only her queen: move our 'own dead / her alive' share down to the top three's share of
        #     her-alive among own-dead round-500 games; moved games become 'both dead' at OUR both-dead rate
        own_dead = c["r500 own dead / her dead"] + c["r500 own dead / her alive"]
        t_own_dead = tc["r500 own dead / her dead"] + tc["r500 own dead / her alive"]
        if own_dead and t_own_dead:
            her_alive_share_top = tc["r500 own dead / her alive"] / t_own_dead
            moved = c["r500 own dead / her alive"] - own_dead * her_alive_share_top
            alt["her queen dies as often as against the top three (own-dead games), moved games won at our both-dead rate"] += \
                w + moved * rate(c, cw, "r500 own dead / her dead", 0.0)
        else:
            alt["her queen dies as often as against the top three (own-dead games), moved games won at our both-dead rate"] += w
        # (e) only our queen: our 'r500' games get the top three's share of own-alive; moved games:
        #     from 'dead/dead' to 'alive/dead' (win), from 'dead/alive' to 'alive/alive' (our both-alive rate, else top's)
        r5 = sum(c[s] for s in STATES[2:])
        t5 = sum(tc[s] for s in STATES[2:])
        if r5 and t5:
            # among her-dead round-500 games: share with own alive
            hd = c["r500 own alive / her dead"] + c["r500 own dead / her dead"]
            thd = tc["r500 own alive / her dead"] + tc["r500 own dead / her dead"]
            ha = c["r500 own alive / her alive"] + c["r500 own dead / her alive"]
            tha = tc["r500 own alive / her alive"] + tc["r500 own dead / her alive"]
            gain = 0.0
            if hd and thd:
                target = hd * tc["r500 own alive / her dead"] / thd
                moved = max(0.0, target - c["r500 own alive / her dead"])
                gain += moved * (1.0 - rate(c, cw, "r500 own dead / her dead", 0.0))
            if ha and tha:
                target = ha * tc["r500 own alive / her alive"] / tha
                moved = max(0.0, target - c["r500 own alive / her alive"])
                gain += moved * rate(c, cw, "r500 own alive / her alive", rate(tc, tcw, "r500 own alive / her alive", 0.0))
            alt["our queen alive at the end as often as a top-three queen (same her-queen state), short queen as now"] += w + gain
        else:
            alt["our queen alive at the end as often as a top-three queen (same her-queen state), short queen as now"] += w
    print(f"\n{who}: {tot_n} games reach round 300, {base_w} won")
    for k, v in alt.items():
        print(f"   {v:6.1f} wins ({v - base_w:+5.1f})  {k}")

print("\n== 4. Band mix (share of games reaching round 300 in each band) ==")
for g in GROUPS:
    tot = sum(bt[(g, b)][0] for b, _, _ in BANDS if (g, b) in bt)
    print(f"   {g:12s} " + "  ".join(f"{b}: {100 * bt[(g, b)][0] / tot:4.1f}%" for b, _, _ in BANDS if (g, b) in bt) + f"  (n={tot})")
# economy what-if: our band win rates with top-three mix; top three band rates with our mix
for who in ("meow", "meow_live"):
    tot = sum(bt[(who, b)][0] for b, _, _ in BANDS if (who, b) in bt)
    ttot = sum(bt[("top3", b)][0] for b, _, _ in BANDS)
    w_now = sum(bt[(who, b)][1] for b, _, _ in BANDS if (who, b) in bt)
    a = sum(tot * bt[("top3", b)][0] / ttot * bt[(who, b)][1] / bt[(who, b)][0] for b, _, _ in BANDS if (who, b) in bt)
    c2 = sum(bt[(who, b)][0] * bt[("top3", b)][1] / bt[("top3", b)][0] for b, _, _ in BANDS if (who, b) in bt)
    print(f"   {who}: now {w_now} of {tot}; our band win rates with the top three's band mix: {a:.1f}; "
          f"the top three's band win rates with our band mix: {c2:.1f}")
