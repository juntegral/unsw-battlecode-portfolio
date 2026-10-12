#!/usr/bin/env python3
# v1.6g builds (versions/v1.6/VERSION.md §8): variants of exp/v16/bot-g with params.hpp switches set (the source is never edited otherwise).
#   gS        : an unknown map runs SWARM with the Unknown row (CV2_EVAL_UNKNOWN_SWARM; exp/gen's S build)          (b) on
#   gS-noid   : + recognition off (CV2_EVAL_MAPID_OFF; exp/gen's -noid)                                           (b) on, K set
#   gF        : FORTRESS-late CONV2 (CV2_FORT_ON)                                                                 (c) on
#   gF-noid   : + recognition off                                                                                 (c) on, K set
#   *-off     : CONV2_ON false (v1.3 with the same evaluation switches: identity against exp/gen's v1.3 / v1.2 replays)
# usage: python3 exp/v16/mkg.py
import os, re, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'exp', 'v16', 'bot-g')
VARIANTS = {
    'gS': {'CV2_EVAL_UNKNOWN_SWARM': 'true'},
    'gS-noid': {'CV2_EVAL_UNKNOWN_SWARM': 'true', 'CV2_EVAL_MAPID_OFF': 'true'},
    'gF': {'CV2_FORT_ON': 'true'},
    'gF-noid': {'CV2_FORT_ON': 'true', 'CV2_EVAL_MAPID_OFF': 'true'},
    'g-off': {'CONV2_ON': 'false'},
    'gS-off': {'CONV2_ON': 'false', 'CV2_EVAL_UNKNOWN_SWARM': 'true'},
    'gS-noid-off': {'CONV2_ON': 'false', 'CV2_EVAL_UNKNOWN_SWARM': 'true', 'CV2_EVAL_MAPID_OFF': 'true'},
    'gF-noid-off': {'CONV2_ON': 'false', 'CV2_EVAL_MAPID_OFF': 'true'},
}
for name, sw in VARIANTS.items():
    dst = os.path.join(ROOT, 'exp', 'v16', 'bot-' + name)
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    p = os.path.join(dst, 'params.hpp'); s = open(p).read()
    for k, v in sw.items():
        s, n = re.subn(r'(constexpr bool\s+' + k + r'\s*=\s*)(true|false)', lambda m: m.group(1) + v, s)
        assert n == 1, (name, k, n)
    open(p, 'w').write(s)
    print(name, sw)
