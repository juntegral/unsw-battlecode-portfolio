"""Where the last-bot candidates stand: finished games of each of my pair batches, side by side."""
import glob, os, re, collections, time, sys
R = os.path.expanduser('~/meow-redteam/solo/runs/')
print(time.strftime('%H:%M:%S'))
def res(f):
    t = open(f).read()
    m = re.search(r'winner=(\S+) how=\S+ \(([^)]*)\) rounds=(\d+) final_lengths=(\S+)', t)
    return '%s %-24s r%-3s %s' % (m.group(1), m.group(2)[:24], m.group(3), m.group(4)) if m else t[:50]
def pairs(base, arm):
    A = {os.path.basename(os.path.dirname(f)): res(f) for f in glob.glob(R + base + '/*/result.txt')}
    B = {os.path.basename(os.path.dirname(f)): res(f) for f in glob.glob(R + arm + '/*/result.txt')}
    both = sorted(set(A) & set(B))
    same = sum(1 for g in both if A[g] == B[g])
    print('== %s against %s: %d pairs, %d identical result lines (finished: %d / %d)' % (arm, base, len(both), same, len(B), len(A)))
    for g in both:
        if A[g] != B[g]:
            side = g[-1]
            print('   %-38s seat %s  off: %s' % (g[:38], side, A[g]))
            print('   %-38s          on:  %s' % ('', B[g]))
pairs('nr_mD18', 'nr_mNR')
pairs('qda_mD18', 'qda_mQDA')
print('== head to head mCx (CENTER_MAX_CELLS) against mD18; the arm sits in the seat named in the folder')
for f in sorted(glob.glob(R + 'h2h_mCx_v18/*/result.txt')):
    print('   %-40s %s' % (os.path.basename(os.path.dirname(f)), res(f)))
