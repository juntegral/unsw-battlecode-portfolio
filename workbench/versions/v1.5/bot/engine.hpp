// engine.hpp — the engines of the engine layer (ENGINE.md). Each turn main.cpp asks policy.hpp which engine decides, calls
// it, and labels the indicator " E=F" / " E=S".
//   FORTRESS  stack11's decision path: Planner::decide() (plan.cpp) with FORTRESS_CONFIG, i.e. decideImpl<false>, compiled as stack11's decide().
//   SWARM     unsw-swarm v1: the same Planner object (per-process memory carries on) with the row's swarm EngineConfig (policy.hpp
//             makeConfig), i.e. decideImpl<true>: explosion, dispersal, re-split, local feed, spawn clearance (ENGINE.md §3,
//             versions/v1/VERSION.md). With params.hpp SWARM_AS_FORTRESS the config is FORTRESS_CONFIG (the identity build).
#pragma once
#include "plan.hpp"
#include "policy.hpp"

namespace seed0 {

class EngineSwarm {
  public:
    explicit EngineSwarm(Planner& planner) : planner_(planner) {}
    Action decide(const MapPolicy& /*row*/, const EngineConfig& cfg) { planner_.setConfig(&cfg); return planner_.decide(); }
  private:
    Planner& planner_;
};

} // namespace seed0
