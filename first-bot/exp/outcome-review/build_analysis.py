#!/usr/bin/env python3
"""Finalize the staged analysis as a new path, preserving the original draft."""
from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'analyse.py').read_text()
s=s.replace("t['faultGames']+=int(any(sum(r[s]['fl'][42+6])>0 for s in ['A','B'])) if False else 0", "t['faultGames']+=int(any(sum(r[s]['fl'][46])>0 for s in ['A','B']))")
s=s.replace("def write(p,value):", '''last_guard=0
def guard():
    global last_guard
    if time.monotonic()-last_guard<20:return
    last_guard=time.monotonic()
    m=subprocess.check_output(['/usr/bin/memory_pressure'],text=True)
    f=int(re.search(r'System-wide memory free percentage:\\s*(\\d+)%',m)[1])
    d=int(subprocess.check_output(['/bin/df','-g','/'],text=True).splitlines()[-1].split()[3])
    if f<10 or d<20:raise SystemExit('PAUSE resource threshold')

def write(p,value):''')
s=s.replace('for iteration in range(80):','for iteration in range(80):\n            guard()')
s=s.replace('for line in f:\n        if not line.strip():continue','for line in f:\n        guard()\n        if not line.strip():continue')
with open(p/'analyse-v2.py','x') as f:f.write(s)
print('created analyse-v2.py')
