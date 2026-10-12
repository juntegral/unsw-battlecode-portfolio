from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodyx'
for variant in ['on', 'off']:
    bot = task / ('bot-' + variant)
    sources = sorted(p for p in bot.glob('*.cpp') if p.name not in ['main.cpp', 'plan.cpp'])
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'fixtures.cpp'),
                    *map(str, sources), '-o', str(task / ('fixtures-' + variant))], check=True)
subprocess.run(['node', '--stack-size=16384', str(task / 'check-fixtures.js')], cwd=root, check=True)
