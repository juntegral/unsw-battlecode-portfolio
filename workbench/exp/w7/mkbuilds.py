#!/usr/bin/env python3
"""v1.7 / W7 test builds (exp/w7/bot-*), each a copy of a versions/ bot with switch edits in params.hpp:
  bot-v17-g       v1.7 with QUAL_NO_MAPID and MAPID2_ON false: must be v1.6g event for event (V1)
  bot-v16g-noid   v1.6g (versions/v1.6) with CV2_EVAL_MAPID_OFF true: the reference of the shipped v1.7 (V2)
  bot-a           v1.7 + SMALL_REACH_ON (W7a)
  bot-b           v1.7 + SMALL_SPLIT_ON (W7b)
  bot-ab          v1.7 + both
  bot-a2          v1.7 + SMALL_FIRST_ON (W7a', §7)
  bot-a-diag, bot-a2-diag  bot-a / bot-a2 that also write every candidate's base, area safety, continuation and end-tile threat in a MOVE indicator
  bot-c           v1.7 (W7b on since 17:05) + SMALL_ALLYBOX_ON (W7c, §11)
  bot-d           v1.7 (W7b, W7c on since 17:50) + SMALL_DRIFT_ON (W7d, §14)
usage (repository root): python3 exp/w7/mkbuilds.py"""
import os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def build(src, dst, edits):
    d = os.path.join(ROOT, 'exp/w7', dst)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(ROOT, src), d)
    p = os.path.join(d, 'params.hpp'); s = open(p).read()
    for old, new in edits:
        assert s.count(old) == 1, (dst, old)
        s = s.replace(old, new + '   // exp/w7 ' + dst)
    open(p, 'w').write(s)
build('versions/v1.7/bot', 'bot-v17-g', [('constexpr bool   QUAL_NO_MAPID = true;', 'constexpr bool   QUAL_NO_MAPID = false;'), ('constexpr bool   MAPID2_ON = true;', 'constexpr bool   MAPID2_ON = false;')])
build('versions/v1.6/bot', 'bot-v16g-noid', [('constexpr bool   CV2_EVAL_MAPID_OFF = false;', 'constexpr bool   CV2_EVAL_MAPID_OFF = true;')])
build('versions/v1.7/bot', 'bot-a', [('constexpr bool   SMALL_REACH_ON = false;', 'constexpr bool   SMALL_REACH_ON = true;')])
build('versions/v1.7/bot', 'bot-b', [('constexpr bool   SMALL_SPLIT_ON = false;', 'constexpr bool   SMALL_SPLIT_ON = true;')])
build('versions/v1.7/bot', 'bot-ab', [('constexpr bool   SMALL_REACH_ON = false;', 'constexpr bool   SMALL_REACH_ON = true;'), ('constexpr bool   SMALL_SPLIT_ON = false;', 'constexpr bool   SMALL_SPLIT_ON = true;')])
build('versions/v1.7/bot', 'bot-a2', [('constexpr bool   SMALL_FIRST_ON = false;', 'constexpr bool   SMALL_FIRST_ON = true;')])
def diag(dst):
    p = os.path.join(ROOT, 'exp/w7', dst, 'plan.cpp'); s = open(p).read()
    old = "    long long tp4 = nowPoints();\n"
    assert s.count(old) == 1
    s = s.replace(old, old + "    std::string w7diag = \" [\";\n    for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal) { char b[96]; std::string ds; for (int d : cands[i].dirs) ds += DIRCH[d];\n        snprintf(b, sizeof b, \"%s:b%.1f/s%.1f/c%.1f/t%.1f \", ds.c_str(), cands[i].base, safety[i], value[i] - cands[i].base - safety[i], cands[i].tiles.empty() ? 0.0 : threatAt(cands[i].tiles.back())); w7diag += b; }\n    w7diag += \"]\";\n", 1)
    old2 = "    if (c.esc) act.indicator += \" esc\";                                                            // cand-avoid2\n"
    assert s.count(old2) == 1
    s = s.replace(old2, old2 + "    act.indicator += w7diag;   // exp/w7 diag\n", 1)
    open(p, 'w').write(s)
build('versions/v1.7/bot', 'bot-a-diag', [('constexpr bool   SMALL_REACH_ON = false;', 'constexpr bool   SMALL_REACH_ON = true;')]); diag('bot-a-diag')
build('versions/v1.7/bot', 'bot-a2-diag', [('constexpr bool   SMALL_FIRST_ON = false;', 'constexpr bool   SMALL_FIRST_ON = true;')]); diag('bot-a2-diag')
build('versions/v1.7/bot', 'bot-c', [('constexpr bool   SMALL_ALLYBOX_ON = false;', 'constexpr bool   SMALL_ALLYBOX_ON = true;')])
build('versions/v1.7/bot', 'bot-d', [('constexpr bool   SMALL_DRIFT_ON = false;', 'constexpr bool   SMALL_DRIFT_ON = true;')])
print('ok')
