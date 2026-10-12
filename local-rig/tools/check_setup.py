#!/usr/bin/env python3
"""Offline checks that never run a game or execute the opponent binary."""
from contextlib import redirect_stdout
import gzip
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
sys.path.insert(0, str(ROOT))

import batch
import guard
from replay_format import Message
from run_game import game_slot
from show import render, snapshot


def check_guard():
    cases = [('allowed-game', {'tool_name': 'Bash', 'tool_input': {
                 'command': './play.sh starter opponent/bot maps/dev/sqheld_open_small_90018.map 1 runs/test'}}, 0),
             ('denied-path', {'tool_name': 'Read', 'tool_input': {
                 'file_path': '~/meow-dev/notes.txt'}}, 2),
             ('denied-inspection', {'tool_name': 'Bash', 'tool_input': {
                 'command': 'xxd opponent/bot'}}, 2)]
    records = []
    for label, event, expected in cases:
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'guard.py')],
                                input=json.dumps(event), text=True, capture_output=True)
        assert result.returncode == expected, (label, result)
        records.append(dict(label=label, input=event, exit_code=result.returncode,
                            reason=result.stderr.strip()))
    for term in guard.FORBIDDEN:
        assert guard.check({'tool_input': {'nested': [None, {'value': term.upper()}]}})
    for command in ['curl example.org', 'wget example.org', 'gh pr list',
                    'git push origin main', 'ssh host', 'nc -l 1234']:
        assert guard.check({'tool_input': {'command': command}})
    for program in ['strings', 'objdump', 'otool', 'nm', 'lldb', 'gdb', 'hexdump', 'xxd', 'dtruss', 'dtrace']:
        assert guard.check({'tool_input': {'command': program + ' opponent/bot'}})
    for command in ['cat docs/README.md', './starter/build.sh starter', 'rg pearl starter',
                    'git status', 'nm starter/bot']:
        assert guard.check({'tool_input': {'command': command}}) is None
    (ROOT / 'proof/guard-tests.json').write_text(json.dumps(records, indent=2) + '\n')
    return records


def check_maps():
    sets = {group: sorted((ROOT / 'maps' / group).glob('*.map')) for group in ['dev', 'eval']}
    assert len(sets['dev']) == 8 and len(sets['eval']) == 16
    assert not {p.name for p in sets['dev']} & {p.name for p in sets['eval']}
    assert not {p.read_bytes() for p in sets['dev']} & {p.read_bytes() for p in sets['eval']}
    for group, maps in sets.items():
        sizes = []
        for path in maps:
            lines = [line.split() for line in path.read_text().splitlines()]
            dims = next(line for line in lines if line[0] == 'MAP')
            w, h = map(int, dims[1:])
            sizes.append(w*h)
            for name in ['TILE', 'EDGE', 'DRAGON']:
                expected = int(next(line[1] for line in lines if line[0] == name+'_COUNT'))
                assert sum(line[0] == name for line in lines) == expected
            dragons = [line for line in lines if line[0] == 'DRAGON']
            assert sum(line[1] == '0' for line in dragons) == sum(line[1] == '1' for line in dragons)
        assert min(sizes) <= 600 and max(sizes) > 1200
    return '8 dev + 16 eval, disjoint, mixed cell counts, declared counts and starting teams validated'


