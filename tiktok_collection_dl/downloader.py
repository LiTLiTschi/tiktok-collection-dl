from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Collection title helpers
# ---------------------------------------------------------------------------

def get_collection_title(url: str) -> Optional[str]:
    """
    Ask yt-dlp for the collection title without downloading anything.
    Fetches only the first item metadata via --flat-playlist.
    TikTok collections are exposed as playlists in yt-dlp, so
    %(playlist_title)s is the correct field.
    """
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-items", "1",
        "--print", "%(playlist_title)s",
        "--no-warnings",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        lines = result.stdout.strip().splitlines()
        title = lines[0].strip() if lines else None
        # yt-dlp prints "NA" when the field is unavailable
        return title if title and title.upper() != "NA" else None
    except FileNotFoundError:
        return None


def sanitize_folder_name(name: str) -> str:
    """
    Strip characters that are illegal in Windows / Linux folder names
    and trim whitespace.
    """
    name = re.sub(r'[<>:"/\\|?*]', "", name)   # Windows forbidden chars
    name = re.sub(r"[\x00-\x1f]", "", name)      # control characters
    name = re.sub(r"\s+", " ", name).strip()      # collapse whitespace
    return name or "collection"


# ---------------------------------------------------------------------------
# Command builder
# ---------------------------------------------------------------------------

def build_command(url: str, out_dir: Path, cfg: Dict[str, Any]) -> List[str]:
    cmd = [
        "yt-dlp",
        "--format",           "bestaudio/best",
        "--extract-audio",
        "--audio-format",     cfg["audio_format"],
        "--audio-quality",    str(cfg["audio_quality"]),
        "--output",           str(out_dir / cfg["output_template"]),
        "--download-archive", str(out_dir / ".yt-dlp-archive.txt"),
        "--console-title",
    ]
    if cfg.get("no_overwrites"):
        cmd.append("--no-overwrites")
    if cfg.get("ignore_errors"):
        cmd.append("--ignore-errors")
    if cfg.get("extra_yt_dlp_args"):
        cmd.extend(cfg["extra_yt_dlp_args"])
    cmd.append(url)
    return cmd


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(url: str, base_out_dir: Path, cfg: Dict[str, Any]) -> int:
    # Resolve the actual output directory
    if cfg.get("use_collection_folder"):
        print("[tiktok-collection-dl] Fetching collection title...")
        title = get_collection_title(url)
        if title:
            folder_name = sanitize_folder_name(title)
            out_dir = base_out_dir / folder_name
            print(f"[tiktok-collection-dl] Collection : {title!r}")
            print(f"[tiktok-collection-dl] Subfolder  : {folder_name}")
        else:
            out_dir = base_out_dir
            print("[tiktok-collection-dl] Warning: could not determine collection title, "
                  "falling back to base output dir.")
    else:
        out_dir = base_out_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_command(url, out_dir, cfg)

    print(f"[tiktok-collection-dl] Output dir : {out_dir}")
    print(f"[tiktok-collection-dl] Archive    : {out_dir / '.yt-dlp-archive.txt'}")
    print(f"[tiktok-collection-dl] Command    : {' '.join(cmd)}\n")

    try:
        return subprocess.run(cmd, check=False).returncode
    except FileNotFoundError:
        print("[ERROR] yt-dlp not found — is it on your PATH?", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[tiktok-collection-dl] Stopped by user.")
        return 130
