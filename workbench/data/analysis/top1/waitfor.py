#!/usr/bin/env python3
"""Block until a file exists (and has stopped growing) or a directory holds N files.

  python3 waitfor.py file <path> [timeout_s]
  python3 waitfor.py count <dir> <n> [timeout_s]
"""
import os
import sys
import time

mode = sys.argv[1]
start = time.time()
if mode == "file":
    path = sys.argv[2]
    limit = float(sys.argv[3]) if len(sys.argv) > 3 else 540
    last = -1
    while time.time() - start < limit:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size == last and size > 0:
                print("ready", path, size)
                sys.exit(0)
            last = size
        time.sleep(15)
    print("timeout", path, os.path.exists(path))
else:
    d, n = sys.argv[2], int(sys.argv[3])
    limit = float(sys.argv[4]) if len(sys.argv) > 4 else 540
    while time.time() - start < limit:
        have = len([f for f in os.listdir(d) if f.endswith(".json")])
        if have >= n:
            print("ready", have)
            sys.exit(0)
        time.sleep(10)
    print("timeout", len(os.listdir(d)))
