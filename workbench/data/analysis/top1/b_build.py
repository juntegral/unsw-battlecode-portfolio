#!/usr/bin/env python3
"""b_build.py: assemble deep-read-2.md from the part files of sub-session A2.

Order: b_head.md, b_g*.md (sorted by name), b_answers.md, b_table.md, b_losses.md, b_wrong.md, b_unknown.md.
Missing parts are skipped. Nothing else is changed.
"""
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
parts = ["b_head.md"] + sorted(glob.glob(os.path.join(HERE, "b_g[0-9]*.md"))) + ["b_answers.md", "b_table.md", "b_losses.md", "b_wrong.md", "b_unknown.md"]
out = []
for p in parts:
    p = p if os.path.isabs(p) else os.path.join(HERE, p)
    if os.path.exists(p):
        out.append(open(p).read().rstrip() + "\n")
text = "\n".join(out)
open(os.path.join(HERE, "deep-read-2.md"), "w").write(text)
print("deep-read-2.md written:", len(text), "characters,", text.count("\n"), "lines, parts:", len(out))
