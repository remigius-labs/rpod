#!/usr/bin/env python3
"""Draw RPod icon sets in several styles from one set of pixel masks.

Writes, per style, into <out>/<style>/:
  icons.ppm     menu iconset strip, 32 icons of 16x16 (Rockbox themable_icons order)
  playmodes.ppm 9 frames of 13x13 (%mp: stop, play, pause, ffwd, rew, ...)
  battery.ppm   5 frames of 25x13 (empty .. full)
  shuffle.ppm   2 frames of 13x13 (on, off)
  repeat.ppm    5 frames of 13x13 (%mm: off, all, one, shuffle, a-b)
Magenta is transparent. Convert to BMP with magick.
"""
import os, sys

CREAM, DARK, GOLD, HI, LOW, RED = (255,241,220), (18,13,10), (201,162,79), (240,212,136), (59,42,20), (168,50,42)
MAGENTA = (255,0,255)

def m(rows):
    return {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"}

G = {
 "note": m(["......####..", "......#####.", "......##.###", "......##..##", "......##....", "......##....",
            "......##....", "..######....", ".#######....", "########....", ".######.....", "..####......"]),
 "folder": m(["............", "####........", "#####.......", "############", "############", "##........##",
              "##........##", "##........##", "##........##", "############", "############", "............"]),
 "list": m(["............", "###.#######.", "###.#######.", "............", "###.#######.", "###.#######.",
            "............", "###.#######.", "###.#######.", "............", "............", "............"]),
 "play": m(["............", ".##.........", ".####.......", ".######.....", ".########...", ".##########.",
            ".##########.", ".########...", ".######.....", ".####.......", ".##.........", "............"]),
 "gear": m([".....##.....", "..#..##..#..", ".##########.", "..########..", "..###..###..", "####....####",
            "####....####", "..###..###..", "..########..", ".##########.", "..#..##..#..", ".....##....."]),
 "ribbon": m(["..########..", "..########..", "..########..", "..########..", "..########..", "..########..",
              "..########..", "..########..", "..###..###..", "..##....##..", "..#......#..", "............"]),
 "chevron": m(["............", "...##.......", "...###......", "....###.....", ".....###....", "......###...",
               "......###...", ".....###....", "....###.....", "...###......", "...##.......", "............"]),
 "dot": m(["............"] * 4 + ["....####....", "...######...", "...######...", "....####...."] + ["............"] * 4),
 "sun": m([".....##.....", ".#...##...#.", "..#......#..", "....####....", "...######...", "##.######.##",
           "##.######.##", "...######...", "....####....", "..#......#..", ".#...##...#.", ".....##....."]),
 "moon": m(["....####....", "..#####.....", ".#####......", ".####.......", "#####.......", "####........",
            "####........", "#####.......", ".#####....#.", ".#######.##.", "..########..", "....####...."]),
 "sunsmall": m(["............", ".....##.....", "............", "..#.####.#..", "...######...", ".##########.",
                ".##########.", "...######...", "..#.####.#..", "............", ".....##.....", "............"]),
 "stop": m(["............", "............", "..########..", "..########..", "..########..", "..########..",
            "..########..", "..########..", "..########..", "..########..", "............", "............"]),
 "pause": m(["............", ".###....###.", ".###....###.", ".###....###.", ".###....###.", ".###....###.",
             ".###....###.", ".###....###.", ".###....###.", ".###....###.", ".###....###.", "............"]),
 "lock": m(['...#####...', '..##...##..', '.##.....##.', '.##.....##.', '.##.....##.', '###########', '###########', '####...####', '####...####', '#####.#####', '#####.#####', '###########', '###########']),
 "lvl_low": m(['....#####....', '..#########..', '.###.....###.', '.##.......##.', '##.........##', '##.........##', '##.........##', '##.........##', '##.#######.##', '.##.#####.##.', '.###.....###.', '..#########..', '....#####....']),
 "lvl_mid": m(['....#####....', '..#########..', '.###.....###.', '.##.......##.', '##.........##', '##.........##', '##.#######.##', '##.#######.##', '##.#######.##', '.##.#####.##.', '.###.....###.', '..#########..', '....#####....']),
 "lvl_max": m(['....#####....', '..#########..', '.###.....###.', '.##.#####.##.', '##.#######.##', '##.#######.##', '##.#######.##', '##.#######.##', '##.#######.##', '.##.#####.##.', '.###.....###.', '..#########..', '....#####....']),
}
# Rockbox themable_icons order, Icon_Audio .. Icon_Rockbox (32)
# Brightness shortcuts reuse slots the Classic never shows: 5 Firmware = Max, 27 Remote display = Low, 28 Radio = Mid
# Sleep (Now Playing context menu) uses 21 Recording: moon. 31 Main Menu reuses the playlist stack.
# Slots 0 (note), 4 (theme), 14 (trash) and 21 (moon) are drawn by hand
# straight into rpod-gilt.bmp: regenerating the iconset from this file would overwrite them.
ICONS = ["note", "folder", "list", "chevron", "play", "lvl_max", "dot", "gear", "gear", "dot", "ribbon", "sun",
         "note", "dot", "dot", "chevron", "dot", "gear", "chevron", "chevron", "gear", "moon", "dot", "gear",
         "gear", "play", "gear", "lvl_low", "lvl_mid", "folder", "gear", "list"]

S = {  # 11x11 top bar glyphs, drawn at offset 1 in 13x13
 "stop": m(["..........."] * 2 + ["..#######.."] * 7 + ["..........."] * 2),
 "play": m(["...........", "..##.......", "..####.....", "..######...", "..########.", "..#########",
            "..########.", "..######...", "..####.....", "..##.......", "..........."]),
 "pause": m(["..........."] + ["..###.###.."] * 9 + ["..........."]),
 "ffwd": m(["...........", "#....#.....", "##...##....", "###..###...", "####.####..", "##########.",
            "####.####..", "###..###...", "##...##....", "#....#.....", "..........."]),
 "shuffle": m(["...........", "........#..", "##....#####", "..#..#..#..", "...##......", "...##......",
               "..#..#..#..", "##....#####", "........#..", "...........", "..........."]),
 "repeat": m(["...........", "..######...", ".#......#..", "#.......###", "#........#.", "#..........",
              "..........#", ".#........#", "###.......#", "..#......#.", "...######.."]),
}
S["rew"] = {(10 - x, y) for x, y in S["ffwd"]}
S["one"] = S["repeat"] | {(5, 4), (5, 5), (5, 6), (4, 5)}
S["ab"] = m(["..........."] * 3 + [".##....###.", "#..#...#..#", "####...###.", "#..#...#..#", "#..#...###."] + ["..........."] * 3)


def edge(mask):
    return {(x, y) for x, y in mask if any((x + dx, y + dy) not in mask for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))}

