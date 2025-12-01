"""
Flatten repository contents into a single Markdown document.

This script walks the repository tree, records the structure of allowed files,
and writes their contents into a consolidated Markdown file named
``repo_context.md`` at the chosen root directory.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List

SKIP_DIRECTORIES = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".sol",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".sh",
    ".bash",
    ".html",
    ".css",
}

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".sh": "bash",
    ".bash": "bash",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".html": "html",
    ".css": "css",
    ".go": "go",
    ".rs": "rust",
    ".sol": "solidity",
}

OUTPUT_FILENAME = "repo_context.md"


class TreeNode:
    def __init__(self) -> None:
        self.dirs: Dict[str, "TreeNode"] = {}
        self.files: List[str] = []

    def add_path(self, parts: List[str]) -> None:
        if not parts:
            return
        if len(parts) == 1:
            if parts[0] not in self.files:
                self.files.append(parts[0])
            return
        head, *tail = parts
        if head not in self.dirs:
            self.dirs[head] = TreeNode()
        self.dirs[head].add_path(tail)


def parse_arguments() -> Path:
    if len(sys.argv) > 2:
        print("Usage: python flatten_repo_to_md.py [root_path]")
        sys.exit(1)
    root_arg = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(".")
    return root_arg.resolve()


def should_include_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def walk_repository(root: Path) -> tuple[TreeNode, List[Path]]:
    tree_root = TreeNode()
    allowed_files: List[Path] = []
    for current_dir, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRECTORIES]
        rel_dir = Path(current_dir).relative_to(root)
        for name in sorted(filenames):
            if name == OUTPUT_FILENAME:
                continue
            if not should_include_file(name):
                continue
            rel_path = rel_dir / name if str(rel_dir) != "." else Path(name)
            parts = list(rel_path.parts)
            tree_root.add_path(parts)
            allowed_files.append(rel_path)
    allowed_files.sort()
    return tree_root, allowed_files


def render_structure(tree: TreeNode) -> List[str]:
    lines: List[str] = ["# Repository structure", "- `/`"]

    def _render(node: TreeNode, indent: int) -> None:
        spacer = "  " * indent
        for directory in sorted(node.dirs):
            lines.append(f"{spacer}- `{directory}/`")
            _render(node.dirs[directory], indent + 1)
        for filename in sorted(node.files):
            lines.append(f"{spacer}- `{filename}`")

    _render(tree, 1)
    return lines


def language_for_extension(path: Path) -> str:
    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower(), "")


def read_file_contents(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as file:
            return file.read()
    except Exception as exc:  # noqa: BLE001
        return f"[ERROR READING FILE: {exc}]"


def render_file_contents(root: Path, files: List[Path]) -> List[str]:
    lines: List[str] = ["# File contents"]
    for rel_path in files:
        absolute_path = root / rel_path
        language = language_for_extension(rel_path)
        fence = f"```{language}" if language else "```"
        lines.append(f"## `{rel_path.as_posix()}`")
        lines.append(fence)
        lines.append(read_file_contents(absolute_path))
        lines.append("```")
    return lines


def write_output(root: Path, structure_lines: List[str], content_lines: List[str]) -> None:
    output_path = root / OUTPUT_FILENAME
    combined = structure_lines + [""] + content_lines
    output_path.write_text("\n".join(combined), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILENAME} to {root}")


def main() -> None:
    root = parse_arguments()
    tree, files = walk_repository(root)
    structure_lines = render_structure(tree)
    content_lines = render_file_contents(root, files)
    write_output(root, structure_lines, content_lines)


if __name__ == "__main__":
    main()
