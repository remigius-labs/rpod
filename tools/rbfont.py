#!/usr/bin/env python3
"""Read Rockbox .fnt fonts (RB12) and draw text with them, pixel for pixel like the device.

    from rbfont import Font
    f = Font(".../22-Terminus-Bold.fnt")
    pixels = f.text("Resume")      # set of (x, y) inside a box of f.width("Resume") x f.height
"""
import struct


class Font:
    def __init__(self, path):
        d = open(path, "rb").read()
        if d[:4] != b"RB12":
            raise ValueError("not an RB12 font: " + path)
        (self.maxwidth, self.height, self.ascent, _pad, self.first, self.default,
         self.size, nbits, noffset, nwidth) = struct.unpack_from("<HHHHIIIIII", d, 4)
        pos = 36
        self.bits = d[pos:pos + nbits]
        pos += nbits
        wide = nbits >= 0xFFDB
        align = 4 if wide else 2
        pos += (-pos) % align
        fmt, step = ("<I", 4) if wide else ("<H", 2)
        self.offsets = [struct.unpack_from(fmt, d, pos + i * step)[0] for i in range(noffset)] if noffset else None
        pos += noffset * step
        self.widths = list(d[pos:pos + nwidth]) if nwidth else None

    def _index(self, ch):
        i = ord(ch) - self.first
        return i if 0 <= i < self.size else self.default - self.first

    def glyph_width(self, ch):
        return self.widths[self._index(ch)] if self.widths else self.maxwidth

    def glyph(self, ch):
        i = self._index(ch)
        w = self.glyph_width(ch)
        rows = (self.height + 7) // 8
        start = self.offsets[i] if self.offsets else i * w * rows
        px = set()
        for x in range(w):
            for block in range(rows):
                byte = self.bits[start + block * w + x]
                for b in range(8):
                    y = block * 8 + b
                    if y < self.height and byte >> b & 1:
                        px.add((x, y))
        return px, w

    def width(self, s):
        return sum(self.glyph_width(c) for c in s)

    def text(self, s):
        out, x = set(), 0
        for c in s:
            g, w = self.glyph(c)
            out |= {(x + gx, gy) for gx, gy in g}
            x += w
        return out
