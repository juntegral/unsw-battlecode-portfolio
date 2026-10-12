#!/usr/bin/env python3
"""mkbots.py name=SWITCH:value,SWITCH:value ... : write solo/bots/<name>/main.cpp from src/solo/main.cpp with those constants set, and compile."""
import os, re, shutil, subprocess, sys
S = os.path.expanduser('~/meow-redteam/solo')
src = open(os.environ.get('MKSRC', f'{S}/src/solo/main.cpp'), encoding='utf-8').read()
for spec in sys.argv[1:]:
    name, _, sw = spec.partition('=')
    v = src
    for item in filter(None, sw.split(',')):
        k, val = item.split(':')
        v, n = re.subn(rf'(constexpr \w+ {k} = )[^;]+;', rf'\g<1>{val};', v)
        assert n == 1, (k, n)
    d = f'{S}/bots/{name}'; os.makedirs(d, exist_ok=True)
    open(f'{d}/main.cpp', 'w', encoding='utf-8').write(v)
    for h in ('helper.hpp', 'sonar_codec.hpp'): shutil.copy(f'{S}/src/main3/{h}', f'{d}/{h}')
    r = subprocess.run(['nice', '-n', '10', 'c++', '-std=c++20', '-O2', f'{d}/main.cpp', '-o', f'{d}/bot'], capture_output=True, text=True)
    print(name, 'ok' if r.returncode == 0 else 'FAILED\n' + r.stderr[-800:])
