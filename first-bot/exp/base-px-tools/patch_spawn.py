# Adds a spawn-rate model of unseen pearls (known map) to buildTargets. usage: python3 patch_spawn.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
rep("""    std::vector<int8_t> mspawn;                                           // known map: 1 if the tile ever spawns pearls, 0 never""",
"""    std::vector<int8_t> mspawn;                                           // known map: 1 if the tile ever spawns pearls, 0 never
    std::vector<float> mmean;                                             // known map: mean gap between spawn attempts (0 never)""")
rep("""        mdest.assign(N * 4, -1); mspawn.assign(N, 0);""", """        mdest.assign(N * 4, -1); mspawn.assign(N, 0); mmean.assign(N, 0.f);""")
rep("""            int pi = M.spawn[t] - 48; mspawn[t] = (pi > 0 && pi < M.nPal && M.pal[pi * 2 + 1] > 0) ? 1 : 0;""",
"""            int pi = M.spawn[t] - 48; mspawn[t] = (pi > 0 && pi < M.nPal && M.pal[pi * 2 + 1] > 0) ? 1 : 0;
            if (mspawn[t]) mmean[t] = 0.5f * (M.pal[pi * 2] + M.pal[pi * 2 + 1]);""")
rep("""            if (style::FOUNTAIN_V > 0 && gapMin[t] > 0 && gapMin[t] <= 40 && inView[t] != round && round - seenR[t] >= gapMin[t] && style::FOUNTAIN_V > v) { v = style::FOUNTAIN_V; sp = -1; }""",
"""            if (style::FOUNTAIN_V > 0 && gapMin[t] > 0 && gapMin[t] <= 40 && inView[t] != round && round - seenR[t] >= gapMin[t] && style::FOUNTAIN_V > v) { v = style::FOUNTAIN_V; sp = -1; }
            // px5: known map: a tile out of view that spawns pearls holds one with a probability that grows with the time
            // since we last saw it empty (an attempt we saw scheduled and that has passed counts as one)
            if (style::SPAWN_V > 0 && mapIdx >= 0 && mspawn[t] && inView[t] != round && !(pearlR[t] >= 0 && pearlR[t] > emptyR[t])) {
                double pr;
                bool seenEmpty = emptyR[t] >= 0 && spawnSeenR[t] >= emptyR[t];
                if (seenEmpty && spawnR[t] > round) pr = 0.0;                           // seen empty, next attempt still ahead
                else if (seenEmpty && spawnR[t] > 0 && spawnR[t] <= round) pr = 1.0;     // the attempt we saw scheduled has passed
                else pr = std::min(1.0, (round - emptyR[t]) / (double)mmean[t]);          // unknown phase (never seen: emptyR = -1)
                double sv = style::SPAWN_V * pr;
                if (sv > v) { v = sv; sp = -1; }
            }""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "// --- movement ---"
assert old in s
s = s.replace(old, """// --- px5: known-map spawn model ---
constexpr double SPAWN_V = 0.45;            // value of an unseen spawning tile x P(pearl there) (seen pearl 1.0, scheduled 0.7)

// --- movement ---""", 1)
open(p, 'w').write(s)
print('patched', d)
