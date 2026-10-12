#!/usr/bin/env python3
# v1.6h2 builds (versions/v1.6/VERSION.md §13): variants of exp/v16/bot-h2 (= versions/v1.6/bot v1.6g+H0 + H1, H1b, H2, H3) with params.hpp switches set.
#   h2F      : FORTRESS-late CONV2 through the spread gate (CV2_FORT_ON); the candidate (the SWARM path is the same as bot-h2's)
#   h2F-noid : + recognition off (the qualifier condition; the known maps as unseen ones)
#   h2-off   : the four v1.6h2 switches off (= v1.6g+H0; identity)
# usage: python3 exp/v16/mkh2.py
import os, re, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'exp', 'v16', 'bot-h2')
VARIANTS = {
    'h2F': {'CV2_FORT_ON': 'true'},
    'h2F-noid': {'CV2_FORT_ON': 'true', 'CV2_EVAL_MAPID_OFF': 'true'},
    'h2-off': {'CV2_JIT_ON': 'false', 'CV2_TRAIL_ON': 'false', 'CV2_TB_ON': 'false', 'CV2_SPREAD_ON': 'false'},
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
