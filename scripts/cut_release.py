#!/usr/bin/env python3
"""Cut a new dated CHANGELOG release.

Moves all content under `## [Unreleased]` into a new `## [YYYY.MM.DD]` section
and leaves `## [Unreleased]` empty (with the standard separator) ready for the
next round of PRs.

Usage:
    python scripts/cut_release.py                  # cut release for today
    python scripts/cut_release.py --dry-run        # print result, do not write
    python scripts/cut_release.py --date 2026.04.23  # override the target date
    python scripts/cut_release.py --changelog CUSTOM.md  # non-default path

Exit codes:
    0 — release cut, or no-op (empty [Unreleased])
    1 — error (malformed CHANGELOG, today already has a release, etc.)
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sys


UNRELEASED_HEADER = "## [Unreleased]"


def find_sections(text: str) -> tuple[str, list[str]]:
    """Split CHANGELOG into (header, list-of-sections).

    Each section starts at a `## [` header and continues up to the next one.
    The header portion is everything before the first `## [`.
    """
    match = re.search(r"^## \[", text, re.MULTILINE)
    if not match:
        raise ValueError("No `## [...]` sections found in CHANGELOG")

    header = text[: match.start()]
    body = text[match.start() :]
    sections = re.split(r"(?=^## \[)", body, flags=re.MULTILINE)
    sections = [s for s in sections if s.strip()]
    if not sections:
        raise ValueError("No release sections found after `## [...]` header")
    return header, sections


def has_meaningful_content(section_body: str) -> bool:
    """Return True if the [Unreleased] section contains real content.

    A bare section with only separators, blank lines, or whitespace counts as
    empty — there is nothing worth moving to a dated release.
    """
    for line in section_body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "---":
            continue
        return True
    return False


def cut(text: str, today: str) -> tuple[str | None, str]:
    """Return (new_text, status_message).

    `new_text` is None when there is nothing to cut (empty [Unreleased]).
    """
    header, sections = find_sections(text)

    first = sections[0]
    if not first.startswith(UNRELEASED_HEADER):
        raise ValueError(
            f"First release section is not `{UNRELEASED_HEADER}` — "
            "refusing to cut to avoid corrupting the file"
        )

    # Check for collision: today already has a release
    for s in sections[1:]:
        if s.startswith(f"## [{today}]"):
            raise ValueError(
                f"Release for {today} already exists. Resolve manually "
                "(append content to the existing section, or use a suffix "
                "like YYYY.MM.DD.N)"
            )

    # Split the [Unreleased] section into its header line and its body
    head_line, _, body = first.partition("\n")
    assert head_line == UNRELEASED_HEADER

    if not has_meaningful_content(body):
        return None, "No unreleased changes — nothing to cut."

    # Build:
    #   - empty [Unreleased] with separator
    #   - new dated section with the previous [Unreleased] body
    #   - the rest of the file unchanged
    new_unreleased = f"{UNRELEASED_HEADER}\n\n---\n\n"
    new_dated = f"## [{today}]\n{body}"
    rest = "".join(sections[1:])

    return (
        header + new_unreleased + new_dated + rest,
        f"Cut release {today}",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        type=pathlib.Path,
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Override the release date (format: YYYY.MM.DD). Defaults to today (UTC).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resulting file to stdout without writing.",
    )
    args = parser.parse_args(argv)

    if not args.changelog.exists():
        print(f"ERROR: {args.changelog} not found", file=sys.stderr)
        return 1

    today = args.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y.%m.%d")
    if not re.match(r"^\d{4}\.\d{2}\.\d{2}$", today):
        print(f"ERROR: --date must match YYYY.MM.DD, got '{today}'", file=sys.stderr)
        return 1

    try:
        result, message = cut(args.changelog.read_text(), today)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if result is None:
        print(message)
        return 0

    if args.dry_run:
        sys.stdout.write(result)
        print(f"\n--- dry run: would have written the above to {args.changelog} ---", file=sys.stderr)
        return 0

    args.changelog.write_text(result)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
