#!/usr/bin/env python3
"""a_build.py: assemble deep-read.md from a_head.md, a_g01.md, a_g02.md, a_tail.md (sub-session A).

Before the "Decisive moment" line of every game it inserts three bullets taken from the digest of that game
(a_out/dg_<id>.txt, or dg/<id>.txt for the two games of the first pass): contact counts, roles (who rams, by
attacker length and number of steps) and sonar ping counts. Nothing else is changed.
"""
import ast
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def digest(gid):
    for p in (f"a_out/dg_{gid}.txt", f"dg/{gid}.txt"):
        p = os.path.join(HERE, p)
        if os.path.exists(p):
            return open(p).read()
    return ""


def lit(text, pattern):
    m = re.search(pattern, text)
    if not m:
        return None
    try:
        return ast.literal_eval(m.group(1))
    except Exception:
        return None


OUT = {"left": "left", "RAMMED": "rammed by an own dragon", "it rammed someone": "rammed an own dragon",
       "died noaction": "killed itself", "still near at end/queen death": "still near when the queen died or the game ended"}


def bullets(gid):
    t = digest(gid)
    if not t:
        return []
    own100 = lit(t, r"rams on enemy heads by own: per 100 rounds (\{.*?\});") or {}
    ownby = lit(t, r"rams on enemy heads by own: per 100 rounds \{.*?\}; by attacker length/steps (\{.*?\})\n") or {}
    opp100 = lit(t, r"rams on enemy heads by opp: per 100 rounds (\{.*?\});") or {}
    m = re.search(r"within 6 steps of the own queen: (\d+) episodes; outcomes (\{.*?\})\n", t)
    hist = lit(t, r"length histogram every 100 rounds: (\[.*?\])\n") or []
    son = re.search(r"sonar pings per 100 rounds: own (\{.*?\}) \| opp (\{.*?\})", t)

    def grp(lens, adjacent):
        return sum(v for (ln, st), v in ownby.items() if ln in lens and (st == "adjacent") == adjacent)

    out = []
    line = f"- **Mid-game contact (digest counts).** Own rams on enemy heads: {sum(own100.values())} (per 100 rounds {', '.join(str(own100.get(k, 0)) for k in range(5))}); the opponent's rams on own heads: {sum(opp100.values())}."
    if m:
        oc = ast.literal_eval(m.group(2))
        line += f" Enemy heads that came within 6 steps of the own queen: {m.group(1)} (" + ", ".join(f"{OUT.get(k, k)} {v}" for k, v in oc.items()) + ")." if oc else f" Enemy heads that came within 6 steps of the own queen: {m.group(1)}."
    out.append(line)
    if ownby:
        out.append("- **Roles (digest counts).** Own rams by attacker: 2-long from the next cell "
                   f"{grp(('2',), True)}, 2-long with a 2-3-step move {grp(('2',), False)}, 3-4-long from the next cell {grp(('3-4',), True)}, "
                   f"3-4-long with a 2-4-step move {grp(('3-4',), False)}, 5-9-long {grp(('5-9',), True) + grp(('5-9',), False)}, "
                   f"10 or longer {grp(('10-19', '20+'), True) + grp(('10-19', '20+'), False)}."
                   + (" Own lengths at r200: " + ", ".join(f"{k}-long {v}" for k, v in sorted(dict(hist)[200].items(), key=lambda kv: (len(kv[0]), kv[0]))) + "." if hist and 200 in dict(hist) else ""))
    else:
        out.append("- **Roles (digest counts).** No own ram on an enemy head in this game.")
    if son:
        o, p = ast.literal_eval(son.group(1)), ast.literal_eval(son.group(2))
        out.append(f"- **Sonar.** Rays sent per 100 rounds: own {', '.join(str(o.get(k, 0)) for k in range(5))}; opponent {', '.join(str(p.get(k, 0)) for k in range(5))}. The values are packed and cannot be read.")
    return out


def games(path):
    res = []
    gid = None
    for line in open(os.path.join(HERE, path)).read().split("\n"):
        m = re.match(r"### \d+\. (\d+) ", line)
        if m:
            gid = m.group(1)
        if line.startswith("- Decisive moment:") and gid:
            res.extend(bullets(gid))
        res.append(line)
    return "\n".join(res)


parts = [open(os.path.join(HERE, "a_head.md")).read(), games("a_g01.md"), games("a_g02.md"), open(os.path.join(HERE, "a_tail.md")).read()]
open(os.path.join(HERE, "deep-read.md"), "w").write("".join(p if p.endswith("\n") else p + "\n" for p in parts))
print("deep-read.md written:", sum(p.count("\n") for p in parts), "lines")
