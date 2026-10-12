"""Remove empty horizontal padding edges from packed Cap'n Proto replays."""
import struct


def _unpack(raw):
    out = bytearray()
    i = 0
    while i < len(raw):
        tag = raw[i]
        i += 1
        word = bytearray(8)
        for k in range(8):
            if tag >> k & 1:
                word[k] = raw[i]
                i += 1
        out.extend(word)
        if tag in (0, 255):
            count = raw[i]
            i += 1
            if tag == 0:
                out.extend(bytes(8 * count))
            else:
                end = i + 8 * count
                if end > len(raw):
                    raise ValueError('truncated packed run')
                out.extend(raw[i:end])
                i = end
    return out


def _pack(data):
    out = bytearray()
    i = 0
    n = len(data) // 8
    while i < n:
        word = data[i * 8:i * 8 + 8]
        tag = sum(1 << k for k in range(8) if word[k])
        out.append(tag)
        out.extend(x for x in word if x)
        if tag in (0, 255):
            j = i + 1
            while j < n and j - i - 1 < 255:
                following = data[j * 8:j * 8 + 8]
                if (tag == 0 and any(following)) or (tag == 255 and 0 in following):
                    break
                j += 1
            out.append(j - i - 1)
            if tag == 255:
                out.extend(data[(i + 1) * 8:j * 8])
            i = j
        else:
            i += 1
    return bytes(out)


def strip_padding(raw: bytes) -> bytes:
    """Return the original bytes if parsing or a safe repair is impossible."""
    try:
        return _strip_padding(raw)
    except Exception:
        return raw


def _strip_padding(raw):
    data = _unpack(raw)
    nseg = struct.unpack_from('<I', data)[0] + 1
    if nseg > (len(data) - 4) // 4:
        return raw
    sizes = struct.unpack_from(f'<{nseg}I', data, 4)
    start = (4 + 4 * nseg + 7) // 8 * 8
    segments = []
    for size in sizes:
        end = start + 8 * size
        if end > len(data):
            return raw
        segments.append((start, end))
        start = end
    if start != len(data):
        return raw
    candidates = []
    for start, end in segments:
        for pointer in range(start, end, 8):
            value = struct.unpack_from('<Q', data, pointer)[0]
            if value & 3 != 1 or (value >> 32) & 7 != 2:
                continue
            offset = (value >> 2) & 0x3fffffff
            if offset & (1 << 29):
                offset -= 1 << 30
            text_start = pointer + 8 + 8 * offset
            count = value >> 35
            text_end = text_start + count
            if count < 1 or not start <= text_start < text_end <= end:
                continue
            if data[text_start:text_start + 4] == b'MAP ' and data[text_end - 1] == 0:
                candidates.append((pointer, value, text_start, text_end))
    if len(candidates) != 1:
        return raw
    pointer, value, start, end = candidates[0]
    text = bytes(data[start:end - 1]).decode('utf-8')
    lines = text.split('\n')
    header = lines[0].split()
    if len(header) != 3 or '\0' in text or not lines[-1 if lines[-1] else -2] == 'END':
        return raw
    width, height = map(int, header[1:])
    if width <= 0 or height <= 0:
        return raw
    edges = set()
    counts = []
    out = []
    dropped = 0
    for line in lines:
        fields = line.split()
        if fields and fields[0] == 'EDGE_COUNT':
            if len(fields) != 2:
                return raw
            counts.append(int(fields[1]))
        elif fields and fields[0] == 'EDGE':
            if len(fields) != 4:
                return raw
            edge, kind, partner = map(int, fields[1:])
            if edge in edges or not 0 <= edge < (2 * height + 1) * (width + 1):
                return raw
            edges.add(edge)
            row, x = divmod(edge, width + 1)
            if row % 2 == 0 and x == width:
                if kind != 0 or partner != -1:
                    return raw
                dropped += 1
                continue
        out.append(line)
    if counts != [len(edges)] or not dropped:
        return raw
    new = '\n'.join(f'EDGE_COUNT {len(edges) - dropped}' if line.split()[:1] == ['EDGE_COUNT']
                    else line for line in out).encode('utf-8')
    struct.pack_into('<Q', data, pointer, (value & ((1 << 35) - 1)) | ((len(new) + 1) << 35))
    data[start:end] = new + bytes(end - start - len(new))
    return _pack(data)
