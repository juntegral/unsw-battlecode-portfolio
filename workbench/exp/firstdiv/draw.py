import sys
sys.dont_write_bytecode = True
import json, pathlib, subprocess, re, textwrap, importlib.util, os
P = pathlib.Path(__file__).resolve().parent
ROOT = P.parents[1]
spec = importlib.util.spec_from_file_location('firstdiv_canvas', ROOT / 'exp/queen-rammed/canvas.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
manifest = []
for name in ['bodymem', 'bodyx', 'freecost', 'qsight']:
    data = json.loads((P / (name + '.json')).read_text())
    for row in data['rows']:
        if row['status'] != 'matched' or not (any(v == 'harm' for v in row['classification'].values()) or any(v == 'harm' for v in row['queen']['classification'].values())):
            continue
        target = row['changed'][0]['turn']['on']['head']
        folder = P / 'boards' / name
        folder.mkdir(parents=True, exist_ok=True)
        stem = row['key'].replace(':', '_')
        panels = []
        for k in [0, 1]:
            for arm in ['on', 'off']:
                cmd = ['node', 'exp/v16/board.js', row['files'][arm], row['side'], str(row['R'] + k), str(target['x']), str(target['y']), '4', row['key'].split(':')[1], 'a']
                text = subprocess.check_output(cmd, cwd=ROOT, env={**os.environ, 'UNSW_RULES': '123'}, text=True)
                if not text.strip():
                    raise RuntimeError('missing board ' + stem + arm)
                panels.append({'arm': arm, 'round': row['R'] + k, 'text': text, 'command': cmd})
        (folder / (stem + '.txt')).write_text('\n\n'.join(p['arm'].upper() + '\n' + p['text'] for p in panels))
        c = m.Canvas(1100, 900)
        c.text(20, 16, name.upper() + '  ' + row['key'], scale=2)
        c.text(20, 42, 'FIRST CHANGE R' + str(row['R']) + '  DRAGON #' + str(row['id']) + '  CENTER ' + str(target['x']) + ',' + str(target['y']), scale=2)
        for i, panel in enumerate(panels):
            x0 = 20 + (i % 2) * 550
            y0 = 80 + (i // 2) * 380
            action = row['actions'][panel['arm']]['text']
            c.text(x0, y0, panel['arm'].upper() + ' R' + str(panel['round']) + '  FORK ACTION ' + action, scale=2)
            lines = panel['text'].strip().splitlines()
            c.text(x0, y0 + 24, lines[0], scale=1)
            grid = []
            for line in lines[1:]:
                match = re.match(r'\s*(\d+)\s+([.*a-zA-Z]+)$', line)
                if match:
                    grid.append((int(match[1]), match[2]))
            for gy, (yy, chars) in enumerate(grid):
                c.text(x0, y0 + 55 + gy * 27, str(yy), scale=2)
                for gx, ch in enumerate(chars):
                    px, py = x0 + 44 + gx * 27, y0 + 48 + gy * 27
                    col = '#ffffff'
                    if ch == '*': col = '#f9dd76'
                    elif ch in 'xX': col = '#cc5260' if ch == 'X' else '#f6c2c8'
                    elif ch.isalpha(): col = '#2477a8' if ch.isupper() else '#abd2e8'
                    c.rect(px, py, 25, 25, col)
                    if ch not in '.*': c.text(px + 6, py + 6, ch, '#ffffff' if ch.isupper() else '#17212b', scale=2)
                    elif ch == '*': c.rect(px + 10, py + 10, 5, 5, '#846817')
            legend = lines[-1]
            for j, line in enumerate(textwrap.wrap(legend, 65)):
                c.text(x0, y0 + 303 + j * 14, line, scale=1)
        c.text(20, 865, 'BLUE=OUR HEAD/BODY  RED=ENEMY HEAD/BODY  YELLOW=PEARL', scale=2)
        c.text(20, 887, 'ROUND START. KELP EDGES OMITTED BY EXP/V16/BOARD.JS. UPPERCASE FONT: HEADS USE DARK TILES.', scale=1)
        f = folder / (stem + '.png')
        c.save(f)
        manifest.append({'name': name, 'key': row['key'], 'R': row['R'], 'id': row['id'], 'figure': str(f.relative_to(P)), 'ascii': str((folder / (stem + '.txt')).relative_to(P)), 'panels': panels})
        print(name, row['key'], flush=True)
(P / 'boards.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
