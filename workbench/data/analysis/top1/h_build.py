#!/usr/bin/env python3
"""Assemble hypotheses.md from the part files h_p*.md (in name order).  Usage: python3 h_build.py"""
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(HERE, "h_p*.md")))
text = "\n\n".join(open(p).read().strip("\n") for p in parts) + "\n"
open(os.path.join(HERE, "hypotheses.md"), "w").write(text)
print("hypotheses.md:", len(text.splitlines()), "lines from", [os.path.basename(p) for p in parts])
