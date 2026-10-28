# RPod

Rockbox for the iPod Classic (6th/7th gen), modernized around one art style: a dithered painting of
a hermit, with gold gilt icons, titles and selection drawn to match. RPod has one look, and every
screen is built for it.

![RPod on an iPod Classic](media/rpod.gif)

## The look

- **The painting.** A dithered monk painting sits behind every menu. The boot splash shows it full
  screen with the RPOD logo at 3x; shutdown shows it dimmed with the message in gilt.
- **Gilt.** Icons are gold, drawn pixel by pixel. Menu titles are drawn like the logo: dark rim,
  gold body, lit top-left edge.
- **The selected row.** A see-through gold wash, so the painting shows through the row you are on.
  The text is letterpressed, with a soft lit edge under each letter.
- **Now Playing.** One gilt panel: the song on top, the cover with album, artist and time beside
  it, a thin progress bar below. Turning the wheel swaps the time for the volume. The menus keep a
  small player panel under the list while something plays.
- **Popups, yes/no questions and the quick screen.** These darken the painting to the same tint as
  the top bar. The question is gilt, the choices cream, and long lines wrap at a sentence end.
- **Busy screens.** The whole area darkens and a gilt progress bar fills.
- **Scrollbar.** Gilt, spanning the whole list, lined up with the battery and the mode icons.

## What changed from stock Rockbox

About 1,100 lines of C on top of stock Rockbox. Release by release: `CHANGELOG.md`.

**Browsing**
- Album cards: open an artist under `/Artists` and every album shows as a card with its cover and
  name. An album without art gets the monk. Only the rows on screen load their cover, and a few
  stay cached. "All Songs" is pinned first.
- Bookmarks as cards: cover, book name and time.
- Files: a gilt icon for every kind of file. A playlist opened here shows its songs, and play
  starts from the song you pick.
- Files and Playlists from the main menu always open at the top, never in the last folder or
  playlist you were in.
- Every song in a playlist has the note icon.

**Volume**
- Volume reads 0 to 100, in even steps: every click moves it the same amount.
- The volume bar is full at 100.
- The volume limit is fixed at 0 dB, so the headphone output stays at a sane level.

**Menus**
- Main menu, Settings and the Now Playing menu trimmed to six items each, with the icons lined up
  row by row across them.
- Sleep in the Now Playing menu: 15, 30 or 60 minutes, or End of track, which pauses when the
  current file ends (one file per chapter makes it "end of chapter" for audiobooks).
- Brightness gets its own shortcut folder: Low, Mid, Max.
- Repeat is Off, All or One. Shorter menu names through a custom language file.

**Small things**
- Song titles on screen drop remaster notes: "Song (2011 Remaster)" shows "Song". Files and tags
  stay as they are.
- A line still scrolling from the previous screen stops before the next one draws.
- The selected row keeps its highlight after the list wraps around.
- The shutdown screen no longer crashes.

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
