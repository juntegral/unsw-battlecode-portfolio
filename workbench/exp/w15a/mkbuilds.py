#!/usr/bin/env python3
"""W15a builds (exp/w15a/bot-*), each a copy of versions/v1.7/bot with switch edits in params.hpp:
  bot-base        v1.7 at 1a00684 (H0 merged; W7b, W7c on): the W15a reference
  bot-base-diag   bot-base that also writes every candidate's base, area safety, continuation and end-tile threat in a MOVE indicator
  bot-off         v1.7 with the W15a code, every W15a switch off: must equal bot-base event for event
  bot-s / bot-k / bot-t   v1.7 + DEADSPLIT_ON / DEADKNOWN_ON / ESCTAIL_ON (VERSION.md §17)
  bot-t2          bot-t whose trigger is any child region without a known cycle (no walled-corridor condition on an unknown region)
  bot-p           v1.7 + ESCPEEL_ON (VERSION.md §18: the elite start-pocket exit, peel 2 off the tail while the board traps us)
usage (repository root): python3 exp/w15a/mkbuilds.py [names...]"""
import os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def build(src, dst, edits):
    d = os.path.join(ROOT, 'exp/w15a', dst)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(ROOT, src), d)
    p = os.path.join(d, 'params.hpp'); s = open(p).read()
    for old, new in edits:
        assert s.count(old) == 1, (dst, old)
        s = s.replace(old, new + '   // exp/w15a ' + dst)
    open(p, 'w').write(s)
def diag(dst):
    p = os.path.join(ROOT, 'exp/w15a', dst, 'plan.cpp'); s = open(p).read()
    old = "    long long tp4 = nowPoints();\n"
    assert s.count(old) == 1
    s = s.replace(old, old + "    std::string w7diag = \" [\";\n    for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal) { char b[96]; std::string ds; for (int d : cands[i].dirs) ds += DIRCH[d];\n        snprintf(b, sizeof b, \"%s:b%.1f/s%.1f/c%.1f/t%.1f \", ds.c_str(), cands[i].base, safety[i], value[i] - cands[i].base - safety[i], cands[i].tiles.empty() ? 0.0 : threatAt(cands[i].tiles.back())); w7diag += b; }\n    w7diag += \"]\";\n", 1)
    old2 = "    if (c.esc) act.indicator += \" esc\";                                                            // cand-avoid2\n"
    assert s.count(old2) == 1
    s = s.replace(old2, old2 + "    act.indicator += w7diag;   // exp/w15a diag\n", 1)
    open(p, 'w').write(s)
want = set(sys.argv[1:])
if want & {'bot-off', 'bot-s', 'bot-k', 'bot-t'} or not want:
    pass
def on(n): return not want or n in want
if on('bot-base'): build('versions/v1.7/bot', 'bot-base', [])
if on('bot-base-diag'): build('versions/v1.7/bot', 'bot-base-diag', []); diag('bot-base-diag')
if on('bot-off'): build('versions/v1.7/bot', 'bot-off', [])
if on('bot-s'): build('versions/v1.7/bot', 'bot-s', [('constexpr bool   DEADSPLIT_ON = false;', 'constexpr bool   DEADSPLIT_ON = true;')])
if on('bot-k'): build('versions/v1.7/bot', 'bot-k', [('constexpr bool   DEADKNOWN_ON = false;', 'constexpr bool   DEADKNOWN_ON = true;')])
if on('bot-t'): build('versions/v1.7/bot', 'bot-t', [('constexpr bool   ESCTAIL_ON = false;', 'constexpr bool   ESCTAIL_ON = true;')])
def t2(dst):
    p = os.path.join(ROOT, 'exp/w15a', dst, 'plan.cpp'); s = open(p).read()
    old = "    if (r == 1) {\n        int along = -1;"
    assert s.count(old) == 1
    s = s.replace(old, "    if (false) {   // exp/w15a t2: any region without a known cycle\n        int along = -1;", 1)
    open(p, 'w').write(s)
if on('bot-p'): build('versions/v1.7/bot', 'bot-p', [('constexpr bool   ESCPEEL_ON = false;', 'constexpr bool   ESCPEEL_ON = true;')])
if on('bot-t2'): build('versions/v1.7/bot', 'bot-t2', [('constexpr bool   ESCTAIL_ON = false;', 'constexpr bool   ESCTAIL_ON = true;')]); t2('bot-t2')
print('ok')
