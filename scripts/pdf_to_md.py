#!/usr/bin/env python3
"""LinkedIn Profile.pdf → canonical ATS resume markdown."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from linkedin_profile_lib import (
    extract_pdf_elements,
    parse_pdf_elements,
    render_resume_markdown,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--keep-raw", action="store_true",
                    help="Keep opendataloader's intermediate JSON.")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    workdir = args.out.parent if args.keep_raw else Path(tempfile.mkdtemp())
    elements = extract_pdf_elements(args.input, workdir)
    doc = parse_pdf_elements(elements)
    args.out.write_text(render_resume_markdown(doc))
    print(
        f"wrote {args.out}: name={doc.name!r}, "
        f"experience={len(doc.sections.get('Experience', []))}, "
        f"education={len(doc.sections.get('Education', []))}, "
        f"skills={len(doc.skills)}, certs={len(doc.certifications)}, "
        f"honors={len(doc.honors)}"
    )


if __name__ == "__main__":
    main()
