#!/usr/bin/env python3
# exp/gen (unknown-map baseline, exp/gen/PLAN.md): builds for v1.2 / v1.3 / v1.5 with two compile switches added to a copy:
#   GEN_DEFAULT_SWARM: an unknown map (World::mapNone) runs the SWARM engine with the generic row UNKNOWN_SWARM_POLICY (the per-parameter median
#     of the seven swarm-family rows; fam "Unknown" so that v1.3's makeConfig strcmp never sees a null name) instead of DEFAULT_POLICY (FORTRESS);
#     a map not recognised yet (first windows) keeps DEFAULT_POLICY, so recognised maps play as shipped;
#   GEN_MAPID_OFF: recognition forced off (World::initMapId leaves no table candidate: mapNone from the first turn), for the known maps.
# usage: python3 exp/gen/mkbuilds.py   (writes exp/gen/bot-<v12|v13|v15>-<F|S>[-noid]/; the F build with recognition on is the original)
import os, re, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = {'v12': 'versions/v1.2/bot', 'v13': 'versions/v1.3/bot', 'v15': 'versions/v1.5/bot'}
def build(ver, swarm, noid):
    name = f"bot-{ver}-{'S' if swarm else 'F'}{'-noid' if noid else ''}"
    dst = os.path.join(ROOT, 'exp', 'gen', name)
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(os.path.join(ROOT, SRC[ver]), dst)
    p = os.path.join(dst, 'params.hpp'); s = open(p).read()
    tail = '}} // namespace seed0::P'
    i = s.rindex(tail)
    s = s[:i] + ('// ---- exp/gen (unknown-map baseline, exp/gen/PLAN.md) ----\n'
                 f'constexpr bool   GEN_DEFAULT_SWARM = {"true" if swarm else "false"};   // an unknown map (World::mapNone) runs SWARM with policy.hpp UNKNOWN_SWARM_POLICY\n'
                 f'constexpr bool   GEN_MAPID_OFF = {"true" if noid else "false"};       // recognition forced off (World::initMapId: mapNone from the first turn)\n\n') + s[i:]
    open(p, 'w').write(s)
    p = os.path.join(dst, 'policy.hpp'); s = open(p).read()
    old = "inline constexpr MapPolicy DEFAULT_POLICY = {nullptr, '*', Engine::FORTRESS, 0, 0, 0, 0, 0, 0, false};\n"
    assert old in s
    s = s.replace(old, old + ("// exp/gen: the generic swarm row for unknown maps (GEN_DEFAULT_SWARM): the per-parameter median of the seven swarm-family rows above\n"
                             "// (h100 28, clock 335, h10 6, h25 6, h50 11, h250 38, d8 veto); fam \"Unknown\" matches no table name\n"
                             "inline constexpr MapPolicy UNKNOWN_SWARM_POLICY = {\"Unknown\", '*', Engine::SWARM, 28, 335, 6, 6, 11, 38, true};\n"))
    old = "    return DEFAULT_POLICY;\n}"
    assert old in s
    s = s.replace(old, "    return P::GEN_DEFAULT_SWARM && w.mapNone ? UNKNOWN_SWARM_POLICY : DEFAULT_POLICY;   // exp/gen\n}")
    open(p, 'w').write(s)
    p = os.path.join(dst, 'mapid.cpp'); s = open(p).read()
    old = "    nMapCand = 0; mapChecks = 0; mapIdx = -1; mapFam = -1; mapLayout = '?'; mapType = 0; mapNone = false; mapDecidedRound = -1;\n"
    assert old in s
    s = s.replace(old, old + "    if (P::GEN_MAPID_OFF) { mapNone = true; return; }   // exp/gen: recognition forced off\n")
    open(p, 'w').write(s)
    return name
for ver in SRC:
    for swarm, noid in [(True, False), (False, True), (True, True)]:
        print(build(ver, swarm, noid))
