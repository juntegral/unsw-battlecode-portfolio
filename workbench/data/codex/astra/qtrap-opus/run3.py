import os, subprocess, sys, shutil, threading, time
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~/meow-redteam')
M = dict(maze='maps/ladder/ladder_maze_1.map', weakhold='maps/ladder/ladder_weakhold_1.map',
         cor24='maps/gx/gx_corridors_24x12_911101.map', stripes='maps/ladder/ladder_stripes_1.map',
         cor64='maps/gx/gx_corridors_64x16_911102.map', default='maps/ladder/ladder_default_1.map')
B = dict(off='qtid', m='qtm', t='qtt')
OLD = [int(x) for x in sys.argv[1:]]
order = [('maze', 'mD17'), ('weakhold', 'mD17'), ('cor24', 'mD17'), ('stripes', 'mD17'), ('cor64', 'm3base'),
         ('default', 'm3base'), ('default', 'mD17'), ('cor64', 'mD17')]
jobs = [(B[a], opp, M[name], f'{H}/solo/runs/qt_{a}/{name}-{opp}-seed1-side0') for name, opp in order for a in ('off', 'm', 't')]
lock = threading.Lock()
running = [0]


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def play(j):
    bot, opp, path, out = j
    if os.path.exists(out + '/result.txt'):
        return
    while True:
        with lock:
            if running[0] + sum(alive(p) for p in OLD) < 2:
                running[0] += 1
                break
        time.sleep(1)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    subprocess.run([f'{H}/play.sh', f'{H}/solo/bots/{bot}', f'{H}/solo/bots/{opp}', f'{H}/{path}', '1', out],
                   cwd=H, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with lock:
        running[0] -= 1
    print('done', out, flush=True)


with ThreadPoolExecutor(2) as ex:
    list(ex.map(play, jobs))
