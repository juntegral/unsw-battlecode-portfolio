from pathlib import Path
import importlib.util, os, re, subprocess, sys, textwrap
sys.dont_write_bytecode = True
task = Path(__file__).resolve().parent
root = task.parents[1]
spec = importlib.util.spec_from_file_location('board_canvas', root / 'exp/queen-rammed/canvas.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
jobs = [
    ('free-growth', 'bot-hunter_Colosseum_A_1', 'Colosseum', 'A', [7, 8], 14, 5, 5, 'COLOSSEUM #0 L5: ON NW / OFF W', 'ON FREE 2. COST 1.6 TO 0. L5 TO 6. NO PAYMENT.'),
    ('free-tail', 'bot-hunter_trophy_A_1', 'trophy', 'A', [11, 12], 23, 1, 5, 'TROPHY #0 L5: ON WS / OFF S', 'ON FREE 2. L5 TO 5. NORMAL TAIL ADVANCES TWO.'),
    ('harm-death', 'bot-hunter_Colosseum_A_1', 'Colosseum', 'A', [44, 45], 6, 7, 7, 'QUEEN HARM: COLOSSEUM A HUNTER R44', 'ON SS HEAD 6,8: ENEMY #6 NEEE RAMS. OFF ALIVE. NOT FEED.')
]
for name, key, map_name, side, rounds, x, y, radius, title, caption in jobs:
    panel_width = 600
    panel_height = 130 + (2 * radius + 1) * 27 + 70
    c = m.Canvas(panel_width * 2, panel_height * 2 + 115)
    c.text(20, 14, title, scale=2)
    for iy, rr in enumerate(rounds):
        for ix, arm in enumerate(['on', 'off']):
            base_x, base_y = ix * panel_width, 45 + iy * panel_height
            cmd = ['node', 'exp/v16/board.js', f'exp/freecost2/{arm}/games/{key}/game.replay', side, str(rr), str(x), str(y), str(radius), map_name, 'a']
            raw = subprocess.check_output(cmd, cwd=root, env={**os.environ, 'UNSW_RULES':'123'}, text=True)
            (task / f'board-{name}-{arm}-{rr}.txt').write_text(raw)
            lines = raw.strip().splitlines()
            c.text(base_x+20, base_y, f'{arm} ROUND {rr} START', scale=2)
            c.text(base_x+20, base_y+24, lines[0])
            grid = [(int(z.group(1)),z.group(2)) for line in lines if (z:=re.match(r'\s*(\d+)\s+([.*a-zA-Z]+)$',line))]
            for gy,(yy,chars) in enumerate(grid):
                c.text(base_x+20, base_y+58+gy*27, yy, scale=2)
                for gx,ch in enumerate(chars):
                    px,py=base_x+65+gx*27,base_y+50+gy*27
                    color='#ffffff' if ch=='.' else '#f9dd76' if ch=='*' else '#cc5260' if ch=='X' else '#f6c2c8' if ch=='x' else '#2477a8' if ch.isupper() else '#abd2e8'
                    c.rect(px,py,25,25,color)
                    if ch.isalpha(): c.text(px+7,py+7,ch,'#ffffff' if ch.isupper() else '#17212b',scale=2)
                    if ch=='*': c.rect(px+10,py+10,5,5,'#846817')
            for j,line in enumerate(textwrap.wrap(lines[-1],85)):
                c.text(base_x+20,base_y+70+len(grid)*27+j*13,line)
    c.text(20,c.h-55,caption,scale=2)
    c.text(20,c.h-24,'BLUE OUR HEAD/BODY. RED ENEMY. YELLOW PEARL. ROUND START; KELP EDGES OMITTED.')
    c.save(task / f'board-{name}.png')
    print(name)
