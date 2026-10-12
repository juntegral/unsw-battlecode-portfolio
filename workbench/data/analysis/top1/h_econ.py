#!/usr/bin/env python3
"""Economy footing: win rate by own/enemy total length at round 300 in fine bands, by map class, and what a
relative gain in our total length would do to our band mix.

Reads h_out/base.json. Prints to stdout (h_out/econ.txt).
1. Fine bands of the ratio at round 300: games and wins for meow, meow live, top three; by map class
   (large = over 1,200 cells = the maps where our code switches at round 150; other = 1,200 cells or fewer).
2. What-if: multiply OUR total length at round 300 by (1 + g) on the games of one class and re-apply OUR OWN
   win rate per coarse band (0.67 / 1 / 1.5 cuts): expected wins for g = 10, 20, 30, 40, 60, 100%.
   Also the same with a smooth (logistic) fit of our own win/loss on log(ratio).
3. Games that do not reach round 300 (wipe-outs before): count and result, by class.
"""
import json
import math
from collections import Counter, defaultdict

rows = json.load(open("h_out/base.json"))
FINE = [0, 0.2, 0.33, 0.5, 0.67, 0.85, 1.0, 1.25, 1.5, 2.0, 1e9]
COARSE = [0, 0.67, 1.0, 1.5, 1e9]


def grp(r):
    out = []
    if "meow" in r["groups"]:
        out.append("meow")
        if r["build"] == "live":
            out.append("meow_live")
        if r["battle"] in ("tc30-test-new", "tc30-dev1b-new"):
            out.append("meow_tc30")
    if any(x in r["groups"] for x in ("Vibing++", "SSS", "forgot")):
        out.append("top3")
    return out


def cls(r):
    return "large" if r["cells"] > 1200 else "other"


def ratio(r, rnd=300):
    a, b = r.get(f"my_tot{rnd}"), r.get(f"op_tot{rnd}")
    if a is None or b is None or b == 0:
        return None
    return a / b


def bidx(x, cuts):
    for i in range(len(cuts) - 1):
        if cuts[i] <= x < cuts[i + 1]:
            return i
    return len(cuts) - 2


print("== 1. Fine bands of own/enemy total length at round 300 (games that reach round 300): games, wins ==")
tab = defaultdict(lambda: [0, 0])
for r in rows:
    x = ratio(r)
    if x is None:
        continue
    for g in grp(r):
        for c in (cls(r), "all"):
            k = (g, c, bidx(x, FINE))
            tab[k][0] += 1
            tab[k][1] += r["win"]
hdr = "  ".join(f"{FINE[i]:.2f}-{FINE[i + 1]:.2f}" if FINE[i + 1] < 1e8 else f">{FINE[i]:.2f}" for i in range(len(FINE) - 1))
print("bands: " + hdr)
for g in ("meow", "meow_live", "meow_tc30", "top3"):
    for c in ("all", "large", "other"):
        cells = []
        for i in range(len(FINE) - 1):
            n, w = tab[(g, c, i)]
            cells.append(f"{w}/{n}" if n else "-")
        print(f"{g:10s} {c:6s} " + "  ".join(f"{x:>9s}" for x in cells))

print("\n== 1b. Median ratio at rounds 100/150/200/300/400 (games that reach the round) ==")
for g in ("meow_live", "meow_tc30", "top3"):
    for c in ("large", "other"):
        line = []
        for rnd in (100, 150, 200, 300, 400):
            xs = sorted(ratio(r, rnd) for r in rows if g in grp(r) and cls(r) == c and ratio(r, rnd) is not None)
            line.append(f"r{rnd}: {xs[len(xs) // 2]:.2f} (n={len(xs)})" if xs else f"r{rnd}: -")
        print(f"{g:10s} {c:6s} " + "  ".join(line))

print("\n== 2. What-if: our total length at round 300 times (1+g), our own win rate per coarse band ==")
for who in ("meow", "meow_live"):
    mine = [r for r in rows if who in grp(r) and ratio(r) is not None]
    cw = defaultdict(lambda: [0, 0])
    for r in mine:
        k = bidx(ratio(r), COARSE)
        cw[k][0] += 1
        cw[k][1] += r["win"]
    rate = {k: v[1] / v[0] for k, v in cw.items()}
    trate = defaultdict(lambda: [0, 0])
    for r in rows:
        if "top3" in grp(r) and ratio(r) is not None:
            k = bidx(ratio(r), COARSE)
            trate[k][0] += 1
            trate[k][1] += r["win"]
    # logistic fit on log ratio, our own games (Newton iterations)
    xs = [math.log(max(0.02, ratio(r))) for r in mine]
    ys = [r["win"] for r in mine]
    a = b = 0.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(xs, ys):
            p = 1 / (1 + math.exp(-(a + b * x)))
            g0 += y - p
            g1 += (y - p) * x
            w = p * (1 - p)
            h00 += w
            h01 += w * x
            h11 += w * x * x
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-12:
            break
        a += (h11 * g0 - h01 * g1) / det
        b += (h00 * g1 - h01 * g0) / det
    base = sum(ys)
    print(f"\n{who}: {len(mine)} games reach round 300, {base} won; own band win rates "
          + ", ".join(f"{rate[k]:.2f}" for k in sorted(rate)) + f"; logistic on log(ratio): a={a:.2f} b={b:.2f}")
    for scope in ("large", "other", "all"):
        line = []
        for g in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.6, 1.0):
            exp_band = exp_log = 0.0
            for r in mine:
                x = ratio(r)
                if scope == "all" or cls(r) == scope:
                    x2 = x * (1 + g)
                else:
                    x2 = x
                exp_band += rate[bidx(x2, COARSE)] - rate[bidx(x, COARSE)]
                exp_log += 1 / (1 + math.exp(-(a + b * math.log(max(0.02, x2))))) - 1 / (1 + math.exp(-(a + b * math.log(max(0.02, x)))))
            line.append(f"+{int(g * 100)}%: {exp_band:+.1f} / {exp_log:+.1f}")
        n_scope = sum(1 for r in mine if scope == "all" or cls(r) == scope)
        print(f"   games moved: {scope:5s} (n={n_scope:3d})  wins by band table / by logistic   " + "   ".join(line))

print("\n== 3. Games that end before round 300 ==")
for who in ("meow", "meow_live", "top3"):
    c = Counter()
    for r in rows:
        if who in grp(r) and ratio(r) is None:
            c[(cls(r), "W" if r["win"] else "L")] += 1
    print(who, dict(c))
