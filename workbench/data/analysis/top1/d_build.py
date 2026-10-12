#!/usr/bin/env python3
"""d_build.py: assemble deep-read-4.md from the part files d_p*.md (sub-session A4).

A line of the form  @@include <path>@@  in a part is replaced by the content of that file (generated tables in
d_out/).  Parts are joined in name order.  Prints the size of the result.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(HERE, "d_p*.md")))
out = []
for p in parts:
    text = open(p).read().rstrip("\n")

    def inc(m):
        return open(os.path.join(HERE, m.group(1))).read().rstrip("\n")

    out.append(re.sub(r"^@@include (.+?)@@$", inc, text, flags=re.M))
doc = "\n\n".join(out) + "\n"
open(os.path.join(HERE, "deep-read-4.md"), "w").write(doc)
print(f"deep-read-4.md: {len(doc.splitlines())} lines, {len(doc)} characters, from {len(parts)} parts")
