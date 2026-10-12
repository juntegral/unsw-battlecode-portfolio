#!/usr/bin/env python3
"""Q2 builds (exp/q2/bot-*), each a copy of versions/v1.8/bot with switch edits in params.hpp:
  bot-v18off   v1.8 with every Q2 switch off: must equal bot-v17 (v1.7 at 8654c5e) event for event
  bot-a / bot-b / bot-c   Q2A_NOSPLIT_ON / Q2B_SAFE_ON / Q2C_HUNT_ON
  bot-ab, bot-abc        combinations
  bot-abcn       abc + Q2A_NOESC_ON (the queen skips enemy-doom escape splits)
  bot-abcnd      abcn + Q2D_FREESTEP_ON (our free steps)
  bot-v18off2    v1.8 with every switch off after Q2a2 and Q2d were added (identity again)
  bot-abcnef     abcn + Q2E_ROOM_ON + Q2F_NOBOX_ON
  bot-v18off3    every switch off after Q2e and Q2f were added
  bot-cand       Q2a (+ worker rule) a2 b c e f (+ zone) g on, DEADSPLIT_ON (v1.8 default on): the Q2 candidate without free steps
  bot-candd      bot-cand + Q2D_FREESTEP_ON
  bot-hunter     bot-cand with a stronger hunt (QUEEN_HUNT_VALUE 10, QUEEN_HUNT_MEMORY 12): the queen-hunting sparring partner
  bot-cand2      bot-cand + Q2H_STALL_ON (and Q2a's no-feed, part of Q2A_NOSPLIT_ON since 22:2x)
  bot-cand2d     bot-cand2 + Q2D_FREESTEP_ON
  bot-cand3      bot-cand2 + Q2I_CAUTION_ON (the queen assumes any head reaches her; no claims or grabs)
  bot-cand4      bot-cand3 + Q2F2_GRADED_ON + Q2J_ESCORT_ON (graded clearance; pieces trade with hunters beside her)
  bot-v18off4    every switch off (DEADSPLIT_ON default on) after Q2f2, Q2i and Q2j were added
  bot-cand5      bot-cand4 + Q2DQ_ON (free-step moves for the queen alone)
  bot-v18off5    every switch off after the instruction paths were kept apart (ks2Threat, tradeValue): identity on deadline-bound maps
  bot-cand6      bot-cand4 + Q2K_PACK_ON (the queen stays within reach of the pack); Q2h's geometry exemption in the code since 23:58
  bot-v18off6    every switch off after Q2k was added
usage (repository root): python3 exp/q2/mkbuilds.py [names...]"""
import os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def build(dst, edits):
    d = os.path.join(ROOT, 'exp/q2', dst)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(ROOT, 'versions/v1.8/bot'), d)
    p = os.path.join(d, 'params.hpp'); s = open(p).read()
    for old, new in edits:
        assert s.count(old) == 1, (dst, old)
        s = s.replace(old, new + '   // exp/q2 ' + dst)
    open(p, 'w').write(s)
A = ('constexpr bool   Q2A_NOSPLIT_ON = false;', 'constexpr bool   Q2A_NOSPLIT_ON = true;')
B = ('constexpr bool   Q2B_SAFE_ON = false;', 'constexpr bool   Q2B_SAFE_ON = true;')
C = ('constexpr bool   Q2C_HUNT_ON = false;', 'constexpr bool   Q2C_HUNT_ON = true;')
N = ('constexpr bool   Q2A_NOESC_ON = false;', 'constexpr bool   Q2A_NOESC_ON = true;')
D = ('constexpr bool   Q2D_FREESTEP_ON = false;', 'constexpr bool   Q2D_FREESTEP_ON = true;')
E = ('constexpr bool   Q2E_ROOM_ON = false;', 'constexpr bool   Q2E_ROOM_ON = true;')
F = ('constexpr bool   Q2F_NOBOX_ON = false;', 'constexpr bool   Q2F_NOBOX_ON = true;')
G = ('constexpr bool   Q2G_DOOMFLAG_ON = false;', 'constexpr bool   Q2G_DOOMFLAG_ON = true;')
HV = ('constexpr double QUEEN_HUNT_VALUE = 3.0;', 'constexpr double QUEEN_HUNT_VALUE = 10.0;')
HM = ('constexpr int    QUEEN_HUNT_MEMORY = 6;', 'constexpr int    QUEEN_HUNT_MEMORY = 12;')
Hs = ('constexpr bool   Q2H_STALL_ON = false;', 'constexpr bool   Q2H_STALL_ON = true;')
I = ('constexpr bool   Q2I_CAUTION_ON = false;', 'constexpr bool   Q2I_CAUTION_ON = true;')
F2 = ('constexpr bool   Q2F2_GRADED_ON = false;', 'constexpr bool   Q2F2_GRADED_ON = true;')
J = ('constexpr bool   Q2J_ESCORT_ON = false;', 'constexpr bool   Q2J_ESCORT_ON = true;')
DQ = ('constexpr bool   Q2DQ_ON = false;', 'constexpr bool   Q2DQ_ON = true;')
K = ('constexpr bool   Q2K_PACK_ON = false;', 'constexpr bool   Q2K_PACK_ON = true;')
want = set(sys.argv[1:])
def on(n): return not want or n in want
if on('bot-v18off'): build('bot-v18off', [])
if on('bot-a'): build('bot-a', [A])
if on('bot-b'): build('bot-b', [B])
if on('bot-c'): build('bot-c', [B, C])   # Q2c always with Q2b: our queen must not chase the enemy queen into a mutual kill
if on('bot-ab'): build('bot-ab', [A, B])
if on('bot-abc'): build('bot-abc', [A, B, C])
if on('bot-abcn'): build('bot-abcn', [A, N, B, C])
if on('bot-abcnd'): build('bot-abcnd', [A, N, B, C, D])
if on('bot-v18off2'): build('bot-v18off2', [])
if on('bot-abcnef'): build('bot-abcnef', [A, N, B, C, E, F])
if on('bot-v18off3'): build('bot-v18off3', [])
if on('bot-cand'): build('bot-cand', [A, N, B, C, E, F, G])
if on('bot-candd'): build('bot-candd', [A, N, B, C, D, E, F, G])
if on('bot-hunter'): build('bot-hunter', [A, N, B, C, E, F, G, HV, HM])
if on('bot-cand2'): build('bot-cand2', [A, N, B, C, E, F, G, Hs])
if on('bot-cand2d'): build('bot-cand2d', [A, N, B, C, D, E, F, G, Hs])
if on('bot-cand3'): build('bot-cand3', [A, N, B, C, E, F, G, Hs, I])
if on('bot-cand4'): build('bot-cand4', [A, N, B, C, E, F, G, Hs, I, F2, J])
if on('bot-v18off4'): build('bot-v18off4', [])
if on('bot-cand5'): build('bot-cand5', [A, N, B, C, E, F, G, Hs, I, F2, J, DQ])
if on('bot-v18off5'): build('bot-v18off5', [])
if on('bot-cand6'): build('bot-cand6', [A, N, B, C, E, F, G, Hs, I, F2, J, K])
if on('bot-v18off6'): build('bot-v18off6', [])
print('ok')
