import glob, os, collections
S0 = "~/01. Project/개인 프로젝트/unsw-swarm/"
def ext(d, rec=False):
    c = collections.Counter()
    it = glob.glob(d + ("/**/*" if rec else "/*"), recursive=rec)
    for f in it:
        if os.path.isfile(f):
            c[os.path.splitext(f)[1] or 'none'] += 1
    return dict(c)
print("S/tools", ext(S0 + "tools"))
t = [os.path.basename(f) for f in glob.glob(S0 + "tools/test_*")] + [os.path.basename(f) for f in glob.glob(S0 + "tools/check-*")]
print("tests/checks", len(t))
print("dossier/work", ext(S0 + "data/analysis/ladder/dossier/work"))
print("dossier/online+local", ext(S0 + "data/analysis/ladder/dossier/online"), ext(S0 + "data/analysis/ladder/dossier/local"))
print("astra scripts", ext(S0 + "data/codex/astra", True))
print("archive", ext(S0 + "archive/final-session-scripts"))
print("smoke at-*.sh", len(glob.glob(S0 + "data/online/smoke/at-*.sh")), "sh total", len(glob.glob(S0 + "data/online/smoke/*.sh")))
B = "work"
print("B/work", ext(B))
print("B/loop tests", len(glob.glob(B + "/loop/tests/test_*.py")))
print("R/solo/tools", os.listdir("~/meow-redteam/solo/tools"))
c = collections.Counter(os.path.basename(f).split('_')[0] for f in glob.glob(S0 + "data/analysis/ladder/dossier/work/*.py"))
print(c.most_common(70))
print("src dirs", len(os.listdir("~/meow-redteam/solo/src")), sorted(os.listdir("~/meow-redteam/solo/src"))[:12])
