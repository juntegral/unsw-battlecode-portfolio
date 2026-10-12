#!/usr/bin/env python3
"""d_md.py: the classification tables of question (a) as markdown (sub-session A4).  Writes d_out/md_class.md.

Same data and kinds as d_tab.py (d_out/cls through d_tab.load()); only the layout differs, so that the report's
tables are generated and not typed.
"""
from collections import Counter, defaultdict

import d_tab

COLS = [("meow", "meow, all 401"), ("meow live", "meow live bot"), ("meow cand", "meow candidates"), ("opp", "our opponents"),
        ("forgot", "forgot"), ("SSS", "SSS"), ("Vibing++", "Vibing++")]
KINDS = [("alive", "alive at the end"),
         ("ram: stepped in", "rammed: stepped into reach (killer in view, began outside reach, a safe step existed)"),
         ("ram: stayed in", "rammed: stayed in reach (killer in view, began inside reach, a safe step existed)"),
         ("ram: cornered", "rammed: cornered (killer in view, no one-step move out of reach)"),
         ("ram: unseen", "rammed: killer's head not in her view at the start of her last turn"),
         ("ram: model miss", "rammed on a cell my reach model called safe"),
         ("boxed: ally body", "boxed in: a team-mate's body or head on her last exit"),
         ("boxed: terrain dead end", "boxed in: terrain dead end (kelp and her own body)"),
         ("boxed: enemy", "boxed in: an enemy body on her last exit (alone or with a team-mate)"),
         ("boxed: own body", "boxed in: only her own body, not a dead end"),
         ("own ram", "she moved her head into a head"),
         ("other", "other (portal step onto a body, stride crash, no action with a free cell, team-mate rams her)")]
MERGE = {"boxed: ally+enemy": "boxed: enemy", "boxed: enemy body": "boxed: enemy", "crash: portal": "other", "crash: stride": "other",
         "crash: other": "other", "no action": "other", "ally ram": "other"}
BANDS = ("0-49", "50-99", "100-299", "300+")


def kind_of(x):
    return MERGE.get(x["kind"], x["kind"])


