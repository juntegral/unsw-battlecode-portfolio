#!/usr/bin/env python3
"""Assemble deep-read-5.md from the part files e_r*.md (in name order). Missing parts are skipped, so the report is
always complete for what has been written so far. A line of the form
    @@include e_out/some_file.md@@
in a part is replaced by that file's text (used for the tables that a script generates).
Usage: python3 e_build.py"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(HERE, "e_r[0-9]*_*.md")))
out = []
for p in parts:
    text = open(p).read().rstrip() + "\n"

    def inc(m):
        return open(os.path.join(HERE, m.group(1))).read().strip("\n")

    text = re.sub(r"^@@include (\S+)@@$", inc, text, flags=re.M)
    out.append(text)
text = "\n".join(out)
open(os.path.join(HERE, "deep-read-5.md"), "w").write(text)
print("deep-read-5.md: %d parts, %d lines, %d bytes" % (len(parts), text.count("\n"), len(text.encode())))
for p in parts:
    print("  ", os.path.basename(p), os.path.getsize(p))
