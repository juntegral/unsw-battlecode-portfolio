from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem'
for variant in ['on', 'off']:
    bot = task / ('bot-' + variant)
    sources = sorted(p for p in bot.glob('*.cpp') if p.name != 'main.cpp')
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'replay-world.cpp'),
                    *map(str, sources), '-o', str(task / ('replay-world-' + variant))], check=True)
