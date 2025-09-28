#!/usr/bin/env python3
"""Markdownファイルのフロントマター日付をファイル名と同期させるスクリプト。

- ファイル名の YYYY-MM-DD 部分を抽出し、`date:` フィールドと一致させる。
- フロントマターが無い場合は追加する（末尾に空行を含む）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


def extract_date_from_name(path: Path) -> str | None:
    match = DATE_PATTERN.search(path.name)
    return match.group(1) if match else None


def detect_newline(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    if "\n" in text:
        return "\n"
    return "\r\n"


def line_ending_for(line: str, default: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return default


def ensure_frontmatter(content: str, newline: str, target_date: str) -> tuple[str, bool]:
    prefix = f"---{newline}"
    if content.startswith(prefix):
        start_index = len(prefix)
        closing_seq = f"{newline}---"
        closing_index = content.find(closing_seq, start_index)
        if closing_index == -1:
            rebuilt = build_frontmatter(target_date, newline) + content[start_index:]
            return rebuilt, True

        frontmatter_block = content[start_index:closing_index]
        closing_end = closing_index + len(closing_seq)
        if content.startswith(newline, closing_end):
            post_closing = newline
            body_start = closing_end + len(newline)
        else:
            post_closing = ""
            body_start = closing_end

        body = content[body_start:]

        frontmatter_lines = frontmatter_block.splitlines(keepends=True)
        target_line = f"date: {target_date}"
        date_line_idx = next(
            (idx for idx, line in enumerate(frontmatter_lines) if line.strip().startswith("date:")),
            None,
        )

        if date_line_idx is not None:
            current_line = frontmatter_lines[date_line_idx].rstrip("\r\n")
            if current_line == target_line:
                return content, False
            line_ending = line_ending_for(frontmatter_lines[date_line_idx], newline)
            frontmatter_lines[date_line_idx] = f"{target_line}{line_ending}"
        else:
            line_ending = line_ending_for(frontmatter_lines[0], newline) if frontmatter_lines else newline
            frontmatter_lines.insert(0, f"{target_line}{line_ending}")

        updated_frontmatter_block = "".join(frontmatter_lines)
        new_content = "".join(
            [
                f"---{newline}",
                updated_frontmatter_block,
                "---",
                post_closing,
                body,
            ]
        )
        return new_content, True

    new_content = build_frontmatter(target_date, newline) + content
    return new_content, True


def build_frontmatter(target_date: str, newline: str) -> str:
    return f"---{newline}date: {target_date}{newline}---{newline}{newline}"


def process_file(path: Path) -> bool:
    target_date = extract_date_from_name(path)
    if not target_date:
        return False

    raw_bytes = path.read_bytes()

    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        print(f"[SKIP] {path} (utf-8 で読めません)")
        return False

    newline = detect_newline(raw_text)
    updated_content, changed = ensure_frontmatter(raw_text, newline, target_date)

    if not changed:
        return False

    updated_bytes = updated_content.encode("utf-8")
    path.write_bytes(updated_bytes)
    print(f"[FIX]  {path}")
    return True


def iter_markdown_files(root: Path):
    for path in sorted(root.rglob("*.md")):
        yield path


def main(argv: list[str]) -> int:
    if argv:
        targets = [Path(arg) for arg in argv]
    else:
        targets = [Path(__file__).resolve().parent]

    total = 0
    for target in targets:
        if target.is_file():
            total += process_file(target)
        elif target.is_dir():
            for md_path in iter_markdown_files(target):
                total += process_file(md_path)
        else:
            print(f"[WARN] {target} は存在しません")

    print(f"[DONE] {total} 件更新")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

