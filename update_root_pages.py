#!/usr/bin/env python3
"""docs/.pages をサブフォルダのメタデータから自動生成する補助スクリプト。

- 各サブフォルダの .pages から `title: カテゴリ｜年月` を読み取り、カテゴリ毎にフォルダをグルーピング
- 既存の docs/.pages が持つカテゴリ順を尊重しつつ、新規カテゴリは自動追加
- 生成した nav 構造を Python リストで返したり、ファイルに書き出したりできる
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

CATEGORY_EXCLUDE = {"assets", "stylesheets"}


def extract_category_from_pages(pages_path: Path) -> str | None:
    """`.pages` のタイトル行からカテゴリ名を抽出する。"""
    try:
        for raw_line in pages_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.lstrip("\ufeff").strip()
            if not line.startswith("title:"):
                continue
            title = line.split(":", 1)[1].strip().strip('"').strip("'")
            if not title:
                return None
            category, _, _ = title.partition("｜")
            return category or None
    except FileNotFoundError:
        return None
    return None


def collect_category_mapping(docs_dir: Path) -> Tuple[Dict[str, List[str]], List[str]]:
    """カテゴリ -> フォルダ一覧、および検出順を返す。"""
    mapping: Dict[str, List[str]] = {}
    discovered_order: List[str] = []

    for child in sorted(docs_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        if child.name.startswith('.'):
            continue
        if child.name in CATEGORY_EXCLUDE:
            continue

        category = extract_category_from_pages(child / ".pages")
        if not category:
            continue

        if category not in mapping:
            mapping[category] = []
            discovered_order.append(category)

        mapping[category].append(child.name.replace('\\', '/'))

    for paths in mapping.values():
        paths.sort(reverse=True)

    return mapping, discovered_order


def read_existing_category_order(root_pages_path: Path) -> List[str]:
    """既存 docs/.pages の nav からカテゴリ順を抽出する。"""
    if not root_pages_path.is_file():
        return []

    order: List[str] = []
    for raw_line in root_pages_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.lstrip("\ufeff").strip()
        if not line.startswith("- "):
            continue
        entry = line[2:]
        if entry.endswith(":"):
            name = entry[:-1].strip()
            if name:
                order.append(name)
    return order


def build_order(mapping: Dict[str, List[str]], discovered_order: List[str], existing_order: List[str]) -> List[str]:
    ordered: List[str] = [cat for cat in existing_order if cat in mapping]
    for cat in discovered_order:
        if cat not in ordered:
            ordered.append(cat)
    return ordered


def build_nav_structure(mapping: Dict[str, List[str]], ordered_categories: List[str], include_index: bool = True) -> List[object]:
    nav: List[object] = []
    if include_index:
        nav.append("index.md")

    for category in ordered_categories:
        paths = mapping.get(category)
        if not paths:
            continue
        children = [{"path": path} for path in paths]
        nav.append({category: children})

    return nav


def format_nav_as_pages(nav: List[object]) -> str:
    """MkDocs Awesome Pages 用の nav YAML テキストに整形する。"""
    lines: List[str] = ["nav:"]
    for entry in nav:
        if isinstance(entry, str):
            lines.append(f"  - {entry}")
            continue
        if isinstance(entry, dict):
            for category, children in entry.items():
                lines.append(f"  - {category}:")
                for child in children:
                    lines.append(f"      - path: {child['path']}")
    return "\n".join(lines) + "\n"


def generate_navigation(docs_dir: Path) -> List[object]:
    mapping, discovered_order = collect_category_mapping(docs_dir)
    existing_order = read_existing_category_order(docs_dir / ".pages")
    ordered_categories = build_order(mapping, discovered_order, existing_order)
    return build_nav_structure(mapping, ordered_categories)


def write_root_pages(docs_dir: Path, nav: List[object]) -> Path:
    content = format_nav_as_pages(nav)
    root_pages_path = docs_dir / ".pages"
    root_pages_path.write_text(content, encoding="utf-8")
    return root_pages_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate root .pages nav from subfolders")
    parser.add_argument("docs_dir", nargs="?", default="docs", help="MkDocs docs directory")
    parser.add_argument("--print", action="store_true", help="Print nav structure instead of writing file")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.is_dir():
        raise SystemExit(f"Docs directory not found: {docs_dir}")

    nav = generate_navigation(docs_dir)

    if args.print:
        print(nav)
        return

    path = write_root_pages(docs_dir, nav)
    print(f"Updated {path} with {len(nav) - 1} categories.")


if __name__ == "__main__":
    main()
