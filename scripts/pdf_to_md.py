#!/usr/bin/env python3
"""LinkedIn Profile.pdf → canonical resume.md.

Uses opendataloader-pdf's JSON output, which preserves the LinkedIn export's
heading hierarchy:

  heading level 1 → the user's name (rendered ~26pt)
  heading level 2 → body sections (Extracto/Summary, Experiencia, Educación)
  heading level 3 → page-1 sidebar sections (Aptitudes principales,
                    Languages, Certifications, Honors-Awards)

Handles English and Spanish LinkedIn exports.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import opendataloader_pdf

SECTION_ALIASES = {
    "Contact":        ["Contact", "Contactar"],
    "Skills":         ["Top Skills", "Aptitudes principales"],
    "Languages":      ["Languages", "Idiomas"],
    "Certifications": ["Certifications", "Licenses & Certifications",
                       "Licencias y certificaciones"],
    "Honors":         ["Honors-Awards", "Honors & Awards", "Reconocimientos"],
    "Summary":        ["Summary", "About", "Extracto", "Acerca de"],
    "Experience":     ["Experience", "Experiencia"],
    "Education":      ["Education", "Educación", "Formación"],
    "Projects":       ["Projects", "Proyectos"],
    "Publications":   ["Publications", "Publicaciones"],
    "Volunteer":      ["Volunteer Experience", "Experiencia de voluntariado"],
}
SECTION_LOOKUP = {
    a.lower(): canon for canon, aliases in SECTION_ALIASES.items() for a in aliases
}

EN_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?"
ES_MONTH = (r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
            r"sept?iembre|octubre|noviembre|diciembre)")
DATE_TOKEN = (rf"(?:(?:{EN_MONTH}\s+\d{{4}})|"
              rf"(?:{ES_MONTH}\s+de\s+\d{{4}})|"
              rf"\d{{4}})")
END_TOKEN = rf"(?:Present|Actualidad|Presente|{DATE_TOKEN})"
DATE_RE = re.compile(
    rf"^{DATE_TOKEN}\s*[-–—]\s*{END_TOKEN}(?:\s.*)?$", re.IGNORECASE,
)
PAGE_RE = re.compile(r"^\s*(?:Page|Página)\s+\d+\s+(?:of|de)\s+\d+\s*$", re.I)
URL_RE = re.compile(
    r"(?:https?://\S+|(?:www\.|linkedin\.com|github\.com)[\w./\-]+)", re.I,
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
BULLET_PREFIX = re.compile(r"^[•‣◦▪▫●○\-\*]\s*")

EMIT_ORDER = ["Education", "Experience", "TechSkills", "Projects",
              "Honors", "Publications", "Volunteer"]

# ---------------------------------------------------------------------------
# Spanish → English translation (LinkedIn export language is account-locale).
# ---------------------------------------------------------------------------
ES_MONTHS_EN = {
    "enero": "January", "febrero": "February", "marzo": "March",
    "abril": "April", "mayo": "May", "junio": "June", "julio": "July",
    "agosto": "August", "septiembre": "September", "setiembre": "September",
    "octubre": "October", "noviembre": "November", "diciembre": "December",
}
ES_PHRASES = {
    "Ciencias de la Computación": "Computer Science",
    "Ciencias de la computación": "Computer Science",
    "Ingeniería de Sistemas": "Systems Engineering",
    "Ingeniería de sistemas": "Systems Engineering",
}


def split_date_location(meta: str) -> str:
    """LinkedIn renders an entry's date line as one whitespace-joined string:
        "February 2024 - Present (2 yrs 4 mos) Reston, Virginia, United States"
    Split it into `<date> · <location>` so md_to_tex's splitter places them
    in the right tex columns. Idempotent (returns unchanged if already split
    or if no location is present).
    """
    if not meta or "·" in meta:
        return strip_elapsed_duration(meta)
    # Prefer the duration-paren anchor when present: location is whatever
    # comes after the closing paren.
    m = re.search(r"\)\s+(.+)$", meta)
    if m and m.group(1).strip():
        return f"{strip_elapsed_duration(meta[:m.start()+1].strip())} · {m.group(1).strip()}"
    # No duration parens (e.g. Education "2016 - 2021 Some City"). Split on
    # the end of the date range, recognized via END_TOKEN.
    m = re.match(rf"^(.+?{END_TOKEN})\s+([A-Z].+)$", meta, re.IGNORECASE)
    if m:
        return f"{strip_elapsed_duration(m.group(1).strip())} · {m.group(2).strip()}"
    return strip_elapsed_duration(meta)


def strip_elapsed_duration(text: str) -> str:
    """Remove LinkedIn elapsed-duration parens like '(2 yrs 4 mos)'."""
    text = re.sub(r"\s*\([^)]*(?:yr|yrs|mo|mos)[^)]*\)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def translate(s: str) -> str:
    if not s:
        return s
    for k, v in ES_PHRASES.items():
        s = s.replace(k, v)
    for es, en in ES_MONTHS_EN.items():
        s = re.sub(rf"\b{es}\b", en, s, flags=re.IGNORECASE)
    # "January de 2024" → "January 2024" (the connecting "de")
    s = re.sub(r"\bde\s+(?=\d{4}\b)", "", s)
    # Durations
    s = re.sub(r"\baños\b", "yrs", s)
    s = re.sub(r"\baño\b", "yr", s)
    s = re.sub(r"\bmeses\b", "mos", s)
    s = re.sub(r"\bmes\b", "mo", s)
    s = re.sub(r"\bActualidad\b|\bPresente\b", "Present", s)
    return s


# ---------------------------------------------------------------------------
# Tech-skill detection. Curated keyword bank — extend as needed.
# ---------------------------------------------------------------------------
SKILL_CATEGORIES: dict[str, list[str]] = {
    "Languages": ["Python", "JavaScript", "TypeScript", "Node.js",
                  "PHP", "Java", "Go"],
    "Frameworks": ["FastAPI", "Flask", "Django-Ninja", "Django",
                   "Express.js", "Vue.js", "React"],
    "Cloud & DevOps": [
        "AWS Lambda", "AWS S3", "AWS DynamoDB", "AWS Step Functions",
        "AWS EventBridge", "AWS CDK", "AWS Powertools", "AWS API Gateway",
        "AWS SQS", "AWS SNS", "AWS Appflow", "AWS",
        "GCP", "Docker", "Kubernetes", "Terraform", "GitHub Actions",
        "Serverless", "CI/CD",
    ],
    "Databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "RabbitMQ"],
    "APIs & Integrations": [
        "Salesforce", "Plaid", "Twilio", "Polygon",
        "InteractiveBrokers", "TradingView", "Shopify",
        "Encompass", "Socure", "FedEx", "DHL", "UPS",
    ],
    "Testing & Tools": ["Pytest", "Moto", "Selenium", "RQ", "Cryptography"],
}
# Common typos / variants in the source PDF, mapped to canonical names.
SKILL_VARIANTS = {
    "PostgresSQL": "PostgreSQL",
    "Postgres SQL": "PostgreSQL",
    "Postgres": "PostgreSQL",
    "NodeJS": "Node.js",
}


def extract_skills(corpus: str) -> dict[str, list[str]]:
    for variant, canonical in SKILL_VARIANTS.items():
        corpus = re.sub(rf"\b{re.escape(variant)}\b", canonical, corpus,
                        flags=re.IGNORECASE)
    # Match longest skill names first so "AWS Lambda" wins over "AWS".
    flat = [(cat, sk) for cat, sks in SKILL_CATEGORIES.items() for sk in sks]
    flat.sort(key=lambda x: -len(x[1]))
    masked = corpus
    grouped: dict[str, list[str]] = {}
    for cat, sk in flat:
        pat = re.compile(rf"\b{re.escape(sk)}\b", re.IGNORECASE)
        if pat.search(masked):
            grouped.setdefault(cat, []).append(sk)
            masked = pat.sub(" " * len(sk), masked)
    for cat in grouped:
        grouped[cat].sort(key=str.lower)
    return grouped


@dataclass
class Entry:
    title: str = ""
    meta: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class Doc:
    name: str = ""
    headline: str = ""
    location: str = ""
    contacts: list[str] = field(default_factory=list)
    summary_text: str = ""
    skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    honors: list[str] = field(default_factory=list)
    sections: dict[str, list[Entry]] = field(default_factory=dict)
    tech_skills: dict[str, list[str]] = field(default_factory=dict)


def extract(pdf: Path, workdir: Path) -> list[dict]:
    opendataloader_pdf.convert(
        input_path=[str(pdf)], output_dir=str(workdir), format="json",
    )
    candidates = list(workdir.rglob(f"{pdf.stem}.json")) or \
                 list(workdir.rglob("*.json"))
    if not candidates:
        sys.exit(f"opendataloader produced no JSON in {workdir}")
    flat: list[dict] = []
    _walk(json.loads(candidates[0].read_text()), flat)
    return flat


def _walk(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("content"), str) and node["content"].strip():
            out.append(node)
        for v in node.values():
            _walk(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk(v, out)


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def section_for_heading(content: str) -> str | None:
    return SECTION_LOOKUP.get(_clean(content).lower())


def parse(elements: list[dict]) -> Doc:
    doc = Doc()

    # Step 1: identify the name (highest-priority hl=1 heading).
    name_idx = None
    for i, el in enumerate(elements):
        if el.get("heading level") == 1:
            doc.name = _clean(el["content"])
            name_idx = i
            break

    # Step 2: walk elements, tracking current section by heading levels 2/3.
    current: str | None = None
    section_buf: dict[str, list[dict]] = {}
    # Lines between the name and the first body section are headline/location.
    header_buf: list[str] = []
    saw_first_body_section = False

    for i, el in enumerate(elements):
        if i == name_idx:
            # Reset so subsequent paragraphs go to header_buf, not the
            # last sidebar section (Honors) that was current pre-name.
            current = None
            continue
        content = _clean(el["content"])
        if not content or PAGE_RE.match(content):
            continue
        hl = el.get("heading level")
        if hl in (2, 3):
            sk = section_for_heading(content)
            if sk:
                current = sk
                section_buf.setdefault(sk, [])
                if hl == 2 or sk in ("Summary", "Experience", "Education"):
                    saw_first_body_section = True
                continue
            # Unknown heading — skip but reset current to avoid bleed.
            current = None
            continue
        # Non-heading content.
        if name_idx is not None and i > name_idx and not saw_first_body_section \
                and current is None:
            header_buf.append(content)
        elif current is not None:
            section_buf[current].append(el)
        # else: orphan content before the name — ignore.

    # Step 3: split header_buf into headline + location.
    # LinkedIn typically renders one paragraph "<headline>\n<location>" but
    # opendataloader may emit them as one element with embedded \n. Split.
    flat_header: list[str] = []
    for h in header_buf:
        flat_header.extend(p.strip() for p in re.split(r"\s*\n\s*", h) if p.strip())
    if flat_header:
        # Heuristic: the last line is the location (short, no @|/), the
        # earlier lines join into the headline.
        if len(flat_header) == 1:
            # Try to split: location is often the trailing capitalized word(s).
            line = flat_header[0]
            doc.headline = line
        else:
            doc.location = flat_header[-1]
            doc.headline = " ".join(flat_header[:-1])

    # Step 4: fill per-section data.
    for el in section_buf.get("Contact", []):
        for line in re.split(r"\s*\n\s*", el["content"]):
            for m in EMAIL_RE.findall(line):
                doc.contacts.append(m)
            for m in URL_RE.findall(line):
                doc.contacts.append(m.rstrip(".,;"))

    if "Summary" in section_buf:
        doc.summary_text = " ".join(
            _clean(e["content"]) for e in section_buf["Summary"]
        ).strip()

    for el in section_buf.get("Skills", []):
        doc.skills.extend(_split_skills(_clean(el["content"])))

    for el in section_buf.get("Languages", []):
        doc.languages.append(_clean(el["content"]))

    for el in section_buf.get("Certifications", []):
        # Each line is a separate certification.
        for line in re.split(r"\s*\n\s*", el["content"]):
            line = _clean(line)
            if line:
                doc.certifications.append(line)

    for el in section_buf.get("Honors", []):
        for line in re.split(r"\s*\n\s*", el["content"]):
            line = _clean(line)
            if line:
                doc.honors.append(line)

    for name in ("Experience", "Education", "Projects",
                 "Publications", "Volunteer"):
        if name in section_buf:
            doc.sections[name] = _parse_entries(section_buf[name])

    # Translate Spanish → English on every user-visible field.
    doc.name = translate(doc.name)
    doc.headline = translate(doc.headline)
    doc.location = translate(doc.location)
    doc.summary_text = translate(doc.summary_text)
    doc.languages = [translate(l) for l in doc.languages]
    doc.certifications = [translate(c) for c in doc.certifications]
    doc.honors = [translate(h) for h in doc.honors]
    for entries in doc.sections.values():
        for e in entries:
            e.title = translate(e.title)
            e.meta = split_date_location(translate(e.meta))
            e.bullets = [translate(b) for b in e.bullets]

    # Extract tech skills from experience + projects bullets.
    corpus_parts: list[str] = []
    for key in ("Experience", "Projects"):
        for e in doc.sections.get(key, []):
            corpus_parts.append(e.title)
            corpus_parts.extend(e.bullets)
    doc.tech_skills = extract_skills(" ".join(corpus_parts))

    return doc


def _split_skills(line: str) -> list[str]:
    if "," in line:
        return [s.strip() for s in line.split(",") if s.strip()]
    # LinkedIn renders top skills as space-separated multi-word items. We can't
    # perfectly split (e.g. "Amazon Step Functions Amazon DynamoDB Amazon S3"
    # has no separator) — preserve as a single string and let the user split.
    return [line]


def _parse_entries(elements: list[dict]) -> list[Entry]:
    """LinkedIn entry pattern in the JSON stream:
        Company / School     fs >= 12  (sometimes hl=4)
        Title / Degree       fs ~ 11.5 (sometimes hl=5)
        <date range>         fs ~ 10.5, matches DATE_RE
        Intro paragraph(s)   fs ~ 10.5, no '-' prefix
        - Bullets            fs ~ 10.5, '-' prefix
    Font size distinguishes "next-entry header" lines (>=11) from
    intro/body lines (<=10.5), removing the ambiguity that pure text
    heuristics can't resolve.
    """
    entries: list[Entry] = []
    pending: list[str] = []   # company/title lines awaiting a date

    def emit(meta: str) -> None:
        e = Entry(meta=meta)
        org = pending[0] if pending else ""
        title = pending[1] if len(pending) > 1 else ""
        e.title = f"{org} — {title}" if title else org
        pending.clear()
        entries.append(e)

    for el in elements:
        for raw in re.split(r"\s*\n\s*", el["content"]):
            line = raw.strip()
            if not line:
                continue
            fs = el.get("font size") or 0
            if DATE_RE.match(line):
                emit(line)
                continue
            if BULLET_PREFIX.match(line):
                text = BULLET_PREFIX.sub("", line)
                if entries:
                    entries[-1].bullets.append(text)
                else:
                    pending.append(text)
                continue
            if fs >= 11:
                # Company / title for the *next* entry.
                pending.append(line)
            else:
                # Intro/body paragraph for the current entry.
                if entries:
                    entries[-1].bullets.append(line)
                else:
                    pending.append(line)

    # Flush trailing pending — happens for entries whose only date sits at the
    # end of a line (e.g. Education: "Degree · (2016 - 2021)") and so didn't
    # trigger DATE_RE. Emit a date-less entry from what we have.
    if pending:
        emit("")

    return entries


def render(doc: Doc) -> str:
    out: list[str] = []
    out.append(f"# {doc.name or 'Unknown'}")
    bits = [b for b in (doc.headline, doc.location) if b]
    if bits:
        out.append(f"> {' · '.join(bits)}")
    if doc.contacts:
        out.append(f"> {' · '.join(dict.fromkeys(doc.contacts))}")
    out.append("")

    for name in EMIT_ORDER:
        if name == "Summary" and doc.summary_text:
            out += ["## Summary", doc.summary_text, ""]
        elif name == "TechSkills" and doc.tech_skills:
            out.append("## Skills")
            for cat, items in doc.tech_skills.items():
                out.append(f"**{cat}:** {', '.join(items)}")
            out.append("")
        elif name == "Skills" and doc.skills:
            out += ["## Skills", ", ".join(dict.fromkeys(doc.skills)), ""]
        elif name == "Languages" and doc.languages:
            out += ["## Languages", ", ".join(doc.languages), ""]
        elif name == "Certifications" and doc.certifications:
            out.append("## Certifications")
            for c in doc.certifications:
                out.append(f"### {c}")
            out.append("")
        elif name == "Honors" and doc.honors:
            out.append("## Honors & Awards")
            for h in doc.honors:
                out.append(f"### {h}")
            out.append("")
        elif name in doc.sections and doc.sections[name]:
            display = {"Volunteer": "Volunteer Experience"}.get(name, name)
            out.append(f"## {display}")
            for e in doc.sections[name]:
                out.append(f"### {e.title or '(untitled)'}")
                if e.meta:
                    out.append(f"*{e.meta}*")
                for b in e.bullets:
                    out.append(f"- {b}")
                out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--keep-raw", action="store_true",
                    help="Keep opendataloader's intermediate JSON.")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    workdir = args.out.parent if args.keep_raw else Path(tempfile.mkdtemp())
    elements = extract(args.input, workdir)
    doc = parse(elements)
    args.out.write_text(render(doc))
    print(f"wrote {args.out}: name={doc.name!r}, "
          f"experience={len(doc.sections.get('Experience', []))}, "
          f"education={len(doc.sections.get('Education', []))}, "
          f"skills={len(doc.skills)}, certs={len(doc.certifications)}, "
          f"honors={len(doc.honors)}")


if __name__ == "__main__":
    main()
