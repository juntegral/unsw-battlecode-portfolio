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
    int sonarFromT = -1;        // our head after this action: where a single ray leaves from (probe bookkeeping)
    bool sonarAll = false;      // send the message on all four rays (no echo attribution)
    int relayId = -1, relayRound = -1, relayT = -1, relayLen = 0; // relay the king's position instead of our own (c10d)
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
    std::vector<int> goalDist_;        // path distance to the gathering goal (c10)
    bool goalOn_ = false; int goalT_ = -1; bool gatherKing_ = false;
    int goalId_ = -1, goalRound_ = -1, goalLen_ = 0;
    int turnCounter_ = 0;
    int survivedExposures_ = 0; bool exposedPending_ = false; // cand-avoid2: evidence that shorter heads decline trades
    bool exactlyExposed(int t) const;
    long long nodes_ = 0;
    bool late_ = false, ahead_ = false;
    bool kingSafe_ = false;            // stack1 M3: we are the king in the last KS_ROUNDS
    bool kingSafe2_ = false;           // stack3 ks2: we are the king in the last KS2_ROUNDS
    std::vector<int16_t> enemyDist2_;  // stack3 ks2: path distance (<= KS2_REACH) an enemy head can sprint to; 99 otherwise
    std::vector<int16_t> enemyNearLen2_;// its length (99 when its tail is unseen)
    int escSplitRound_ = -100;         // stack1: our last escape split (its stub is not a conversion feeder)
    int lastFragRound_ = -1000;        // stack2 S1: our last fragment split
    bool grabOn_ = false;              // stack2 S2: fresh death drops pull this dragon this turn
    std::vector<int> grabTiles_;       // stack2 S2: fresh death drops within GRAB_REACH this turn
    // cand-portal1: unexplored portals
    double frontierBase_ = 0.0;        // this turn's value of an unexplored portal edge (hunger x time x unseen map)
    bool probeOk_ = false;             // last turn's single ray left our current head and hit no dragon
    std::vector<int> headDist_;        // path distance from our head over known edges (bodies ignored), -1 unreached
    std::vector<double> frontierField_;// best single unexplored-portal pull per tile (max, not sum)
    // stack4 tg: the trade length of the nearest enemy (enemyNearLen_ holds its reach length: + a pearl beside its head, an
    // unseen tail raised to TG_UNSEEN_LEN), and stack3's field as it was, kept for the " tg" tag
    std::vector<int16_t> enemyTradeLen_;
    std::vector<int16_t> enemyDistOld_, enemyNearLenOld_; std::vector<uint8_t> enemyPseudoOld_;
    bool gxOff_ = false;               // stack4 gx: the gathering goal is off this turn only for lack of rounds
    mutable bool splitTailBlocked_ = false; // stack4 split tail: the tail rule stopped a policy split this turn
    mutable int splitTailDist_ = 99;   // stack4 split tail: our tail's distance to the nearest known enemy head
    // stack5 csplit / F / cov
    int lastCsplitRound_ = -1000;      // csplit: our last coverage split
    mutable int csplitTarget_ = 0;     // csplit: this turn's unit target (for the tag)
    bool seedMap_ = false;             // csplit E1: a start dragon saw a start with many dragons or a long one
    int homeT_ = -1;                   // F / cov: our first head tile (our side = nearer to it than its mirror image is)
    bool fGoal_ = false; int fTarget_ = -1; // F: the goal is a fountain group; the fountain chosen
    bool ourSide(int t) const;         // F / cov
    // stack8 F2 / F2p / cl / ce
    bool fTable_ = false;              // F2: this turn's F target came from the recognised map's fountains and territory
    int fPause_ = -1;                  // F2p: the claimed pearl for which the F pull is off this turn (-1 none)
    std::vector<std::pair<int, int>> claims_; // claims: (tile, round claimed), kept CLAIM_ROUNDS while the pearl stays
    std::vector<int> clTiles_, ceTiles_;      // cl / ce: this turn's claims whose rule changed the attraction (for the tags)
    // stack9 lsplit / fc / cov
    int lastLsplitRound_ = -1000;      // lsplit: our last late re-split
    mutable int lsplitTarget_ = 0;     // lsplit: this turn's unit target (for the tag)
    mutable bool fragWide_ = false;    // fc: this turn's frag split needed the wider cap (units >= frag's own cap)

    void computeEnemyDistance();
    void computeAttract();
    void computeSoftPenalty();
    void computeGoal();
    void computeFrontier();
    double frontierValue(int t, int d) const;   // > 0 iff (t, d) is an unexplored portal worth trying now
    double blindRisk(int len) const;
    double threatAt(int t) const;
    double threatAtOld(int t) const;            // stack4 tg: stack3's threat at t (for the tag only)
    double ks2Threat(int t) const;              // stack3 ks2: the late king's threat beyond distance 4
    double threatCore(int d, int le, int leTrade, bool pseudo) const;
    double exploreValue(int t);
    double portalPenalty(int from, int d, int to) const;
    double pxPenalty(int from, int d, int to) const; // stack4 px: the extra for a crossing toward our own crowd
    double areaSafety(int startT, int startRemoved, const std::vector<int>& pathTiles);
    double dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);
    bool tileEnterable(int t, int step, int removed, const std::vector<int>& path) const;
    double tradeValue(int enemyId) const;
    double tradeValueBase(int enemyId) const;   // merge2's rule, without stack1 M2
    bool smallRam(int enemyId) const;           // stack1 M2 applies to this enemy head
    bool wantSplit(int& size) const;
    bool childSafe() const;                     // the child born at our tail can move (no enemy head in view)
    bool wantFrag(int& size) const;             // stack2 S1
    bool wantCsplit(int& size) const;           // stack5 csplit
    bool csplitChildSafe(int tailDist, int minExits) const; // stack5 csplit: childSafe() without its "no enemy head in view" rule
    void computeFountainGoal();                 // stack5 F
    bool wantBSplit(int& size) const;           // cand-mapid bsplit (Schooltime b early split)
    bool wantKcap(int& size) const;             // stack7 kcap (king length cap before r250)
    bool wantFloor(int& size) const;            // stack7 floor (unit-floor split)
    bool floorMapOn() const;                    // stack7: this process recognised a map family where floor is on
    bool kcapMapOn() const;                     // stack7: ... where kcap is on
    bool wantLsplit(int& size) const;           // stack9 lsplit (late re-split of a length 4-6 dragon)
    bool covSide(int t) const;                  // stack9 cov: our side by the recognised map's territory (F2's rule), else ourSide()
    bool longerAllyKnown(int maxAge) const;     // stack2 S1: an ally seen or heard within maxAge rounds is longer than us
    bool freshDrop(int t) const;                // stack2 S2: t holds a death drop we first saw within GRAB_ROUNDS
    int pickSonarDir(int fromT, int facing, bool* probe = nullptr) const;
    void setSonar(Action& act) const;
    int pickHotspot() const;
    // stack10 lnt / utab
    double lntVetoBest_ = -1e18;                // lnt: this turn's best trade candidate value the veto removed (for the " lntv" tag)
    int lntVetoD3_ = 0;                         // lnt: its d3
    mutable bool csplitTab_ = false;            // utab: this turn's csplit target came from the layout table
    int lntD3(int enemyId) const;               // ally heads in view - (enemy heads in view other than the target)
    bool lntRam(int enemyId) const;             // the ram branch applies to this adjacent enemy head
    bool lntKint(int enemyId) const;            // the veto's exception: the target may be the enemy's longest
    bool lntVeto(int enemyId) const;            // the veto applies to a trade with this enemy
    double tradeValuePreVeto(int enemyId) const;// the trade value without the veto (the " lntv" tag)
    void lntVetoNote(double pre, double cost, int enemyId); // a vetoed trade candidate worth pre - cost without the veto
    int utabTarget() const;                     // utab: the table target for this round, -1 if the layout is not decided
    // stack11 gh / kx / lwk (params.hpp stack11 section)
    std::vector<uint8_t> ghDrop_;               // gh: 1 on a fresh drop left to a longer ally this turn
    std::vector<int> ghdTiles_;                 // gh: those tiles (cleared next turn; the tag names the nearest)
    bool ghOn_ = false;                         // gh: some drop is left to a longer ally this turn
    std::vector<int16_t> kxDist_;               // kx: path distance (<= KX_DIST) from enemy heads seen within KX_STALE rounds; 99 beyond
    std::vector<int> kxQ_;                      // kx: BFS queue
    bool kxOn_ = false;                         // kx: the king-away leaf penalty applies this turn
    bool lwkHeld_ = false;                      // lwk: the king-class rule stopped a late-window feed this turn
    void computeGhDrops();                      // gh: ghDrop_ / ghdTiles_ / ghOn_
    void computeKingAway();                     // kx: kxDist_ / kxOn_
    bool kingFresh() const;                     // kx: no ally longer than us with news within KX_KING_FRESH rounds
    bool kxMapOn() const;                       // kx: a recognised KX map family
    double pearlValue(int t, double p) const;   // gh: p, or p x CONTEST_ALLY_CLOSER on a drop left to a longer ally
};

long long nowPoints();

} // namespace seed0
