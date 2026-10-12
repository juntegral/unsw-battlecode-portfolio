# px7: the king eats what lands near it: late, the team's king (by its own knowledge) weighs pearls more and discounts
# distance less, so pearls 2-4 steps away (sacrifices) are taken. usage: python3 patch_kingeat.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
rep("""    double gpow[128];""", """    double gpow[128], gpowK[128];""")
rep("""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }""",
"""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
        g = 1.0; for (int i = 0; i < 128; i++) { gpowK[i] = g; g *= style::KING_GAMMA; }""")
rep("""        bfs(s, 60, dist);
        double pv = 0;""",
"""        bfs(s, 60, dist);
        double pv = 0;
        // px7: the late king takes the pearls around it (mostly sacrifices): more weight, gentler distance discount
        bool kingEat = amKing && L >= style::KING_MIN_LEN && round >= style::SAC_START - 20;
        const double* gp = kingEat ? gpowK : gpow;""")
rep("""            pv += v * gpow[std::min(arrive, 127)];
        }""",
"""            pv += v * gp[std::min(arrive, 127)] * (kingEat ? style::KING_PEARL_MULT : 1.0);
        }""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "// --- movement ---"
assert old in s
s = s.replace(old, """// --- px7: the king eats what lands near it ---
constexpr double KING_GAMMA = 0.88;         // late king: per-step discount of pearl value (others: GAMMA)
constexpr double KING_PEARL_MULT = 2.0;     // late king: pearl value multiplier

// --- movement ---""", 1)
open(p, 'w').write(s)
print('patched', d)
