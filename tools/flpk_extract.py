"""FLPK (Surviving Mars: Relaunched .fpk) extractor, v2.

Directory record: u32 offset | u32 packed | u32 size | name[nameLen] | u32 extra
  packed: loword 0, byte2 = flags, byte3 = nameLen
  flags: 0x10 stored, 0x30 zstd-wrapped, 0x01 directory
  dir: offset/size = child table offset (relative to dirOffset) / byte length
  file 'size' = STORED byte length in the fpk (wrapper included for 0x30)

ZSTD wrapper: 'ZSTD' | u32 decompressedSize | u32 chunkSize (0x400) |
  u32 headerLen | (chunk-boundary u32 table when multi-chunk) | zstd frames.
  Extraction scans the stored region for zstd frame magics and concatenates —
  robust to the table semantics; verified against decompressedSize.
"""
import io, os, struct, sys
import zstandard
import sys

# The Windows console defaults to cp1252 and this tool prints the project's
# non-ASCII vocabulary; without this it dies on its own output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


ZMAGIC = b"\x28\xb5\x2f\xfd"

def parse_table(buf, table_off, table_size, dir_off, prefix, out):
    p = table_off
    end = table_off + table_size
    skip = []  # child-table ranges claimed by dir entries in THIS table
    while p + 12 <= end:
        if any(a <= p < b for a, b in skip):
            p += 1
            continue
        off, packed, size = struct.unpack_from("<III", buf, p)
        flags = (packed >> 16) & 0xFF
        namelen = (packed >> 24) & 0xFF
        if packed & 0xFFFF or namelen == 0:
            break  # padding / end of this table's records
        name = buf[p+12:p+12+namelen].decode("utf-8", "replace")
        if flags == 0x01:
            child = dir_off + off
            skip.append((child, child + size))
            parse_table(buf, child, size, dir_off, prefix + name + "/", out)
        else:
            out.append((prefix + name, flags, off, size))
        p += 16 + namelen

def extract(fpk_path, out_root):
    buf = open(fpk_path, "rb").read()
    assert buf[:4] == b"FLPK", fpk_path
    dir_off = struct.unpack_from("<I", buf, 0x0C)[0]
    dir_size = struct.unpack_from("<I", buf, 0x14)[0]
    files = []
    parse_table(buf, dir_off, dir_size, dir_off, "", files)
    dctx = zstandard.ZstdDecompressor()
    for relpath, flags, off, size in files:
        dest = os.path.join(out_root, relpath.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if flags == 0x10:
            data = buf[off:off+size]
        elif flags == 0x30:
            assert buf[off:off+4] == b"ZSTD", f"{relpath}: no ZSTD at 0x{off:X}"
            want = struct.unpack_from("<I", buf, off + 4)[0]
            region = buf[off:off+size]
            hdrlen = struct.unpack_from("<I", region, 12)[0]
            nbound = (hdrlen - 16) // 4
            starts = [hdrlen] + list(
                struct.unpack_from("<%dI" % nbound, region, 16)) if nbound \
                else [hdrlen]
            ends = starts[1:] + [len(region)]
            parts = []
            for s, e in zip(starts, ends):
                blob = region[s:e]
                if blob[:4] == ZMAGIC:
                    parts.append(dctx.stream_reader(io.BytesIO(blob)).read())
                else:
                    parts.append(blob)  # incompressible chunk stored raw
            data = b"".join(parts)[:want]
            if len(data) != want:
                print(f"  WARN {relpath}: got {len(data)} != header {want}")
        else:
            print(f"  SKIP {relpath}: unknown flags 0x{flags:02X}")
            continue
        with open(dest, "wb") as f:
            f.write(data)
        print(f"  {relpath}  ({len(data)} bytes)")

if __name__ == "__main__":
    src_root, out_base = sys.argv[1], sys.argv[2]
    for item in sorted(os.listdir(src_root)):
        fpk = os.path.join(src_root, item, "ModContent.fpk")
        if os.path.isfile(fpk):
            print(f"== {item} ==")
            extract(fpk, os.path.join(out_base, item))
