# King safety: keep a reserve of unit slots for emergency stub splits, and big dragons stay out of enemy sprint reach.
# usage: python3 patch_safety.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
rep("""    bool wantSplit(int& c) {
        if (units >= unitLimit || L < 4) return false;""",
"""    bool wantSplit(int& c) {
        if (units >= unitLimit - style::SPLIT_RESERVE || L < 4) return false; // px5: slots left for trapped big dragons' stubs""")
rep("""        if (L >= style::THREAT_LEN) {
            int r = eReach[s];
            if (r <= 1) sc -= style::THREAT1;
            else if (r == 2 && eReachLen[s] >= 3) sc -= style::THREAT2;
            else if (r == 3 && eReachLen[s] >= 4) sc -= style::THREAT3;
        }""",
"""        if (L >= style::THREAT_LEN) {
            int r = eReach[s];
            if (r <= 1) sc -= style::THREAT1;
            else if (r == 2 && eReachLen[s] >= 3) sc -= style::THREAT2;
            else if (r == 3 && eReachLen[s] >= 4) sc -= style::THREAT3;
            // px5: a big dragon is the prize of every enemy piece (they sprint 2-3 steps to ram it): stay out of reach
            if (L >= style::SAFE_LEN) {
                double danger = r <= 1 ? 1.0 : (r == 2 && eReachLen[s] >= 3) ? 1.0 : (r == 3 && eReachLen[s] >= 4) ? 0.6 : 0.0;
                sc -= style::SAFE_W * danger;
            }
        }""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "// --- movement ---"
assert old in s
s = s.replace(old, """// --- px5: king safety ---
constexpr int SPLIT_RESERVE = 4;            // voluntary splits stop this many units below the unit limit
constexpr int SAFE_LEN = 10;                // dragons this long ...
constexpr double SAFE_W = 6.0;              // ... avoid tiles an enemy head can reach with its sprint (x1, x0.6 for 3 steps)

// --- movement ---""", 1)
open(p, 'w').write(s)
print('patched', d)
