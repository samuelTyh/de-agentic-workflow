#!/usr/bin/env python3
"""Extract a single release section from CHANGELOG.md.

Used by the post-merge tagging pipeline to populate the annotated tag's
message body. Output goes to stdout; non-zero exit code on errors.

Usage:
    python scripts/extract_release_notes.py --version 2026.04.23
    python scripts/extract_release_notes.py --version 2026.04.23 --changelog CUSTOM.md

Output format:
    Release <version>

    <verbatim contents of the release section, without the `## [version]`
    header line and without the trailing `---` separator>
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


def extract(text: str, version: str) -> str:
    """Return the body of the `## [<version>]` section.

    Strips leading blank lines and any trailing `---` separator + blanks so
    the result can be used directly as a tag message body.
    """
    header_re = re.compile(rf"^##\s+\[{re.escape(version)}\]\s*$")
    next_section_re = re.compile(r"^##\s+\[")

    captured: list[str] = []
    in_section = False
    for line in text.splitlines():
        if header_re.match(line):
            in_section = True
            continue
        if in_section and next_section_re.match(line):
            break
        if in_section:
            captured.append(line)

    if not captured:
        raise ValueError(f"Release section [{version}] not found in CHANGELOG")

    while captured and not captured[0].strip():
        captured.pop(0)
    while captured and (not captured[-1].strip() or captured[-1].strip() == "---"):
        captured.pop()

    if not captured:
        raise ValueError(f"Release section [{version}] is empty")

    return "\n".join(captured)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--version",
        required=True,
        help="Release version in CHANGELOG format, e.g. 2026.04.23",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        type=pathlib.Path,
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    args = parser.parse_args(argv)

    if not re.match(r"^\d{4}\.\d{2}\.\d{2}$", args.version):
        print(
            f"ERROR: --version must match YYYY.MM.DD, got '{args.version}'",
            file=sys.stderr,
        )
        return 1

    if not args.changelog.exists():
        print(f"ERROR: {args.changelog} not found", file=sys.stderr)
        return 1

    try:
        notes = extract(args.changelog.read_text(), args.version)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Release {args.version}")
    print()
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
