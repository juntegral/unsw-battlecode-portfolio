import os, subprocess, sys, shutil
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~/meow-redteam')
maps = [('maze', 'maps/ladder/ladder_maze_1.map'), ('weakhold', 'maps/ladder/ladder_weakhold_1.map'),
        ('cor24', 'maps/gx/gx_corridors_24x12_911101.map'), ('stripes', 'maps/ladder/ladder_stripes_1.map'),
        ('cor64', 'maps/gx/gx_corridors_64x16_911102.map'), ('default', 'maps/ladder/ladder_default_1.map')]
jobs = []
for opp in ('m3base', 'mD17'):
    for name, path in maps:
        for arm, bot in (('t', 'qtt'), ('off', 'qtid'), ('m', 'qtm')):
            out = f'{H}/solo/runs/qt_{arm}/{name}-{opp}-seed1-side0'
            jobs.append((bot, opp, path, out))


def play(j):
    bot, opp, path, out = j
    if os.path.exists(out + '/result.txt'):
        return
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    subprocess.run([f'{H}/play.sh', f'{H}/solo/bots/{bot}', f'{H}/solo/bots/{opp}', f'{H}/{path}', '1', out],
                   cwd=H, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('done', out, flush=True)


with ThreadPoolExecutor(4) as ex:
    list(ex.map(play, jobs))
