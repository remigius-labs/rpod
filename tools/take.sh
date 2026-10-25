#!/bin/bash
# One recorded run through RPod in an invisible sim (Xvfb :99), driven by scripted key presses.
# Output: 320x240 lossless, 30 fps. Nothing touches the real screen or keyboard.
# The route: black, boot, menu, Files > Artists > All Them Witches, the album covers, an album,
# a song, Now Playing, the menu with the player panel, stop, shut down.
set -u
export DISPLAY=:99
OUT=${1:-raw.mkv}
SIM=${RPOD_SIM:-$(cd "$(dirname "$0")/../../rockbox/build-sim" 2>/dev/null && pwd)}

ffmpeg -v quiet -y -f x11grab -framerate 30 -draw_mouse 0 -video_size 320x240 -i :99 \
       -c:v libx264rgb -crf 0 -preset ultrafast "$OUT" &
REC=$!
sleep 1.0                                   # a moment of black before the boot
(cd "$SIM" && SDL_VIDEODRIVER=x11 setsid -f ./rockboxui --nobackground >/dev/null 2>&1)
sleep 2.5
W=$(xdotool search --class rockboxui | head -1)
xdotool windowfocus "$W"

p()     { xdotool keydown --window "$W" "$1"; sleep 0.10; xdotool keyup --window "$W" "$1"; sleep "${2:-0.45}"; }
hold()  { xdotool keydown --window "$W" "$1"; sleep "$2"; xdotool keyup --window "$W" "$1"; sleep "${3:-0.6}"; }
glide() { local key=$1 n=$2 gap=${3:-0.4}; for _ in $(seq "$n"); do p "$key" "$gap"; done; }

sleep 1.4                                   # the main menu settles after the splash
glide Down 5 0.42; sleep 0.4                # down the menu, the gold over the dome
glide Up 1 0.6                              # back to Files
p Return 0.9                                # Files: Artists, Playlists
p Return 0.9                                # Artists
p Return 1.6                                # All Them Witches: All Songs, then the albums
glide Down 12 0.42; sleep 0.6               # down through every cover
glide Up 11 0.30; sleep 0.6                 # back up to A Sweet Release EP
p Return 1.4                                # the album's songs
p Return 5.0                                # play: Now Playing
p Escape 2.4                                # the main menu with the player panel
glide Down 2 0.5; glide Up 2 0.5; sleep 0.8
p Return 2.0                                # Now Playing once more
hold space 1.3 1.6                          # hold Play: stop
hold space 4.5 3.0                          # hold Play while stopped: gilt "Shutting down..."

kill -INT $REC; wait $REC 2>/dev/null
echo "recorded $OUT"
