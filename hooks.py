from __future__ import annotations

"""MkDocs hooks: ルート .pages をビルド時に自動生成/復元する。"""
from pathlib import Path
from typing import Any, Optional

from update_root_pages import generate_navigation, write_root_pages

_ORIGINAL_ROOT_PAGES: Optional[str] = None


def _root_pages_path(config: dict[str, Any]) -> Path:
    docs_dir = Path(config["docs_dir"]).resolve()
    return docs_dir / ".pages"


def on_config(config: dict[str, Any]) -> dict[str, Any]:
    global _ORIGINAL_ROOT_PAGES
    path = _root_pages_path(config)
    if path.exists():
        _ORIGINAL_ROOT_PAGES = path.read_text(encoding="utf-8")
    else:
        _ORIGINAL_ROOT_PAGES = None

    nav = generate_navigation(path.parent)
    write_root_pages(path.parent, nav)
    return config


def on_post_build(config: dict[str, Any]) -> None:
    global _ORIGINAL_ROOT_PAGES
    path = _root_pages_path(config)
    if _ORIGINAL_ROOT_PAGES is None:
        if path.exists():
            path.unlink()
    else:
        path.write_text(_ORIGINAL_ROOT_PAGES, encoding="utf-8")
    _ORIGINAL_ROOT_PAGES = None
