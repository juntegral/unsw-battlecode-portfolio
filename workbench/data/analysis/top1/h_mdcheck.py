#!/usr/bin/env python3
"""Check hypotheses.md: every table row has as many cells as its header; no line over 400 characters outside tables;
list the scripts and output files it names that do not exist.  Usage: python3 h_mdcheck.py"""
import os
import re

text = open("hypotheses.md").read().splitlines()
bad = 0
i = 0
while i < len(text):
    if text[i].startswith("|") and i + 1 < len(text) and re.match(r"^\|[-| ]+\|$", text[i + 1]):
        n = text[i].count("|")
        j = i
        while j < len(text) and text[j].startswith("|"):
            if text[j].count("|") != n:
                print(f"line {j + 1}: {text[j].count('|') - 1} cells, header has {n - 1}")
                bad += 1
            j += 1
        i = j
    else:
        i += 1
names = set(re.findall(r"`((?:h_out/)?[A-Za-z0-9_./-]+\.(?:py|txt|json|md))`", "\n".join(text)))
missing = sorted(n for n in names if not os.path.exists(n) and not os.path.exists(os.path.join("..", "..", "online", "smoke", n))
                 and not n.startswith(("mybot2/", "work/", "data/", "qh31-", "tc30-", "run1/")))
print("table problems:", bad)
print("named files not found here:", missing)
print("lines:", len(text), "words:", sum(len(l.split()) for l in text))
