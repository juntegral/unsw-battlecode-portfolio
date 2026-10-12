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
#pragma once
#include <cstdint>

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
                       // cand-stack12.md), before SwarmParams::headCap. 0 = none. Unused in v0.
};

inline constexpr MapPolicy MAP_POLICY[] = {
    // fortress maps (ENGINE.md: Autarky 37/90, Prisoners Dilemma 22/90, Portals 16/90 top-6 wins over 15 waves)
    {"Autarky", '*', Engine::FORTRESS, 0},
    {"Prisoners_Dilemma", '*', Engine::FORTRESS, 0},   // a (6 dragons) and b (the 10-dragon PD10)
    {"Portals", '*', Engine::FORTRESS, 0},
    // swarm maps (ENGINE.md: Trauma 3/90, Slithery Fight 3/90, the other five 0/450)
    {"Trauma", '*', Engine::SWARM, 18},
    {"Slithery_Fight", '*', Engine::SWARM, 57},
    {"Slithery_Fight", 'a', Engine::SWARM, 60},
    {"Slithery_Fight", 'b', Engine::SWARM, 54},
    {"Schooltime", '*', Engine::SWARM, 30},
    {"Schooltime", 'a', Engine::SWARM, 44},
    {"Schooltime", 'b', Engine::SWARM, 16},
    {"Default", '*', Engine::SWARM, 19},              // elimination type
    {"Devil", '*', Engine::SWARM, 26},                // elimination type
    {"Devil", 'a', Engine::SWARM, 29},
    {"Devil", 'b', Engine::SWARM, 23},
    {"Queen_Of_Spades", '*', Engine::SWARM, 13},      // elimination type
    {"Queen_Of_Spades", 'a', Engine::SWARM, 13},
    {"Queen_Of_Spades", 'b', Engine::SWARM, 12},
    {"Trophy", '*', Engine::SWARM, 31},               // elimination type
};
inline constexpr MapPolicy DEFAULT_POLICY = {nullptr, '*', Engine::FORTRESS, 0};

// The row for this process's recognition state: the decided layout's row, else its family's row, else DEFAULT_POLICY.
inline const MapPolicy& lookupPolicy(const World& w) {
    for (const MapPolicy& p : MAP_POLICY) if (p.layout != '*' && w.mapIs(p.fam, p.layout)) return p;
    for (const MapPolicy& p : MAP_POLICY) if (p.layout == '*' && w.mapFamIs(p.fam)) return p;
    return DEFAULT_POLICY;
}

// Per-process selector: looks the row up again only when the recognition state (World::mapStateCode) changes.
class PolicySelector {
  public:
    const MapPolicy& get(const World& w) {
        const int s = w.mapStateCode();
        if (s != state_) { cur_ = &lookupPolicy(w); state_ = s; }
        return *cur_;
    }
  private:
    int state_ = -1000;                       // no mapStateCode() value
    const MapPolicy* cur_ = &DEFAULT_POLICY;
};

} // namespace seed0
