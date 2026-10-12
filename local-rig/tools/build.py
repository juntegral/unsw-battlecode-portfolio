#!/usr/bin/env python3
"""Compile a local C or C++ bot directory to a native executable."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('output', nargs='?', type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    output = (args.output or directory / 'bot').resolve()
    if not directory.is_dir() or not directory.is_relative_to(ROOT):
        parser.error('bot directory must exist inside this workspace')
    if not output.is_relative_to(ROOT):
        parser.error('output binary must be inside this workspace')
    sources = sorted(p for p in directory.rglob('*')
                     if p.suffix in ('.c', '.cpp', '.cc', '.cxx') and p.is_file())
    if not sources or any(not p.resolve().is_relative_to(ROOT) for p in sources):
        parser.error('expected local C/C++ source files')
    cpp = any(p.suffix != '.c' for p in sources)
    compiler = shlex.split(os.environ.get('CXX' if cpp else 'CC', 'c++' if cpp else 'cc'))
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(compiler + ['-std=c++20' if cpp else '-std=c17', '-O2', '-I', str(directory)]
                   + [str(p) for p in sources] + ['-o', str(output)], check=True)
    print(output.relative_to(ROOT))


if __name__ == '__main__':
    main()
