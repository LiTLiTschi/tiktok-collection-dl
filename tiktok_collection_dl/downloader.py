from __future__ import annotations
import hashlib
import re
import shlex
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Archive path
# ---------------------------------------------------------------------------

def get_archive_path(out_dir: Path, url: str) -> Path:
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
    return out_dir / f".yt-dlp-archive-{url_hash}.txt"


# ---------------------------------------------------------------------------
# Collection info / folder name
# ---------------------------------------------------------------------------

_SUPPORTED_FIELDS = ("uploader", "playlist_title")
_DELIM = "|||"


def extract_title_from_tiktok_url(url: str) -> Optional[str]:
    """
    Extract and URL-decode the collection name from a TikTok collection URL.

    Format: https://www.tiktok.com/@username/collection/CollectionName-NumericID
    The numeric ID is always >= 10 digits, avoiding false matches on collection
    names that contain dashes followed by short numbers.

    Examples:
        .../collection/sample%3F-7543443541872102166  ->  'sample?'
        .../collection/Voice%20Samples-748497016...   ->  'Voice Samples'
    """
    match = re.search(r'/collection/(.+?)-(\d{10,})(?:[/?#]|$)', url)
    if match:
        decoded = urllib.parse.unquote(match.group(1))
        return decoded.strip() or None
    return None


def get_collection_info(url: str) -> Dict[str, Optional[str]]:
    """
    Fetch collection metadata.

    Title resolution order:
      1. URL extraction (primary) — always clean, no uploader prefix, works for
         private collections, no extra network call.
      2. yt-dlp metadata (fallback) — only used when URL extraction fails.

    Uploader is always fetched from yt-dlp (not available in URL).
    All values are URL-decoded.
    """
    info: Dict[str, Optional[str]] = {f: None for f in _SUPPORTED_FIELDS}

    # Step 1: title from URL — fast, reliable, no network call
    url_title = extract_title_from_tiktok_url(url)
    if url_title:
        info["playlist_title"] = url_title
        print(f"[tiktok-collection-dl] playlist_title (URL): {url_title!r}")

    # Step 2: yt-dlp for uploader + title fallback only
    print_template = _DELIM.join(f"%({f})s" for f in _SUPPORTED_FIELDS)
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-items", "1",
        "--print", print_template,
        "--no-warnings",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        parts = line.split(_DELIM)
        for i, field in enumerate(_SUPPORTED_FIELDS):
            raw = parts[i].strip() if i < len(parts) else ""
            if raw and raw.upper() != "NA":
                decoded = urllib.parse.unquote(raw)
                if field == "playlist_title" and info["playlist_title"]:
                    pass  # URL already gave us a clean title — skip yt-dlp's dirty version
                else:
                    info[field] = decoded
    except FileNotFoundError:
        pass

    return info


