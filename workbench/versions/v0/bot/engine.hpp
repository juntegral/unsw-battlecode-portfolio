// engine.hpp — the engines of the engine layer (ENGINE.md). Each turn main.cpp asks policy.hpp which engine decides, calls
// it, and labels the indicator " E=F" / " E=S".
//   FORTRESS  stack11's decision path: Planner::decide() (plan.cpp), unchanged.
//   SWARM     v0 stub: forwards to FORTRESS through the same Planner object, so the per-process memory (Planner and World)
//             carries on as before and every action is stack11's (tools/fingerprint.js identical to benchmark/). Later
//             versions put the swarm economy here (ENGINE.md §3, §5) and read SWARM_PARAMS and the map row's targets.
#pragma once
#include "plan.hpp"
#include "policy.hpp"

namespace seed0 {

class EngineSwarm {
  public:
    explicit EngineSwarm(Planner& fortress) : fortress_(fortress) {}
    Action decide(const MapPolicy& /*row*/) { return fortress_.decide(); }   // v0: no behaviour of its own
  private:
    Planner& fortress_;
};

} // namespace seed0
