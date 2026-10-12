#!/usr/bin/env python3
"""Two copies of the same code: the higher-rated one stays parked (idle), the lower one plays.
When the playing copy has climbed above the parked one it swaps them (activates the parked copy) and says so in #meow.
Plain script, no model. usage: python3 tools/park_watch.py [--once] [--dry-run] [--manual]
--manual only asks a person to swap, as before."""
import datetime, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = datetime.timezone(datetime.timedelta(hours=9))
END = datetime.datetime(2026, 10, 9, 15, tzinfo=KST)
LOG = os.path.join(ROOT, "data/online/park/log.jsonl")
STATE = os.path.join(ROOT, "data/online/park/state.json")
NOTE = os.path.join(ROOT, "data/guide/px-park.txt")
EVERY = 300
MARGIN = 5          # the playing copy must lead by this much before a swap is worth a click
REPEAT = 3600       # the same swap is announced again only after this long
STUCK = 1800        # an automatic swap that keeps failing is handed to a person after this long


def submissions():
    out = subprocess.run(["node", "tools/online.js", "submissions", "--all", "--json"], cwd=ROOT,
                         capture_output=True, text=True, timeout=120, check=True).stdout
    data = json.loads(out)
    return data if isinstance(data, list) else data.get("submissions", [])


def rating(sub):
    value = sub.get("rating")
    return value if type(value) in (int, float) else None


def look(subs):
    """The active copy and the best idle copy of the same code, or a reason there is nothing to compare."""
    active = next((s for s in subs if s.get("status") == "active"), None)
    if not active or not active.get("sourceHash") or rating(active) is None:
        return None, None, "no active submission with a hash and a rating"
    idle = [s for s in subs if s.get("sourceHash") == active["sourceHash"] and s.get("status") == "idle"
            and s["id"] != active["id"] and rating(s) is not None]
    if not idle:
        return active, None, "the active version has no idle copy of the same code"
    return active, max(idle, key=lambda s: (rating(s), -s["id"])), ""


def tag(sub):
    return f"v{sub.get('version')} ({rating(sub)})"


def read_state():
    try:
        return json.load(open(STATE))
    except (OSError, ValueError):
        return {}


def swap(parked):
    """Activate the parked copy. Returns (done, last line of the tool's output)."""
    run = subprocess.run(["node", "tools/submit.js", "activate", str(parked["id"]), "--confirm", "--purpose", "two-copy swap"],
                         cwd=ROOT, capture_output=True, text=True, timeout=180)
    return run.returncode == 0, ((run.stdout + run.stderr).strip().splitlines() or [""])[-1][:200]


def step(now, subs, state, swap=None):
    """Return (text to post or None, new state). With swap given, a due swap is done here; without it a person is asked."""
    active, parked, why = look(subs)
    row = {"at": now.isoformat(), "active": active and {k: active.get(k) for k in ("id", "version", "rating")},
           "parked": parked and {k: parked.get(k) for k in ("id", "version", "rating")}, "note": why}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as out:
        out.write(json.dumps(row) + "\n")
    if not parked:
        return None, state
    pair = [active["id"], parked["id"]]
    text = None
    if state.get("asked") and state["asked"]["pair"] == pair[::-1]:
        # The two swapped places since the last notice: the higher number is parked now.
        text = f"locked in. {tag(parked)} is parked now, {tag(active)} is the playing copy"
        state = {}
    elif rating(active) >= rating(parked) + MARGIN:
        done, said = swap(parked) if swap else (False, "")
        last = state.get("asked")
        if done:
            text = f"\U0001F501 swapped. {tag(active)} is parked now, {tag(parked)} is the playing copy"
            state = {}
        elif swap and not last:
            # Usually one of our battles is live; the next check tries again. A person is asked only if it stays stuck.
            print(now.strftime("%m-%d %H:%M"), "swap not done:", said, flush=True)
            state = {"asked": {"pair": pair, "at": now.timestamp(), "quiet": True}}
        elif not last or last["pair"] != pair or now.timestamp() - last["at"] >= (STUCK if last.get("quiet") else REPEAT):
            text = (f"swap due. the playing copy {tag(active)} is above the parked copy {tag(parked)}. "
                    f"to lock it in, make v{parked.get('version')} the active version on the site. "
                    f"v{active.get('version')} then keeps its {rating(active)}")
            state = {"asked": {"pair": pair, "at": now.timestamp()}}
    elif state.get("asked") and state["asked"]["pair"] == pair:
        # It fell back below before anyone swapped; forget the notice.
        state = {}
    return text, state


def main():
    once, dry, manual = "--once" in sys.argv, "--dry-run" in sys.argv, "--manual" in sys.argv
    while datetime.datetime.now(KST) < END:
        now = datetime.datetime.now(KST)
        try:
            text, state = step(now, submissions(), read_state(), None if dry or manual else swap)
            if text and dry:
                print(text)
            elif text:
                open(NOTE, "w").write(text + "\n")
                subprocess.run([sys.executable, os.path.join(ROOT, "tools/meowbot.py"), "--announce-file", NOTE], cwd=ROOT)
                print(now.strftime("%m-%d %H:%M"), "posted:", text[:80], flush=True)
            if not dry:
                json.dump(state, open(STATE, "w"))
        except Exception as exc:
            print(now.strftime("%m-%d %H:%M"), "error", type(exc).__name__, str(exc)[:200], flush=True)
        if once:
            return
        time.sleep(EVERY)


if __name__ == "__main__":
    main()
