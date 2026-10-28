#!/bin/sh
# Builds the one-zip RPod release from a Rockbox build folder with the RPod patch applied:
# stock zip, stock themes out, RPod theme, fonts and settings in.
# Usage: tools/make-release.sh <build-ipod6g folder> <fonts folder> <out.zip>
set -eu
build=$(realpath "$1"); fonts=$(realpath "$2"); out=$(realpath "$3")
repo=$(cd "$(dirname "$0")/.." && pwd)
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

(cd "$build" && make zip >/dev/null)
cd "$stage"
unzip -q "$build/rockbox.zip"
r=.rockbox
rm -rf "$r/themes/cabbiev2.cfg" "$r/themes/rockbox_default_icons.cfg" \
       "$r/wps/cabbiev2.wps" "$r/wps/cabbiev2" \
       "$r/wps/classic_statusbar.sbs" "$r/wps/classic_statusbar.rsbs" "$r/wps/classic_statusbar" \
       "$r/backdrops/cabbiev2.bmp" "$r/fonts/15-Adobe-Helvetica.fnt"
cp -r "$repo/theme/.rockbox/." "$r/"
for f in 14-Nimbus 14-Terminus 16-Terminus 16-Terminus-Bold 20-Terminus-Bold 22-Terminus-Bold; do
    cp "$fonts/$f.fnt" "$r/fonts/"
done
cat "$r/themes/Hermit.cfg" "$r/rpod.cfg" > "$r/config.cfg"
rm "$r/rpod.cfg"
cp "$repo/theme/LICENSE" "$r/RPOD-THEME-LICENSE.txt"
rm -f "$out"
zip -qr9 "$out" .rockbox
echo "$out"
