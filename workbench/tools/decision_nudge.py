#!/usr/bin/env python3
"""Hourly decision check: when a card has waited an hour or more for a person, say so in #meow via meowbot.
Plain script, no model. usage: python3 tools/decision_nudge.py [--once] [--dry-run]. Stops at the freeze."""
import datetime, json, os, subprocess, sys, time
from snooze import active_snoozes, quiet_until
from member_names import member_name

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "forrest-gan2005/battlecode"
KST = datetime.timezone(datetime.timedelta(hours=9))
FREEZE = datetime.datetime(2026, 10, 8, 20, tzinfo=KST)
# name, Discord id, UTC offset (a mention only goes out in their configured waking hours)
PEOPLE = {"by:zhe": ("Zhe", 900000000000000002, 2), "by:qwq": ("QWQ", 900000000000000003, 11),
          "by:junsing": ("jun", 900000000000000005, 9)}
# Configured waking hours in local time (from, until); authors are pinged only inside them.
AWAKE = {"QWQ": (13, 4)}


def awake(person, local):
    start, end = AWAKE.get(person, (9, 24))
    return start <= local < end if start < end else local >= start or local < end
WAITS = {"status:needs-look": "replay check", "status:needs-info": "answers to the loop's questions",
         "status:tested": "decision on the results (ship it, drop it, or revise)", "status:candidate": "OK on the candidate"}


def waiting(now, waiting_cards=None):
    out = subprocess.run(["gh", "issue", "list", "--repo", REPO, "--state", "open", "--limit", "100",
                          "--json", "number,labels,updatedAt"], capture_output=True, text=True, check=True).stdout
    rows = []
    for issue in json.loads(out):
        labels = [l["name"] for l in issue["labels"]]
        status = next((l for l in labels if l in WAITS), None)
        who = next((PEOPLE[l] for l in labels if l in PEOPLE), None)
        if not status or not who or (status == "status:needs-look" and "by:zhe" not in labels):
            continue
        if waiting_cards is not None:
            waiting_cards.add(issue['number'])
        since = datetime.datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
        minutes = (now - since).total_seconds() / 60
        if minutes < 60:
            continue
        name = next((l[5:] for l in labels if l.startswith("name:")), "")
        rows.append((minutes, issue["number"], name, who, WAITS[status]))
    return sorted(rows, reverse=True)


def filter_snoozed(now, rows, waiting_cards=None, path=None, persist=True):
    active = active_snoozes(now, waiting_cards if waiting_cards is not None else [r[1] for r in rows],
                            path=path, persist=persist)
    return ([r for r in rows if str(r[1]) not in active],
            [(r, active[str(r[1])]) for r in rows if str(r[1]) in active])


def text(now, rows, quiet=()):
    if not rows:
        return None
    lines = [f"⏰ {now.astimezone(KST):%H:%M} KST decision check"]
    for minutes, number, name, (person, uid, offset), what in rows:
        local = (now.astimezone(datetime.timezone.utc) + datetime.timedelta(hours=offset)).hour
        up = awake(person, local)
        person = member_name(person)
        tag = f"<@{uid}>" if up else f"{person} (asleep there, no ping)"
        waited = f"{int(minutes // 60)}h {int(minutes % 60)}m" if minutes < 48 * 60 else f"{int(minutes // 1440)} days"
        # Only the candidate OK is the author's own; a teammate can give the rest.
        proxy = "" if what == WAITS["status:candidate"] else ", or a teammate's"
        lines.append(f"#{number} {name} has waited {waited} for {person}'s {what}{proxy}. {tag}")
    lines.append("reply to this message in your own words, or use /answer card:N text:…")
    if quiet:
        lines.append('still deciding: ' + '; '.join(
            f'#{row[1]} {row[2]} ({member_name(entry["by"])}, quiet until ~{quiet_until(entry)} KST)'
            for row, entry in quiet))
    return "\n".join(lines)[:1900]


def main():
    once, dry = "--once" in sys.argv, "--dry-run" in sys.argv
    while datetime.datetime.now(KST) < FREEZE:
        if not once:
            now = datetime.datetime.now(KST)
            time.sleep(((now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)) - now).total_seconds() + 5)
        now = datetime.datetime.now(KST)
        try:
            waiting_cards = set()
            rows = waiting(now, waiting_cards)
            rows, quiet = filter_snoozed(now, rows, waiting_cards, persist=not dry)
            message = text(now, rows, quiet)
            if message:
                path = os.path.join(ROOT, "data/guide/px-decisions.txt")
                if dry:
                    print(message)
                else:
                    open(path, "w").write(message + "\n")
                    subprocess.run([sys.executable, os.path.join(ROOT, "tools/meowbot.py"), "--announce-file", path], cwd=ROOT)
                    print(now.strftime("%m-%d %H:%M"), "posted", [r[1] for r in rows], flush=True)
            else:
                print(now.strftime("%m-%d %H:%M"), "nothing waiting an hour or more", flush=True)
        except Exception as exc:
            print(now.strftime("%m-%d %H:%M"), "error", type(exc).__name__, str(exc)[:200], flush=True)
        if once:
            return


if __name__ == "__main__":
    main()
