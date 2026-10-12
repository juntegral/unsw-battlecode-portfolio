"""Packed Cap'n Proto reader adapted from the permitted harness replay.py."""
import gzip
import struct


def unpack_packed(data):
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        tag = data[i]
        i += 1
        if tag == 0:
            out += bytes(8)
            count = data[i]
            i += 1
            out += bytes(8 * count)
            continue
        word = bytearray(8)
        for bit in range(8):
            if tag & (1 << bit):
                word[bit] = data[i]
                i += 1
        out += word
        if tag == 0xFF:
            count = data[i]
            i += 1
            out += data[i:i + 8 * count]
            i += 8 * count
    return bytes(out)


class Message:
    def __init__(self, raw):
        count = struct.unpack_from("<I", raw, 0)[0] + 1
        sizes = struct.unpack_from("<%dI" % count, raw, 4)
        start = 4 + 4 * count
        if start % 8:
            start += 8 - start % 8
        self.segments = []
        for size in sizes:
            self.segments.append(raw[start:start + 8 * size])
            start += 8 * size

    def root(self):
        return follow(self, 0, 0)

    def word(self, seg, index):
        return struct.unpack_from("<Q", self.segments[seg], 8 * index)[0]


class Struct:
    __slots__ = ("msg", "seg", "data", "dwords", "pwords")

    def __init__(self, msg, seg, data, dwords, pwords):
        self.msg, self.seg, self.data = msg, seg, data
        self.dwords, self.pwords = dwords, pwords

    def _bytes(self, offset, size):
        base = 8 * self.data + offset
        if offset + size > 8 * self.dwords:
            return bytes(size)
        return self.msg.segments[self.seg][base:base + size]

    def i32(self, off):
        return struct.unpack("<i", self._bytes(off, 4))[0]

    def u32(self, off):
        return struct.unpack("<I", self._bytes(off, 4))[0]

    def u16(self, off):
        return struct.unpack("<H", self._bytes(off, 2))[0]

    def u64(self, off):
        return struct.unpack("<Q", self._bytes(off, 8))[0]

    def bit(self, index):
        byte = self._bytes(index // 8, 1)
        return bool(byte[0] & (1 << (index % 8)))

    def pointer(self, index):
        if index >= self.pwords:
            return None
        return follow(self.msg, self.seg, self.data + self.dwords + index)

    def text(self, index):
        val = self.pointer(index)
        if val is None:
            return ""
        return bytes(val.raw_bytes()).rstrip(b"\x00").decode("utf8", "replace")


class List:
    __slots__ = ("msg", "seg", "start", "count", "elem", "dwords", "pwords")

    def __init__(self, msg, seg, start, count, elem, dwords=0, pwords=0):
        self.msg, self.seg, self.start = msg, seg, start
        self.count, self.elem = count, elem
        self.dwords, self.pwords = dwords, pwords

    def raw_bytes(self):
        return self.msg.segments[self.seg][self.start:self.start + self.count]

    def __len__(self):
        return self.count

    def __iter__(self):
        step = self.dwords + self.pwords
        for k in range(self.count):
            if self.elem == 7:
                yield Struct(self.msg, self.seg, self.start // 8 + k * step,
                             self.dwords, self.pwords)
            elif self.elem == 3:
                yield struct.unpack_from("<H", self.msg.segments[self.seg],
                                         self.start + 2 * k)[0]
            else:
                raise NotImplementedError("list element size %d" % self.elem)


def follow(msg, seg, word_index):
    ptr = msg.word(seg, word_index)
    if ptr == 0:
        return None
    kind = ptr & 3
    if kind == 2:
        pad_seg = (ptr >> 32) & 0xFFFFFFFF
        pad_off = (ptr >> 3) & 0x1FFFFFFF
        if (ptr >> 2) & 1:
            far = msg.word(pad_seg, pad_off)
            target_seg = (far >> 32) & 0xFFFFFFFF
            target = (far >> 3) & 0x1FFFFFFF
            tag = msg.word(pad_seg, pad_off + 1)
            return decode_pointer(msg, target_seg, target, tag)
        return follow(msg, pad_seg, pad_off)
    offset = (ptr >> 2) & 0x3FFFFFFF
    if offset >= 0x20000000:
        offset -= 0x40000000
    target = word_index + 1 + offset
    return decode_pointer(msg, seg, target, ptr)


def decode_pointer(msg, seg, target, ptr):
    kind = ptr & 3
    if kind == 0:
        dwords = (ptr >> 32) & 0xFFFF
        pwords = (ptr >> 48) & 0xFFFF
        return Struct(msg, seg, target, dwords, pwords)
    elem = (ptr >> 32) & 7
    count = (ptr >> 35) & 0x1FFFFFFF
    if elem == 7:
        tag = msg.word(seg, target)
        items = (tag >> 2) & 0x3FFFFFFF
        dwords = (tag >> 32) & 0xFFFF
        pwords = (tag >> 48) & 0xFFFF
        return List(msg, seg, 8 * (target + 1), items, 7, dwords, pwords)
    if elem == 2:
        return List(msg, seg, 8 * target, count, 2)
    return List(msg, seg, 8 * target, count, elem)


def point(struct_or_none):
    if struct_or_none is None:
        return None
    return (struct_or_none.i32(0), struct_or_none.i32(4))


def load(path):
    with open(path, "rb") as handle:
        blob = handle.read()
    if blob[:2] == b"\x1f\x8b":
        blob = gzip.decompress(blob)
    return Message(unpack_packed(blob))
