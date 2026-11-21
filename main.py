#!/usr/bin/env python3
"""Validate entry.png (exactly 1024x1024, at most 1 MiB) and copy it to
$MAKEFUN_OUTPUT_DIR (default /output) as entry.png. Stdlib only."""
import os
import shutil
import struct
import sys

MAX_BYTES = 1024 * 1024  # 1 MiB
EXPECTED = (1024, 1024)
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def png_dimensions(path):
    with open(path, "rb") as fh:
        data = fh.read(33)
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    if not os.path.isfile(SRC):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the 1 MiB cap", file=sys.stderr)
        return 1
    dims = png_dimensions(SRC)
    if dims != EXPECTED:
        print(f"entry.png is {dims[0]}x{dims[1]}, expected 1024x1024",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print(f"OK: entry.png {dims[0]}x{dims[1]}, {size} bytes -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
