import glob, os
S0 = "~/01. Project/개인 프로젝트/unsw-swarm/"
A = S0 + "archive/final-session-scripts/"
fs = [f for f in glob.glob(A + "*") if os.path.isfile(f)]
txt = {f: open(f, encoding='utf-8', errors='replace').read() for f in fs}
print(len(fs), "files")
for k in ["play.sh", "mkbots.py", "shasum", "submit.js", "online.js", "tools/meowbot.py", "team_watch", "nohup", "run.log", "-done", "xargs", "cmp -l", "cx.sh", "o1_scan", "ladder_replay", "MKSRC", "tools/pair_report", "tools/smoke.py", "h2h_tally", "gx_tally", "pgrep", "killtree", "wait_any", "until"]:
    print("%-20s %d" % (k, sum(1 for f in fs if k in txt[f])))
R = "~/meow-redteam/solo/runs"
d = [x for x in os.listdir(R) if os.path.isdir(os.path.join(R, x))]
print("arm folders in solo/runs:", len(d))
n = 0
for x in d:
    n += len(glob.glob(os.path.join(R, x, "*", "result.txt")))
print("result.txt games under solo/runs:", n)
B = "~/meow-redteam/solo/bots"
print("bots built:", len(os.listdir(B)))
S = S0 + "data/online/"
print("battle folders live-one1:", len(glob.glob(S + "live-one1/b*")))
print("smoke game jsons:", len(glob.glob(S + "smoke/*/game-*.json")))
print("requests.jsonl lines:", sum(1 for _ in open(S + "requests.jsonl")))
print("submissions.jsonl lines:", sum(1 for _ in open(S + "submissions.jsonl")))
print("astra dirs:", len([x for x in os.listdir(S0 + "data/codex/astra") if os.path.isdir(S0 + "data/codex/astra/" + x)]))
v = open(S + "smoke/versions.tsv").read().splitlines()
print("versions.tsv", len(v), v[:3], v[-3:])
