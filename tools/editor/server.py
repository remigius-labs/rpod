#!/usr/bin/env python3
"""Local pixel editor for RPod theme art. http://127.0.0.1:8765

GET  /?asset=logo|frame|repeat|shuffle|repeat-one|moon   the editor page
GET  /asset?name=…        current pixels as {w, h, palette, cells} (cell = palette index, 0 = transparent)
GET  /backdrop            the menu backdrop as PNG, for the preview
GET  /cover               a dithered cover, for the frame preview
POST /save?name=…         {w, h, cells} -> BMP (+ PNG), into the sim theme, sim restarted
"""
import json, os, re, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.dirname(HERE)
SIM = os.environ.get("RPOD_SIM", os.path.join(ART, "..", "..", "rockbox", "build-sim"))
THEME = os.path.join(ART, "..", "theme", ".rockbox")
ROCKBOX = os.path.join(SIM, "simdisk", ".rockbox")
SBS = os.path.join(ROCKBOX, "wps", "Hermit.sbs")
MAGENTA = (0xff, 0x00, 0xff)
sys.path.insert(0, ART)
from icons import render  # the gilt style the icons use

ASSETS = {
    "logo": {"file": "rpod-logo-mask.bmp", "png": "rpod-logo.png", "sim": "rpod-logo.bmp", "out": "rpod-logo.bmp",
             "palette": [MAGENTA, (0xff, 0xf1, 0xdc)], "resizable": True, "gilt": True},
    "frame": {"file": "frame-window.bmp", "png": "frame-window.png", "sim": "frame.bmp",
              "palette": [MAGENTA, (0xff, 0xf1, 0xdc), (0x12, 0x0d, 0x0a)], "resizable": False},
    # repeat icon: a 13x13 mask is edited, saved gilded into a 16x16 cell (1px margin)
    "repeat": {"file": "icon-repeat-mask.bmp", "png": "icon-repeat.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
               "resizable": False, "cell": "repeat-icon.bmp"},
    "shuffle": {"file": "icon-shuffle-mask.bmp", "png": "icon-shuffle.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
                "resizable": False, "cell": "shuffle-icon.bmp"},
    "repeat-one": {"file": "icon-repeat-one-mask.bmp", "png": "icon-repeat-one.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
                   "resizable": False, "cell": "repeat-one-icon.bmp"},
    # sleep moon: gilded into slot 21 of the menu iconset (rpod-gilt.bmp, 16x16 cells)
    "moon": {"file": "icon-moon-mask.bmp", "png": "icon-moon.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
             "resizable": False, "slot": 21},
    # delete: slot 14 (Keyboard, only used for .kbd files in the browser)
    "delete": {"file": "icon-delete-mask.bmp", "png": "icon-delete.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
               "resizable": False, "slot": 14},
    # music note: slot 0 (Audio), shows on Sound and on every music file
    "note": {"file": "icon-note-mask.bmp", "png": "icon-note.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
             "resizable": False, "slot": 0},
    # theme: slot 4 (Wps), the Theme menu and skin files only
    "theme": {"file": "icon-theme-mask.bmp", "png": "icon-theme.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
              "resizable": False, "slot": 4},
    # files: slot 29 (Files in the main menu) and slot 1 (folders in the browser), kept the same
    "files": {"file": "icon-files-mask.bmp", "png": "icon-files.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
              "resizable": False, "slot": [29, 1]},
    # bookmark: slot 10 (Bookmarks in the main menu and the context menu)
    "bookmark": {"file": "icon-bookmark-mask.bmp", "png": "icon-bookmark.png", "palette": [MAGENTA, (0xff, 0xf1, 0xdc)],
                 "resizable": False, "slot": 10},
}


def nearest(rgb, palette):
    return min(range(len(palette)), key=lambda i: sum((a - b) ** 2 for a, b in zip(rgb, palette[i])))


def read_asset(name):
    a = ASSETS[name]
    ppm = subprocess.run(["magick", os.path.join(ART, a["file"]), "ppm:-"],
                         capture_output=True, check=True).stdout
    parts = ppm.split(maxsplit=4)
    w, h, data = int(parts[1]), int(parts[2]), parts[4]
    cells = [nearest(tuple(data[i * 3:i * 3 + 3]), a["palette"]) for i in range(w * h)]
    hexes = ["#%02x%02x%02x" % c for c in a["palette"]]
    return {"w": w, "h": h, "palette": hexes, "cells": cells, "resizable": a["resizable"]}


