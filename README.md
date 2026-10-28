# RPod

A Rockbox fork and theme for the iPod Classic (6th/7th gen), built around a painting.

![RPod on an iPod Classic](media/rpod.gif)

## What it is

**The theme (Hermit).** A dithered painting behind every menu, gold gilt icons drawn pixel by pixel,
gilt menu titles in the same style as the RPOD logo, and a see-through gold selection so the
painting shows through the row you are on. Now Playing is one gilt panel: the song on top, the cover
with album, artist and time beside it, a thin progress bar below. The menu keeps a small player
panel under the list while something plays.

**The firmware changes.** About 1,100 lines of C on top of stock Rockbox (what changed when: `CHANGELOG.md`):

- Album covers while browsing: open an artist's folder and every album row shows its cover in a
  gilt frame, the name beside it. Only the rows on screen load their cover, a few stay cached, and
  an album without art gets a small default card. An artist's "All Songs" playlist is pinned first.
- Volume as 0 to 100 in even steps, the bar full at 100, the limit fixed at 0 dB.
- Files and Playlists from the main menu always open at the top. A playlist opened in Files shows
  its songs, each with the note icon.
- Bookmarks as cards (cover, book name, time) and gilt icons for every kind of file.
- Sleep in the Now Playing menu: 15 / 30 / 60 minutes, or End of track, which pauses when the
  current file ends (one file per chapter makes it "end of chapter" for audiobooks).
- Prompts and popups on the darkened painting: yes/no questions, the quick screen and messages draw
  on the same dark tint as the top bar, with the question gilt and the choices in cream.
- A boot splash and a shutdown screen in the same style.
- Remaster notes dropped from song titles on screen ("Song (2011 Remaster)" shows "Song"). The files
  and tags are untouched.
- Menus trimmed to six items each (main menu, Settings, Now Playing menu), with the icons lined up
  row by row across them. Repeat is Off / All / One.
- Two list fixes: a line still scrolling from the previous screen no longer draws over the next one,
  and the selected row keeps its highlight after the list wraps around.

## Install

You need an iPod Classic already running Rockbox (bootloader installed).

1. Build the firmware (below) or use a release zip, and copy its `.rockbox` folder onto the iPod.
2. Install the Rockbox font pack (the theme uses its Terminus and Nimbus fonts).
3. Copy `theme/.rockbox/` onto the iPod's `.rockbox/` folder.
4. On the iPod: Settings > Theme > Browse Theme Files > Hermit.
5. For album covers while browsing, run `tools/make-thumbs.sh` on your music folder and copy the
   thumbnails over. Albums are expected as `Artists/<artist>/<album>/`.

Back up the iPod's `.rockbox` folder first. The bootloader is never touched.

## Build the firmware

The patch applies to Rockbox commit `59cc0282ec38919e22b7448d0f24c0713da4c21e`.

```sh
git clone https://git.rockbox.org/cgit/rockbox.git
cd rockbox
git checkout 59cc0282ec38919e22b7448d0f24c0713da4c21e
git apply ../rpod/firmware/rpod.patch
# ARM toolchain: tools/rockboxdev.sh, then:
mkdir build-ipod6g && cd build-ipod6g
../tools/configure --target=29 --type=n
make -j8 && make zip
```

The custom language file (shorter menu names) builds with `make $PWD/apps/lang/remi.lng` inside the
build folder; a prebuilt one is in `theme/.rockbox/langs/`.

## Tools

Design tools used to make the theme, in `tools/`. They expect a Rockbox simulator build; set
`RPOD_SIM` to its folder (default `../../rockbox/build-sim`).

- `editor/`: a local pixel editor for the logo and icons, with a live preview of the menu they sit in
  (`python3 editor/server.py`, then http://127.0.0.1:8765).
- `icons.py`, `usb-medallion.py`, `mock.py`, `rbfont.py`: icon set, USB screen, offline screen mocks
  drawn with the real Rockbox fonts.
- `make-thumbs.sh`: the album cover thumbnails.
- `take.sh`: records a scripted run through the simulator in a hidden X display (the GIF above).

## Limits

- Built and tested on the iPod Classic 7th gen (Rockbox target ipod6g), 320x240 only.
- Albums split into CD 1 / CD 2 folders do not show a cover in the album rows yet.
- The theme's colours are tuned for the iPod screen; the simulator looks brighter.

## License

- Firmware patch and tools: GPL-2.0, like Rockbox (see `LICENSE`).
- Theme: CC BY-SA 3.0, starting from a theme by Guillaume Cocatre-Zilgien (see `theme/LICENSE`).
