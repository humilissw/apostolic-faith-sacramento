#!/usr/bin/env python3
"""Auto-fix wrong left-padding inside Python multi-line strings (docstrings).

editorconfig-checker flags any line whose left padding is not a multiple of
``indent_size`` from .editorconfig ("Wrong amount of left-padding spaces").
Black deliberately preserves relative indentation inside docstrings and will
never fix those, so they used to fail CI with no formatter able to repair
them automatically.

This hook rounds the leading spaces of content lines *inside triple-quoted
strings* down to the nearest multiple of 4. It is wired as a pre-commit hook
that runs before editorconfig-checker, so offending files are fixed in place
and the commit re-runs automatically.

Scope / safety:
- Only lines strictly inside multi-line string tokens are touched; code
indentation is left to black/ruff (which already guarantee it).
- Strings with a raw (r/R) or bytes (b/B) prefix are skipped: their exact
content can be semantically meaningful (regexes, binary payloads).
- Whitespace-only lines inside strings are normalized to empty only when the
line is entirely spaces; trailing whitespace is handled by the dedicated
pre-commit hook.
- Caveat: re-indenting a docstring could theoretically shift a doctest
continuation line; doctests in this repo start at column 0 and are
unaffected, but be aware when running it elsewhere.

Usage: fix_python_string_indent.py FILE [FILE ...]   (exit 1 if any fixed)
"""

from __future__ import annotations

import io
import sys
import tokenize

INDENT_MULTIPLE = 4


def _string_bounds(src_bytes: bytes):
    """Yield (start_row, end_row, prefix_lower) for multi-line string tokens.

    Rows are 1-based physical line numbers; interior lines are those strictly
    between start_row and end_row. Returns [] if the file cannot be tokenized.
    """
    bounds = []
    try:
        for tok in tokenize.tokenize(io.BytesIO(src_bytes).readline):
            if tok.type != tokenize.STRING or tok.start[0] == tok.end[0]:
                continue
            prefix = tok.string[: tok.string.index(tok.string.lstrip("bBuUfFrR")[0])].lower()
            if "r" in prefix or "b" in prefix:
                continue
            bounds.append((tok.start[0], tok.end[0]))
    except (tokenize.TokenError, SyntaxError, IndentationError, UnicodeDecodeError, ValueError):
        return []
    return bounds


def fix_text(text: str) -> tuple[str, int]:
    """Return (fixed_text, n_lines_fixed) for one file's contents."""
    lines = text.splitlines(keepends=True)
    bounds = _string_bounds(text.encode("utf-8"))
    if not bounds:
        return text, 0

    interior: set[int] = set()
    for start_row, end_row in bounds:
        interior.update(range(start_row + 1, end_row))

    fixed_lines = list(lines)
    n_fixed = 0
    for lineno in sorted(interior):
        line = lines[lineno - 1]
        stripped = line.lstrip(" ")
        if not stripped or stripped.isspace():
            continue  # blank/whitespace-only: nothing sensible to re-indent
        indent = len(line) - len(stripped)
        if indent % INDENT_MULTIPLE == 0:
            continue
        new_indent = " " * (indent - (indent % INDENT_MULTIPLE))
        fixed_lines[lineno - 1] = new_indent + stripped
        n_fixed += 1

    return "".join(fixed_lines), n_fixed


def main(argv: list[str]) -> int:
    changed = 0
    for path in argv:
        if not path.endswith((".py", ".pyi")):
            continue
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fixed, n = fix_text(text)
        if n and fixed != text:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(fixed)
            print(f"fix_python_string_indent: re-indented {n} line(s) in {path}")
            changed += 1
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
