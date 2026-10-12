#!/usr/bin/env python3
"""Check redteam-2.md: every table row has as many cells as its header; every y_ script and output file named in
the text exists; no line is absurdly long outside tables. Output: stdout."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
text = open(os.path.join(HERE, "redteam-2.md")).read()
lines = text.split("\n")
bad = 0
i = 0
while i < len(lines):
    if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|$", lines[i + 1]):
        ncol = lines[i].count("|") - 1
        j = i + 2
        while j < len(lines) and lines[j].startswith("|"):
            if lines[j].count("|") - 1 != ncol:
                bad += 1
                print("table row with %d cells under a header of %d, line %d: %s" % (lines[j].count("|") - 1, ncol, j + 1, lines[j][:90]))
            j += 1
        i = j
    else:
        i += 1
names = set(re.findall(r"`(y_[a-z0-9_]+\.py)`", text))
for n in sorted(names):
    if not os.path.exists(os.path.join(HERE, n)):
        bad += 1
        print("script named but missing:", n)
outs = set(re.findall(r"`(y_out/[a-z0-9_]+\.txt)`", text)) | set("y_out/" + x for x in re.findall(r"`(c[35][a-g]\.txt)`", text))
for n in sorted(outs):
    if not os.path.exists(os.path.join(HERE, n)):
        bad += 1
        print("output named but missing:", n)
have = sorted(f for f in os.listdir(HERE) if f.startswith("y_") and f.endswith(".py"))
for f in have:
    if "`%s`" % f not in text:
        print("script not mentioned in the file:", f)
long_lines = [k + 1 for k, ln in enumerate(lines) if len(ln) > 125 and not ln.startswith("|")]
print("lines:", len(lines), "| table problems and missing files:", bad, "| long text lines:", long_lines[:10])
