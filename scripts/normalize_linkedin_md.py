#!/usr/bin/env python3
"""Normalize and validate optimized LinkedIn markdown."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from linkedin_profile_lib import parse_linkedin_markdown, render_linkedin_markdown


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    doc = parse_linkedin_markdown(args.input.read_text())
    missing: list[str] = []
    if not doc.name:
        missing.append("name (# Full Name)")
    if not doc.headline:
        missing.append("Headline")
    if not doc.about_text:
        missing.append("About")
    if missing:
        sys.exit("missing required LinkedIn sections: " + ", ".join(missing))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_linkedin_markdown(doc))
    print(
        f"wrote {args.out}: "
        f"headline={'yes' if doc.headline else 'no'}, "
        f"about={'yes' if doc.about_text else 'no'}, "
        f"experience={len(doc.sections.get('Experience', []))}"
    )


if __name__ == "__main__":
    main()
