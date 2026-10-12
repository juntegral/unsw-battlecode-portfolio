"""Until the morning: when the loop's 'is built, can you check 2-3 replays?' notice is for an AI card,
follow it with a note that nobody needs to answer. Plain script, no model. Stops at 10:00 KST."""
import datetime, json, os, re, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIRROR = os.path.join(ROOT, "data/discord/900000000000000004.md")
PAT = re.compile(r"^- (\d\d-\d\d \d\d:\d\d) \*\*meowbot😼\*\*: (?:<@\d+> )?#(\d+) (\S+) is built, can you check")
def hits():
    return [m.groups() for m in map(PAT.match, open(MIRROR, encoding="utf-8")) if m]
seen = set(hits())
end = datetime.datetime(2026, 10, 5, 10, 0)
while datetime.datetime.now() < end:
    time.sleep(60)
    subprocess.run(["python3", os.path.join(ROOT, "tools/team_watch.py")], cwd=ROOT, capture_output=True)
    for hit in hits():
        if hit in seen:
            continue
        seen.add(hit)
        _, number, name = hit
        out = subprocess.run(["gh", "issue", "view", number, "--repo", "forrest-gan2005/battlecode", "--json", "labels"],
                             capture_output=True, text=True).stdout
        try:
            labels = [l["name"] for l in json.loads(out)["labels"]]
        except (ValueError, KeyError):
            continue
        if "by:ai" not in labels:
            continue
        path = os.path.join(ROOT, "data/guide", f"px-fyi{number}.txt")
        open(path, "w").write(f"about the #{number} {name} message above. it's an automatic note from the loop and nobody needs to answer it. "
                              f"#{number} is an AI card, so the loop moves on by itself. the replays are there only if you're curious\n")
        subprocess.run(["python3", os.path.join(ROOT, "tools/meowbot.py"), "--announce-file", path], cwd=ROOT)
        print(datetime.datetime.now().strftime("%H:%M"), "posted note for", number, name, flush=True)
