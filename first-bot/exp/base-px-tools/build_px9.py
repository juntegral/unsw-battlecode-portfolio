#!/usr/bin/env python3
"""build_px9.py — regenerate the base-px9 variants from exp/base-px9/bot (run from the repository root).
  base-px9b = px9 + late exit: from FORT_EXIT (330) the fortress peels 2 off its tail once, so the next child is born two
              tiles nearer, in an open-sided cell, and leaves the corridor (an ordinary big dragon, the late king)
  base-px9d = px9b, but the exit only while the team has >= FORT_EXIT_UNITS (22) dragons and up to FORT_EXIT_LAST (420)
  base-px9c = px9d + exp/base-px-tools/patch_rules.py (decision rules R3, R4, R8)
  base-px9e = px9c, but px8's late sacrifice pulls also work with enemy heads in view (only the new top-rule path
              needs none); the receiver floor of 8 stays
  base-px9f = px9c with RULE_SAC off: ablation with R4 and R8 only
"""
import os, shutil, subprocess, sys

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'exp', 'base-px9', 'bot')

def sub(text, old, new, what):
    assert text.count(old) == 1, 'anchor not unique or missing: ' + what
    return text.replace(old, new)

def copy(name):
    d = os.path.join(ROOT, 'exp', name, 'bot')
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(SRC, d)
    return d

def edit(d, name, style_fn, core_fn):
    sp, cp = os.path.join(d, 'style.hpp'), os.path.join(d, 'pxcore.cpp')
    s, c = open(sp).read(), open(cp).read()
    s = sub(s, 'constexpr const char* NAME = "base-px9";', 'constexpr const char* NAME = "%s";' % name, 'name')
    s, c = style_fn(s), core_fn(c)
    open(sp, 'w').write(s); open(cp, 'w').write(c)

EXIT_STYLE = '''constexpr int FORT_EXIT = 330;             // px9b: from this round the fortress peels 2 off its tail once, so the next child is
                                            // born 2 tiles nearer, in an open-sided cell, and walks out to become the late king
'''
def style_b(s):
    return sub(s, 'constexpr bool FORT_QUIET = true;', EXIT_STYLE + 'constexpr bool FORT_QUIET = true;', 'exit style')
def style_d(s):
    return sub(style_b(s), 'constexpr bool FORT_QUIET = true;', '''constexpr int FORT_EXIT_UNITS = 22;         // px9d: ... only while the team has this many dragons (our swarm holds the map and can
constexpr int FORT_EXIT_LAST = 420;         // feed the king); no exit after this round
constexpr bool FORT_QUIET = true;''', 'exit units')

def core_exit(cond):
    def f(c):
        c = sub(c, '''    std::vector<int> fortReg;
    bool fortDecide(Plan& p) {''', '''    std::vector<int> fortReg;
    bool peeled = false;   // px9b
    bool fortDecide(Plan& p) {''', 'peeled')
        c = sub(c, '''        bool canSplit = units < unitLimit && L - 2 >= 2 && childRoom(2) != 0;
        if (bd >= 0 && !(bdDead && !bdPearl)) {''', '''        bool canSplit = units < unitLimit && L - 2 >= 2 && childRoom(2) != 0;
        // px9b: leave late. Peel 2 off the tail once while the head still has room: every later child is born 2 tiles
        // nearer, outside the 1-wide end of the corridor, and becomes an ordinary (big) dragon
        if (%s && !peeled && units < unitLimit && L - 2 >= style::FORT_MIN_LEN) {
            peeled = true; p.kind = Plan::SPLIT; p.child = 2; p.tag = 'P'; return true;
        }
        if (bd >= 0 && !(bdDead && !bdPearl)) {''' % cond, 'peel')
        c = sub(c, '''            if (p.kind == Plan::SPLIT) snprintf(b, sizeof b, "escape-split%d L%d fort R%d", p.child, L, fortN);''',
                '''            if (p.kind == Plan::SPLIT && p.tag == 'P') snprintf(b, sizeof b, "peel-split%d L%d fort R%d", p.child, L, fortN);
            else if (p.kind == Plan::SPLIT) snprintf(b, sizeof b, "escape-split%d L%d fort R%d", p.child, L, fortN);''', 'indicator')
        return c
    return f

db = copy('base-px9b'); edit(db, 'base-px9b', style_b, core_exit('round >= style::FORT_EXIT'))
dd = copy('base-px9d'); edit(dd, 'base-px9d', style_d, core_exit('round >= style::FORT_EXIT && round <= style::FORT_EXIT_LAST && units >= style::FORT_EXIT_UNITS'))
dc = os.path.join(ROOT, 'exp', 'base-px9c', 'bot')
if os.path.exists(dc): shutil.rmtree(dc)
shutil.copytree(dd, dc)
s = open(os.path.join(dc, 'style.hpp')).read()
open(os.path.join(dc, 'style.hpp'), 'w').write(sub(s, 'constexpr const char* NAME = "base-px9d";', 'constexpr const char* NAME = "base-px9c";', 'name c'))
subprocess.check_call([sys.executable, os.path.join(ROOT, 'exp', 'base-px-tools', 'patch_rules.py'), dc])
print('built base-px9b, base-px9d, base-px9c from', SRC)

# base-px9e (see the docstring)
de = os.path.join(ROOT, 'exp', 'base-px9e', 'bot')
if os.path.exists(de): shutil.rmtree(de)
shutil.copytree(dc, de)
s = open(os.path.join(de, 'style.hpp')).read()
open(os.path.join(de, 'style.hpp'), 'w').write(sub(s, 'constexpr const char* NAME = "base-px9c";', 'constexpr const char* NAME = "base-px9e";', 'name e'))
c = open(os.path.join(de, 'pxcore.cpp')).read()
c = sub(c, '        for (auto& s : vis) if (s.team != myTeam && s.head >= 0) return false;\n',
        '        bool enemyInView = false; for (auto& s : vis) if (s.team != myTeam && s.head >= 0) enemyInView = true;\n'
        '        if (enemyInView && round < style::SAC_START) return false;   // px9e: the late px8 pulls ignore enemies\n', 'e enemy')
c = sub(c, '            if (small && m <= 3) q = round < 350 ? style::SAC_EARLY_P : style::SAC_TOP_P;',
        '            if (small && m <= 3 && !enemyInView) q = round < 350 ? style::SAC_EARLY_P : style::SAC_TOP_P;', 'e top')
open(os.path.join(de, 'pxcore.cpp'), 'w').write(c)
print('built base-px9e')

# base-px9f = px9c with RULE_SAC off (px8's sacrifice rule): an ablation keeping only R4 (ram table) and R8 (escape)
df = os.path.join(ROOT, 'exp', 'base-px9f', 'bot')
if os.path.exists(df): shutil.rmtree(df)
shutil.copytree(dc, df)
s = open(os.path.join(df, 'style.hpp')).read()
s = sub(s, 'constexpr const char* NAME = "base-px9c";', 'constexpr const char* NAME = "base-px9f";', 'name f')
s = sub(s, 'constexpr bool RULE_SAC = true; ', 'constexpr bool RULE_SAC = false;', 'f sac')
open(os.path.join(df, 'style.hpp'), 'w').write(s)
print('built base-px9f')
