"""Read-only BPUL/ZSTD inspection; native object graph is NOT decoded.

Revision 2: validates the trailing ZSTD frame-offset table that revision 1 rejected.
Adapted from ../power_upgrade_20260928/read_save.py. Writes decoded members to
ignored scratch only, never to the save. Token counts are not object counts.
"""
from pathlib import Path
import hashlib
import struct
import zstandard

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('C:/Users/stkot/Saved Games/Surviving Mars Relaunched/76561198020568696/double hub+elev.savegame.sav')
OUT = ROOT / 'scratch/elevator_rope_20260930/save_decoded'
data = SOURCE.read_bytes()
header = struct.unpack_from('<23I', data)
assert data[:4] == b'BPUL'
fragments = []
for offset, size in zip(header[7::2], header[8::2]):
    fragments.extend(struct.unpack_from('<II', data, i) for i in range(offset, offset + size, 8))


def body(index):
    per = header[2]
    return b''.join(data[s:s+n] for s, n in fragments[index*per:(index+1)*per])


def walk(index, prefix=''):
    raw = body(index)
    pos = 0
    while pos < len(raw):
        fid, flags, n = struct.unpack_from('<IIH', raw, pos)
        name = raw[pos+10:pos+10+n].decode()
        pos += 10+n
        if flags & 1:
            yield from walk(fid-1, prefix+name+'/')
        else:
            yield prefix+name, body(fid-1)


print('source:', SOURCE)
before = hashlib.sha256(data).hexdigest()
print('save SHA256:', before)
for name, raw in walk(0):
    if raw[:4] == b'ZSTD':
        want = struct.unpack_from('<I', raw, 4)[0]
        remaining, parts, offsets = raw[12:], [], []
        while remaining.startswith(b'\x28\xb5\x2f\xfd'):
            offsets.append(len(raw) - len(remaining))
            decoder = zstandard.ZstdDecompressor().decompressobj()
            parts.append(decoder.decompress(remaining))
            remaining = decoder.unused_data
        assert remaining == struct.pack('<%dI' % len(offsets), *offsets), (name, 'frame-offset table mismatch')
        raw = b''.join(parts)
        assert len(raw) == want, (name, len(raw), want)
    dest = OUT / name
    assert dest.resolve().is_relative_to(OUT.resolve())
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    tokens = {t.decode(): raw.count(t) for t in (
        b'SpaceElevatorRope', b'SpaceElevatorCabin', b'SMROptInElevatorDepot', b'smr_depot_prop')}
    print(name, 'bytes:', len(raw), 'SHA256:', hashlib.sha256(raw).hexdigest(), 'tokens:', tokens)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before, 'save changed during read'
print('Original save unchanged; no object identity/ownership claim from these token counts.')
