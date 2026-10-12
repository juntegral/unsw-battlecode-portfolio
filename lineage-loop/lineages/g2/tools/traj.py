#!/usr/bin/env python3
"""Record (round, id, team, x, y, length) for every dragon turn. usage: traj.py MAP BOTA BOTB SEED OUT.tsv"""
import sys, os, pathlib
sys.path.insert(0, os.path.dirname(__file__))
import g2eval
from unswbc.engine import EngineModule, DEBUG_LIMITS
from unswbc.sandbox import SandboxBot, SandboxPool, WasmPool
mp_, a, b, seed, outp = sys.argv[1:6]; seed = int(seed)
ra, rb = g2eval.resolve(a), g2eval.resolve(b)
pools = {}
for team, (argv, d, kind) in (("A", ra), ("B", rb)):
    pools[team] = (WasmPool if kind == "wasm" else SandboxPool)(argv, cwd=str(d), key=f"{seed:016x}-{team.lower()}")
live, teams, rows, deaths = {}, {}, [], []
def spawn(i, init):
    t = next((l.split()[1] for l in init.decode().splitlines() if l.startswith("TEAM")), "A"); teams[i] = t
    live[i] = SandboxBot(pools[t], init=init, name=str(i))
def reply(i, block):
    L = block.decode().split("\n")
    rnd = int(L[0].split()[1]); ln = int(L[2].split()[1])
    nm = int(L[4].split()[1]); k = 5 + nm
    if L[k].startswith("ECHOES"): k += 1
    x, y = L[k + 24].split()[:2]
    out = live[i].ask(block)
    act = " ".join(l for l in out.decode(errors="replace").split("\n") if l.startswith(("MOVE", "SPLIT")))
    rows.append((rnd, i, teams[i], int(x), int(y), ln, act))
    return out
def death(i, rnd, reason):
    deaths.append((rnd, i, teams.get(i), reason))
    b_ = live.pop(i, None)
    if b_: b_.stop()
try:
    res = EngineModule().run(pathlib.Path(mp_).read_bytes(), reply, death, spawn, lambda l: None, DEBUG_LIMITS, seed)
finally:
    for x in live.values(): x.stop()
    for p in pools.values(): p.close()
with open(outp, "w") as f:
    for r in rows: f.write("\t".join(map(str, r)) + "\n")
    for d in deaths: f.write("D\t" + "\t".join(map(str, d)) + "\n")
print("winner", res.winner, "rounds", res.rounds + 1)
