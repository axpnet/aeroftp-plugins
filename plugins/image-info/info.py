#!/usr/bin/env python3
"""Image Info plugin for AeroFTP. Reads JSON args from stdin, outputs JSON result."""

import json
import os
import struct
import sys


def read_png_dimensions(path):
    with open(path, 'rb') as f:
        f.read(8)  # PNG signature
        f.read(4)  # IHDR length
        f.read(4)  # IHDR type
        w = struct.unpack('>I', f.read(4))[0]
        h = struct.unpack('>I', f.read(4))[0]
    return w, h


def read_jpeg_dimensions(path):
    with open(path, 'rb') as f:
        f.read(2)  # SOI marker
        while True:
            marker = f.read(2)
            if len(marker) < 2:
                break
            if marker[0] != 0xFF:
                break
            if marker[1] in (0xC0, 0xC1, 0xC2):
                f.read(3)  # length + precision
                h = struct.unpack('>H', f.read(2))[0]
                w = struct.unpack('>H', f.read(2))[0]
                return w, h
            else:
                length = struct.unpack('>H', f.read(2))[0]
                f.read(length - 2)
    return None, None


def read_gif_dimensions(path):
    with open(path, 'rb') as f:
        f.read(6)  # GIF header
        w = struct.unpack('<H', f.read(2))[0]
        h = struct.unpack('<H', f.read(2))[0]
    return w, h


def read_bmp_dimensions(path):
    with open(path, 'rb') as f:
        f.read(18)  # BMP header
        w = struct.unpack('<i', f.read(4))[0]
        h = abs(struct.unpack('<i', f.read(4))[0])
    return w, h


def read_webp_dimensions(path):
    with open(path, 'rb') as f:
        f.read(12)  # RIFF header
        chunk = f.read(4)
        if chunk == b'VP8 ':
            f.read(10)
            w = struct.unpack('<H', f.read(2))[0] & 0x3FFF
            h = struct.unpack('<H', f.read(2))[0] & 0x3FFF
            return w, h
        elif chunk == b'VP8L':
            f.read(5)
            b = struct.unpack('<I', f.read(4))[0]
            w = (b & 0x3FFF) + 1
            h = ((b >> 14) & 0x3FFF) + 1
            return w, h
    return None, None


def detect_format(path):
    ext = os.path.splitext(path)[1].lower()
    format_map = {
        '.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG',
        '.gif': 'GIF', '.bmp': 'BMP', '.webp': 'WebP',
        '.svg': 'SVG', '.ico': 'ICO', '.tiff': 'TIFF', '.tif': 'TIFF',
    }
    return format_map.get(ext, ext.upper().lstrip('.'))


def get_dimensions(path, fmt):
    try:
        readers = {
            'PNG': read_png_dimensions,
            'JPEG': read_jpeg_dimensions,
            'GIF': read_gif_dimensions,
            'BMP': read_bmp_dimensions,
            'WebP': read_webp_dimensions,
        }
        reader = readers.get(fmt)
        if reader:
            return reader(path)
    except Exception:
        pass
    return None, None


def analyze(path):
    if not os.path.isfile(path):
        return {"error": f"file not found: {path}"}

    fmt = detect_format(path)
    size = os.path.getsize(path)
    w, h = get_dimensions(path, fmt)

    result = {
        "file": os.path.basename(path),
        "format": fmt,
        "size": size,
        "size_human": f"{size / 1024:.1f} KB" if size < 1048576 else f"{size / 1048576:.1f} MB",
    }

    if w and h:
        result["width"] = w
        result["height"] = h
        result["aspect_ratio"] = f"{w}:{h}"
        result["megapixels"] = round(w * h / 1000000, 2)

    return result


if __name__ == '__main__':
    args = json.load(sys.stdin)
    path = args.get('path', '')

    if not path:
        print(json.dumps({"error": "path parameter is required"}))
        sys.exit(1)

    result = analyze(path)
    print(json.dumps(result))
