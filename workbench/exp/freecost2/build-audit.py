from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[2]
task = root / 'exp/freecost2'
for arm in ['on', 'off']:
    bot = task / ('bot-' + arm)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'replay-world.cpp'),
                    *map(str, sorted(p for p in bot.glob('*.cpp') if p.name != 'main.cpp')),
                    '-o', str(task / ('replay-world-' + arm))], check=True)
    print(arm, 'native diagnostic compiled', flush=True)