def ring(mask):
    out = set()
    for x, y in mask:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if p not in mask:
                    out.add(p)
    return out

def render(mask, style, dim=False):
    """mask -> {pixel: colour} for one style."""
    px = {}
    if style == "outline":
        for p in edge(mask): px[p] = CREAM
    elif style == "solid":
        for p in mask: px[p] = CREAM
    elif style == "gilt":
        for p in ring(mask): px[p] = LOW
        for p in mask: px[p] = GOLD
        for x, y in mask:
            if (x - 1, y) not in mask or (x, y - 1) not in mask: px[(x, y)] = HI
    elif style == "stamp":
        for p in ring(mask): px[p] = CREAM
        for p in mask: px[p] = DARK
    elif style == "illuminated":
        for x, y in mask:
            if (x + 1, y + 1) not in mask: px[(x + 1, y + 1)] = RED
        for p in mask: px[p] = CREAM
    if dim:
        px = {p: tuple(c // 3 + 20 for c in col) for p, col in px.items()}
    return px

def strip(frames, w, h, style, off=None, dims=()):
    img = [[MAGENTA] * w for _ in range(h * len(frames))]
    for i, mask in enumerate(frames):
        o = off
        if o is None or w == 16:  # menu icons: centre the glyph in the 16x16 cell
            x0, x1 = min(x for x, _ in mask), max(x for x, _ in mask)
            y0, y1 = min(y for _, y in mask), max(y for _, y in mask)
            o = ((w - (x1 - x0 + 1)) // 2 - x0, (h - (y1 - y0 + 1)) // 2 - y0)
        for (x, y), col in render(mask, style, dim=i in dims).items():
            X, Y = x + o[0], y + o[1]
            if 0 <= X < w and 0 <= Y < h:
                img[i * h + Y][X] = col
    return img

def battery(level):
    shell = {(x, y) for x in range(1, 22) for y in (1, 11)} | {(x, y) for x in (1, 21) for y in range(1, 12)}
    shell |= {(22, y) for y in range(4, 9)} | {(23, y) for y in range(4, 9)}
    w = [0, 4, 8, 13, 17][level]  # full = 17 wide: a 1px gap to the shell on every side
    fill = {(x, y) for x in range(3, 3 + w) for y in range(3, 10)}
    return shell | fill

def save(img, path):
    h, w = len(img), len(img[0])
    with open(path, "wb") as f:
        f.write(f"P6 {w} {h} 255\n".encode())
        for row in img:
            for c in row: f.write(bytes(c))

def symmetric(mask, vertical=False):
    sx = min(x for x, _ in mask) + max(x for x, _ in mask)
    sy = min(y for _, y in mask) + max(y for _, y in mask)
    lr = mask == {(sx - x, y) for x, y in mask}
    return lr and (not vertical or mask == {(x, sy - y) for x, y in mask})

def check():
    for name in ("ribbon", "dot", "gear", "sun", "lvl_low", "lvl_mid", "lvl_max", "lock"):
        if not symmetric(G[name], vertical=name in ("gear", "sun", "dot")):
            raise SystemExit(f"glyph not symmetric: {name}")

def main(out):
    check()
    for style in ("outline", "solid", "gilt", "stamp", "illuminated"):
        d = os.path.join(out, style); os.makedirs(d, exist_ok=True)
        save(strip([G[n] for n in ICONS], 16, 16, style, (2, 2)), f"{d}/icons.ppm")
        # top bar state icons: same 16x16 cells and centring as the menu icons, so they line up
        modes = [G["stop"], G["play"], G["pause"], S["ffwd"], S["rew"]] + [G["dot"]] * 4
        save(strip(modes, 16, 16, style), f"{d}/playmodes.ppm")
        save(strip([battery(i) for i in range(5)], 25, 13, style), f"{d}/battery.ppm")
        save(strip([S["shuffle"], S["shuffle"]], 13, 13, style, (1, 1), dims={1}), f"{d}/shuffle.ppm")
        save(strip([S["repeat"], S["repeat"], S["one"], S["shuffle"], S["ab"]], 13, 13, style, (1, 1), dims={0}),
             f"{d}/repeat.ppm")

if __name__ == "__main__":
    main(sys.argv[1])
