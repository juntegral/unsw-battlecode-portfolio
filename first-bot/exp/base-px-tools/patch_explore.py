# Known map: exploration toward spawning tiles weighted by P(pearl there) (spawn model), replaces the lost unknown-portal
# curiosity. Requires patch_spawn.py (mmean, SPAWN_V) to be applied first. usage: python3 patch_explore.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
# factor the spawn probability into a helper used by buildTargets and by exploration
rep("""            if (style::SPAWN_V > 0 && mapIdx >= 0 && mspawn[t] && inView[t] != round && !(pearlR[t] >= 0 && pearlR[t] > emptyR[t])) {
                double pr;
                bool seenEmpty = emptyR[t] >= 0 && spawnSeenR[t] >= emptyR[t];
                if (seenEmpty && spawnR[t] > round) pr = 0.0;                           // seen empty, next attempt still ahead
                else if (seenEmpty && spawnR[t] > 0 && spawnR[t] <= round) pr = 1.0;     // the attempt we saw scheduled has passed
                else pr = std::min(1.0, (round - emptyR[t]) / (double)mmean[t]);          // unknown phase (never seen: emptyR = -1)
                double sv = style::SPAWN_V * pr;
                if (sv > v) { v = sv; sp = -1; }
            }""",
"""            if (style::SPAWN_V > 0 && mapIdx >= 0 && mspawn[t] && inView[t] != round && !(pearlR[t] >= 0 && pearlR[t] > emptyR[t])) {
                double sv = style::SPAWN_V * spawnProb(t);
                if (sv > v) { v = sv; sp = -1; }
            }""")
rep("""    const Seen* seenById(int id) const {""",
"""    // known map: probability that an out-of-view spawning tile holds a pearl we have not seen
    double spawnProb(int t) const {
        bool seenEmpty = emptyR[t] >= 0 && spawnSeenR[t] >= emptyR[t];
        if (seenEmpty && spawnR[t] > round) return 0.0;                        // seen empty, next attempt still ahead
        if (seenEmpty && spawnR[t] > 0 && spawnR[t] <= round) return 1.0;       // the attempt we saw scheduled has passed
        return std::min(1.0, (round - emptyR[t]) / (double)mmean[t]);            // unknown phase (never seen: emptyR = -1)
    }
    const Seen* seenById(int id) const {""")
rep("""            int best = -1;
            for (int t : q) if ((seenR[t] < 0 || round - seenR[t] > style::STALE_AGE) && (mapIdx < 0 || mspawn[t])) { best = t; break; }
            double ex = best >= 0 ? style::EXPLORE_W * std::pow(0.93, dist[best]) : 0.0;""",
"""            int best = -1;
            double ex = 0.0;
            if (mapIdx >= 0 && style::EXPLORE_MAP_W > 0) {
                // px3c: known map: the best out-of-view spawning tile, by P(pearl) and distance (replaces portal curiosity)
                for (int t : q) {
                    if (!mspawn[t] || inView[t] == round || leave[t]) continue;
                    if (pearlR[t] >= 0 && pearlR[t] > emptyR[t]) continue;   // a remembered pearl is a target already
                    double v = style::EXPLORE_MAP_W * spawnProb(t) * gexp[std::min(dist[t], 127)];
                    if (v > ex) ex = v;
                }
            } else {
                for (int t : q) if ((seenR[t] < 0 || round - seenR[t] > style::STALE_AGE) && (mapIdx < 0 || mspawn[t])) { best = t; break; }
                ex = best >= 0 ? style::EXPLORE_W * std::pow(0.93, dist[best]) : 0.0;
            }""")
rep("""    double gpow[128];""", """    double gpow[128], gexp[128];""")
rep("""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }""",
"""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
        g = 1.0; for (int i = 0; i < 128; i++) { gexp[i] = g; g *= 0.93; }""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "constexpr double SPAWN_V = 0.45;"
assert old in s
s = s.replace(old, """constexpr double SPAWN_V = 0.45;
constexpr double EXPLORE_MAP_W = 0.50;      // known map: exploration value of the best out-of-view spawning tile x P(pearl) x 0.93^steps""", 1)
open(p, 'w').write(s)
print('patched', d)
