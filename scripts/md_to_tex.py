#!/usr/bin/env python3
"""resume.md → resume.tex (Jake Gutierrez's template) → resume.pdf.

Parses the canonical schema from README.md and renders into a Jinja2
LaTeX template using `(((  )))` / `((*  *))` delimiters to avoid
colliding with LaTeX's `{}` braces and `%` comments.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jinja2

LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def tex_escape(s: str) -> str:
    out = []
    for ch in s:
        out.append(LATEX_ESCAPES.get(ch, ch))
    return "".join(out)


def classify_contact(c: str) -> dict:
    """Return {label, url} for a contact line.
    Email → mailto: link, label is the address.
    URLs → display as a readable host/path label without scheme.
    Plain text (e.g. city/country with no domain dot) → no href, label only.
    The url goes inside \\href{...} verbatim (no tex escaping); the label
    is tex-escaped at template-context time.
    """
    c = c.strip()
    if "@" in c and "/" not in c:
        return {"label": c, "url": f"mailto:{c}"}
    # Plain text: no dot that looks like a domain TLD and no scheme
    if not c.startswith(("http://", "https://")) and "." not in c:
        return {"label": c, "url": None}
    url = c if c.startswith(("http://", "https://")) else f"https://{c}"
    label = re.sub(r"^https?://", "", c, flags=re.IGNORECASE).rstrip("/")
    label = re.sub(r"^www\.", "", label, flags=re.IGNORECASE)
    return {"label": label, "url": url}


@dataclass
class Entry:
    title: str = ""        # "Acme Corp — Senior Engineer"
    meta: str = ""         # "Jan 2022 – Present · San Francisco"
    bullets: list[str] = field(default_factory=list)


@dataclass
class Resume:
    name: str = ""
    headline: str = ""
    location: str = ""
    contacts: list[str] = field(default_factory=list)
    summary: str = ""
    skills: str = ""
    skill_groups: list[tuple[str, str]] = field(default_factory=list)
    languages: str = ""
    sections: dict[str, list[Entry]] = field(default_factory=dict)


def parse_md(text: str) -> Resume:
    r = Resume()
    lines = text.splitlines()
    i = 0

    # Header block.
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        r.name = lines[i][2:].strip()
        i += 1
    # Quoted contact lines.
    quoted: list[str] = []
    while i < len(lines) and lines[i].startswith(">"):
        quoted.append(lines[i].lstrip("> ").strip())
        i += 1
    if quoted:
        first = [p.strip() for p in quoted[0].split("·")]
        r.headline = first[0] if first else ""
        r.location = first[1] if len(first) > 1 else ""
    if len(quoted) > 1:
        r.contacts = [p.strip() for p in quoted[1].split("·") if p.strip()]

    # Sections.
    current: str | None = None
    cur_entry: Entry | None = None
    section_body: list[str] = []

    def flush_freeform() -> None:
        nonlocal section_body
        # Skills section uses **Category:** items lines; parse them out
        # before falling back to free-form join.
        if current == "Skills":
            for ln in section_body:
                m = re.match(r"\*\*(.+?):\*\*\s*(.+)", ln.strip())
                if m:
                    r.skill_groups.append((m.group(1).strip(),
                                            m.group(2).strip()))
            if not r.skill_groups:
                r.skills = " ".join(s.strip() for s in section_body
                                     if s.strip()).strip()
            section_body = []
            return
        joined = " ".join(s.strip() for s in section_body if s.strip()).strip()
        if not joined:
            section_body = []
            return
        if current == "Summary":
            r.summary = joined
        elif current == "Languages":
            r.languages = joined
        section_body = []

    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            flush_freeform()
            cur_entry = None
            current = line[3:].strip()
            r.sections.setdefault(current, [])
        elif line.startswith("### "):
            flush_freeform()
            cur_entry = Entry(title=line[4:].strip())
            r.sections.setdefault(current or "Misc", []).append(cur_entry)
        elif line.startswith("*") and line.rstrip().endswith("*") and cur_entry:
            cur_entry.meta = line.strip().strip("*").strip()
        elif line.startswith("- ") and cur_entry:
            cur_entry.bullets.append(line[2:].strip())
        else:
            if cur_entry is None:
                section_body.append(line)
        i += 1
    flush_freeform()
    return r


def split_title(title: str) -> tuple[str, str]:
    """Split 'Org — Role' (or 'Org - Role') into (left, right) for the
    template. Falls back to (title, '')."""
    for sep in [" — ", " – ", " - "]:
        if sep in title:
            left, right = title.split(sep, 1)
            return left.strip(), right.strip()
    return title.strip(), ""


def split_meta(meta: str) -> tuple[str, str]:
    """Split 'Jan 2022 – Present · San Francisco' into (date, location)."""
    if "·" in meta:
        date, loc = meta.split("·", 1)
        return normalize_date(date), loc.strip()
    return normalize_date(meta), ""


def normalize_date(date: str) -> str:
    """Drop LinkedIn elapsed-duration parens, keeping only month/year range."""
    date = re.sub(r"\s*\([^)]*\)", "", date)
    return re.sub(r"\s+", " ", date).strip()


def to_template_ctx(r: Resume) -> dict:
    def entries(name: str) -> list[dict]:
        out = []
        for e in r.sections.get(name, []):
            left, right = split_title(e.title)
            date, loc = split_meta(e.meta)
            out.append({
                "left": tex_escape(left),
                "right": tex_escape(right),
                "date": tex_escape(date),
                "loc": tex_escape(loc),
                "bullets": [tex_escape(b) for b in e.bullets],
            })
        return out

    contacts = []
    for raw in r.contacts:
        info = classify_contact(raw)
        contacts.append({"label": tex_escape(info["label"]), "url": info["url"]})

    # Note: don't name the value key "items" — Jinja's dot lookup would hit
    # dict.items (the method) instead of our value.
    skill_groups = [
        {"category": tex_escape(cat), "skills": tex_escape(items)}
        for cat, items in r.skill_groups
    ]

    return {
        "name": tex_escape(r.name),
        "headline": tex_escape(r.headline),
        "location": tex_escape(r.location),
        "contacts": contacts,
        "summary": tex_escape(r.summary),
        "skills": tex_escape(r.skills),
        "skill_groups": skill_groups,
        "languages": tex_escape(r.languages),
        "experience": entries("Experience"),
        "education": entries("Education"),
        "projects": entries("Projects"),
        "certifications": entries("Certifications"),
    }


def render_tex(ctx: dict, template_path: Path) -> str:
    env = jinja2.Environment(
        block_start_string="((*", block_end_string="*))",
        variable_start_string="(((", variable_end_string=")))",
        comment_start_string="((=", comment_end_string="=))",
        trim_blocks=True, lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(str(template_path.parent)),
        autoescape=False,
    )
    return env.get_template(template_path.name).render(**ctx)



def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--template", type=Path,
        default=Path(__file__).resolve().parent.parent
        / "templates" / "jake_resume.tex.j2",
    )
    ap.add_argument("--compile", action="store_true",
                    help="Run latexmk -pdf on the output .tex.")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    resume = parse_md(args.input.read_text())
    ctx = to_template_ctx(resume)
    args.out.write_text(render_tex(ctx, args.template))
    print(f"wrote {args.out}")

    if args.compile:
        if not shutil.which("latexmk"):
            sys.exit("--compile requested but latexmk not on PATH")
        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", args.out.name],
            cwd=args.out.parent, check=True,
        )
        print(f"wrote {args.out.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
