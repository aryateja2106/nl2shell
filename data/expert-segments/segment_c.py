"""
Expert-quality NL-to-shell pairs — Segment C.

Categories:
  1. Advanced macOS (pmset, spctl, codesign, profiles, log show, xattr, sips, mdls, tmutil)
  2. Media Processing (ffmpeg, ImageMagick, sox, yt-dlp, ghostscript/qpdf/pdftk)
  3. Regex & Pattern Matching (grep -P, sed, awk, perl one-liners, named captures)
  4. Environment & Shell Config (.zshrc, PATH, alias, trap, set options, history)

No overlap with expert_pairs.py (which covers: stderr/stdout, human-readable output,
pipe mastery, process substitution, xargs/find, macOS basics, one-liners, JSON/API,
git, docker, network/security, text processing, modern CLI tools, sysadmin,
dev workflow).
"""

PAIRS: list[tuple[str, str]] = [
    # =========================================================================
    # ADVANCED MACOS — pmset, spctl, codesign, profiles, log show, xattr,
    # sips, mdls, tmutil  (20 pairs)
    # =========================================================================

    # pmset — power management
    (
        "show current power management settings",
        "pmset -g",
    ),
    (
        "prevent display sleep when on AC power",
        "sudo pmset -c displaysleep 0",
    ),
    (
        "set battery-only sleep to 10 minutes",
        "sudo pmset -b sleep 10",
    ),
    (
        "show power management assertion reasons why sleep is blocked",
        "pmset -g assertions",
    ),
    (
        "check what woke the Mac from sleep last time",
        "pmset -g log | grep -E 'Wake|Sleep' | tail -20",
    ),

    # spctl / codesign — security and code signing
    (
        "check if a binary is allowed by Gatekeeper",
        "spctl --assess --verbose /Applications/SomeApp.app",
    ),
    (
        "show code signing details of an application",
        "codesign -dvv /Applications/SomeApp.app 2>&1",
    ),
    (
        "verify the code signature of a binary is intact",
        "codesign --verify --strict --verbose=2 /usr/local/bin/mytool",
    ),
    (
        "sign a binary with your developer identity",
        "codesign --force --sign 'Developer ID Application: Acme Corp' /path/to/binary",
    ),
    (
        "show all Gatekeeper rules currently in effect",
        "spctl --list",
    ),

    # log show — unified logging
    (
        "show kernel logs from the last 5 minutes",
        "log show --predicate 'process == \"kernel\"' --last 5m --style compact",
    ),
    (
        "stream live system log filtered to a subsystem",
        "log stream --predicate 'subsystem == \"com.apple.network\"' --level debug",
    ),
    (
        "find recent crashes for a specific process",
        "log show --predicate 'process == \"Safari\" AND messageType == fault' --last 1h",
    ),

    # xattr — extended attributes
    (
        "list all extended attributes on a file",
        "xattr -l ~/Downloads/SomeApp.dmg",
    ),
    (
        "remove quarantine flag from a downloaded file",
        "xattr -d com.apple.quarantine ~/Downloads/SomeApp.dmg",
    ),
    (
        "strip all extended attributes from a directory recursively",
        "xattr -cr ~/Downloads/untrusted_folder",
    ),

    # sips / mdls — image metadata
    (
        "resize an image to 800px wide preserving aspect ratio",
        "sips --resampleWidth 800 photo.jpg",
    ),
    (
        "batch convert all PNGs to JPEG in current directory",
        "sips -s format jpeg *.png --out converted/",
    ),
    (
        "show all metadata for an image file",
        "mdls photo.jpg",
    ),

    # tmutil — Time Machine
    (
        "start an immediate Time Machine backup",
        "tmutil startbackup --auto --rotation",
    ),
    (
        "list all Time Machine snapshot dates",
        "tmutil listbackups",
    ),
    (
        "show how much data changed since the last backup",
        "tmutil compare -n | tail -5",
    ),

    # =========================================================================
    # MEDIA PROCESSING — ffmpeg, ImageMagick, sox, yt-dlp, PDF tools (20 pairs)
    # =========================================================================

    # ffmpeg
    (
        "trim a video from 00:01:30 to 00:04:00 without re-encoding",
        "ffmpeg -ss 00:01:30 -to 00:04:00 -i input.mp4 -c copy trimmed.mp4",
    ),
    (
        "extract audio track from a video as mp3",
        "ffmpeg -i video.mp4 -vn -ar 44100 -ac 2 -b:a 192k audio.mp3",
    ),
    (
        "convert a video to a gif with palette optimization",
        "ffmpeg -i input.mp4 -vf 'fps=15,scale=640:-1:flags=lanczos,palettegen' palette.png && ffmpeg -i input.mp4 -i palette.png -filter_complex 'fps=15,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse' output.gif",
    ),
    (
        "concatenate multiple mp4 files seamlessly",
        "printf 'file %s\\n' clip1.mp4 clip2.mp4 clip3.mp4 > filelist.txt && ffmpeg -f concat -safe 0 -i filelist.txt -c copy merged.mp4",
    ),
    (
        "extract a single frame from video at timestamp",
        "ffmpeg -ss 00:02:15 -i video.mp4 -frames:v 1 -q:v 2 frame.jpg",
    ),
    (
        "reduce video bitrate for web streaming",
        "ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset slow -acodec aac -b:a 128k web.mp4",
    ),
    (
        "add subtitles from srt file to video",
        "ffmpeg -i video.mp4 -vf subtitles=subs.srt output_with_subs.mp4",
    ),

    # ImageMagick
    (
        "convert and compress a TIFF to JPEG with 85 quality",
        "convert input.tiff -quality 85 output.jpg",
    ),
    (
        "batch watermark all images in a directory",
        "mogrify -draw \"text 10,30 'Copyright 2026'\" -font Helvetica -pointsize 20 -fill 'rgba(255,255,255,0.5)' *.jpg",
    ),
    (
        "create a contact sheet thumbnail grid from images",
        "montage *.jpg -geometry 200x150+4+4 -tile 4x contactsheet.jpg",
    ),
    (
        "strip all EXIF metadata from images in place",
        "mogrify -strip *.jpg",
    ),

    # sox — audio processing
    (
        "convert wav to mp3 using sox and lame",
        "sox input.wav -t mp3 output.mp3",
    ),
    (
        "trim an audio file to keep seconds 30 through 90",
        "sox input.wav output.wav trim 30 60",
    ),
    (
        "normalize audio volume to prevent clipping",
        "sox --norm input.wav normalized.wav",
    ),
    (
        "split audio file on silence for track detection",
        "sox input.wav output.wav silence 1 0.1 0.1% 1 3.0 0.1% : newfile : restart",
    ),

    # yt-dlp
    (
        "download a YouTube video as best quality mp4",
        "yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' -o '%(title)s.%(ext)s' 'https://youtu.be/VIDEO_ID'",
    ),
    (
        "extract only audio from a YouTube playlist as mp3",
        "yt-dlp -x --audio-format mp3 --audio-quality 0 -o '%(playlist_index)02d - %(title)s.%(ext)s' 'https://www.youtube.com/playlist?list=PLAYLIST_ID'",
    ),
    (
        "download subtitles for a video without downloading video",
        "yt-dlp --skip-download --write-subs --sub-lang en 'https://youtu.be/VIDEO_ID'",
    ),

    # PDF tools
    (
        "merge multiple PDFs into one with ghostscript",
        "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=merged.pdf part1.pdf part2.pdf part3.pdf",
    ),
    (
        "extract pages 3 through 7 from a PDF using qpdf",
        "qpdf --empty --pages input.pdf 3-7 -- extracted.pdf",
    ),
    (
        "split a PDF into one file per page",
        "qpdf --split-pages input.pdf page_%d.pdf",
    ),

    # =========================================================================
    # REGEX & PATTERN MATCHING — grep -P, sed, awk, perl, named captures (20 pairs)
    # =========================================================================

    # grep -P (PCRE)
    (
        "extract all IPv4 addresses from a file using PCRE",
        "grep -oP '(?<![0-9])(?:[0-9]{1,3}\\.){3}[0-9]{1,3}(?![0-9])' file.txt | sort -u",
    ),
    (
        "match lines containing a word boundary with PCRE",
        "grep -P '\\bfoo\\b' file.txt",
    ),
    (
        "find lines where a number is followed by specific text using lookahead",
        "grep -P '[0-9]+(?= errors found)' build.log",
    ),
    (
        "extract content inside double quotes using named capture",
        "grep -oP '\"(?P<value>[^\"]+)\"' config.json | grep -oP '(?<=\")[^\"]+(?=\")'",
    ),
    (
        "match lines that do NOT contain any digit",
        "grep -P '^[^0-9]+$' file.txt",
    ),
    (
        "extract function call arguments using PCRE",
        "grep -oP 'connect\\(\\K[^)]+' db.py",
    ),

    # sed with complex regex
    (
        "replace only the second occurrence of a pattern on each line",
        "sed 's/foo/bar/2' file.txt",
    ),
    (
        "delete lines between two inclusive patterns",
        "sed '/BEGIN/,/END/d' file.txt",
    ),
    (
        "insert a line before a pattern match",
        "sed '/^server {/i\\    # managed block' nginx.conf",
    ),
    (
        "append text after a matching line",
        "sed '/listen 80/a\\    listen 443 ssl;' nginx.conf",
    ),
    (
        "extract a capture group using sed extended regex",
        "sed -nE 's/.*version[[:space:]]+([0-9.]+).*/\\1/p' Makefile",
    ),

    # awk pattern matching
    (
        "print lines where field 3 is greater than 1000",
        "awk '$3 > 1000' metrics.txt",
    ),
    (
        "print lines between pattern start and end inclusive",
        "awk '/^START$/,/^END$/' logfile.txt",
    ),
    (
        "sum field 2 only for lines matching a pattern",
        "awk '/ERROR/ {sum += $2} END {print sum}' app.log",
    ),
    (
        "reformat columns rearranging field order",
        "awk -F',' '{print $3, $1, $2}' OFS='|' data.csv",
    ),

    # perl one-liners
    (
        "in-place replace with perl across multiple files",
        "perl -pi -e 's/old_api_endpoint/new_api_endpoint/g' **/*.ts",
    ),
    (
        "extract and print a named capture group with perl",
        "perl -nE 'say $+{host} if /host=(?<host>[\\w.]+)/' config.txt",
    ),
    (
        "delete lines matching a pattern in-place with perl",
        "perl -ni -e 'print unless /^#/' config.py",
    ),
    (
        "use perl lookahead to match word not followed by suffix",
        "perl -nE 'say if /foo(?!bar)/' file.txt",
    ),
    (
        "transliterate characters in-place with perl",
        "perl -pi -e 'tr/a-z/A-Z/' file.txt",
    ),
    (
        "use perl to join continuation lines ending with backslash",
        "perl -0777 -pe 's/\\\\\n//g' Makefile",
    ),

    # =========================================================================
    # ENVIRONMENT & SHELL CONFIG — .bashrc/.zshrc, PATH, alias, trap,
    # shell options, history  (20 pairs)
    # =========================================================================

    # PATH manipulation
    (
        "prepend a directory to PATH for the current session only",
        "export PATH=\"/usr/local/opt/ruby/bin:$PATH\"",
    ),
    (
        "add a directory to PATH permanently in zsh",
        "echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.zshrc && source ~/.zshrc",
    ),
    (
        "remove a specific entry from PATH without restarting shell",
        "export PATH=$(echo \"$PATH\" | tr ':' '\\n' | grep -v '/usr/local/opt/old' | tr '\\n' ':' | sed 's/:$//')",
    ),
    (
        "show all directories in PATH one per line",
        "echo \"$PATH\" | tr ':' '\\n'",
    ),
    (
        "check which binary in PATH would run for a command",
        "type -a python3",
    ),

    # alias / function definitions
    (
        "define a persistent alias in zsh",
        "echo \"alias ll='ls -lAh --color=auto'\" >> ~/.zshrc && source ~/.zshrc",
    ),
    (
        "define a shell function to make and enter a directory",
        "mkcd() { mkdir -p \"$1\" && cd \"$1\"; }",
    ),
    (
        "define a function to activate a python venv if it exists",
        "activate() { [[ -f .venv/bin/activate ]] && source .venv/bin/activate || echo 'no .venv found'; }",
    ),
    (
        "unset an alias that is shadowing a system command",
        "unalias ls",
    ),
    (
        "list all currently defined shell functions",
        "declare -f",
    ),

    # trap handlers
    (
        "run cleanup function on script exit regardless of success",
        "trap 'rm -f /tmp/lockfile.$$; echo cleaned up' EXIT",
    ),
    (
        "catch SIGINT in a script and exit gracefully",
        "trap 'echo; echo \"Interrupted — exiting\"; exit 130' INT",
    ),
    (
        "re-enable default SIGPIPE handling after suppressing it",
        "trap '' PIPE",
    ),
    (
        "print error line number on any command failure",
        "trap 'echo \"Error at line $LINENO\" >&2' ERR",
    ),

    # Shell option settings
    (
        "enable strict mode for safer scripting",
        "set -euo pipefail",
    ),
    (
        "enable debug tracing to see every command before execution",
        "set -x",
    ),
    (
        "disable glob expansion temporarily for a single command",
        "set -f; cp *.txt /tmp/; set +f",
    ),
    (
        "turn on extended globbing in zsh",
        "setopt EXTENDED_GLOB",
    ),

    # History management
    (
        "search zsh history interactively with fzf",
        "history 0 | fzf --tac --no-sort | awk '{$1=\"\"; print $0}' | xargs",
    ),
    (
        "append current session history to history file immediately",
        "history -a",
    ),
    (
        "increase zsh history size and avoid duplicates",
        "echo 'HISTSIZE=100000; SAVEHIST=100000; setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY' >> ~/.zshrc",
    ),
    (
        "show the last 20 commands with timestamps in bash",
        "HISTTIMEFORMAT='%F %T  ' history 20",
    ),
    (
        "clear the current shell history without touching the file",
        "history -c",
    ),
    (
        "re-execute the last command that started with a prefix",
        "!git",
    ),
    (
        "export a variable so all child processes inherit it",
        "export DATABASE_URL='postgresql://user:pass@localhost:5432/mydb'",
    ),
    (
        "source a .env file into the current shell safely",
        "set -a && source .env && set +a",
    ),
]

# Sanity check at import time
assert len(PAIRS) >= 80, f"Expected >= 80 pairs, got {len(PAIRS)}"
