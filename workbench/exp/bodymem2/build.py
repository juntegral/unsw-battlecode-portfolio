#!/usr/bin/env python3
"""Compile only; never start games or call the CLI."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / "exp/bodymem2"
PACKAGE = ROOT.parent / "UNSW/.unswbc-123"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(1, str(ROOT.parent / "UNSW/.venv-ppo/lib/python3.13/site-packages"))
os.environ["XDG_CACHE_HOME"] = str(TASK / "build-cache")
os.environ["UNSWBC_NO_UPDATE"] = "1"
os.environ["UNSWBC_NO_VSCODE"] = "1"
from unswbc import clangtool, sandbox

cache = TASK / "build-cache/unswbc"
cache.mkdir(parents=True, exist_ok=True)
home = clangtool.toolchain()
for wasm in (home / "clang.wasm", home / "root/bin/wasm-ld"):
    target = sandbox.compiled_path(wasm)
    previous = ROOT / ".cache/unswbc" / target.name
    if not target.exists() and previous.is_file():
        shutil.copy2(previous, target)

out = TASK / "compiled"
out.mkdir(exist_ok=True)
report = {}
for variant in ("base", "off", "on"):
    artifact = clangtool.build(TASK / f"bot-{variant}")
    blob = artifact.read_bytes()
    (out / f"{variant}.wasm").write_bytes(blob)
    report[variant] = {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
report["off_equals_original_v18_wasm"] = (out / "base.wasm").read_bytes() == (out / "off.wasm").read_bytes()
(TASK / "compile-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if not report["off_equals_original_v18_wasm"]:
    sys.exit("off wasm differs from original v1.8")
