#!/usr/bin/env python3
"""d_qrun.py <gid:side[:extra args separated by ;]> ...: run d_q.py for many queens in parallel, each into
d_out/q/<gid>_<side>.txt (sub-session A4, helper).  With side 'AB' both queens are done."""
import os
import subprocess
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))


def one(spec):
    p = spec.split(":")
    gid, side = p[0], p[1]
    extra = p[2].split(";") if len(p) > 2 and p[2] else []
    out = os.path.join(HERE, "d_out", "q", f"{gid}_{side}.txt")
    with open(out, "w") as f:
        subprocess.run([sys.executable, os.path.join(HERE, "d_q.py"), gid, side] + extra, stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
    return spec


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "d_out", "q"), exist_ok=True)
    specs = []
    for a in sys.argv[1:]:
        p = a.split(":")
        if p[1] == "AB":
            specs += [":".join([p[0], "A"] + p[2:]), ":".join([p[0], "B"] + p[2:])]
        else:
            specs.append(a)
    os.nice(10)
    with Pool(3) as pool:
        for s in pool.imap_unordered(one, specs):
            pass
    print("done", len(specs))