def main():
    recs = d_tab.load()
    by = defaultdict(list)
    for x in recs:
        gs = set(x["groups"])
        if "meow" in gs and "meow live" not in gs:
            gs.add("meow cand")
        for g in gs:
            by[g].append(x)
    out = []
    w = out.append
    w("| Kind of end | " + " | ".join(c[1] for c in COLS) + " |")
    w("|---|" + "---|" * len(COLS))
    for k, name in KINDS:
        cells = []
        for c, _ in COLS:
            n = len(by[c])
            v = sum(1 for x in by[c] if kind_of(x) == k)
            cells.append(f"{v} ({100 * v / n:.0f}%)")
        w(f"| {name} | " + " | ".join(cells) + " |")
    w("| games | " + " | ".join(str(len(by[c])) for c, _ in COLS) + " |")
    w("")
    w("By run (counts; \"-old\" runs and the two ladder downloads are the live bot):")
    w("")
    runs = ["dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old", "stride-new", "passage2-test-new",
            "qh31-test-new", "tc30-test-new", "tc30-dev1b-new"]
    w("| Kind of end | " + " | ".join(r.replace("-test", "") for r in runs) + " |")
    w("|---|" + "---|" * len(runs))
    for k, name in KINDS:
        w(f"| {name.split(' (')[0].split(':')[0] if False else k} | " + " | ".join(str(sum(1 for x in by['run ' + r] if kind_of(x) == k)) for r in runs) + " |")
    w("| games | " + " | ".join(str(len(by["run " + r])) for r in runs) + " |")
    w("")
    w("By round band (rounds 0-49 / 50-99 / 100-299 / 300+), deaths only:")
    w("")
    cols2 = ["meow", "meow live", "opp", "forgot", "SSS", "Vibing++"]
    w("| Kind of death | " + " | ".join(dict(COLS).get(c, c) for c in cols2) + " |")
    w("|---|" + "---|" * len(cols2))
    for k, name in KINDS[1:]:
        cells = []
        for c in cols2:
            cnt = Counter(d_tab.band(x["det"]["r"]) for x in by[c] if kind_of(x) == k)
            cells.append(" / ".join(str(cnt[b]) for b in BANDS))
        w(f"| {k} | " + " | ".join(cells) + " |")
    cells = []
    for c in cols2:
        cnt = Counter(d_tab.band(x["det"]["r"]) for x in by[c] if x["kind"] != "alive")
        cells.append(" / ".join(str(cnt[b]) for b in BANDS))
    w("| all deaths | " + " | ".join(cells) + " |")
    w("")
    w("By queen rules (meow; rules are on when the map has more than 600 cells) and by map size:")
    w("")
    w("| Kind of end | all runs, rules on (256 games) | all runs, rules off (145) | live bot, rules on (175) | live bot, rules off (100) | 600 cells or fewer | 601-1,500 | over 1,500 |")
    w("|---|---|---|---|---|---|---|---|")
    for k, name in KINDS:
        row = []
        for grp in ("meow", "meow live"):
            on = [x for x in by[grp] if x["cells"] > 600]
            off = [x for x in by[grp] if x["cells"] <= 600]
            a, b = sum(1 for x in on if kind_of(x) == k), sum(1 for x in off if kind_of(x) == k)
            row += [f"{a} ({100 * a / len(on):.0f}%)", f"{b} ({100 * b / len(off):.0f}%)"]
        for lo, hi in ((0, 600), (600, 1500), (1500, 99999)):
            row.append(str(sum(1 for x in by["meow"] if kind_of(x) == k and lo < x["cells"] <= hi)))
        w(f"| {k} | " + " | ".join(row) + " |")
    w("")
    w("Her length at death, and for rams the killer's length and the steps of its ramming move (meow, all runs; in brackets the top three together):")
    w("")
    w("| Kind of death | n | her length 2 / 3 / 4 / 5 / 6+ | killer's length 2 / 3 / 4 / 5-9 / 10+ | killer's steps 1 / 2 / 3 / 4 / 5+ |")
    w("|---|---|---|---|---|")

    def lens(xs):
        ql = Counter(min(x["det"]["len"], 6) for x in xs)
        return " / ".join(str(ql[i]) for i in range(2, 7))

    def kl(xs):
        c = Counter("2" if x["det"]["k"]["len"] <= 2 else "3" if x["det"]["k"]["len"] == 3 else "4" if x["det"]["k"]["len"] == 4 else "5-9" if x["det"]["k"]["len"] <= 9 else "10+" for x in xs)
        return " / ".join(str(c[i]) for i in ("2", "3", "4", "5-9", "10+"))

    def ks(xs):
        c = Counter(min(x["det"]["k"]["steps"], 5) for x in xs)
        return " / ".join(str(c[i]) for i in range(1, 6))

    for k, name in KINDS[1:]:
        xs = [x for x in by["meow"] if kind_of(x) == k]
        ys = [x for x in by["top three"] if kind_of(x) == k]
        if not xs and not ys:
            continue
        ram = k.startswith("ram")
        w(f"| {k} | {len(xs)} ({len(ys)}) | {lens(xs)} ({lens(ys)}) | " + (f"{kl(xs)} ({kl(ys)}) | {ks(xs)} ({ks(ys)}) |" if ram else "- | - |"))
    w("")
    w("What the game became (meow, all runs; in brackets the live bot): won by wipe-out / lost by wipe-out / round 500 won / round 500 lost with her queen dead too / round 500 lost with her queen alive:")
    w("")
    w("| Kind of end | games | wipe-out won | wipe-out lost | round 500 won | round 500 lost, both queens dead | round 500 lost, her queen alive |")
    w("|---|---|---|---|---|---|---|")
    tot = Counter()
    totl = Counter()
    for k, name in KINDS:
        xs = [x for x in by["meow"] if kind_of(x) == k]
        if not xs:
            continue
        c = Counter()
        cl = Counter()
        for x in xs:
            o = d_tab.outcome(x)
            key = o if o.startswith("wipe") else "r500 W" if " W " in o else o
            c[key] += 1
            tot[key] += 1
            if "meow live" in x["groups"]:
                cl[key] += 1
                totl[key] += 1
        nl = sum(1 for x in xs if "meow live" in x["groups"])
        w(f"| {k} | {len(xs)} ({nl}) | " + " | ".join(f"{c[q]} ({cl[q]})" for q in ("wipe W", "wipe L", "r500 W", "r500 L her dead", "r500 L her alive")) + " |")
    w(f"| all | {len(by['meow'])} ({len(by['meow live'])}) | " + " | ".join(f"{tot[q]} ({totl[q]})" for q in ("wipe W", "wipe L", "r500 W", "r500 L her dead", "r500 L her alive")) + " |")
    open("d_out/md_class.md", "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
