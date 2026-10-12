#!/usr/bin/env python3
"""d_cols.py <file> <first line> <last line> <col,col,...>: print chosen '|'-separated columns of a table file,
one measure per line (sub-session A4, helper for reading wide tables).  Column 0 is the row label."""
import sys

path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cols = [int(c) for c in sys.argv[4].split(",")]
for i, line in enumerate(open(path), 1):
    if a <= i <= b:
        p = [x.strip() for x in line.rstrip("\n").split("|")]
        if len(p) < 2:
            print(line.rstrip())
            continue
        print(" | ".join(p[c] if c < len(p) else "" for c in [0] + cols))
