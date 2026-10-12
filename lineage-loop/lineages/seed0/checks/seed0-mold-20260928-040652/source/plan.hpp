// plan.hpp — chooses this turn's action from the world model.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "world.hpp"

namespace seed0 {

struct Action {
    enum Kind { MOVE, SPLIT } kind = MOVE;
    std::string dirs = "N";     // for MOVE: one letter per step
    int splitSize = 0;          // for SPLIT
    std::vector<int> path;      // tiles the head will occupy in order (for MOVE)
    int sonarDir = -1;          // ray to send this turn (-1 none)
    int hotT = -1;              // hotspot tile to advertise
    int safeDir = -1;           // best legal single step, emitted first as a fallback line
    std::string indicator;      // short debug label
    double score = 0.0;
};

class Planner {
  public:
    explicit Planner(World& w) : w_(w) {}
    Action decide();
  private:
    World& w_;
    std::vector<double> attract_;      // pearl attraction field
    std::vector<int> distBuf_, queue_, parBuf_;
    std::vector<int16_t> enemyDist_;   // path distance (<=4) from the nearest enemy head; 99 otherwise
    std::vector<int16_t> enemyNearLen_;// estimated length of that enemy
    std::vector<uint8_t> enemyPseudo_; // 1 if the nearest "head" is a higher-id enemy's tail (latent child)
    std::vector<double> softPenalty_;  // echo lines + predicted head paths
    std::vector<int> exploreStamp_; std::vector<double> exploreVal_;
    int turnCounter_ = 0;
    long long nodes_ = 0;
    bool late_ = false, ahead_ = false;

    void computeEnemyDistance();
    void computeAttract();
    void computeSoftPenalty();
    double threatAt(int t) const;
    double exploreValue(int t);
    double portalPenalty(int from, int d, int to) const;
    double areaSafety(int startT, int startRemoved, const std::vector<int>& pathTiles);
    double dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);
    bool tileEnterable(int t, int step, int removed, const std::vector<int>& path) const;
    double tradeValue(int enemyId) const;
    bool wantSplit(int& size) const;
    int pickSonarDir() const;
    int pickHotspot() const;
};

long long nowPoints();

} // namespace seed0
