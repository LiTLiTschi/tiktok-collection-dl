from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    raise ImportError("pyyaml is required: pip install pyyaml")

FILENAME = "tiktok_collection_dl_config.yaml"

# Loaded in order — later entries override earlier ones (cwd wins over global)
CONFIG_LOCATIONS = [
    Path.home() / ".config" / FILENAME,      # 3 — global user
    Path.cwd() / ".config" / FILENAME,       # 2 — project hidden dir
    Path.cwd() / FILENAME,                   # 1 — cwd (highest priority)
]

DEFAULTS: Dict[str, Any] = {
    "audio_format":           "mp3",
    "audio_quality":          "0",       # 0 = best VBR, 9 = worst
    "output_template":        "%(playlist_index)s - %(title)s.%(ext)s",
    "ignore_errors":          True,
    "no_overwrites":          True,
    "use_collection_folder":  False,     # put downloads in a subfolder named after the collection
    "default_output_dir":     None,      # None = cwd
    "extra_yt_dlp_args":      [],
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    for path in CONFIG_LOCATIONS:
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            cfg.update(data)
            print(f"[config] Loaded: {path}")
    return cfg
