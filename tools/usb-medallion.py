#!/usr/bin/env python3
"""USB screen art: a USB-A plug drawn to real proportions (1px = 1mm), flat gilt like the icons.
Writes usb-medallion.bmp at 2x. Run from theme-art/."""
import sys, math
sys.path.insert(0, ".")
from mock import *
from icons import symmetric
SHADE = (150, 116, 52)
def rect(x0, y0, w, h): return {(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)}
# columns 0..15, centre between 7 and 8
shell = rect(2, 0, 12, 12)                        # 12 x 12 metal shell
holes = rect(5, 2, 2, 4) | rect(9, 2, 2, 4)       # two 2x4 holes near the tip, 3mm in from each side
housing = rect(0, 13, 16, 20) - {(0, 32), (15, 32), (0, 31), (15, 31), (1, 32), (14, 32)}   # 16 x 20, rounded bottom
relief = rect(4, 33, 8, 3) | rect(5, 36, 6, 3)    # strain relief 8 -> 6
cable = rect(6, 39, 4, 8)                         # 4mm cable stub
plug = shell | housing | relief | cable
assert symmetric(plug)
trident = set()                                   # on the housing, stem 2px wide on the centre line
trident |= rect(7, 17, 2, 12)                                         # stem
trident |= rect(7, 15, 2, 1) | rect(6, 16, 4, 1)                      # arrow head
trident |= {(6, 24), (5, 23), (4, 22), (4, 21)} | rect(3, 19, 3, 2)   # left branch to a round end
trident |= {(9, 26), (10, 25), (11, 24), (11, 23)} | rect(10, 20, 3, 3)   # right branch to a square end
trident |= rect(6, 28, 4, 3) - {(6, 30), (9, 30)}                     # base ball
cut = holes | rect(2, 12, 12, 1) & plug           # holes and the seam; no symbol on the housing
lines = set()
lines |= rect(4, 26, 8, 1) | rect(4, 28, 8, 1) | rect(4, 30, 8, 1)   # grip ridges on the housing
lines |= rect(4, 34, 8, 1) | rect(5, 37, 6, 1)              # grooves on the strain relief
# flat: one gilt pass over plug + ring, like the icons (gold, dark outline, lit top/left edge); holes and trident are gaps
from icons import render
CX, CY, R1, R2 = 7.5, 22, 25.5, 28.5               # ring centred on the plug body
ring = {(x, y) for y in range(-10, 60) for x in range(-25, 41) if R1 <= math.hypot(x - CX, y - CY) < R2}
shape = plug - (cut - holes)                      # no ring, just the plug
px = render(shape, "gilt")       # lit edges come from the outer shape only
for q in holes: px[q] = LOW                # holes: plain dark, no lit edges around them
for q in lines: px[q] = LOW                # detail lines, flat dark
px = {(x, y): c for (x, y), c in px.items() if y <= CY + R2 + 4}
xs = [x for x, _ in px]; ys = [y for _, y in px]; x0, y0 = min(xs), min(ys)
w0, h0 = max(xs) - x0 + 1, max(ys) - y0 + 1
with open("usb-medallion.ppm", "wb") as f:
    f.write(f"P6 {w0} {h0} 255\n".encode())
    f.write(b"".join(bytes(px.get((x + x0, y + y0), (255, 0, 255))) for y in range(h0) for x in range(w0)))
print(w0, h0)
