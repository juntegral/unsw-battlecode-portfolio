#!/usr/bin/env python3
"""Capture engine input blocks + replies for chosen dragons/rounds and render the 7x7 view.
usage: capture.py MAP BOTA BOTB SEED DID R1-R2"""
import sys, os, pathlib
sys.path.insert(0, os.path.dirname(__file__))
import g2eval
from unswbc.engine import EngineModule, DEBUG_LIMITS
from unswbc.sandbox import SandboxBot, SandboxPool, WasmPool
mp_, a, b, seed, did, rr = sys.argv[1:7]
seed = int(seed); did = int(did); r1, r2 = map(int, rr.split('-'))
ra, rb = g2eval.resolve(a), g2eval.resolve(b)
pools = {}
for team, (argv, d, kind) in (("A", ra), ("B", rb)):
    pools[team] = (WasmPool if kind == "wasm" else SandboxPool)(argv, cwd=str(d), key=f"{seed:016x}-{team.lower()}")
live, teams = {}, {}
def spawn(i, init):
    t = next((l.split()[1] for l in init.decode().splitlines() if l.startswith("TEAM")), "A"); teams[i] = t
    live[i] = SandboxBot(pools[t], init=init, name=str(i))
def render(block):
    L = block.decode().split("\n")
    rnd = L[0]; tiles = []; i = 0
    while not L[i].startswith("DRAGON_BODIES"): i += 1
    tl = [l for l in L[:i] if len(l.split()) == 4 and not l.startswith("ECHOES")][-49:]
    nb = int(L[i].split()[1]); bodies = [l.split() for l in L[i+1:i+1+nb]]
    he = [l.split() for l in L[i+1+nb:i+1+nb+8]]; ve = [l.split() for l in L[i+1+nb+8:i+1+nb+15]]
    pos = {}
    for tm, idd, x, y, f, h in bodies: pos[(int(x), int(y))] = (tm, idd, f, h)
    out = [rnd + " " + " ".join(L[1:5])]
    for r in range(8):
        out.append("".join("+" + ({"." :" ", "w": "-"}.get(he[r][c], "~")) for c in range(7)) + "+")
        if r == 7: break
        row = ""
        for c in range(8):
            ch = {".": " ", "w": "|"}.get(ve[r][c], "~")
            row += ch
            if c < 7:
                x, y, p, t = map(int, tl[r * 7 + c].split())
                if (x, y) in pos:
                    tm, idd, f, h = pos[(x, y)]
                    row += (tm if h == "1" else tm.lower()) if idd != str(did) else ("@" if h == "1" else f.lower())
                else: row += "*" if p else ("." if t >= 0 else " ")
        out.append(row)
    return "\n".join(out)
def reply(i, block):
    out = live[i].ask(block)
    if i == did:
        rnd = int(block.split(b"\n", 1)[0].split()[1])
        if r1 <= rnd <= r2:
            print(render(block)); print("-> " + out.decode().replace("\n", " | ")); print()
    return out
def death(i, rnd, reason):
    if i == did: print(f"DIED round {rnd} reason {reason}")
    b_ = live.pop(i, None)
    if b_: b_.stop()
try:
    EngineModule().run(pathlib.Path(mp_).read_bytes(), reply, death, spawn, lambda l: None, DEBUG_LIMITS, seed)
finally:
    for x in live.values(): x.stop()
    for p in pools.values(): p.close()