def restart_sim():
    subprocess.run(["pkill", "-x", "rockboxui"])
    for _ in range(40):
        if subprocess.run(["pgrep", "-x", "rockboxui"], capture_output=True).returncode:
            break
        time.sleep(0.25)
    time.sleep(0.5)
    env = dict(os.environ, SDL_VIDEODRIVER="x11")
    subprocess.Popen(["setsid", "-f", "./rockboxui", "--nobackground"], cwd=SIM, env=env,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def save_asset(name, w, h, cells):
    a = ASSETS[name]
    ppm = os.path.join(HERE, name + ".ppm")
    with open(ppm, "wb") as f:
        f.write(f"P6 {w} {h} 255\n".encode())
        f.write(b"".join(bytes(a["palette"][c]) for c in cells))
    subprocess.run(["magick", ppm, "-type", "TrueColor", "BMP3:" + os.path.join(ART, a["file"])], check=True)
    if a.get("slot") is not None:  # menu icon: gild the mask into its iconset cell
        mask = {(i % w, i // w) for i, c in enumerate(cells) if c}
        px = render(mask, "gilt")
        xs = [x for x, _ in px]; ys = [y for _, y in px]
        ox = 1 - min(xs)  # menu icons share a left edge at x=1, like the rest of the set
        oy = (16 - (max(ys) - min(ys) + 1)) // 2 - min(ys)
        iconset = os.path.join(THEME, "icons", "rpod-gilt.bmp")
        raw = bytearray(subprocess.run(["magick", iconset, "-depth", "8", "rgb:-"], capture_output=True, check=True).stdout)
        for slot in (a["slot"] if isinstance(a["slot"], list) else [a["slot"]]):
            y0 = slot * 16
            for y in range(16):
                for x in range(16):
                    c = px.get((x - ox, y - oy), MAGENTA)
                    i = ((y0 + y) * 16 + x) * 3
                    raw[i:i + 3] = bytes(c)
        with open(ppm, "wb") as f:
            f.write(f"P6 16 {len(raw) // 48} 255\n".encode())
            f.write(bytes(raw))
        subprocess.run(["magick", ppm, "-type", "TrueColor", "BMP3:" + iconset], check=True)
        subprocess.run(["cp", iconset, os.path.join(ROCKBOX, "icons", "rpod-gilt.bmp")], check=True)
        subprocess.run(["magick", os.path.join(ART, a["file"]), "-transparent", "#ff00ff", os.path.join(ART, a["png"])], check=True)
        restart_sim()
        return
    if a.get("cell"):  # icon: gild the mask into a 16x16 cell and put it in the theme
        mask = {(i % w, i // w) for i, c in enumerate(cells) if c}
        px = render(mask, "gilt")
        off = (16 - w) // 2
        with open(ppm, "wb") as f:
            f.write(b"P6 16 16 255\n")
            f.write(b"".join(bytes(px.get((x - off, y - off), MAGENTA)) for y in range(16) for x in range(16)))
        cell = os.path.join(ART, a["cell"])
        subprocess.run(["magick", ppm, "-type", "TrueColor", "BMP3:" + cell], check=True)
        subprocess.run(["cp", cell, os.path.join(ROCKBOX, "wps", "Hermit", a["cell"])], check=True)
        subprocess.run(["magick", os.path.join(ART, a["file"]), "-transparent", "#ff00ff", os.path.join(ART, a["png"])], check=True)
        restart_sim()
        return
    if a.get("gilt"):  # the mask is what gets edited; the theme gets it gilded
        mask = {(i % w, i // w) for i, c in enumerate(cells) if c}
        px = render(mask, "gilt")  # the dark rim reaches 1px past the mask, so add a 1px margin
        w, h = w + 2, h + 2
        with open(ppm, "wb") as f:
            f.write(f"P6 {w} {h} 255\n".encode())
            f.write(b"".join(bytes(px.get((i % w - 1, i // w - 1), MAGENTA)) for i in range(w * h)))
    bmp = os.path.join(ART, a.get("out", a["file"]))
    subprocess.run(["magick", ppm, "-type", "TrueColor", "BMP3:" + bmp], check=True)
    subprocess.run(["magick", bmp, "-transparent", "#ff00ff", os.path.join(ART, a["png"])], check=True)
    subprocess.run(["cp", bmp, os.path.join(ROCKBOX, "wps", "Hermit", a["sim"])], check=True)
    if name == "logo":  # keep the logo centred in the title bar at its new width
        sbs = open(SBS).read()
        sbs = re.sub(r"%Vl\(rlogo,\d+,\d+,\d+,\d+,-\)", f"%Vl(rlogo,{(320 - w) // 2},1,{w},{h},-)", sbs)
        open(SBS, "w").write(sbs)
    restart_sim()


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def png(self, path):
        out = subprocess.run(["magick", path, "png:-"], capture_output=True, check=True).stdout
        self.send(200, out, "image/png")

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        elif u.path == "/asset" and q.get("name", [""])[0] in ASSETS:
            self.send(200, json.dumps(read_asset(q["name"][0])).encode(), "application/json")
        elif u.path == "/backdrop":
            self.png(os.path.join(ROCKBOX, "backdrops", "hermit-menu.bmp"))
        elif u.path == "/menu":  # context menu as the iPod draws it (real font, real selection), moon cell left empty
            import mock
            sc = mock.Screen(os.path.join(ROCKBOX, "backdrops", "hermit-menu-bar.bmp"))
            iconset = os.path.join(THEME, "icons", "rpod-gilt.bmp")
            q = parse_qs(u.query)
            sel = int(q.get("sel", ["0"])[0])  # the row being drawn: selected, its icon left empty
            rows = [("Sleep", 21), ("Add to Playlist...", 2), ("Playback", 25), ("Bookmarks", 10), ("Sound", 0), ("Delete File", 14)]
            if q.get("menu", [""])[0] == "main":
                rows = [("Resume", 25), ("Bookmarks", 10), ("Playlists", 0), ("Brightness", 11), ("Files", 29), ("Settings", 20)]
            if q.get("menu", [""])[0] == "settings":
                rows = [("Playback", 25), ("Manage Settings", 8), ("Sound", 0), ("Theme", 4), ("Main Menu", 31), ("General", 23)]
            rows[sel] = (rows[sel][0], None)
            for i, (label, icon) in enumerate(rows):
                y = 29 + i * 22
                fg = (232, 217, 181)
                if i == sel:
                    sc.rect(0, y, 320, 22, mock.GOLD); sc.rect(0, y, 320, 1, mock.LOW); sc.rect(0, y + 1, 320, 1, mock.HI)
                    fg = mock.LOW
                if icon is not None:
                    sc.image(1, y + 1, iconset, (0, 16 * icon, 16, 16))
                sc.text(18, y, label, "22-Terminus-Bold.fnt", fg)
            path = os.path.join(HERE, "menu-preview.png")
            sc.save(path)
            self.send(200, open(path, "rb").read(), "image/png")
        elif u.path == "/iconset":  # magenta = transparent, like on the device
            out = subprocess.run(["magick", os.path.join(THEME, "icons", "rpod-gilt.bmp"), "-transparent", "#ff00ff", "png:-"],
                                 capture_output=True, check=True).stdout
            self.send(200, out, "image/png")
        elif u.path == "/cover":
            self.png(os.path.join(SIM, "simdisk", "Music", "1000mods", "Repeated exposure to", "cover.100x100.bmp"))
        else:
            self.send(404, b"not found", "text/plain")

    def do_POST(self):
        u = urlparse(self.path)
        name = parse_qs(u.query).get("name", [""])[0]
        if u.path != "/save" or name not in ASSETS:
            return self.send(404, b"not found", "text/plain")
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        w, h, cells = int(d["w"]), int(d["h"]), d["cells"]
        n = len(ASSETS[name]["palette"])
        if not (1 <= w <= 200 and 1 <= h <= 240 and len(cells) == w * h and all(0 <= c < n for c in cells)):
            return self.send(400, b"bad data", "text/plain")
        save_asset(name, w, h, cells)
        self.send(200, b'{"ok":true}', "application/json")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
