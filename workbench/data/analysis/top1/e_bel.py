#!/usr/bin/env python3
"""What our dragons believe about their leader (meow only; games whose sonar pings are readable, see e_belief.py).

Our bot's feeding and its pearl zone both hang on one value per dragon: the id, length and position of the leader it
has heard of. This script compares that belief with the board, every 5 rounds:
  1. per 25-round block: share of our dragons (all but the true longest) whose believed leader is the true longest /
     is dead / is alive but dead-or-less-than-half-as-long as the true longest; how many could feed the true longest by
     our rules (believe it, within 15 cells, at most half its length) against the same without the belief test;
  2. the same split by map class and for round-500 games with both queens dead;
  3. after every split in which our longest dragon (8+) kept 2-3 segments and gave the rest to a new id: how many
     rounds until half of our dragons believe the new id, and what the team believed meanwhile;
  4. our `noaction` (feeder) deaths: was the dragon it died next to the team's true longest?
Reads e_out/w4. Output: e_out/bel.txt
"""
from collections import Counter, defaultdict

import e_data as D

P = D.Out("bel.txt")


def readable(r):
    d = r.d
    return d["nping"] > 1000 and d["badping"] / d["nping"] < 0.05


def part1(recs, title):
    n = len(recs)
    if not n:
        return
    P("\n--- %s: %d games with readable sonar" % (title, n))
    P("    %-72s" % "rounds" + "".join("%9s" % ("%d-%d" % (b, b + 24)) for b in range(150, 500, 25)))
    acc = defaultdict(lambda: [0] * 12)
    for r in recs:
        for row in r.s["bel"]:
            if row[1] == 0:
                continue
            b = row[0] // 25 * 25
            a = acc[b]
            a[0] += row[1]      # senders
            a[1] += row[2]      # true
            a[2] += row[3]      # dead
            a[3] += row[13]     # small or dead
            a[4] += row[14]     # eligible n
            a[5] += row[15]     # eligible len
            a[6] += row[16]     # geo n
            a[7] += row[17]     # geo len
            a[8] += 1
            a[9] += row[12]     # age
            a[10] += 1 if row[2] * 2 >= row[1] else 0
            a[11] += row[10]    # true leader length
    def line(name, fn):
        P("    %-72s" % name + "".join("%9s" % (fn(acc[b]) if acc[b][8] else "-") for b in range(150, 500, 25)))
    line("dragons whose believed leader is the true longest", lambda a: D.pct(a[1], a[0]))
    line("... is a dead dragon", lambda a: D.pct(a[2], a[0]))
    line("... is dead or less than half as long as the true longest", lambda a: D.pct(a[3], a[0]))
    line("samples (every 5 rounds) in which at least half believe the true longest", lambda a: D.pct(a[10], a[8]))
    line("mean age of the news, rounds", lambda a: "%.1f" % (a[9] / a[8]))
    line("true longest, mean length", lambda a: "%.1f" % (a[11] / a[8]))
    line("could feed it by our rules (believe it, within 15, half its length): dragons", lambda a: "%.1f" % (a[4] / a[8]))
    line("... the same without the belief test", lambda a: "%.1f" % (a[6] / a[8]))
    line("could feed it: their summed length", lambda a: "%.1f" % (a[5] / a[8]))
    line("... the same without the belief test", lambda a: "%.1f" % (a[7] / a[8]))


def part3(recs, title):
    """After a leader split that keeps 2-3: rounds until half of the senders believe the true longest again."""
    waits = []
    never = 0
    during = Counter()
    for r in recs:
        bel = r.s["bel"]
        for x in r.s["splits"]:
            if not (x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= 150):
                continue
            r0 = x[0]
            got = None
            for row in bel:
                if row[0] <= r0:
                    continue
                if row[0] > r0 + 60:
                    break
                if row[1] and row[2] * 2 >= row[1]:
                    got = row[0] - r0
                    break
                # what is believed meanwhile
                if row[1]:
                    during["the top believed id is dead" if row[9] == 0 else
                           "the top believed id is alive but shorter than half the true longest" if row[9] * 2 <= row[10] else "other"] += 1
            if got is None:
                never += 1
            else:
                waits.append(got)
    if waits or never:
        w = sorted(waits)
        P("    %s: %d leader splits that kept 2-3 (leader 8+, from round 150); half of the team believes the true longest again after: "
          "median %s rounds, quartiles %s / %s; not within 60 rounds (or another split first): %d" % (
              title, len(waits) + never, D.med(w), w[len(w) // 4] if w else "-", w[(3 * len(w)) // 4] if w else "-", never))
        tot = sum(during.values())
        P("       5-round samples in between: " + ", ".join("%s %s" % (k, D.pct(v, tot)) for k, v in during.most_common()))


def part4(recs, title):
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    c = Counter()
    pearls = Counter()
    for r in recs:
        for x in r.s["deaths"]:
            if not (x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]]):
                continue
            if x[DI["tid"]] < 0:
                k = "no own dragon twice as long within 8 path steps"
            elif x[DI["tlong"]] == 1:
                k = "next to the team's true longest"
            elif x[DI["tlen"]] >= 8:
                k = "next to another own dragon of 8+"
            else:
                k = "next to another own dragon under 8"
            c[k] += 1
            pearls[k + "|drop"] += x[DI["drop"]]
            pearls[k + "|fed"] += x[DI["e_t"]]
            pearls[k + "|lin"] += x[DI["e_lin"]]
            pearls[k + "|enemy"] += x[DI["e_e"]]
            pearls[k + "|len"] += x[2]
    tot = sum(c.values())
    P("    %s: %d `noaction` deaths (%.1f a game)" % (title, tot, tot / len(recs)))
    for k, v in c.most_common():
        P("       %-52s %5d = %s | their length %d, pearls dropped %d: the dragon next to them ate %s, the final lineage ate %s, the enemy %s" % (
            k, v, D.pct(v, tot), pearls[k + "|len"], pearls[k + "|drop"], D.pct(pearls[k + "|fed"], pearls[k + "|drop"]),
            D.pct(pearls[k + "|lin"], pearls[k + "|drop"]), D.pct(pearls[k + "|enemy"], pearls[k + "|drop"])))


def main():
    recs = [r for r in D.rows() if r.me and r.study]
    rd = [r for r in recs if readable(r)]
    sets = Counter(r.set for r in rd)
    P("meow study games: %d; with readable sonar: %d (%s)" % (len(recs), len(rd), dict(sets)))
    part1([r for r in rd if not r.big], "maps of 1,200 cells or fewer, all games that reach the round")
    part1([r for r in rd if not r.big and r.bd], "maps of 1,200 cells or fewer, round-500 games with both queens dead")
    part1([r for r in rd if r.big], "maps over 1,200 cells, all games")
    part1([r for r in rd if r.big and r.bd], "maps over 1,200 cells, round-500 games with both queens dead")
    P("\n--- after a leader split")
    part3([r for r in rd if not r.big], "maps of 1,200 cells or fewer")
    part3([r for r in rd if r.big], "maps over 1,200 cells")
    P("\n--- whom our feeders die next to (all meow study games, sonar not needed)")
    part4([r for r in recs if not r.big], "maps of 1,200 cells or fewer")
    part4([r for r in recs if r.big], "maps over 1,200 cells")
    part4([r for r in recs if r.bd], "round-500 games with both queens dead, all maps")


if __name__ == "__main__":
    main()
