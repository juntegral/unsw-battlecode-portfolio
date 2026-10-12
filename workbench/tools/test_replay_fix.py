import struct
import gzip
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from replay_fix import _pack, _unpack, strip_padding


def replay(text, offset=0):
    blob = text.encode() + b'\0'
    blob += bytes(-len(blob) % 8)
    words = offset + 1 + len(blob) // 8
    header = struct.pack('<II', 0, words)
    pointer = 1 | (offset << 2) | (2 << 32) | ((len(text.encode()) + 1) << 35)
    return _pack(header + struct.pack('<Q', pointer) + b'\xff' * (offset * 8) + blob)


def map_text(padded=True, bad_kind=0, partner=-1):
    lines = ['MAP 2 1', 'MAP_NAME synthetic']
    edges = [f'EDGE {i} {bad_kind if i == 2 else 0} {partner if i == 2 else -1}'
             for i in range(9) if padded or i not in (2, 8)]
    return '\n'.join(lines + [f'EDGE_COUNT {len(edges)}'] + edges + ['END', ''])


class PaddingTests(unittest.TestCase):
    def test_synthetic_repair_and_length(self):
        raw = replay(map_text(), offset=2)
        fixed = strip_padding(raw)
        self.assertNotEqual(raw, fixed)
        unpacked = _unpack(fixed)
        count = struct.unpack_from('<Q', unpacked, 8)[0] >> 35
        self.assertEqual(bytes(unpacked[32:32 + count]), map_text(False).encode() + b'\0')
        self.assertEqual(unpacked[:8], _unpack(raw)[:8])
        self.assertEqual(unpacked[16:32], b'\xff' * 16)
        self.assertEqual(bytes(unpacked[32 + count:]), bytes(len(unpacked) - 32 - count))
        self.assertEqual(strip_padding(fixed), fixed)

    def test_clean_and_nonempty_padding_unchanged(self):
        for text in (map_text(False), map_text(bad_kind=1), map_text(bad_kind=2), map_text(partner=1)):
            with self.subTest(text=text):
                raw = replay(text)
                self.assertEqual(strip_padding(raw), raw)

    def test_malformed_unchanged(self):
        cases = [b'', b'garbage', b'\xff', b'\xff12345678\x01', b'\x00',
                 replay(map_text().replace('EDGE_COUNT 9', 'EDGE_COUNT 8')),
                 replay(map_text().replace('MAP 2 1', 'MAP 0 1')),
                 replay(map_text().replace('END', 'BROKEN'))]
        raw = replay(map_text())
        cases.extend(raw[:i] for i in range(len(raw)))
        for raw in cases:
            with self.subTest(raw=raw):
                self.assertEqual(strip_padding(raw), raw)

    def test_negative_near_pointer_and_multiple_segments(self):
        blob = map_text().encode() + b'\0'
        padded = blob + bytes(-len(blob) % 8)
        offset = -len(padded) // 8 - 1
        pointer = 1 | ((offset & 0x3fffffff) << 2) | (2 << 32) | (len(blob) << 35)
        header = struct.pack('<IIII', 1, 1, len(padded) // 8 + 1, 0)
        raw = _pack(header + bytes(8) + padded + struct.pack('<Q', pointer))
        fixed = strip_padding(raw)
        self.assertIn(map_text(False).encode() + b'\0', _unpack(fixed))
        self.assertEqual(strip_padding(fixed), fixed)

    def test_real_generated_matches_diagnosed_fix(self):
        source = Path('~/meow-loop-out/card-36/attempt-2/replays/base_sq_rooms_large_10044_13600_0.replay')
        expected = Path('~/.claude/jobs/e3d433df/tmp/replay-debug/fixed_all/base_sq_rooms_large_10044_13600_0.replay')
        if not source.exists() or not expected.exists():
            self.skipTest('real replay fixture missing')
        self.assertEqual(strip_padding(source.read_bytes()), expected.read_bytes())

    def test_real_official_unchanged(self):
        source = Path('~/meow-loop-out/card-39/attempt-1/replays/base_default_13900_0.replay')
        if not source.exists():
            self.skipTest('official replay fixture missing')
        raw = source.read_bytes()
        self.assertEqual(strip_padding(raw), raw)


class AttachmentTests(unittest.IsolatedAsyncioTestCase):
    async def test_repair_before_size_check_and_gzip(self):
        import meowbot as bot

        raw = replay(map_text())
        fixed = strip_padding(raw)
        for compressed in (False, True):
            with self.subTest(compressed=compressed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                card = root / 'card-1'
                card.mkdir()
                source = card / 'sample.replay'
                source.write_bytes(raw)
                (card / 'look.json').write_text(json.dumps({'replays': ['sample.replay']}))
                limit = max(len(gzip.compress(fixed, 9)), len(fixed) - 1) if compressed else len(fixed)
                self.assertLess(limit, len(raw))
                channel = SimpleNamespace(send=AsyncMock())
                discord = SimpleNamespace(File=Mock(side_effect=lambda stream, filename:
                                                   (stream.getvalue(), filename)))
                with patch.object(bot, 'LOOK_DIR', directory), patch.object(bot, 'LOOK_INLINE_BYTES', limit), \
                        patch.object(bot, 'state_message', return_value='Check 2 to 3 replays'):
                    await bot.send_state_message(channel, 1, {'status': 'needs-look'}, discord)
                self.assertEqual(channel.send.await_count, 2)
                payload, filename = channel.send.await_args_list[1].kwargs['file']
                self.assertEqual(gzip.decompress(payload) if compressed else payload, fixed)
                self.assertEqual(filename, 'sample.replay.gz' if compressed else 'sample.replay')
                self.assertEqual(source.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
