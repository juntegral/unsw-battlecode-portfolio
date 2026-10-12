from pathlib import Path
import collections
import hashlib
import json
import re
import struct
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
T = json.loads((OUT / 'tables.json').read_text())
REPORT = ROOT / 'research/observations/queen-rammed.md'
errors = []
checks = collections.Counter()


def check(ok, label):
    checks[label] += 1
    if not ok:
        errors.append(label)


for prefix, games_key, deaths_key in (
    ('main', 'mainGames', 'mainDeaths'),
    ('original', 'mainGames', 'originalDeaths'),
    ('identity', 'identityGames', 'identityDeaths'),
):
    games = T[games_key]
    if prefix == 'original':
        games = [g for g in games if g['stratum'] != 'id-flip']
    deaths = T[deaths_key]
    summary = T[prefix + 'Summary']
    check(summary['games'] == len(games), 'summary games')
    check(summary['deaths'] == len(deaths), 'summary deaths')
    check(summary['causes'] == dict(collections.Counter(d['cause'] for d in deaths)), 'summary causes')
    check(summary['classes'] == dict(collections.Counter(d['class'] for d in deaths)), 'summary classes')
    check({g['death'] for g in games if g['death']} == {d['id'] for d in deaths}, 'death coverage')

check(len(T['mainGames']) == 118 and len(T['mainDeaths']) == 89, 'all default census')
check(len(T['originalDeaths']) == 87 and len(T['identityDeaths']) == 2, 'stratified census')
check(len({g['id'] for g in T['mainGames']}) == 118, 'unique main ids')
check(len(T['sideGames']) == 773, 'side census')
manifest = {m['dir']: m for m in T['buildInventory']}
current_sha = T['metadata']['build']['sha256']
check(hashlib.sha256((OUT / 'current-default.wasm').read_bytes()).hexdigest() == current_sha, 'compiled build hash')
for g in T['mainGames']:
    for a in g['aliases']:
        check(manifest[a['dir']]['role'] == 'main', 'alias main role')
        check(manifest[a['dir']]['buildSha256'] == current_sha, 'alias current bytes')
    check((ROOT / g['file']).is_file(), 'replay reference')

for d in T['mainDeaths']:
    raw = json.loads((OUT / d['raw']).read_text())
    check(raw['game']['queenId'] == d['queenId'], 'queen identity')
    check(d['length'] >= 2, 'fatal length')
    for field in ('round', 'cause', 'length', 'lastTurnRoom', 'piecesWithin3Heads', 'piecesWithin3Body', 'safeFirstStep'):
        check(field in d, 'required death field')
    if d['cause'] == 'rammed':
        k = d['killer']
        for field in ('id', 'lengthAtOwnTurn', 'freeSteps', 'contactPathLength', 'inLastQueenView', 'inPreviousRoundQueenView'):
            check(field in k, 'required killer field')
        check(k['freeSteps'] == (k['lengthAtOwnTurn'] + 3) // 4, 'killer free budget')
        check(k['M'] == k['freeSteps'] + k['lengthAtOwnTurn'] - 2, 'killer reach formula')
        check(k['contactPathLength'] <= k['requestedSteps'], 'contact path length')
    for s in d['safeFirstStep']['steps']:
        check(s['safeM'] == all(not h['Mdanger'] for h in s['hunters']), 'M step classification')
        check(s['safeFamily'] == all(not h['danger'] for h in s['family']), 'R1 step classification')
        for h in s['hunters']:
            check(h['M'] == (h['L'] + 3) // 4 + h['L'] - 2, 'first-step reach formula')
    check(d['safeFirstStep']['safeM'] == [s['dir'] for s in d['safeFirstStep']['steps'] if s['safeM']], 'M directions')
    check(d['safeFirstStep']['safeFamily'] == [s['dir'] for s in d['safeFirstStep']['steps'] if s['safeFamily']], 'R1 directions')

check(T['metadata']['botSourceChangedSinceSnapshot'] == [], 'bot source unchanged')
check(T['verification']['reconstructionNonzeroChecks'] == {} and T['verification']['reconstructionErrors'] == [], 'reconstruction clean')
check(T['verification']['mechanics']['errors'] == [], 'movement verification clean')
check(T['verification']['geometry']['errors'] == [], 'geometry verification clean')

report = REPORT.read_text()
ids = re.findall(r'^\| \[(g\d+)\]\(', report, re.M)
check(len(ids) == 89 and set(ids) == {d['id'] for d in T['mainDeaths']}, 'report every death')
for target in re.findall(r'\]\(([^)]+)\)', report):
    if not target.startswith(('http:', 'https:', '#')):
        check((REPORT.parent / target.split('#')[0]).resolve().exists(), 'report link exists')
images = re.findall(r'!\[[^]]*\]\(([^)]+)\)', report)
check(len(images) == 3, 'three board pictures')
for target in images:
    data = (REPORT.parent / target).read_bytes()
    check(data[:8] == b'\x89PNG\r\n\x1a\n', 'board PNG signature')
    w, h = struct.unpack('>II', data[16:24])
    check(w >= 1000 and h >= 600, 'board dimensions')
elite = T['eliteComparison']['survivors']
check(len(elite) == 24, 'elite all survivors')
check(sum(e['rounds'] == 500 for e in elite) == 6, 'elite censoring')
check(sum(e['rounds'] < 500 for e in elite) == 18, 'elite early survivors')

out = {'checkedLocal': subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip(), 'checks': dict(checks), 'errors': errors}
(OUT / 'qa.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))
raise SystemExit(bool(errors))
