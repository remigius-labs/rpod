#!/bin/bash
# Write pre-dithered, pre-sized covers next to each album's art, for the RPod theme:
#   cover.56x56.bmp (menu player) and cover.100x100.bmp (Now Playing), 32 colours so they stay readable.
# Rockbox picks these by size when "album art: prefer image file" is set.
# Only adds files; never touches audio or the original cover.
#
#   ./dither-covers.sh <music dir>            dry run: lists what it would write
#   ./dither-covers.sh <music dir> --write    writes the files
set -euo pipefail
ROOT=${1:?usage: dither-covers.sh <music dir> [--write]}
WRITE=${2:-}
SIZES="56 100"

albums=0; written=0; skipped=0
while IFS= read -r -d '' src; do
    dir=$(dirname "$src")
    albums=$((albums + 1))
    for s in $SIZES; do
        out="$dir/cover.${s}x${s}.bmp"
        if [ -e "$out" ]; then skipped=$((skipped + 1)); continue; fi
        if [ "$WRITE" = "--write" ]; then
            magick "$src" -resize "${s}x${s}^" -gravity center -extent "${s}x${s}" +repage \
                -modulate 100,85 -dither FloydSteinberg -colors 32 \
                -type TrueColor "BMP3:$out"
        else
            echo "would write: $out"
        fi
        written=$((written + 1))
    done
done < <(find "$ROOT" -type f \( -iname cover.jpg -o -iname cover.jpeg -o -iname cover.png -o -iname folder.jpg \) -print0)

verb=$([ "$WRITE" = "--write" ] && echo "written" || echo "to write")
echo "$albums album covers found · $written files $verb · $skipped already there"
