from __future__ import annotations

from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page


class Plugin(BasePlugin):
    def on_page_markdown(self, markdown: str, page: Page, config, files):
        if getattr(page, "meta", None) is None:
            page.meta = {}
        if page.meta.get("title"):
            return markdown
        src_path = getattr(page.file, "src_path", "")
        if not src_path:
            return markdown
        stem = Path(src_path).stem
        if not stem:
            return markdown
        page.meta["title"] = stem
        page.title = stem
        return markdown
