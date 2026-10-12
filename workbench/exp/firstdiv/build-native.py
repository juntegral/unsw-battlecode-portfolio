from pathlib import Path
import subprocess, sys
p = Path(__file__).resolve().parent
root = p.parents[1]
for name in sys.argv[1:] or ['bodymem', 'bodyx', 'freecost', 'qsight']:
    for arm in ['on', 'off']:
        bot = root / 'exp' / name / ('bot-' + arm)
        cmd = ['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot)]
        if name == 'bodymem':
            cmd += ['-DFIRSTDIV_BODYMEM']
        cmd += [str(p / 'native.cpp'), *map(str, sorted(f for f in bot.glob('*.cpp') if f.name != 'main.cpp')), '-o', str(p / ('native-' + name + '-' + arm))]
        subprocess.run(cmd, check=True)
        print(name, arm, flush=True)
