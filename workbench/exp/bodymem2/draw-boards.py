import os, pathlib, subprocess, importlib.util, re, textwrap, sys
sys.dont_write_bytecode = True
task = pathlib.Path(__file__).resolve().parent
root = task.parents[1]
spec = importlib.util.spec_from_file_location('canvas', root / 'exp/queen-rammed/canvas.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
jobs = [
    ('free', 'proxy4_king_big_empty_A_1', 'A', 146, 37, 15, 6, 'BIG EMPTY #48 L8 EE FREE 2', 'LENGTH 8. TAIL ADVANCED TWO. FREE LIMIT 2.'),
    ('restore', 'bot-hunter_schooltime_B_1', 'B', 474, 23, 19, 7, 'SCHOOLTIME #355 L12 SSW', 'ON RESTORES ALL 12 TILES. OFF OMITS TILE 925 AFTER PORTAL.')
]
for name, key, side, rr, x, y, radius, title, caption in jobs:
    c = m.Canvas(1180, 670)
    c.text(20, 15, title, scale=2)
    for i, r in enumerate([rr, rr+1]):
        cmd = ['node', 'exp/v16/board.js', f'exp/bodymem2/on/games/{key}/game.replay', side, str(r), str(x), str(y), str(radius), key.split('_')[1], 'a']
        raw = subprocess.check_output(cmd, cwd=root, env={**os.environ, 'UNSW_RULES':'123'}, text=True)
        (task / f'board-{name}-{r}.txt').write_text(raw)
        lines = raw.strip().splitlines()
        c.text(20+i*580, 50, 'ON ROUND '+str(r)+' START', scale=2)
        grid = [(int(z.group(1)), z.group(2)) for line in lines if (z := re.match(r'\s*(\d+)\s+([.*a-zA-Z]+)$',line))]
        for gy, (yy, chars) in enumerate(grid):
            c.text(20+i*580, 92+gy*29, yy, scale=2)
            for gx, ch in enumerate(chars):
                px, py = 60+i*580+gx*29, 86+gy*29
                col = '#ffffff' if ch=='.' else '#f9dd76' if ch=='*' else '#cc5260' if ch=='X' else '#f6c2c8' if ch=='x' else '#2477a8' if ch.isupper() else '#abd2e8'
                c.rect(px,py,27,27,col)
                if ch.isalpha():c.text(px+7,py+7,ch,'#ffffff' if ch.isupper() else '#17212b',scale=2)
                if ch=='*':c.rect(px+11,py+11,5,5,'#846817')
        for j, line in enumerate(textwrap.wrap(lines[-1],80)):
            c.text(20+i*580, 548+j*14, line)
    c.text(20, 610, caption, scale=2)
    c.text(20, 645, 'BLUE OUR HEAD/BODY. RED ENEMY. YELLOW PEARL. ROUND START; KELP EDGES OMITTED.',scale=1)
    c.save(task / f'board-{name}.png')
    print(name)
