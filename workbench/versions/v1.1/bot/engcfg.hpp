// engcfg.hpp — the runtime values that differ between engines (unsw-swarm v1; ENGINE.md §3, versions/v1/VERSION.md).
// policy.hpp fills one per recognised map and layout. Which rules run is the engine's (Planner::decideImpl<SW>: the swarm instantiation
// has its own split, target and feed rules; versions/v1/VERSION.md "SWARM rule table"); this struct carries the per-map values and the
// swarm sub-rules that can be switched off one at a time. FORTRESS_CONFIG holds stack11's values (benchmark/ identical).
#pragma once
#include "params.hpp"

namespace seed0 {

struct EngineConfig {
    char tag = 'F';                  // the " E=<tag>" label
    bool swarm = false;              // Planner::decide() runs the swarm instantiation (false for SWARM_AS_FORTRESS too)
    bool econW4 = false;             // v1 5b: the FORTRESS instantiation with the W4-era economy (Autarky, PD6)
    // ---- phase A: explosion (sx) ----
    bool explode = false;
    int headTarget = 0;              // A: our living units at r100 (the map/layout row), capped
    // ---- phase B: eat and re-split (sr) ----
    bool resplit = false;
    int headTargetB = 0;             // B: max(r100 target, SwarmParams::headsR250), capped
    bool resplitNeedDeficit = false; // research transfer 17: 2 + 2 only while a service deficit exists
    // ---- phase C: conversion ----
    int convStart = P::CONV_START;   // the swarm engine's local feed (sf) clock (per map; FORTRESS keeps stack1 conv at CONV_START)
    int broadcastRound = P::GATHER_BROADCAST; // every ray carries our message from here
    // ---- dispersal, claims, spawn clearance ----
    bool disperse = false;           // sd: replaces F (stack5 / stack8 F2)
    bool claimSonar = false;         // the hotspot field carries our sd target; allies' hotspots are claims, not attraction sources
    bool spawnClear = false;         // sc
    // ---- v1 final (map atlas interim) ----
    int curve[5] = {0, 0, 0, 0, 0};  // head targets at r10 / r25 / r50 / r100 / r250 (linear between, held after r250)
    bool d8Veto = false;             // the trade veto on local balance d8 <= LNT_D8_VETO (heads within Manhattan 8), not stack10's d3
    // ---- v1.1 (versions/v1.1/VERSION.md) ----
    const unsigned char (*front)[5] = nullptr;   // A: head share % by frontier bin at r25 / r50 / r100 / r250 (policy.hpp FRONT_POLICY); nullptr = v1's sd
    bool kingFloor = false;                      // B: the king class keeps its path distance floor to enemy heads
    // A: the share of bin b at round r (percent): linear between the checkpoints, r25's before r25, held after r250
    double frontShare(int r, int b) const {
        static constexpr int R[4] = {25, 50, 100, 250};
        if (r <= R[0]) return front[0][b];
        for (int i = 1; i < 4; i++) if (r <= R[i]) return front[i - 1][b] + (double)(front[i][b] - front[i - 1][b]) * (r - R[i - 1]) / (R[i] - R[i - 1]);
        return front[3][b];
    }
    int headsAt(int r) const {
        static constexpr int R[5] = {10, 25, 50, 100, 250};
        if (r <= R[0]) return curve[0];
        for (int i = 1; i < 5; i++) if (r <= R[i]) return curve[i - 1] + (curve[i] - curve[i - 1]) * (r - R[i - 1]) / (R[i] - R[i - 1]);
        return curve[4];
    }
};

inline constexpr EngineConfig FORTRESS_CONFIG{};

} // namespace seed0