def check_starter():
    # A single protocol block, not a game. Only EAST is open from the head.
    init = ['ID 0', 'TEAM A', 'MAP 16 14', 'UNIT_LIMIT 64',
            'ROUND 0', 'DIR E', 'LENGTH 3', 'UNIT_COUNT 1', 'NUM_MSGS 0', 'ECHOES 0 0 0 0 0']
    tiles = [f'{x} {y} 0 10' for y in range(4, 11) for x in range(5, 12)]
    parts = ['DRAGON_BODIES 3', 'A 0 8 7 E 1', 'A 0 7 7 E 0', 'A 0 6 7 E 0']
    horizontal = [['.' for _ in range(7)] for _ in range(8)]
    vertical = [['.' for _ in range(8)] for _ in range(7)]
    horizontal[3][3] = horizontal[4][3] = 'w'
    vertical[3][3] = 'w'
    block = '\n'.join(init + tiles + parts + [' '.join(row) for row in horizontal + vertical] + ['ENDGAME'])+'\n'
    result = subprocess.run([str(ROOT / 'starter/bot')], input=block,
                            text=True, capture_output=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert re.findall(r'^MOVE (\w+)$', result.stdout, re.M) == ['E'], result.stdout
    assert 'PROTOCOL 3\nENDTURN\n' in result.stdout
    (ROOT / 'proof/starter-protocol.txt').write_text(result.stdout)
    return 'built native starter parsed engine protocol and selected the only open, unoccupied direction (E)'


class Fixture:
    """Small independent Cap'n Proto encoder for a clearly labelled synthetic replay."""
    def __init__(self):
        self.data = bytearray(8)

    def alloc(self, words):
        start = len(self.data)//8
        self.data.extend(bytes(words*8))
        return start

    def word(self, at, value):
        struct.pack_into('<Q', self.data, at*8, value)

    def put(self, at, offset, fmt, value):
        struct.pack_into('<'+fmt, self.data, at*8+offset, value)

    def ref(self, slot, target, dwords, pwords):
        self.word(slot, (((target-slot-1) & 0x3fffffff) << 2) | (dwords << 32) | (pwords << 48))

    def structure(self, slot, dwords, pwords):
        target = self.alloc(dwords+pwords)
        self.ref(slot, target, dwords, pwords)
        return target

    def text(self, slot, value):
        value = value.encode()+b'\0'
        target = self.alloc((len(value)+7)//8)
        self.data[target*8:target*8+len(value)] = value
        self.word(slot, 1 | ((target-slot-1)<<2) | (2<<32) | (len(value)<<35))

    def points(self, slot, points):
        target = self.alloc(1+len(points))
        self.word(slot, 1 | ((target-slot-1)<<2) | (7<<32) | (len(points)<<35))
        self.word(target, (len(points)<<2) | (1<<32))
        for i, (x,y) in enumerate(points):
            self.put(target+1+i, 0, 'i', x)
            self.put(target+1+i, 4, 'i', y)

    def point(self, slot, cell):
        target = self.structure(slot, 1, 0)
        self.put(target, 0, 'i', cell[0])
        self.put(target, 4, 'i', cell[1])

    def packed(self):
        raw = struct.pack('<II', 0, len(self.data)//8)+self.data
        output = bytearray()
        for start in range(0,len(raw),8):
            word = raw[start:start+8]
            tag = sum((bool(value)<<i) for i,value in enumerate(word))
            output.append(tag)
            output.extend(value for value in word if value)
            if tag in (0,255):
                output.append(0)
        return gzip.compress(output, mtime=0)


def check_replay():
    fixture = Fixture()
    root = fixture.structure(0, 2, 5)
    fixture.put(root, 0, 'I', 2)
    fixture.text(root+2, 'MAP 8 8\nMAP_NAME synthetic-reader-check\nEDGE 0 1 -1\nEDGE 10 2 3\n'
                 'DRAGON 0 4 3 3 2 3 1 3 0 3\nDRAGON 1 3 6 6 5 6 4 6\nEND\n')
    fixture.text(root+3, 'fixture-A')
    fixture.text(root+4, 'fixture-B')
    kinds = [3, 0, 9, 3, 0, 10, 11]
    events = fixture.alloc(1+len(kinds)*2)
    fixture.word(root+5, 1 | ((events-(root+5)-1)<<2) | (7<<32) | (len(kinds)*2<<35))
    fixture.word(events, (len(kinds)<<2) | (1<<32) | (1<<48))
    for index, kind in enumerate(kinds):
        at = events+1+2*index
        fixture.put(at, 0, 'H', kind)
        datawords,pointers = (2,2) if kind == 10 else (1,2) if kind == 9 else (1,1) if kind == 3 else (1,0)
        payload = fixture.structure(at+1, datawords, pointers)
        if kind == 0:
            fixture.put(payload, 0, 'i', 0 if index==1 else 1)
        elif kind == 3:
            fixture.put(payload, 0, 'B', 1 if index==0 else 0)
            fixture.point(payload+1, (4,3))
        elif kind == 9:
            fixture.put(payload, 4, 'H', 1)
            fixture.point(payload+1, (4,3))
            fixture.point(payload+2, (0,3))
        elif kind == 10:
            fixture.put(payload, 4, 'i', 2)
            fixture.put(payload, 10, 'H', 3)
            fixture.points(payload+2, [(4,3),(3,3),(2,3)])
            fixture.points(payload+3, [(0,3),(1,3)])
        elif kind == 11:
            fixture.put(payload, 0, 'i', 1)
    result = fixture.structure(root+6, 1, 2)
    fixture.put(result, 4, 'H', 1)
    a = fixture.structure(result+1, 2, 0)
    fixture.put(a, 0, 'i', 2)
    fixture.put(a, 4, 'i', 3)
    fixture.put(a, 8, 'i', 5)
    fixture.put(a, 12, 'i', 3)
    fixture.structure(result+2, 2, 0)
    path = ROOT / 'proof/synthetic.replay'
    path.write_bytes(fixture.packed())
    initial, first, final = [snapshot(path, n) for n in [0,1,2]]
    assert len(initial['dragons'][0]['body']) == 4 and (4,3) in initial['pearls']
    assert len(first['dragons'][0]['body']) == 5 and (4,3) not in first['pearls']
    assert set(final['dragons']) == {0,2}
    assert [len(final['dragons'][i]['body']) for i in [0,2]] == [3,2]
    assert snapshot(path)['round'] == 2 and final['standings'][0]['total'] == 5
    with io.StringIO() as output:
        with redirect_stdout(output):
            render(final)
        (ROOT/'proof/synthetic-board.txt').write_text(output.getvalue())
    # A separate three-segment double-far pointer fixture.
    raw = struct.pack('<IIII', 2, 1, 2, 1)
    raw += struct.pack('<Q', 6 | (1<<32))
    raw += struct.pack('<QQ', 2 | (2<<32), 1<<32)
    raw += struct.pack('<ii', 123, 456)
    decoded = Message(raw).root()
    assert decoded.i32(0)==123 and decoded.i32(4)==456
    return 'synthetic gzip/packed replay: initial pearls, rounds, growth, split, death, board, and double-far pointers passed'


def check_batch():
    for group, count in [('dev',8),('eval',16)]:
        jobs = list(batch.plan(ROOT/'starter',ROOT/'opponent/bot',group,[1,2],ROOT/'proof/not-run'))
        assert len(jobs)==count*2*2
        assert len({job[3] for job in jobs})==len(jobs)
        assert all(Path(job[4][0])==ROOT/'play.sh' for job in jobs)
        for first,second in zip(jobs[::2],jobs[1::2]):
            assert first[4][1:3] == list(reversed(second[4][1:3]))
    records = [dict(map_name='fixture', first_bot_side=side, winner=win,
                    how='elimination' if win != 'draw' else 'round_limit', verdict='test')
               for side in (0,1) for win in (0,1,'draw')]
    summary = batch.summary(records)
    assert 'fixture | 0 | 3 | 1 | 1 | 1' in summary
    assert 'fixture | 1 | 3 | 1 | 1 | 1' in summary
    assert 'TOTAL | both | 6 | 2 | 2 | 2' in summary
    (ROOT/'proof/synthetic-batch-summary.txt').write_text(summary+'\n')
    return 'dev/eval job plans, both orders, seeds, play.sh routing, and side-relative summaries passed; no batch run'


def check_locks():
    output = ROOT/'proof/lock-check'
    output.mkdir(exist_ok=True)
    workers = [subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),
                                 '--lock-worker',str(output/f'{i}.json')]) for i in range(5)]
    for worker in workers:
        assert worker.wait(timeout=15)==0
    intervals = [json.loads(path.read_text()) for path in output.glob('*.json')]
    events = sorted([(row['enter'],1) for row in intervals]+[(row['leave'],-1) for row in intervals])
    active=peak=0
    for _,delta in events:
        active+=delta
        peak=max(peak,active)
    assert peak==2 and active==0, peak
    return 'five lock-only processes shared the real game slots: peak holders=2 (no games)'


def main():
    if len(sys.argv)==3 and sys.argv[1]=='--lock-worker':
        with game_slot():
            enter=time.monotonic()
            time.sleep(0.3)
            leave=time.monotonic()
            Path(sys.argv[2]).write_text(json.dumps(dict(enter=enter,leave=leave)))
        return
    guard_results = check_guard()
    checks = [check_maps(),check_starter(),check_replay(),check_batch(),check_locks()]
    report = dict(guard_samples=guard_results,checks=checks,games_run=0)
    (ROOT/'proof/offline-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    for check in checks:
        print('PASS:',check)
    print('PASS: guard samples exited 0, 2, 2; all protected strings, inspection commands, and network rules checked')


if __name__=='__main__':
    main()
