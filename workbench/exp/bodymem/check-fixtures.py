from pathlib import Path
import json
import subprocess
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem'
report = {}
for variant in ['on', 'off']:
    bot = task / ('bot-' + variant)
    sources = sorted(p for p in bot.glob('*.cpp') if p.name not in ['main.cpp', 'plan.cpp'])
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'fixtures.cpp'),
                    *map(str, sources), '-o', str(task / ('fixtures-' + variant))], check=True)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'transition.cpp'),
                    *map(str, sources), '-o', str(task / ('transition-' + variant))], check=True)
    result = subprocess.run([str(task / ('fixtures-' + variant))], check=True, capture_output=True, text=True)
    report[variant] = json.loads(result.stdout)
assert report['on']['resyncDrift'] == 0
(task / 'fixture-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
