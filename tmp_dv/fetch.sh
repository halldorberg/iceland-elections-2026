#!/bin/sh
u="$1"
f="tmp_dv/articles/$(echo "$u" | sed 's|/eyjan/||; s|/|_|g').html"
[ -s "$f" ] && exit 0
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" "https://www.dv.is$u" -o "$f"
