#!/usr/bin/env python3
# v1.1b = versions/v1.1/bot + target commitment + the swarm sd pull FG_W_FRONT (versions/v1.1/VERSION.md §5.2), applied to a copy.
# usage: python3 exp/v11/make_v11b.py <copy of versions/v1.1/bot>
import sys, os
d = sys.argv[1]
def edit(f, pairs):
    p = os.path.join(d, f); s = open(p).read()
    for a, b in pairs:
        assert a in s, (f, a[:60]); s = s.replace(a, b)
    open(p, 'w').write(s)
edit('plan.hpp', [
 ("    double dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);",
  "    template <int MODE> double dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);   // v1.1b: per engine (the SWARM leaf pulls to sd with FG_W_FRONT)"),
 ("    int sdAnchor_ = -1, sdSince_ = -1;                // sd: the held target (a spawn tile of our side) and the round we took it",
  "    int sdAnchor_ = -1, sdSince_ = -1;                // sd: the held target (a spawn tile of our side) and the round we took it\n    int sdTaken_ = -1;                                 // v1.1b: the round the held target was first chosen (the commitment clock)"),
])
edit('plan.cpp', [
 ("double Planner::dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline) {",
  "template <int MODE> double Planner::dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline) {"),
 ("        if (goalOn_) v -= fGoal_ ? P::FG_W * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)   // stack5 F: hold the group",
  "        if (goalOn_) v -= fGoal_ ? (MODE == 2 ? P::FG_W_FRONT : P::FG_W) * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)   // stack5 F: hold the group (v1.1b: the swarm sd pull FG_W_FRONT)"),
 ("        v += dfs(u, d, depth + 1, maxDepth, removed + (eat ? 0 : 1), lenNow + (eat ? 1 : 0), path, deadline);",
  "        v += dfs<MODE>(u, d, depth + 1, maxDepth, removed + (eat ? 0 : 1), lenNow + (eat ? 1 : 0), path, deadline);"),
 ("            double cont = dfs(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);",
  "            double cont = dfs<MODE>(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);"),
 ("    if (sdAnchor_ >= 0 && fl(sdAnchor_) > 0.0 && headDist_[sdAnchor_] >= 0 && w_.round - sdSince_ < P::SD_LEASE && ours(sdAnchor_, P::SD_HYST)) target = sdAnchor_;",
  """    // v1.1b commitment: a frontier target is held until we arrive (within FG_HOLD of it) or for SD_COMMIT_MAX rounds, while it stays ours (the
    // local check: v1.1's targets were held 3.4 turns and middle-bin targets, 7.3 steps away on average, reached 42%)
    const bool commit = front && sdAnchor_ >= 0 && headDist_[sdAnchor_] > P::FG_HOLD && w_.round - sdTaken_ < P::SD_COMMIT_MAX;
    if (sdAnchor_ >= 0 && fl(sdAnchor_) > 0.0 && headDist_[sdAnchor_] >= 0 && (w_.round - sdSince_ < P::SD_LEASE || commit) && ours(sdAnchor_, P::SD_HYST)) target = sdAnchor_;"""),
 ("    if (target != sdAnchor_ || w_.round - sdSince_ >= P::SD_LEASE) sdSince_ = w_.round;",
  "    if (target != sdAnchor_) sdTaken_ = w_.round;                                   // v1.1b\n    if (target != sdAnchor_ || w_.round - sdSince_ >= P::SD_LEASE) sdSince_ = w_.round;"),
])
edit('params.hpp', [
 ("constexpr int    BEACON_RELAY_AGE = 1;",
  """constexpr int    BEACON_RELAY_AGE = 1;
// v1.1b (versions/v1.1/VERSION.md §5.2, after the local check; the SWARM engine only): a frontier sd target is held until arrival (within FG_HOLD)
// for at most SD_COMMIT_MAX rounds while it stays ours, and the search leaf pulls to it FG_W_FRONT a tile beyond FG_HOLD (v1: FG_W 0.12, the
// same as the gathering pull). Local check (112 paired swarm games, proxies): targets held 4.6 turns (v1.1 3.4), middle-bin heads r100 34% (28%).
constexpr int    SD_COMMIT_MAX = 30;
constexpr double FG_W_FRONT = 0.4;"""),
])
print('v1.1b patch applied to', d)
