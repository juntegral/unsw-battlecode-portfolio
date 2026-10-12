#!/usr/bin/env python3
# v1.6h builds (versions/v1.6/VERSION.md §10): variants of exp/v16/bot-h with params.hpp switches set (the source is never edited otherwise).
#   hF       : FORTRESS-late CONV2 through the spread gate (CV2_FORT_ON)                       the FORTRESS-default set, held-out maps (recognition on)
#   hF-noid  : + recognition off (CV2_EVAL_MAPID_OFF)                                          the FORTRESS-default set, known maps
#   h-off    : the four v1.6h switches off (= v1.6g; identity)
# usage: python3 exp/v16/mkh.py
import os, re, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'exp', 'v16', 'bot-h')
VARIANTS = {
    'hF': {'CV2_FORT_ON': 'true'},
    'hF-noid': {'CV2_FORT_ON': 'true', 'CV2_EVAL_MAPID_OFF': 'true'},
    'h-off': {'CV2_EVIDENCE_LEN': 'false', 'CV2_JIT_ON': 'false', 'CV2_TB_ON': 'false', 'CV2_SPREAD_ON': 'false'},
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
