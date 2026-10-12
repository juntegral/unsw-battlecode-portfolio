"""unA-opus: health lines for named run arms (seat A = the arm). Run from ROOT: python3 -B data/codex/astra/unA-opus/h2.py <arm> ..."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/unA-opus')
import health
for arm in sys.argv[1:]:
    for folder in sorted((health.RUNS / arm).glob('*-seed*-side*')):
        if (folder / 'result.txt').exists() and (folder / 'game.replay').exists():
            try:
                health.line(arm, folder, int(folder.name[-1]), arm[7:21])
            except Exception as ex:
                print('FAIL', folder.name, repr(ex)[:200])
