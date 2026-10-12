// policy.hpp — the engine layer's assignment table: which engine decides this turn, from the recognised map family, then
// map, then layout (World::mapFam / mapIdx / mapLayout, recognised per process in mapid.cpp from its own windows).
//
// Source of the assignment and the targets: ENGINE.md ("엔진 등록부와 지도별 배정", and §2 / §3 A of the v1 draft).
//   - FORTRESS: the three maps split by walls (Autarky, Prisoners Dilemma a/b, Portals), 75 of stack11's 81 top-6 wins.
//   - SWARM: the other seven (Trauma, Slithery Fight, Schooltime, Default, Devil, Queen Of Spades, Trophy), 6 of 630.
//   - Not recognised yet (a process's first window, a split child before its own decision), an unknown map, or "none" (a
//     contradiction after a decision): FORTRESS (ENGINE.md §2: "인식 전에는 요새 엔진의 첫 수를 쓴다").
// v0 (versions/v0/VERSION.md): the table already holds the v1 assignment, but the SWARM engine is a stub that forwards to
// FORTRESS (engine.hpp), so every turn runs stack11's decision path unchanged. The per-map swarm targets below are data
// only; nothing reads them yet. Change the assignment here and in ENGINE.md together.
// unsw-swarm v1: each row also gives the swarm engine's conversion clock, and makeConfig() turns a row into the runtime EngineConfig
// (engcfg.hpp) that Planner::decide() reads: FORTRESS_CONFIG (stack11) for fortress rows, the swarm engine's switches for swarm rows.
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>

#include "engcfg.hpp"
#include "world.hpp"

