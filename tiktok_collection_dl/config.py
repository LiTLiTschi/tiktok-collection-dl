from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    raise ImportError("pyyaml is required: pip install pyyaml")

FILENAME = "tiktok_collection_dl_config.yaml"

CONFIG_LOCATIONS = [
    Path.home() / ".config" / FILENAME,
    Path.cwd() / ".config" / FILENAME,
    Path.cwd() / FILENAME,
]

DEFAULTS: Dict[str, Any] = {
    "audio_format":                        "mp3",
    "audio_quality":                       "0",
    "output_template":                     "%(playlist_index)s - %(title)s.%(ext)s",
    "ignore_errors":                       True,
    "no_overwrites":                       True,
    "use_collection_folder":               False,
    "collection_folder_template":          "%(playlist_title)s",
    # Ugly fix: strip the uploader prefix yt-dlp bakes into playlist_title
    # e.g. "gohome.gi-My Collection" -> "My Collection"
    "strip_uploader_from_collection_title": False,
    "embed_collection_as_album":           False,
    # Ugly fix: pass --windows-filenames to yt-dlp so illegal chars become _
    # instead of being percent-encoded (e.g. %3F -> _)
    "windows_safe_filenames":              False,
    "default_output_dir":                  None,
    "extra_yt_dlp_args":                   [],
}


def _format_yaml_error(err: yaml.YAMLError) -> str:
    mark = getattr(err, "problem_mark", None)
    problem = getattr(err, "problem", str(err))
    if mark:
        return f"{problem} (line {mark.line + 1}, column {mark.column + 1})"
    return problem


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    for path in CONFIG_LOCATIONS:
        if not path.is_file():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(
                f"[ERROR] Invalid YAML in:\n"
                f"        {path}\n"
                f"        {_format_yaml_error(e)}\n\n"
                f"  Common causes:\n"
                f"    - Unquoted % signs  -->  output_template: \"%(title)s.%(ext)s\"\n"
                f"    - Tabs instead of spaces for indentation\n"
                f"    - Missing space after colon  (key:value  -->  key: value)\n"
                f"    - Unquoted special characters: : {{ }} [ ] , & * # ? | - < > = ! % @ \\`",
                file=sys.stderr,
            )
            raise SystemExit(2)

        if data is None:
            continue
        if not isinstance(data, dict):
            print(
                f"[ERROR] Config must be a YAML mapping (key: value pairs).\n"
                f"        Got {type(data).__name__} instead in:\n"
                f"        {path}",
                file=sys.stderr,
            )
            raise SystemExit(2)

        unknown = set(data.keys()) - set(DEFAULTS.keys())
        if unknown:
            print(
                f"[WARNING] Unknown config key(s) in {path}: {', '.join(sorted(unknown))}\n"
                f"          Valid keys: {', '.join(sorted(DEFAULTS.keys()))}"
            )

        cfg.update(data)
        print(f"[config] Loaded: {path}")
    return cfg
