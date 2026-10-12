import os, subprocess, sys, shutil, threading, time
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~/meow-redteam')
M = dict(maze='maps/ladder/ladder_maze_1.map', weakhold='maps/ladder/ladder_weakhold_1.map',
         cor24='maps/gx/gx_corridors_24x12_911101.map', stripes='maps/ladder/ladder_stripes_1.map',
         cor64='maps/gx/gx_corridors_64x16_911102.map', default='maps/ladder/ladder_default_1.map')
B = dict(off='qtid', m='qtm', t='qtt')
OLD = [int(x) for x in sys.argv[1:]]
order = [('maze', 'mD18', 1), ('weakhold', 'mD18', 1), ('cor24', 'mD18', 1), ('stripes', 'mD18', 1), ('default', 'mD18', 1), ('cor64', 'mD18', 1), ('maze', 'mD18', 2), ('weakhold', 'mD18', 2), ('maze', 'm3base', 4), ('weakhold', 'm3base', 3)]
jobs = [(B[a], opp, M[name], f'{H}/solo/runs/qt_{a}/{name}-{opp}-seed{sd}-side0', sd) for name, opp, sd in order for a in ('m', 't')]
lock = threading.Lock()
running = [0]


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def play(j):
    bot, opp, path, out, sd = j
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
    subprocess.run([f'{H}/play.sh', f'{H}/solo/bots/{bot}', f'{H}/solo/bots/{opp}', f'{H}/{path}', str(sd), out],
                   cwd=H, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with lock:
        running[0] -= 1
    print('done', out, flush=True)


with ThreadPoolExecutor(2) as ex:
    list(ex.map(play, jobs))
