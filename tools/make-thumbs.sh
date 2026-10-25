#!/bin/bash
# Make the album covers RPod shows while browsing: a cover.32x32.bmp (album rows), cover.56x56.bmp
# (menu player panel) and cover.80x80.bmp (Now Playing) in every album folder.
#
#   make-thumbs.sh <Artists folder> <staging folder>
#
# Albums are <Artists>/<artist>/<album>/. The art comes from a cover image in the folder
# (cover.jpg, folder.jpg, front.jpg, cover.png) or else from the first song's embedded art.
# Thumbnails go into the staging folder, in the same folder layout, so nothing on the iPod is
# touched. Copy them over afterwards with only the thumbnails included:
#
#   rsync -rtm --include='*/' --include='cover.*x*.bmp' --exclude='*' <staging>/ <Artists>/
#
# Needs ImageMagick (magick) and ffmpeg.
set -u
SRC=${1:?Artists folder}
OUT=${2:?staging folder}
SIZES="32 56 80"

total=$(find "$SRC" -mindepth 2 -maxdepth 2 -type d | wc -l)
i=0; made=0; none=0
while IFS= read -r album; do
    i=$((i + 1))
    rel=${album#"$SRC"/}
    dest="$OUT/$rel"
    mkdir -p "$dest"
    art="$dest/.art.png"
    cover=$(find "$album" -maxdepth 1 -type f \( -iname 'cover.jpg' -o -iname 'cover.jpeg' -o -iname 'folder.jpg' \
             -o -iname 'front.jpg' -o -iname 'cover.png' \) | head -1)
    if [ -n "$cover" ]; then
        magick "$cover[0]" "$art" 2>/dev/null
    else
        song=$(find "$album" -maxdepth 1 -type f \( -iname '*.mp3' -o -iname '*.flac' -o -iname '*.m4a' -o -iname '*.ogg' \) | sort | head -1)
        [ -n "$song" ] && ffmpeg -v quiet -y -i "$song" -an -frames:v 1 "$art" 2>/dev/null
    fi
    if [ -s "$art" ]; then
        for n in $SIZES; do
            magick "$art" -strip -resize "${n}x${n}!" -colors 32 -dither FloydSteinberg -type TrueColor "BMP3:$dest/cover.${n}x${n}.bmp"
        done
        made=$((made + 1))
    else
        none=$((none + 1))
        echo "no art: $rel" >> "$OUT/no-art.txt"
    fi
    rm -f "$art"
    [ $((i % 25)) -eq 0 ] && printf '%3d%%  %d/%d\n' $((i * 100 / total)) "$i" "$total"
done < <(find "$SRC" -mindepth 2 -maxdepth 2 -type d | sort)
echo "covers for $made albums, $none without art (see $OUT/no-art.txt)"
