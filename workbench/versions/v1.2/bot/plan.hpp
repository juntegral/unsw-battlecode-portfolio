// plan.hpp — chooses this turn's action from the world model.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "engcfg.hpp"
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
    // unsw-swarm v1: the engine configuration for this turn (engcfg.hpp, policy.hpp). decide() runs decideImpl<true> for the swarm
    // engine and decideImpl<false> for FORTRESS: the FORTRESS instantiation is stack11's decide() (every swarm switch is compiled out
    // there), so the judge's point clock, which the search's deadlines read, sees the same instructions as benchmark/.
    void setConfig(const EngineConfig* c) { cfg_ = c; }
  private:
    World& w_;
    // MODE 0 FORTRESS, 1 FORTRESS_W4 (5b), 2 SWARM, 3 PORTALS (exp/portals: the Portals module, ptmod.cpp; runs only in a process whose config
    // has portals set, policy.hpp; the other instantiations compile exactly as before, every module block is compiled out)
    template <int MODE> __attribute__((noinline)) Action decideImpl();
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
    template <int MODE> void computeAttractT();  // v1: SWARM keeps grab / cov / claims off dead-end pockets (2-core); FORTRESS_W4 has no cov / claims
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
    template <int MODE> double dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);   // v1.1b: per engine (the SWARM leaf pulls to sd with FG_W_FRONT)
    bool tileEnterable(int t, int step, int removed, const std::vector<int>& path) const;
    double tradeValue(int enemyId) const;
    double tradeValueBase(int enemyId) const;   // merge2's rule, without stack1 M2
    bool smallRam(int enemyId) const;           // stack1 M2 applies to this enemy head
    bool wantSplit(int& size) const;
    bool childSafe() const;                     // the child born at our tail can move (no enemy head in view)
    bool wantFrag(int& size, bool fc = true) const; // stack2 S1 (fc: stack9's wider cap; v1 5b: off on Autarky and PD6)
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
    int lntD8(int enemyId) const;               // v1 final: our heads - enemy heads (seen or heard within 3 rounds) within Manhattan 8 of our head, the pair excluded
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
    // unsw-swarm v1 swarm engine (params.hpp v1 section, engcfg.hpp)
    const EngineConfig* cfg_ = &FORTRESS_CONFIG;
    int lastSxRound_ = -1000, lastSrRound_ = -1000;   // sx / sr: our last explosion / re-split
    mutable int sxTarget_ = 0, srTarget_ = 0;         // this turn's unit targets (for the tags)
    mutable int sxWhy_ = 0, srWhy_ = 0;               // 3: the child's spot failed (" sxc" / " src"), 4: no service deficit (" srn")
    int sdAnchor_ = -1, sdSince_ = -1;                // sd: the held target (a spawn tile of our side) and the round we took it
    int sdTaken_ = -1;                                 // v1.1b: the round the held target was first chosen (the commitment clock)
    int sdKind_ = 0;                                   // sd: 1 uniquely nearest, 2 uncovered
    int sdFree_ = 0;                                   // sd: a free spawn group besides ours is within reach (the re-split's service deficit)
    int flowKey_ = -1000000; char sideChar_ = '?';     // sd: the flow table's recognition state and our side's territory char
    std::vector<double> flow_;                         // sd: fountain flow per 2-core tile (1 / mean gap; -1: observed rule)
    struct ClaimHeard { int anchor, from, id, round; };
    std::vector<ClaimHeard> claimsHeard_;              // sd: allies' claims (their sonar hotspot field), kept SD_TTL rounds
    std::vector<uint8_t> scMark_; std::vector<int> scTiles_; // sc: tiles whose spawn this turn's clearance penalty protects
    int sfHeld_ = -1;                                  // sf: this turn's local feed held for the recipient's pickup queue (its id)
    bool wantExplode(int& size) const;                 // sx
    bool wantResplit(int& size) const;                 // sr
    bool roomOk() const;                               // sx / sr: >= SX_ROOM free tiles reachable from our tail (pf's pfRoomOk)
    void computeDisperseGoal();                        // sd (replaces computeFountainGoal)
    void computeGoalSwarm();                           // no gathering: only the relay of the longest fresh ally
    void takeClaims();                                 // sd: allies' hotspots become claims (not attraction sources)
    void addSpawnClear();                              // sc
    void updateSide();                                 // sd / sc: our side's territory char (sideChar_)
    int sideOf(int t) const;                           // 1 ours, 2 theirs, 0 neutral, -1 unknown
    std::string beliefTag() const;                     // v1 belief tag " bl<len>@x,y k<0|1>"
    // unsw-swarm v1.1 (params.hpp v1.1 section, versions/v1.1/VERSION.md)
    int sdBin_ = -1;                                   // A: the frontier bin of this turn's sd target (-1 none or no table)
    bool sdContest_ = false;                           // A: the target is one an enemy head reaches no later than we do (tag " sd..c")
    int sdRedir_ = -1; char sdRedirWhy_ = 0;           // A guard (diagnostic): the top-deficit bin had no group we may take (" fr<b><o|p|n>")
    std::vector<int16_t> kfDist_; std::vector<int> kfQ_; // B: path distance (<= KF_TARGET) from enemy heads seen within KF_STALE rounds; 99 beyond
    bool kfOn_ = false;                                // B: the king floor applies this turn (king class, some enemy head within KF_TARGET)
    mutable int beaconRelayRound_ = -1000;             // C: our last beacon relay (FORTRESS before GATHER_BROADCAST)
    mutable int beaconTag_ = 0;                        // C: 1 this turn's rays are the king's beacon (" kb"), 2 a beacon relay (" kbr")
    bool kingClass() const;                            // the swarm engine's king class (the " sk" tag): fresh iAmLongest, L >= 8 or past the clock
    void computeKingFloor();                           // B: kfDist_ / kfOn_
    double kingFloorCost(int t) const;                 // B: the choice cost of ending this turn's move on t
    // exp/portals: the Portals module (ptmod.cpp; params.hpp "exp/portals" section)
    bool ptKing_ = false;                              // this turn: we are the king class (iAmLongest, length >= KING_MIN_LEN)
    int ptFire_ = 0;                                   // this turn's rule firings on candidates (bit 1 king dead end, 2 king blind crossing, 4 piece crossing near the king)
    int ptExit(int t, int d) const;                    // the tile across edge d of t by the static board (ptmap.hpp); -1 kelp
    double ptKingTilePen(int t) const;                 // the king class's price for standing on t (ptmap DEAD)
    double ptStepPenalty(int from, int d, int to, bool blind);  // the module's penalty on one step of a candidate (sets ptFire_ bits)
    double dfsPt(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline);
    void computeGoalPt();                              // computeGoal with the module's gathering clock and endgame (no unit / length floor)
};

long long nowPoints();

} // namespace seed0
