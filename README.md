# tiktok-collection-dl

Download TikTok collections as best-quality audio via **yt-dlp** — installable Python CLI with YAML config support.

## Install

```powershell
git clone https://github.com/LiTLiTschi/tiktok-collection-dl.git
cd tiktok-collection-dl
pip install -e .
```

## Usage

```
tiktok-collection-dl <collection_url> [output_dir] [options]
```

**Examples:**

```powershell
# Download to current directory
tiktok-collection-dl "https://www.tiktok.com/@user/collection/..."

# Download to a specific folder
tiktok-collection-dl "https://www.tiktok.com/@user/collection/..." "D:\Music\TikTok"

# Override format/quality
tiktok-collection-dl "https://www.tiktok.com/@user/collection/..." --audio-format opus --audio-quality 0

# Batch mode — read URLs from list.txt in the output folder
tiktok-collection-dl "D:\Music\TikTok"
```

## Config File

Drop a `tiktok_collection_dl_config.yaml` in any of these locations (higher = higher priority):

| Priority | Path |
|---|---|
| 1 (highest) | `./tiktok_collection_dl_config.yaml` |
| 2 | `./.config/tiktok_collection_dl_config.yaml` |
| 3 (global) | `~/.config/tiktok_collection_dl_config.yaml` |
| CLI flags | override everything |

All configs are merged — local files only need to override what differs.

**Example config:**

```yaml
audio_format: mp3
audio_quality: "0"               # V0 ~245 kbps VBR (best)
output_template: "%(playlist_index)s - %(title)s.%(ext)s"
ignore_errors: true
no_overwrites: true
use_collection_folder: false     # create a subfolder named after each collection
default_output_dir: "D:/Music/TikTok"
extra_yt_dlp_args: []
```

## Batch mode (list.txt)

Create a `list.txt` file in your output directory with one TikTok collection URL per line.
Lines starting with `#` are treated as comments and skipped.

```
# My TikTok collections
https://www.tiktok.com/@user/collection/Name-123456789
https://www.tiktok.com/@otheruser/collection/Name-987654321
```

Then run with just the output directory — the script reads the list automatically:
```powershell
tiktok-collection-dl "D:\Music\TikTok"
```

## Collection folder mode

When `use_collection_folder: true`, a subfolder named after each collection is automatically
created inside the output directory. Each collection gets its own folder and its own
`.yt-dlp-archive.txt` skip list.

```
D:\Music\TikTok\
└── Dance Hits\
    ├── 01 - Track Name.mp3
    └── .yt-dlp-archive.txt
```

## Skip logic

A hidden `.yt-dlp-archive.txt` file is kept inside the output (or collection) folder.
yt-dlp records every downloaded video ID there, so re-running safely skips already-downloaded tracks.

## Requirements

- Python 3.9+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) on your PATH
- [pyyaml](https://pypi.org/project/PyYAML/)