namespace seed0 {

enum class Engine : uint8_t { FORTRESS = 0, SWARM = 1 };
constexpr char engineTag(Engine e) { return e == Engine::SWARM ? 'S' : 'F'; }   // the " E=<tag>" indicator label (main.cpp)

// ---- per-engine parameters (later versions fill these; v0 reads none of them) ----
struct FortressParams {
    // FORTRESS = stack11 (submission 13393): plan.cpp with params.hpp as it is. No engine-level parameters yet.
};
struct SwarmParams {
    // ENGINE.md §3 A (explosion, r0-99): split rates, in new heads per length >= 4 head-round (top winners 0.64 / 0.39;
    // stack11 0.08, intake-gap.md), and the cap on any head target (the unit limit is 64).
    double splitRateR0_49 = 0.50;
    double splitRateR50_99 = 0.35;
    int headCap = 56;
    // §3 A: a child's spot needs an exit on the tail side and >= 8 empty tiles reachable one step beyond enemy heads (pf's pfRoomOk)
    int childRoomMin = 8;
    // §3 B (eat and re-split, r100-~r350): target heads at r250 (top 51, stack11 16)
    int headsR250 = 25;
    // §3 C (gather, r~350-499): fresh = seen or heard within this many rounds
    int kingNewsFresh = 20;
};
constexpr FortressParams FORTRESS_PARAMS{};
constexpr SwarmParams SWARM_PARAMS{};

// ---- per-map parameters ----
// One row per family (layout '*': the layout not decided yet, or no layout-specific row) and one per layout where the
// targets differ. fam is the mapdb.hpp family name (the name of the family's a map).
struct MapPolicy {
    const char* fam;   // nullptr: the default row
    char layout;       // 'a' / 'b' once this process decided that layout; '*' the family
    Engine engine;     // ENGINE.md assignment
    int headsR100;     // SWARM target: our living units at r100 = the top winners' r100 count (ENGINE.md §3 A table, from
                       // cand-stack12.md), before SwarmParams::headCap. 0 = none.
    int convClock;     // v1 SWARM: the round the local feed (sf) starts. 0 = none.
    // v1 final (coordinator 03:30; exp/map-atlas/INTERIM.md §2, top winners' medians over 17,057 games): the head curve at r10 / r25 / r50 /
    // r100 / r250 (linear between, held after r250), the conversion clock above, and the trade veto on local balance d8 (true) or the
    // stack10 in-view d3 rule (false: Slithery Fight, where outnumbered trades are not a loss, +0.2 to +0.3 a contact).
    int h10, h25, h50, h250;
    bool d8Veto;
};

inline constexpr MapPolicy MAP_POLICY[] = {
    // fortress maps (ENGINE.md: Autarky 37/90, Prisoners Dilemma 22/90, Portals 16/90 top-6 wins over 15 waves)
    {"Autarky", '*', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false},
    {"Prisoners_Dilemma", '*', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false},   // a (6 dragons) and b (the 10-dragon PD10); layout not decided yet
    {"Prisoners_Dilemma", 'a', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false},   // PD6: the W4-era economy (makeConfig, FORT_W4_ON)
    {"Prisoners_Dilemma", 'b', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false},   // PD10: stack11
    {"Portals", '*', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false},
    // swarm maps (ENGINE.md: Trauma 3/90, Slithery Fight 3/90, the other five 0/450). v1 final (map atlas interim, coordinator 03:30): head
    // curve r10/25/50/100/250 = top winners' medians (capped at 56); clock 250 on the SE maps (the elite step-up at r240 -> r250), the atlas
    // clock on the EL maps; family rows (layout not decided yet) take the mean of the two layouts
    //  fam / layout / engine / h100 / clock / h10 / h25 / h50 / h250 / d8 veto
    {"Trauma", '*', Engine::SWARM, 17, 250, 4, 4, 7, 38, true},
    {"Slithery_Fight", '*', Engine::SWARM, 56, 250, 20, 30, 45, 56, false},
    {"Slithery_Fight", 'a', Engine::SWARM, 56, 250, 20, 31, 47, 56, false},
    {"Slithery_Fight", 'b', Engine::SWARM, 56, 250, 20, 30, 43, 56, false},
    {"Schooltime", '*', Engine::SWARM, 30, 300, 6, 6, 10, 52, true},
    {"Schooltime", 'a', Engine::SWARM, 45, 250, 6, 6, 13, 56, true},
    {"Schooltime", 'b', Engine::SWARM, 16, 340, 6, 6, 8, 49, true},
    {"Default", '*', Engine::SWARM, 19, 340, 7, 8, 11, 38, true},              // elimination type
    {"Devil", '*', Engine::SWARM, 28, 335, 6, 8, 15, 37, true},                // elimination type
    {"Devil", 'a', Engine::SWARM, 31, 340, 6, 8, 17, 39, true},
    {"Devil", 'b', Engine::SWARM, 24, 330, 6, 7, 12, 35, true},
    {"Queen_Of_Spades", '*', Engine::SWARM, 13, 400, 2, 4, 7, 22, true},      // elimination type
    {"Queen_Of_Spades", 'a', Engine::SWARM, 13, 400, 2, 4, 7, 23, true},
    {"Queen_Of_Spades", 'b', Engine::SWARM, 12, 400, 2, 4, 7, 21, true},
    {"Trophy", '*', Engine::SWARM, 30, 360, 2, 5, 15, 44, true},               // elimination type
};
inline constexpr MapPolicy DEFAULT_POLICY = {nullptr, '*', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false};

// v1.1 frontier allocation (versions/v1.1/VERSION.md A): the elite winners' head share (whole percent) by frontier bin, own-deep [0, .2) to enemy-deep
// [.8, 1] (frontdb.hpp), at r25 / r50 / r100 / r250 (linear between, held after r250; EngineConfig::frontShare). Source: exp/spatial-all/tables.json
// (Codex spatial study, all ten maps, generated 2026-10-01 04:32 KST), maps["<Map>/<layout>"].classes["elite-winners"].checkpoints[r].headShare,
// games reaching the checkpoint (N below); printed by exp/v11/frontrows.js. Family rows (layout not decided yet): the mean of the two layouts.
// A swarm row without an entry here keeps v1's sd. The head count stays v1's atlas curve (MAP_POLICY); only the allocation reads these.
struct FrontPolicy {
    const char* fam;
    char layout;
    unsigned char share[4][5];   // r25, r50, r100, r250 x bins 0..4
};
inline constexpr FrontPolicy FRONT_POLICY[] = {
    {"Trauma", '*', {{95, 5, 0, 0, 0}, {75, 25, 1, 0, 0}, {54, 22, 24, 0, 0}, {41, 22, 32, 4, 1}}},   // Trauma/a elite winners, N 1811/1811/1811/1804 (r25/50/100/250), heads/game 4.4/7.5/17.9/38.8
    {"Slithery_Fight", 'a', {{55, 26, 18, 1, 1}, {49, 29, 20, 2, 1}, {51, 26, 20, 2, 1}, {51, 23, 21, 3, 1}}},   // Slithery Fight/a, N 881/881/876/874, heads/game 30.9/47.1/59.3/61.2
    {"Slithery_Fight", 'b', {{55, 26, 18, 1, 1}, {48, 28, 21, 2, 1}, {52, 26, 19, 2, 1}, {56, 23, 17, 3, 1}}},   // Slithery Fight/b, N 938/938/937/935, heads/game 30.0/43.3/53.8/60.5
    {"Schooltime", 'a', {{12, 28, 46, 9, 5}, {6, 16, 63, 11, 4}, {4, 11, 70, 10, 4}, {4, 10, 72, 10, 4}}},   // Schooltime/a, N 1005/1005/1004/987, heads/game 6.0/13.6/44.5/59.3
    {"Schooltime", 'b', {{10, 31, 40, 13, 6}, {8, 24, 46, 16, 7}, {6, 18, 55, 15, 6}, {5, 14, 62, 14, 5}}},   // Schooltime/b, N 978/977/977/907, heads/game 5.9/7.9/16.1/47.2
    {"Default", '*', {{6, 24, 54, 9, 7}, {3, 16, 65, 12, 3}, {3, 15, 65, 14, 3}, {3, 15, 63, 15, 4}}},   // Default/a, N 1894/1894/1876/1481, heads/game 7.5/11.0/19.1/38.1
    {"Devil", 'a', {{16, 30, 54, 0, 0}, {10, 25, 58, 7, 0}, {16, 28, 42, 12, 2}, {21, 30, 32, 13, 4}}},   // Devil/a, N 792/774/642/185, heads/game 8.2/16.2/30.9/38.7
    {"Devil", 'b', {{14, 29, 56, 1, 0}, {8, 24, 60, 7, 0}, {14, 26, 44, 14, 3}, {20, 28, 33, 14, 4}}},   // Devil/b, N 779/762/612/133, heads/game 7.1/11.8/24.1/35.2
    {"Queen_Of_Spades", 'a', {{5, 52, 33, 7, 3}, {7, 43, 28, 17, 5}, {8, 32, 33, 21, 6}, {8, 26, 37, 21, 8}}},   // Queen Of Spades/a, N 842/834/788/432, heads/game 4.0/7.3/13.6/23.4
    {"Queen_Of_Spades", 'b', {{10, 49, 30, 9, 2}, {9, 43, 24, 19, 6}, {10, 33, 29, 21, 8}, {10, 25, 33, 22, 9}}},   // Queen Of Spades/b, N 842/837/790/438, heads/game 3.8/6.8/12.2/21.7
    {"Trophy", '*', {{3, 30, 55, 10, 2}, {3, 27, 51, 17, 2}, {4, 28, 40, 23, 4}, {5, 28, 36, 25, 6}}},   // Trophy/a, N 1551/1509/1341/359, heads/game 5.6/14.6/31.0/43.6
    {"Slithery_Fight", '*', {{55, 26, 18, 1, 1}, {49, 29, 20, 2, 1}, {52, 26, 20, 2, 1}, {54, 23, 19, 3, 1}}},   // Slithery Fight a/b mean
    {"Schooltime", '*', {{11, 30, 43, 11, 6}, {7, 20, 54, 13, 5}, {5, 15, 63, 13, 5}, {4, 12, 67, 12, 5}}},   // Schooltime a/b mean
    {"Devil", '*', {{15, 29, 55, 1, 0}, {9, 25, 59, 7, 0}, {15, 27, 43, 13, 3}, {20, 29, 33, 14, 4}}},   // Devil a/b mean
    {"Queen_Of_Spades", '*', {{8, 51, 31, 8, 2}, {8, 43, 26, 18, 5}, {9, 32, 31, 21, 7}, {9, 26, 35, 21, 8}}},   // Queen Of Spades a/b mean
};
inline const FrontPolicy* lookupFront(const MapPolicy& row) {
    if (!row.fam) return nullptr;
    for (const FrontPolicy& f : FRONT_POLICY) if (f.layout == row.layout && std::strcmp(f.fam, row.fam) == 0) return &f;
    return nullptr;
}

// v1: the runtime configuration of a row. FORTRESS rows (and SWARM rows in the SWARM_AS_FORTRESS identity build) get FORTRESS_CONFIG; the
// swarm engine (its rule set: versions/v1/VERSION.md "SWARM rule table"): explosion (sx) to the row's r100 target, re-split (sr) to
// max(target, headsR250) with the service-deficit rule, local feed (sf) from the row's clock, every ray from r1, dispersal (sd) with sonar
// claims, spawn clearance (sc). Targets <= min(headCap, unit limit - 8).
inline EngineConfig makeConfig(const MapPolicy& row, int unitLimit) {
    EngineConfig c;
    if (row.engine != Engine::SWARM) {
        // v1 5b (coordinator 03:30; map atlas: our Autarky king500 64 -> 52 -> 42 over W0-W4 / W5-W9 / W10-W12 while r100 heads went 5 -> 11-13
        // at the same r250 mass; PD6 32 -> 21): the W4-era economy on Autarky and PD6. PD10 and Portals stay stack11.
        if (P::FORT_W4_ON && row.fam && (std::strcmp(row.fam, "Autarky") == 0 || (std::strcmp(row.fam, "Prisoners_Dilemma") == 0 && row.layout == 'a'))) {
            c.econW4 = true; c.tag = 'W';
        }
        // exp/portals: the Portals row keeps FORTRESS's switches and runs the module's instantiation decideImpl<3> (params.hpp PT_*; tag stays 'F')
        if (P::PT_ON && row.fam && std::strcmp(row.fam, "Portals") == 0) c.portals = true;
        return c;
    }
    c.tag = 'S';
    if (P::SWARM_AS_FORTRESS) return c;
    c.swarm = true;
    const int cap = std::min(SWARM_PARAMS.headCap, unitLimit - P::SX_HEADROOM);
    c.explode = true; c.headTarget = std::min(row.headsR100, cap);
    c.resplit = true; c.headTargetB = std::min(row.h250, cap); c.resplitNeedDeficit = true;
    c.curve[0] = std::min(row.h10, cap); c.curve[1] = std::min(row.h25, cap); c.curve[2] = std::min(row.h50, cap);
    c.curve[3] = std::min(row.headsR100, cap); c.curve[4] = std::min(row.h250, cap);
    c.convStart = row.convClock > 0 ? row.convClock : 375; c.broadcastRound = 1;
    c.disperse = true; c.claimSonar = true; c.spawnClear = true; c.d8Veto = row.d8Veto;
    if (P::FRONTIER_ON) { const FrontPolicy* f = lookupFront(row); if (f) c.front = f->share; }   // v1.1 A
    c.kingFloor = P::KING_FLOOR_ON;                                                              // v1.1 B
    // v1.6.1 (W2): every strcmp below is guarded, so a SWARM default or an Unknown row (fam nullptr) gets none of these and cannot crash
    c.harvest = P::HARVEST_ON && row.fam && (std::strcmp(row.fam, "Trauma") == 0 || std::strcmp(row.fam, "Slithery_Fight") == 0);   // v1.3 HV
    c.harvestQueue = c.harvest && P::HV2_ON && std::strcmp(row.fam, "Trauma") == 0;                                        // v1.3 HV2
    // v1.6 CONV2 (conv2.cpp): the SE rows Slithery Fight a/b (and its family row: both layouts take it), Schooltime a, Trauma
    c.conv2 = P::CONV2_ON && row.fam && (std::strcmp(row.fam, "Slithery_Fight") == 0 || std::strcmp(row.fam, "Trauma") == 0 ||
                                         (std::strcmp(row.fam, "Schooltime") == 0 && row.layout == 'a'));
    c.cv2KMin = c.conv2 && std::strcmp(row.fam, "Trauma") != 0 ? P::CV2_KMIN : 0;   // v1.6b: Trauma keeps the bootstrap
    return c;
}

// The row for this process's recognition state: the decided layout's row, else its family's row, else DEFAULT_POLICY.
inline const MapPolicy& lookupPolicy(const World& w) {
    for (const MapPolicy& p : MAP_POLICY) if (p.layout != '*' && w.mapIs(p.fam, p.layout)) return p;
    for (const MapPolicy& p : MAP_POLICY) if (p.layout == '*' && w.mapFamIs(p.fam)) return p;
    return DEFAULT_POLICY;
}

// Per-process selector: looks the row up again only when the recognition state (World::mapStateCode) changes. v1: config() is the
// row's EngineConfig (rebuilt with the row).
class PolicySelector {
  public:
    const MapPolicy& get(const World& w) {
        const int s = w.mapStateCode();
        if (s != state_) { cur_ = &lookupPolicy(w); state_ = s; cfg_ = makeConfig(*cur_, w.unitLimit); }
        return *cur_;
    }
    const EngineConfig& config() const { return cfg_; }
  private:
    int state_ = -1000;                       // no mapStateCode() value
    const MapPolicy* cur_ = &DEFAULT_POLICY;
    EngineConfig cfg_ = FORTRESS_CONFIG;
};

} // namespace seed0
