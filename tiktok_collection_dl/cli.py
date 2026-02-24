from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List

from . import __version__
from .config import load_config
from .downloader import run


def read_list_file(path: Path) -> List[str]:
    """
    Read URLs from a list.txt file.
    - Lines starting with # are treated as comments and skipped.
    - Blank lines are skipped.
    """
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def looks_like_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://", "www."))


def main():
    parser = argparse.ArgumentParser(
        prog="tiktok-collection-dl",
        description=(
            "Download TikTok collections as best-quality audio.\n\n"
            "If no URL is given, reads URLs from list.txt in the output directory."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="TikTok collection URL, or path to output dir when using list.txt",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Destination folder (default: cwd or config default_output_dir)",
    )
    parser.add_argument(
        "--audio-format",
        default=None,
        help="Override audio format: mp3, m4a, opus, flac ...",
    )
    parser.add_argument(
        "--audio-quality",
        default=None,
        help="Override VBR quality (0=best ... 9=worst)",
    )
    args = parser.parse_args()

    print(f"[tiktok-collection-dl] v{__version__}")

    cfg = load_config()

    if args.audio_format:
        cfg["audio_format"] = args.audio_format
    if args.audio_quality:
        cfg["audio_quality"] = args.audio_quality

    # -----------------------------------------------------------------------
    # Smart disambiguation:
    # If only one positional arg was given and it looks like a local path
    # (not a URL), treat it as output_dir rather than url.
    # -----------------------------------------------------------------------
    url_arg        = args.url
    output_dir_arg = args.output_dir

    if url_arg and not looks_like_url(url_arg) and output_dir_arg is None:
        output_dir_arg = url_arg
        url_arg = None

    # -----------------------------------------------------------------------
    # Resolve output directory
    # -----------------------------------------------------------------------
    if output_dir_arg:
        out_dir = Path(output_dir_arg).expanduser().resolve()
    elif cfg.get("default_output_dir"):
        out_dir = Path(cfg["default_output_dir"]).expanduser().resolve()
    else:
        out_dir = Path.cwd()

    # -----------------------------------------------------------------------
    # Collect URLs  (CLI arg  >  list.txt in output dir)
    # -----------------------------------------------------------------------
    if url_arg:
        urls = [url_arg]
    else:
        list_file = out_dir / "list.txt"
        if list_file.is_file():
            urls = read_list_file(list_file)
            if not urls:
                print(
                    f"[ERROR] {list_file} exists but contains no URLs "
                    "(only comments / blank lines).",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"[tiktok-collection-dl] Found list.txt \u2014 {len(urls)} URL(s) queued")
        else:
            print(
                f"[ERROR] No URL given and no list.txt found in:\n"
                f"        {out_dir}\n\n"
                f"  Pass a URL:  tiktok-collection-dl \"https://www.tiktok.com/...\"\n"
                f"  Or create:   {list_file}",
                file=sys.stderr,
            )
            sys.exit(1)

    # -----------------------------------------------------------------------
    # Download each URL
    # -----------------------------------------------------------------------
    exit_code = 0
    for i, url in enumerate(urls, 1):
        if len(urls) > 1:
            print(f"\n[tiktok-collection-dl] \u2500\u2500 {i}/{len(urls)}: {url}")
        result = run(url, out_dir, cfg)
        if result != 0:
            exit_code = result

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
