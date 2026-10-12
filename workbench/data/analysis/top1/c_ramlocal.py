#!/usr/bin/env python3
"""c_ramlocal.py <team_id> <size> [max_games=200] [jobs=4] [opp_ids]: who eats the pearls of a ram, and why (all games).

For every ram between the two teams (a head moves into an enemy head, both die) in the team's games against 2000+
opponents on maps of the given size (Schooltime left out; opp_ids = comma list restricts the opponents):
  - heads of each team within 4 and within 8 path steps of the ram cell at that moment (the two dying dragons not counted)
  - every pearl the two corpses drop: eaten by which team, how many rounds later, or not eaten within 20 rounds
Output: pearls eaten by the team / by the enemy / left, split by the local head balance (own heads within 8 steps minus
enemy heads within 8 steps) and by who started the ram; the mean wait; the same split by round phase.
Writes one JSON line per game to c_out/ramlocal_<team>_<size>.jsonl (rams with their counts) for later use.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import Hooks2, Walk2  # noqa: E402

LOOK = 20


class R(Hooks2):
    def __init__(self):
        self.rams = []
        self.by_dead = {}
        self.pending_victim = None

    def death(self, g, did, reason, length, body, actor):
        if reason != "headon":
            return
        if did == actor:
            # the mover dies second; its pearls belong to the ram opened by its victim's death
            pv = self.pending_victim
            self.pending_victim = None
            if pv is not None and pv[0] == did:
                self.by_dead[did] = pv[1]
            return
        # the victim dies first: open the ram record here so that its pearls are attributed
        self.pending_victim = None
        if actor is None or actor not in g.bodies:
            return
        vid, vside, vlen, cell = did, g.teams[did], length, body[0]
        rside = g.teams[actor]
        if rside == vside:
            return
        b = g.board
        near = b.bfs(cell, 8)
        cnt = Counter()
        for d2, body2 in g.bodies.items():
            if d2 == actor or d2 == vid:
                continue
            dd = near.get(body2[0])
            if dd is not None:
                s2 = g.teams[d2]
                cnt[(s2, 8)] += 1
                if dd <= 4:
                    cnt[(s2, 4)] += 1
        rec = dict(round=g.round, rside=rside, rlen=g.act_start[1] if g.act_start else 0, vlen=vlen, cell=cell,
                   A4=cnt[("A", 4)], A8=cnt[("A", 8)], B4=cnt[("B", 4)], B8=cnt[("B", 8)], pearls=[])
        rec["units"] = {s: sum(1 for d2 in g.bodies if g.teams[d2] == s) for s in "AB"}
        self.by_dead[vid] = len(self.rams)
        self.pending_victim = (actor, len(self.rams))
        self.rams.append(rec)

    def pearl_new(self, g, cell, origin):
        if origin[0] == "corpse" and origin[3] == "headon":
            i = self.by_dead.get(origin[2])
            if i is not None:
                self.rams[i]["pearls"].append([origin[1], None, None])   # corpse side, eater side, wait

    def eat(self, g, did, cell, origin):
        if origin[0] == "corpse" and origin[3] == "headon":
            i = self.by_dead.get(origin[2])
            if i is not None:
                ram = self.rams[i]
                for p in ram["pearls"]:
                    if p[0] == origin[1] and p[1] is None:
                        p[1] = g.teams[did]
                        p[2] = g.round - ram["round"]
                        break


def work(job):
    gid, path = job
    r = R()
    try:
        Walk2(path).run(r)
    except Exception as e:  # noqa: BLE001
        return gid, None, repr(e)
    return gid, r.rams, None


if __name__ == "__main__":
    team = int(sys.argv[1])
    size_want = sys.argv[2]
    maxg = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    opps = {int(x) for x in sys.argv[5].split(",")} if len(sys.argv) > 5 else None
    todo = []
    side_of = {}
    for g in csv.DictReader(open("games.csv")):
        if g["map"] == "Schooltime":
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        if size != size_want:
            continue
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            try:
                if float(g[f"team{o}Elo"]) < 2000:
                    continue
            except ValueError:
                continue
            if opps and int(g[f"team{o}Id"]) not in opps:
                continue
            todo.append((g["game_id"], g["replay_path"]))
            side_of[g["game_id"]] = (s, g["map"], int(g[f"team{o}Id"]))
    todo = todo[:: max(1, len(todo) // maxg)][:maxg]
    tag = f"{team}_{size_want}" + ("_" + "_".join(str(x) for x in sorted(opps)) if opps else "")
    out = open(f"c_out/ramlocal_{tag}.jsonl", "w")
    agg = defaultdict(Counter)
    nram = Counter()
    with Pool(jobs) as pool:
        for gid, rams, err in pool.imap_unordered(work, todo):
            if err:
                print("error", gid, err)
                continue
            s, mp, oid = side_of[gid]
            o = "B" if s == "A" else "A"
            out.write(json.dumps({"gid": gid, "side": s, "map": mp, "opp": oid, "rams": rams}) + "\n")
            for ram in rams:
                bal = ram[s + "8"] - ram[o + "8"]
                bcls = "<=-3" if bal <= -3 else "-2..-1" if bal < 0 else "0" if bal == 0 else "+1..+2" if bal <= 2 else ">=+3"
                role = "we rammed" if ram["rside"] == s else "we were rammed"
                ph = "r0-99" if ram["round"] < 100 else "r100-199" if ram["round"] < 200 else "r200-299" if ram["round"] < 300 else "r300+"
                for key in (("all", "all"), ("balance", bcls), ("role", role), ("phase", ph), ("role+balance", role + " " + bcls)):
                    a = agg[key]
                    a["rams"] += 1
                    a["own8"] += ram[s + "8"]
                    a["en8"] += ram[o + "8"]
                    a["own4"] += ram[s + "4"]
                    a["en4"] += ram[o + "4"]
                    for cside, eater, wait in ram["pearls"]:
                        a["pearls"] += 1
                        if eater is None or wait > LOOK:
                            a["left"] += 1
                            if eater == s:
                                a["late_own"] += 1
                            elif eater == o:
                                a["late_en"] += 1
                        elif eater == s:
                            a["own"] += 1
                            a["own_wait"] += wait
                            a["own_from_own" if cside == s else "own_from_enemy"] += 1
                        else:
                            a["en"] += 1
                            a["en_wait"] += wait
                            a["en_from_own" if cside == o else "en_from_enemy"] += 1
    out.close()
    print(f"=== RAM PEARLS team {team}, {size_want} maps, {len(todo)} games" + (f", opponents {sorted(opps)}" if opps else ""))
    print("split | rams | mean heads within 8 steps own / enemy (within 4: own / enemy) | pearls dropped | eaten within 20 rounds by own team % (mean wait) / by the enemy % (mean wait) / not eaten in 20 rounds % | "
          "own team's pearls came from: own corpses / enemy corpses; enemy's from: its own corpses / our corpses")
    order = {"all": 0, "role": 1, "balance": 2, "phase": 3, "role+balance": 4}
    bord = {"<=-3": 0, "-2..-1": 1, "0": 2, "+1..+2": 3, ">=+3": 4}
    for key in sorted(agg, key=lambda k: (order[k[0]], k[1].split(" ")[0:3] if k[0] != "balance" else "", bord.get(k[1].split(" ")[-1], 9), k[1])):
        a = agg[key]
        n, p = max(1, a["rams"]), max(1, a["pearls"])
        print(f"{key[0]:12s} {key[1]:26s} | {a['rams']:5d} | {a['own8'] / n:4.1f} / {a['en8'] / n:4.1f} ({a['own4'] / n:3.1f} / {a['en4'] / n:3.1f}) | {a['pearls']:5d} | "
              f"own {100 * a['own'] / p:3.0f}% ({a['own_wait'] / max(1, a['own']):3.1f}) / enemy {100 * a['en'] / p:3.0f}% ({a['en_wait'] / max(1, a['en']):3.1f}) / left {100 * a['left'] / p:3.0f}% | "
              f"{a['own_from_own']}/{a['own_from_enemy']} ; {a['en_from_own']}/{a['en_from_enemy']}")
