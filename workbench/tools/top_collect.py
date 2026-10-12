#!/usr/bin/env python3
"""Collect replays of battles between top teams (read-only, no tickets).
usage: python3 tools/top_collect.py [--min-elo 2000] [--watch 12] [--every 180] [--cap-gb 6] [--until 2026-10-05T09:00]
Every --every seconds: read the leaderboard, look at the six recent battles of the --watch best teams, and download
finished battles where both teams are at or above --min-elo into data/top1/<battleId>/ (via tools/online.js download).
Index: data/top1/index.jsonl (one row per battle). Stops at --until or when data/top1 reaches --cap-gb.
"""
import argparse, datetime, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "top1")
REPLAYS = os.path.join(ROOT, "data", "online", "top1")  # online.js download writes under data/online/
KST = datetime.timezone(datetime.timedelta(hours=9))


def node(*args, parse=True):
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "online.js"), *args], capture_output=True, text=True, cwd=ROOT, timeout=900)
    if not parse:
        return r.returncode
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def size_gb(path):
    total = 0
    for base, _, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(base, f)) for f in files)
    return total / 1024 ** 3


def log(*a):
    print(datetime.datetime.now(KST).strftime("%m-%d %H:%M:%S"), *a, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-elo", type=int, default=2000)
    ap.add_argument("--watch", type=int, default=12)
    ap.add_argument("--every", type=int, default=180)
    ap.add_argument("--focus", type=int, default=0, help="keep only battles involving the N best teams")
    ap.add_argument("--cap-gb", type=float, default=6.0)
    ap.add_argument("--until", default="2026-10-05T09:00")
    a = ap.parse_args()
    until = datetime.datetime.fromisoformat(a.until).replace(tzinfo=KST)
    os.makedirs(OUT, exist_ok=True)
    index = os.path.join(OUT, "index.jsonl")
    seen = set()
    if os.path.exists(index):
        seen = {json.loads(l)["battle"] for l in open(index) if l.strip()}
    while datetime.datetime.now(KST) < until:
        if size_gb(REPLAYS) >= a.cap_gb:
            log("disk cap reached, stopping")
            return
        board = node("leaderboard", "--top", str(max(a.watch, 40)), "--json") or []
        rows = board if isinstance(board, list) else board.get("rows") or board.get("teams") or []
        elo = {t["id"]: t["elo"] for t in rows}
        name = {t["id"]: t["name"] for t in rows}
        new = 0
        focus = {t["id"] for t in rows[:a.focus]} if a.focus else None
        watch = [t for t in rows if t["elo"] >= a.min_elo][:a.watch]
        for t in watch:
            prof = node("team", str(t["id"]), "--json") or {}
            for b in prof.get("recent", []):
                bid = b["id"]
                if bid in seen or b.get("outcome") == "live" or "pending" in (b.get("results") or []):
                    continue
                if t["elo"] < a.min_elo or (b.get("opponentElo") or 0) < a.min_elo:
                    continue
                if focus and t["id"] not in focus and b.get("opponentId") not in focus:
                    continue  # keep only battles that involve one of the top --focus teams
                dest = os.path.join("top1", str(bid))
                rc = node("download", str(bid), "--out", dest, "--no-events", "--purpose", "top-team study", parse=False)
                if rc != 0:
                    log("download failed", bid)
                    continue
                seen.add(bid)
                new += 1
                with open(index, "a") as f:
                    f.write(json.dumps({"battle": bid, "team": t["id"], "teamName": t["name"], "teamElo": t["elo"],
                                        "opp": b.get("opponentId"), "oppName": b.get("opponent"), "oppElo": b.get("opponentElo"),
                                        "ranked": b.get("ranked"), "wins": b.get("wins"), "losses": b.get("losses"),
                                        "at": b.get("at")}, ensure_ascii=False) + "\n")
            time.sleep(1)
        log(f"poll done: +{new} battles, total {len(seen)}, {size_gb(REPLAYS):.2f} GB")
        time.sleep(a.every)
    log("time limit reached, stopping")


if __name__ == "__main__":
    main()
