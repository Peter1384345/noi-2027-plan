# -*- coding: utf-8 -*-
"""纯 python 读取 mp4 的显示宽高（tkhd atom），不需要 ffmpeg。"""
import struct, sys, glob, os

def walk(buf, start, end, depth=0):
    i = start
    while i + 8 <= end:
        size = struct.unpack('>I', buf[i:i+4])[0]
        typ = buf[i+4:i+8]
        hdr = 8
        if size == 1:
            size = struct.unpack('>Q', buf[i+8:i+16])[0]
            hdr = 16
        if size < hdr:
            break
        if typ == b'tkhd':
            d = buf[i+hdr:i+size]
            # tkhd 以 width(4) + height(4) 结尾，取最后 8 字节最稳妥
            w, h = struct.unpack('>II', d[-8:])
            if w and h:
                return w / 65536.0, h / 65536.0
        if typ in (b'moov', b'trak', b'mdia'):
            r = walk(buf, i + hdr, i + size, depth + 1)
            if r:
                return r
        i += size
    return None

for p in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else '*.mp4')):
    with open(p, 'rb') as f:
        buf = f.read()
    wh = walk(buf, 0, len(buf))
    if wh:
        w, h = wh
        print('%-46s %4.0f x %4.0f  ratio %.3f' % (os.path.basename(p), w, h, w / h))
    else:
        print('%-46s ?' % os.path.basename(p))
