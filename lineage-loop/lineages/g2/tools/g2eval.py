#!/usr/bin/env python3
"""g2 local evaluator: runs sandboxed matches through the official unswbc 1.1.0 engine API
and records per-team longest length, total length, deaths by cause and CPU points.
usage: g2eval.py OUT.jsonl OURBOT OPP[,OPP...] SEEDS(e.g. 1-3) [MAPS comma|all] [--jobs 2] [--one-side]
Our bot plays both sides (A and B) of every map/seed unless --one-side."""
import sys, os, json, time, pathlib, multiprocessing as mp
R = "~/01. Project/개인 프로젝트/UNSW"
sys.path[:0] = [R + "/.unswbc-110", R + "/.venv-ppo/lib/python3.13/site-packages"]
os.environ.setdefault("UNSWBC_NO_VSCODE", "1"); os.environ.setdefault("NO_COLOR", "1"); os.environ.setdefault("UNSWBC_NO_UPDATE", "1")
MAPDIR = R + "/maps/online-20260927"

def resolve(bot):
    from unswbc import run as ur
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        return ur._resolve(bot, True)

def play(task):
    mp_, bot_a, bot_b, seed = task
    from unswbc.engine import EngineModule, DEBUG_LIMITS
    from unswbc.sandbox import SandboxBot, SandboxPool, WasmPool, warm_interpreter
    ra, rb = resolve(bot_a), resolve(bot_b)
    if "python" in (ra[2], rb[2]):
        warm_interpreter()
    pools = {}
    for team, (argv, d, kind) in (("A", ra), ("B", rb)):
        maker = WasmPool if kind == "wasm" else SandboxPool
        pools[team] = maker(argv, cwd=str(d), key=f"{seed:016x}-{team.lower()}")
    live, teams, lastlen, deaths, errors = {}, {}, {}, [], []
    pts = {"A": [0, 0], "B": [0, 0]}  # max, sum
    turns = {"A": 0, "B": 0}
    snap = {}  # round -> {team: max length}
    t0 = time.time()

    def spawn(did, init):
        team = next((l.split()[1] for l in init.decode().splitlines() if l.startswith("TEAM")), "A")
        teams[did] = team
        live[did] = SandboxBot(pools[team], init=init, name=str(did))

    def reply(did, block):
        head = block.split(b"\n", 4)
        try:
            rnd = int(head[0].split()[1]); ln = int(head[2].split()[1])
            lastlen[did] = (rnd, ln)
            if rnd % 50 == 49:
                s = snap.setdefault(rnd, {"A": 0, "B": 0})
                s[teams[did]] = max(s[teams[did]], ln)
        except Exception:
            pass
        bot = live[did]
        out = bot.ask(block)
        if bot.error is not None:
            errors.append((teams[did], did, str(bot.error)[:200]))
        m = getattr(bot, "live", None)
        if m and m[0]:
            t = teams[did]; pts[t][0] = max(pts[t][0], m[0]); pts[t][1] += m[0]; turns[t] += 1
        return out

    def death(did, rnd, reason):
        deaths.append((rnd, teams.get(did, "?"), reason, lastlen.get(did, (0, 0))[1]))
        bot = live.pop(did, None)
        if bot is not None:
            bot.stop()

    try:
        res = EngineModule().run(pathlib.Path(mp_).read_bytes(), reply, death, spawn, lambda l: None, DEBUG_LIMITS, seed)
    finally:
        for b in live.values():
            b.stop()
        for p in pools.values():
            p.close()
    longest = {"A": 0, "B": 0}
    for did in live:
        longest[teams[did]] = max(longest[teams[did]], lastlen.get(did, (0, 0))[1])
    dc = {"A": {}, "B": {}}
    for rnd, t, r, ln in deaths:
        if t in dc:
            dc[t][r] = dc[t].get(r, 0) + 1
    return {"map": pathlib.Path(mp_).stem, "A": bot_a, "B": bot_b, "seed": seed, "winner": res.winner,
            "reason": res.end_reason, "rounds": res.rounds + 1, "dragons": [res.a_dragons, res.b_dragons],
            "total": [res.a_length, res.b_length], "longest": [longest["A"], longest["B"]],
            "deaths": dc, "bigdeaths": [(r, t, c, l) for r, t, c, l in deaths if l >= 8],
            "maxpts": [pts["A"][0], pts["B"][0]], "meanpts": [pts["A"][1] // max(1, turns["A"]), pts["B"][1] // max(1, turns["B"])],
            "snap": snap, "errors": errors[:5], "secs": round(time.time() - t0, 1)}

def main():
    argv = sys.argv[1:]; jobs = 2
    if "--jobs" in argv:
        i = argv.index("--jobs"); jobs = int(argv[i + 1]); del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    one = "--one-side" in sys.argv
    out, ours, opps, seeds = args[0], args[1], args[2].split(","), args[3]
    a, _, b = seeds.partition("-"); seeds = list(range(int(a), int(b or a) + 1))
    maps = sorted(str(p) for p in pathlib.Path(MAPDIR).glob("*.map"))
    if len(args) > 4 and args[4] != "all":
        want = args[4].split(","); maps = [m for m in maps if pathlib.Path(m).stem in want]
    def botpath(b):
        if os.path.isdir(b): return os.path.abspath(b)
        return R + "/bots/" + b
    ours = botpath(ours)
    tasks = []
    for opp in opps:
        o = botpath(opp)
        for s in seeds:
            for m in maps:
                tasks.append((m, ours, o, s))
                if not one:
                    tasks.append((m, o, ours, s))
    for b in {t[1] for t in tasks} | {t[2] for t in tasks}:
        resolve(b)  # build once
    with mp.get_context("spawn").Pool(jobs) as pool, open(out, "a") as f:
        for r in pool.imap_unordered(play, tasks):
            r["ours"] = ours
            f.write(json.dumps(r) + "\n"); f.flush()
            side = 0 if r["A"] == ours else 1
            opp = os.path.basename(r["B"] if side == 0 else r["A"])
            res = "D" if r["winner"] is None else ("W" if r["winner"] == "AB"[side] else "L")
            print(f"{r['map']:18s} s{r['seed']} {'AB'[side]} vs {opp:18s} {res} r{r['rounds']:3d} long {r['longest'][side]:3d}-{r['longest'][1-side]:3d} tot {r['total'][side]:4d}-{r['total'][1-side]:4d} n {r['dragons'][side]}-{r['dragons'][1-side]} maxpts {r['maxpts'][side]/1e6:.1f}M {r['secs']}s", flush=True)

if __name__ == "__main__":
    main()