def strip_uploader_prefix(info: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Fallback strip for when URL extraction failed and yt-dlp baked uploader into title."""
    title    = info.get("playlist_title") or ""
    uploader = info.get("uploader") or ""
    if not (title and uploader):
        return info
    if title.lower().startswith(uploader.lower()):
        stripped = title[len(uploader):].lstrip("-_ ")
        if stripped:
            print(
                f"[tiktok-collection-dl] strip_uploader_from_collection_title: "
                f"{title!r} -> {stripped!r}"
            )
            info = dict(info)
            info["playlist_title"] = stripped
    return info


def apply_folder_template(template: str, info: Dict[str, Optional[str]]) -> str:
    result = template
    for field, value in info.items():
        result = result.replace(f"%({field})s", value or "")
    result = re.sub(r"%\([^)]+\)s", "", result)
    return sanitize_folder_name(result) or "collection"


def sanitize_folder_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"[\x00-\x1f]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


# ---------------------------------------------------------------------------
# Metadata flags
# ---------------------------------------------------------------------------

def metadata_flags(cfg: Dict[str, Any], album_name: Optional[str] = None) -> List[str]:
    """
    Build yt-dlp metadata flags from config.

    When embed_collection_as_album is True and we have a clean album_name,
    the album tag is injected directly into the ffmpeg audio extraction call
    via --postprocessor-args.  This bypasses yt-dlp's internal playlist_title
    which is often polluted with uploader prefix and percent-encoded characters.
    """
    flags: List[str] = []
    extra = cfg.get("extra_yt_dlp_args") or []

    if cfg.get("embed_collection_as_album"):
        if album_name:
            # Direct ffmpeg injection: clean Python-resolved title -> album tag.
            # Targets only FFmpegExtractAudio so it doesn't affect other ffmpeg calls.
            # shlex.quote handles spaces and special chars in the album name.
            album_kv = shlex.quote(f"album={album_name}")
            flags += [
                "--postprocessor-args",
                f"ffmpeg-FFmpegExtractAudio:-metadata {album_kv}",
            ]
        else:
            # Fallback: map yt-dlp's playlist_title to album (may be dirty)
            flags += ["--parse-metadata", "playlist_title:%(album)s"]
            if "--add-metadata" not in extra:
                flags.append("--add-metadata")

    if cfg.get("windows_safe_filenames"):
        flags.append("--windows-filenames")

    return flags


# ---------------------------------------------------------------------------
# Command builder
# ---------------------------------------------------------------------------

def build_command(
    url: str,
    out_dir: Path,
    archive: Path,
    cfg: Dict[str, Any],
    album_name: Optional[str] = None,
) -> List[str]:
    cmd = [
        "yt-dlp",
        "--format",           "bestaudio/best",
        "--extract-audio",
        "--audio-format",     cfg["audio_format"],
        "--audio-quality",    str(cfg["audio_quality"]),
        "--output",           str(out_dir / cfg["output_template"]),
        "--download-archive", str(archive),
        "--console-title",
    ]
    if cfg.get("no_overwrites"):
        cmd.append("--no-overwrites")
    if cfg.get("ignore_errors"):
        cmd.append("--ignore-errors")

    cmd.extend(metadata_flags(cfg, album_name=album_name))

    if cfg.get("extra_yt_dlp_args"):
        cmd.extend(cfg["extra_yt_dlp_args"])

    cmd.append(url)
    return cmd


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(url: str, base_out_dir: Path, cfg: Dict[str, Any]) -> int:
    needs_info = cfg.get("use_collection_folder") or cfg.get("embed_collection_as_album")

    if needs_info:
        print("[tiktok-collection-dl] Fetching collection info...")
        info = get_collection_info(url)
        print(f"[tiktok-collection-dl] uploader       : {info.get('uploader') or 'N/A'}")
        print(f"[tiktok-collection-dl] playlist_title : {info.get('playlist_title') or 'N/A'}")

        if cfg.get("strip_uploader_from_collection_title"):
            info = strip_uploader_prefix(info)
    else:
        info = {f: None for f in _SUPPORTED_FIELDS}

    if cfg.get("use_collection_folder"):
        template    = cfg.get("collection_folder_template", "%(playlist_title)s")
        folder_name = apply_folder_template(template, info)
        out_dir     = base_out_dir / folder_name
        print(f"[tiktok-collection-dl] folder template: {template}")
        print(f"[tiktok-collection-dl] folder name    : {folder_name}")
    else:
        out_dir = base_out_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    album_name = info.get("playlist_title") if cfg.get("embed_collection_as_album") else None
    archive    = get_archive_path(out_dir, url)
    cmd        = build_command(url, out_dir, archive, cfg, album_name=album_name)

    print(f"[tiktok-collection-dl] Output dir : {out_dir}")
    print(f"[tiktok-collection-dl] Archive    : {archive}")
    if album_name:
        print(f"[tiktok-collection-dl] Album tag  : {album_name!r}")
    print(f"[tiktok-collection-dl] Command    : {' '.join(cmd)}\n")

    try:
        return subprocess.run(cmd, check=False).returncode
    except FileNotFoundError:
        print("[ERROR] yt-dlp not found \u2014 is it on your PATH?", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[tiktok-collection-dl] Stopped by user.")
        return 130
