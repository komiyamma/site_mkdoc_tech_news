from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files


class Plugin(BasePlugin):
    config_scheme = (
        ("patterns", config_options.Type(list, default=[])),
    )

    def on_files(self, files: Files, config):
        patterns = [str(pattern).replace("\\", "/") for pattern in self.config.get("patterns", [])]
        if not patterns:
            return files
        for file in list(files):
            rel_path = file.src_path.replace("\\", "/")
            name = Path(rel_path).name
            if any(fnmatch(rel_path, pattern) or fnmatch(name, pattern) for pattern in patterns):
                files.remove(file)
        return files
