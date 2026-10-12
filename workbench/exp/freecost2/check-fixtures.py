from pathlib import Path
import json
import subprocess

root = Path(__file__).resolve().parents[2]
task = root / 'exp/freecost2'
report = {}
for arm in ['on', 'off']:
    bot = task / ('bot-' + arm)
    sources = sorted(p for p in bot.glob('*.cpp') if p.name not in ['main.cpp', 'plan.cpp'])
    command = ['/usr/bin/clang++', '-std=c++20', '-O2', '-I', str(bot), str(task / 'fixtures.cpp'),
               *map(str, sources), '-o', str(task / ('fixtures-' + arm))]
    subprocess.run(command, check=True)
    result = subprocess.run([str(task / ('fixtures-' + arm))], check=True, capture_output=True, text=True)
    report[arm] = json.loads(result.stdout)
assert all(report['on'][key] == report['off'][key] for key in ['priceCases', 'cappedReachCases', 'bodyAndPaymentCases'])
(task / 'fixture-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
