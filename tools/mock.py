#!/usr/bin/env python3
"""Compose RPod screens offline from the real theme parts (backdrop, icons, logo, .fnt fonts).

Used for labs, so previews match the device pixel for pixel without driving the simulator.
"""
import os, subprocess
from rbfont import Font

ART = os.path.dirname(os.path.abspath(__file__))
SIM = os.environ.get("RPOD_SIM", os.path.join(ART, "..", "..", "rockbox", "build-sim"))
RB = os.path.join(SIM, "simdisk", ".rockbox")
MUSIC = os.path.join(SIM, "simdisk", "Music")
CREAM, DARK = (0xff, 0xf1, 0xdc), (0x12, 0x0d, 0x0a)
HI, GOLD, LOW = (240, 212, 136), (201, 162, 79), (59, 42, 20)
MAGENTA = (255, 0, 255)
_fonts = {}


def font(name):
    if name not in _fonts:
        _fonts[name] = Font(os.path.join(RB, "fonts", name))
    return _fonts[name]


def load(path):
    """Image -> (w, h, rows of RGB tuples)."""
    ppm = subprocess.run(["magick", path, "ppm:-"], capture_output=True, check=True).stdout
    parts = ppm.split(maxsplit=4)
    w, h, data = int(parts[1]), int(parts[2]), parts[4]
    return w, h, [[tuple(data[(y * w + x) * 3:(y * w + x) * 3 + 3]) for x in range(w)] for y in range(h)]


class Screen:
    def __init__(self, backdrop):
        _, _, self.px = load(backdrop)

    def put(self, x, y, c):
        if 0 <= x < 320 and 0 <= y < 240:
            self.px[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def image(self, x, y, path, crop=None):
        w, h, rows = load(path)
        cx, cy, cw, ch = crop or (0, 0, w, h)
        for yy in range(ch):
            for xx in range(cw):
                c = rows[cy + yy][cx + xx]
                if c != MAGENTA:
                    self.put(x + xx, y + yy, c)

    def dim(self, x, y, w, h, f):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < 320 and 0 <= yy < 240:
                    self.px[yy][xx] = tuple(int(v * f) for v in self.px[yy][xx])

    def text(self, x, y, s, fnt, c, maxw=None, align="left"):
        f = font(fnt)
        w = f.width(s)
        if maxw and w > maxw:
            while s and f.width(s + "…") > maxw:
                s = s[:-1]
            s += "…"
            w = f.width(s)
        if align == "center" and maxw:
            x += (maxw - w) // 2
        for gx, gy in f.text(s):
            self.put(x + gx, y + gy, c)

    def gilt_box(self, x, y, w, h):
        """1px gold outline with a dark outer rim and a lit top/left edge."""
        self.rect(x - 1, y - 1, w + 2, h + 2, LOW)
        self.rect(x, y, w, h, GOLD)
        self.rect(x, y, w, 1, HI)
        self.rect(x, y, 1, h, HI)

    def save(self, path):
        ppm = path + ".ppm"
        with open(ppm, "wb") as f:
            f.write(b"P6 320 240 255\n")
            f.write(b"".join(bytes(c) for row in self.px for c in row))
        subprocess.run(["magick", ppm, path], check=True)
        os.remove(ppm)


def menu(s, items, selected, top=29, row=22, icons=None, playing=True):
    """Top bar + list rows, as Hermit.sbs and the theme draw them."""
    hermit = os.path.join(RB, "wps", "Hermit")
    s.image(1, 5, os.path.join(hermit, "playmodes.bmp"), (0, 16 * (1 if playing else 0), 16, 16))
    w, _, _ = load(os.path.join(hermit, "rpod-logo.bmp"))
    s.image((320 - w) // 2, 1, os.path.join(hermit, "rpod-logo.bmp"))
    s.image(289, 6, os.path.join(hermit, "battery.bmp"), (0, 13 * 4, 25, 13))
    s.image(0, 25, os.path.join(hermit, "rule.bmp"))
    iconset = os.path.join(RB, "icons", "rpod-gilt.bmp")
    for i, (label, icon) in enumerate(items):
        y = top + i * row
        fg = (232, 217, 181)                       # parchment
        if i == selected:                          # gold row, dark + lit top edge, deep-brown text
            s.rect(0, y, 320, row, GOLD); s.rect(0, y, 320, 1, LOW); s.rect(0, y + 1, 320, 1, HI)
            fg = LOW
        s.image(1, y + 1, iconset, (0, 16 * icon, 16, 16))
        s.text(18, y, label, "22-Terminus-Bold.fnt", fg)
