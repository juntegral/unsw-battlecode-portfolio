#!/usr/bin/env python3
"""b_fix1.py <replacements.json>: apply exact text replacements to the part files of deep-read-2.md (sub-session A2).

The JSON maps a part file name to a list of [old, new] pairs. Each old string must occur exactly once in its file;
if any does not, nothing is written for that file and the problem is printed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(sys.argv[1]))
for name, rep in spec.items():
    path = os.path.join(HERE, name)
    text = open(path).read()
    bad = [(old[:70], text.count(old)) for old, new in rep if text.count(old) != 1]
    if bad:
        print("NOT APPLIED to", name, "; these do not occur exactly once:", bad)
        continue
    for old, new in rep:
        text = text.replace(old, new)
    open(path, "w").write(text)
    print("applied", len(rep), "replacements to", name)
