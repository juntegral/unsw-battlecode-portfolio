#!/usr/bin/env python3
"""Collect finished battles of the teams we study (read-only, no tickets).
usage: python3 tools/top3_collect.py [--teams 454,157,306] [--every 240] [--until 2026-10-08T22:00]
Every --every seconds: read the recent battles of each team (tools/online.js team <id> --json) and download the
finished ones that are against a team rated 2000 or more into data/online/top3/<battleId>/.
Index: data/online/top3/index.jsonl (one row per battle)."""
import argparse, datetime, json, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "online", "top3")
KST = datetime.timezone(datetime.timedelta(hours=9))


def node(*args):
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "online.js"), *args], capture_output=True, text=True, cwd=ROOT, timeout=900)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teams", default="454,157,306")
    ap.add_argument("--every", type=int, default=240)
    ap.add_argument("--until", default="2026-10-08T22:00")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    index = os.path.join(OUT, "index.jsonl")
    seen = set()
    if os.path.exists(index):
        seen = {json.loads(l)["battle"] for l in open(index)}
    until = datetime.datetime.fromisoformat(args.until).replace(tzinfo=KST)
    while datetime.datetime.now(KST) < until:
        for team in args.teams.split(","):
            info = node("team", team, "--json")
            if not info:
                continue
            for b in info.get("recent") or []:
                bid = b.get("id")
                if not bid or bid in seen or b.get("outcome") == "live" or "pending" in (b.get("results") or []):
                    continue
                opp = {"id": b.get("opponentId"), "name": b.get("opponent"), "rating": b.get("opponentElo")}
                if (opp.get("rating") or 0) < 2000 or len(b.get("results") or []) < 5:
                    continue
                subprocess.run(["node", os.path.join(ROOT, "tools", "online.js"), "download", str(bid), "--out", f"top3/{bid}",
                                "--no-events", "--purpose", f"study of team {team}"], cwd=ROOT, capture_output=True, text=True, timeout=1800)
                seen.add(bid)
                with open(index, "a") as f:
                    f.write(json.dumps({"battle": bid, "team": int(team), "opponent": opp, "row": b,
                                        "at": datetime.datetime.now(KST).isoformat(timespec="seconds")}) + "\n")
        if args.once:
            break
        time.sleep(args.every)


if __name__ == "__main__":
    main()
