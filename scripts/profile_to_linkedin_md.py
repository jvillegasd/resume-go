#!/usr/bin/env python3
"""Generate LinkedIn-oriented markdown from a PDF or pasted profile text."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from linkedin_profile_lib import (
    extract_pdf_elements,
    parse_pdf_elements,
    parse_profile_text,
    render_linkedin_markdown,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--input-pdf", type=Path,
                       help="LinkedIn Profile.pdf input.")
    group.add_argument("--input-text", type=Path,
                       help="Plain text or markdown profile export.")
    ap.add_argument("--out", type=Path, default=Path("build/linkedin_source.md"))
    ap.add_argument("--keep-raw", action="store_true",
                    help="Keep opendataloader's intermediate JSON when using PDF.")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.input_pdf:
        workdir = args.out.parent if args.keep_raw else Path(tempfile.mkdtemp())
        elements = extract_pdf_elements(args.input_pdf, workdir)
        doc = parse_pdf_elements(elements)
        source_desc = str(args.input_pdf)
    else:
        doc = parse_profile_text(args.input_text.read_text())
        source_desc = str(args.input_text)

    args.out.write_text(render_linkedin_markdown(doc))
    print(
        f"wrote {args.out} from {source_desc}: "
        f"name={doc.name!r}, "
        f"headline={'yes' if doc.headline else 'no'}, "
        f"about={'yes' if doc.about_text else 'no'}, "
        f"experience={len(doc.sections.get('Experience', []))}"
    )


if __name__ == "__main__":
    main()
