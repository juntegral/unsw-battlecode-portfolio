#!/usr/bin/env python3
"""Assemble redteam.md from the part files x_p*.md (in name order). Missing parts are skipped.
The per-candidate parts (x_p1..x_p4b) are written with '##' / '###' headings and are set one level lower here,
so that they sit under '## 2. Per candidate'."""
import glob
import re

parts = sorted(glob.glob("x_p*.md"))
text = ""
for p in parts:
    t = open(p).read().rstrip() + "\n\n"
    if re.match(r"x_p[1-4]", p):
        lines = []
        for line in t.split("\n"):
            if line.startswith("### "):
                line = "#" + line
            elif line.startswith("## "):
                line = "#" + line
            lines.append(line)
        t = "\n".join(lines)
    text += t
open("redteam.md", "w").write(text.rstrip() + "\n")
print("redteam.md:", len(text.splitlines()), "lines from", parts)
