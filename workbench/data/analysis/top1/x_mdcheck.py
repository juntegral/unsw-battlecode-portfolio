#!/usr/bin/env python3
"""Check redteam.md: every table row has as many cells as its header; every x_ script and x_out file named exists."""
import os
import re

lines = open("redteam.md").read().split("\n")
bad = 0
i = 0
while i < len(lines):
    if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[-| ]+\|\s*$", lines[i + 1]):
        n = lines[i].count("|")
        j = i
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            if lines[j].count("|") != n:
                bad += 1
                print("table row with %d bars, header has %d: line %d: %s" % (lines[j].count("|"), n, j + 1, lines[j][:90]))
            j += 1
        i = j
    else:
        i += 1
text = "\n".join(lines)
tick = chr(96)
names = set(re.findall(tick + r"(x_[a-z0-9_]+\.py)" + tick, text))
missing = sorted(n for n in names if not os.path.exists(n))
outs = set(re.findall(tick + r"(x_out/[A-Za-z0-9_./<>-]+)" + tick, text))
missing_out = sorted(o for o in outs if "<" not in o and not os.path.exists(o.rstrip("/")))
print("tables with a bad row:", bad, "| scripts named:", len(names), "missing:", missing, "| outputs named:", len(outs),
      "missing:", missing_out)
have = {f for f in os.listdir(".") if f.startswith("x_") and f.endswith(".py")}
print("scripts on disk not named in the file:", sorted(have - names))
print("lines:", len(lines), "longest line:", max(len(l) for l in lines))
