#!/usr/bin/env python3
"""W2 test builds (exp/w2/bot-*), each a copy of a versions/ bot with one patch:
  bot-off            v1.6.1 with MAPID2_ON = false (C1: must be v1.6 event for event)
  bot-v16-noDevil    v1.6 whose recognition never considers the Devil family (C5: devil.map becomes a same-size unseen map)
  bot-v161-noDevil   v1.6.1, the same
  bot-v16-noPD       v1.6 without the Prisoners Dilemma family (C5 on prisoners_dilemma.map)
  bot-v161-noPD      v1.6.1, the same
usage (repository root): python3 exp/w2/mkbuilds.py"""
import os, shutil, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def copy(src, dst):
    d = os.path.join(ROOT, 'exp/w2', dst)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(ROOT, src), d)
    return d
def patch(path, old, new):
    s = open(path).read()
    assert s.count(old) == 1, (path, old)
    open(path, 'w').write(s.replace(old, new))
d = copy('versions/v1.6.1/bot', 'bot-off')
patch(os.path.join(d, 'params.hpp'), 'constexpr bool   MAPID2_ON = true;', 'constexpr bool   MAPID2_ON = false;   // exp/w2 bot-off')
LOOP = "    for (int i = 0; i < mapdb::COUNT && nMapCand < 16; i++) if (mapdb::MAPS[i].W == geo.W && mapdb::MAPS[i].H == geo.H) mapCand[nMapCand++] = i;\n"
for ver, tag in (('versions/v1.6/bot', 'v16'), ('versions/v1.6.1/bot', 'v161')):
    for fam, short in (('Devil', 'noDevil'), ('Prisoners_Dilemma', 'noPD')):
        d = copy(ver, 'bot-%s-%s' % (tag, short))
        patch(os.path.join(d, 'mapid.cpp'), LOOP,
              "    for (int i = 0; i < mapdb::COUNT && nMapCand < 16; i++) if (mapdb::MAPS[i].W == geo.W && mapdb::MAPS[i].H == geo.H &&\n"
              "        std::strcmp(mapdb::MAPS[mapdb::MAPS[i].fam].name, \"%s\") != 0) mapCand[nMapCand++] = i;   // exp/w2 leave-one-out\n" % fam)
print('ok')
