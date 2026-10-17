"""Minimal NBT and Anvil region reader/writer (no dependencies).

Tags are decoded to plain Python values wrapped in Tag so they round-trip with
their original types: Tag(type_id, value). Compounds are dicts of name -> Tag,
lists are Tag(LIST, (element_type, [Tag, ...])).
"""
import gzip
import io
import struct
import zlib

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)


class Tag:
    __slots__ = ("t", "v")

    def __init__(self, t, v):
        self.t = t
        self.v = v

    def __repr__(self):
        return f"Tag({self.t}, {self.v!r})"


def _read_str(f):
    (n,) = struct.unpack(">H", f.read(2))
    return f.read(n).decode("utf-8", "surrogatepass")


def _write_str(f, s):
    b = s.encode("utf-8", "surrogatepass")
    f.write(struct.pack(">H", len(b)))
    f.write(b)


_FIXED = {BYTE: ">b", SHORT: ">h", INT: ">i", LONG: ">q", FLOAT: ">f", DOUBLE: ">d"}


def _read_payload(f, t):
    if t in _FIXED:
        fmt = _FIXED[t]
        return struct.unpack(fmt, f.read(struct.calcsize(fmt)))[0]
    if t == STRING:
        return _read_str(f)
    if t == BYTE_ARRAY:
        (n,) = struct.unpack(">i", f.read(4))
        return f.read(n)
    if t == INT_ARRAY:
        (n,) = struct.unpack(">i", f.read(4))
        return list(struct.unpack(f">{n}i", f.read(4 * n)))
    if t == LONG_ARRAY:
        (n,) = struct.unpack(">i", f.read(4))
        return list(struct.unpack(f">{n}q", f.read(8 * n)))
    if t == LIST:
        et = f.read(1)[0]
        (n,) = struct.unpack(">i", f.read(4))
        return (et, [Tag(et, _read_payload(f, et)) for _ in range(n)])
    if t == COMPOUND:
        d = {}
        while True:
            ct = f.read(1)[0]
            if ct == END:
                return d
            name = _read_str(f)
            d[name] = Tag(ct, _read_payload(f, ct))
    raise ValueError(f"bad tag type {t}")


def _write_payload(f, tag):
    t, v = tag.t, tag.v
    if t in _FIXED:
        f.write(struct.pack(_FIXED[t], v))
    elif t == STRING:
        _write_str(f, v)
    elif t == BYTE_ARRAY:
        f.write(struct.pack(">i", len(v)))
        f.write(v)
    elif t == INT_ARRAY:
        f.write(struct.pack(f">i{len(v)}i", len(v), *v))
    elif t == LONG_ARRAY:
        f.write(struct.pack(f">i{len(v)}q", len(v), *v))
    elif t == LIST:
        et, items = v
        if not items:
            et = END
        f.write(bytes([et]))
        f.write(struct.pack(">i", len(items)))
        for it in items:
            _write_payload(f, it)
    elif t == COMPOUND:
        for name, child in v.items():
            f.write(bytes([child.t]))
            _write_str(f, name)
            _write_payload(f, child)
        f.write(b"\x00")
    else:
        raise ValueError(f"bad tag type {t}")


def loads(data):
    f = io.BytesIO(data)
    t = f.read(1)[0]
    name = _read_str(f)
    return name, Tag(t, _read_payload(f, t))


def dumps(root, name=""):
    f = io.BytesIO()
    f.write(bytes([root.t]))
    _write_str(f, name)
    _write_payload(f, root)
    return f.getvalue()


def read_file(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    gz = raw[:2] == b"\x1f\x8b"
    return loads(gzip.decompress(raw) if gz else raw), gz


def write_file(path, root, name="", gz=True):
    data = dumps(root, name)
    with open(path, "wb") as fh:
        fh.write(gzip.compress(data) if gz else data)


# ---- Anvil region files (.mca) ----

def read_region(path):
    """Return {index: (timestamp, compression, payload_bytes)} for each stored chunk."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 8192:
        return {}
    chunks = {}
    for i in range(1024):
        (loc,) = struct.unpack(">I", data[i * 4:i * 4 + 4])
        (ts,) = struct.unpack(">I", data[4096 + i * 4:4096 + i * 4 + 4])
        off, count = loc >> 8, loc & 0xFF
        if off == 0 or count == 0:
            continue
        start = off * 4096
        if start + 5 > len(data):
            continue
        (length,) = struct.unpack(">I", data[start:start + 4])
        comp = data[start + 4]
        payload = data[start + 5:start + 4 + length]
        chunks[i] = (ts, comp, payload)
    return chunks


def decode_chunk(comp, payload):
    if comp & 0x80:
        raise ValueError("chunk stored in external .mcc file")
    if comp == 1:
        raw = gzip.decompress(payload)
    elif comp == 2:
        raw = zlib.decompress(payload)
    elif comp == 3:
        raw = payload
    else:
        raise ValueError(f"unsupported chunk compression {comp}")
    return loads(raw)[1]


def write_region(path, chunks):
    """chunks: {index: (timestamp, root_tag)}; written zlib-compressed."""
    header = bytearray(8192)
    body = bytearray()
    sector = 2
    for i in sorted(chunks):
        ts, root = chunks[i]
        comp = zlib.compress(dumps(root))
        blob = struct.pack(">IB", len(comp) + 1, 2) + comp
        pad = (-len(blob)) % 4096
        blob += b"\x00" * pad
        n = len(blob) // 4096
        if n > 255:
            raise ValueError(f"chunk {i} in {path} is too large ({n} sectors)")
        struct.pack_into(">I", header, i * 4, (sector << 8) | n)
        struct.pack_into(">I", header, 4096 + i * 4, ts)
        body += blob
        sector += n
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(body)
