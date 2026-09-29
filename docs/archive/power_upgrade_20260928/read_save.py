from pathlib import Path
import struct, hashlib, zstandard, re

source = Path('C:/Users/stkot/Saved Games/Surviving Mars Relaunched/76561198020568696/Double Hub Build.savegame.sav')
b = source.read_bytes()
header = struct.unpack_from('<23I', b)
assert b[:4] == b'BPUL'
per = header[2]
fragments = []
for off, size in zip(header[7::2], header[8::2]):
    fragments.extend(struct.unpack_from('<II', b, i) for i in range(off, off + size, 8))

def body(index):
    return b''.join(b[s:s+n] for s, n in fragments[index*per:(index+1)*per])

def walk(index, prefix=''):
    data = body(index)
    pos = 0
    while pos < len(data):
        fid, flags, n = struct.unpack_from('<IIH', data, pos)
        name = data[pos+10:pos+10+n].decode()
        pos += 10+n
        if flags & 1:
            yield from walk(fid-1, prefix+name+'/')
        else:
            yield prefix+name, body(fid-1)

print('source:', source)
print('save SHA256:', hashlib.sha256(b).hexdigest())
out = Path('scratch/power_repair_save')
out.mkdir(exist_ok=True)
for name, raw in walk(0):
    if name != 'persist':
        continue
    if raw[:4] == b'ZSTD':
        want = struct.unpack_from('<I', raw, 4)[0]
        remaining, parts = raw[12:], []
        while remaining.startswith(b'\x28\xb5\x2f\xfd'):
            decoder = zstandard.ZstdDecompressor().decompressobj()
            parts.append(decoder.decompress(remaining))
            remaining = decoder.unused_data
        raw = b''.join(parts)
        assert len(raw) == want
    (out/name).write_bytes(raw)
    print(name, len(raw), 'SHA256:', hashlib.sha256(raw).hexdigest(), 'prefix:', repr(raw[:30]))
    for token in [b'base_electricity_production', b'electricity_production', b'SMROptInTrainHub6']:
        hits = [m.start() for m in re.finditer(re.escape(token), raw)]
        print(token.decode(), 'matches:', len(hits))
        for i in hits[:5]:
            print(i, repr(raw[max(0,i-70):i+180]))
