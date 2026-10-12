#!/usr/bin/env python3
"""Assemble redteam-2.md from the part files y_p*.md (in name order). Missing parts are named in the output."""
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(HERE, "y_p*.md")))
out = []
for p in parts:
    with open(p) as f:
        out.append(f.read().rstrip() + "\n")
text = "\n".join(out)
with open(os.path.join(HERE, "redteam-2.md"), "w") as f:
    f.write(text)
print("parts:", [os.path.basename(p) for p in parts])
print("lines:", text.count("\n"), "chars:", len(text))
