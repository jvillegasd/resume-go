#!/usr/bin/env python3
"""Shared parsing/rendering helpers for LinkedIn-derived profile data."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SECTION_ALIASES = {
    "Contact": ["Contact", "Contactar", "Contact Info"],
    "Skills": ["Top Skills", "Skills", "Aptitudes principales", "Aptitudes"],
    "Languages": ["Languages", "Idiomas"],
    "Certifications": ["Certifications", "Licenses & Certifications",
                       "Licencias y certificaciones"],
    "Honors": ["Honors-Awards", "Honors & Awards", "Reconocimientos"],
    "About": ["Summary", "About", "Extracto", "Acerca de"],
    "Experience": ["Experience", "Experiencia"],
    "Education": ["Education", "Educación", "Formación"],
    "Projects": ["Projects", "Proyectos"],
    "Publications": ["Publications", "Publicaciones"],
    "Volunteer": ["Volunteer Experience", "Experiencia de voluntariado"],
    "Headline": ["Headline"],
    "Location": ["Location", "Ubicación"],
}
SECTION_LOOKUP = {
    alias.lower(): canonical
    for canonical, aliases in SECTION_ALIASES.items()
    for alias in aliases
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
YEARISH_RE = re.compile(r"(?:19|20)\d{2}")
PAGE_RE = re.compile(r"^\s*(?:Page|Página)\s+\d+\s+(?:of|de)\s+\d+\s*$", re.I)
URL_RE = re.compile(
    r"(?:https?://\S+|(?:www\.|linkedin\.com|github\.com)[\w./\-]+)", re.I,
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
BULLET_PREFIX = re.compile(r"^[•‣◦▪▫●○\-\*]\s*")
MARKDOWN_TITLE_RE = re.compile(r"^###\s+(.+?)\s*$")
MARKDOWN_META_RE = re.compile(r"^\*(.+)\*\s*$")

RESUME_EMIT_ORDER = [
    "About", "Education", "Experience", "TechSkills", "Projects",
    "Honors", "Publications", "Volunteer",
]
LINKEDIN_EMIT_ORDER = [
    "Headline", "Location", "Contact", "About", "Experience", "Education",
    "Skills", "Certifications", "Languages", "Honors", "Projects",
    "Publications", "Volunteer",
]

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

SKILL_CATEGORIES: dict[str, list[str]] = {
    "Languages": ["Python", "JavaScript", "TypeScript", "Node.js",
                  "PHP", "Java", "Go"],
    "Frameworks": ["FastAPI", "Flask", "Django-Ninja", "Django",
                   "Express.js", "Vue.js", "React"],
    "Cloud & DevOps": [
        "AWS Lambda", "AWS S3", "AWS DynamoDB", "AWS Step Functions",
        "AWS EventBridge", "AWS CDK", "AWS Powertools", "AWS API Gateway",
        "AWS SQS", "AWS SNS", "AWS AppFlow", "AWS", "GCP", "Docker",
        "Kubernetes", "Terraform", "GitHub Actions", "Serverless", "CI/CD",
    ],
    "Databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "RabbitMQ"],
    "APIs & Integrations": [
        "Salesforce", "Plaid", "Twilio", "Polygon", "InteractiveBrokers",
        "TradingView", "Shopify", "Encompass", "Socure", "FedEx", "DHL",
        "UPS",
    ],
    "Testing & Tools": ["Pytest", "Moto", "Selenium", "RQ", "Cryptography"],
}
SKILL_VARIANTS = {
    "PostgresSQL": "PostgreSQL",
    "Postgres SQL": "PostgreSQL",
    "Postgres": "PostgreSQL",
    "NodeJS": "Node.js",
}


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
    about_text: str = ""
    skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    honors: list[str] = field(default_factory=list)
    sections: dict[str, list[Entry]] = field(default_factory=dict)
    tech_skills: dict[str, list[str]] = field(default_factory=dict)


def split_date_location(meta: str) -> str:
    if not meta or "·" in meta:
        return strip_elapsed_duration(meta)
    match = re.search(r"\)\s+(.+)$", meta)
    if match and match.group(1).strip():
        return (
            f"{strip_elapsed_duration(meta[:match.start()+1].strip())}"
            f" · {match.group(1).strip()}"
        )
    match = re.match(rf"^(.+?{END_TOKEN})\s+([A-Z].+)$", meta, re.IGNORECASE)
    if match:
        return (
            f"{strip_elapsed_duration(match.group(1).strip())}"
            f" · {match.group(2).strip()}"
        )
    return strip_elapsed_duration(meta)


def strip_elapsed_duration(text: str) -> str:
    text = re.sub(r"\s*\([^)]*(?:yr|yrs|mo|mos)[^)]*\)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def translate(text: str) -> str:
    if not text:
        return text
    for src, dst in ES_PHRASES.items():
        text = text.replace(src, dst)
    for src, dst in ES_MONTHS_EN.items():
        text = re.sub(rf"\b{src}\b", dst, text, flags=re.IGNORECASE)
    text = re.sub(r"\bde\s+(?=\d{4}\b)", "", text)
    text = re.sub(r"\baños\b", "yrs", text)
    text = re.sub(r"\baño\b", "yr", text)
    text = re.sub(r"\bmeses\b", "mos", text)
    text = re.sub(r"\bmes\b", "mo", text)
    text = re.sub(r"\bActualidad\b|\bPresente\b", "Present", text)
    return text


def extract_skills(corpus: str) -> dict[str, list[str]]:
    for variant, canonical in SKILL_VARIANTS.items():
        corpus = re.sub(rf"\b{re.escape(variant)}\b", canonical, corpus,
                        flags=re.IGNORECASE)
    flat = [(cat, skill) for cat, skills in SKILL_CATEGORIES.items()
            for skill in skills]
    flat.sort(key=lambda item: -len(item[1]))
    masked = corpus
    grouped: dict[str, list[str]] = {}
    for category, skill in flat:
        pattern = re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
        if pattern.search(masked):
            grouped.setdefault(category, []).append(skill)
            masked = pattern.sub(" " * len(skill), masked)
    for category in grouped:
        grouped[category].sort(key=str.lower)
    return grouped


def extract_pdf_elements(pdf: Path, workdir: Path) -> list[dict]:
    import opendataloader_pdf

    opendataloader_pdf.convert(
        input_path=[str(pdf)], output_dir=str(workdir), format="json",
    )
    candidates = list(workdir.rglob(f"{pdf.stem}.json")) or \
        list(workdir.rglob("*.json"))
    if not candidates:
        sys.exit(f"opendataloader produced no JSON in {workdir}")
    flat: list[dict] = []
    _walk_json(json.loads(candidates[0].read_text()), flat)
    return flat


def _walk_json(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("content"), str) and node["content"].strip():
            out.append(node)
        for value in node.values():
            _walk_json(value, out)
    elif isinstance(node, list):
        for value in node:
            _walk_json(value, out)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def section_for_heading(content: str) -> str | None:
    return SECTION_LOOKUP.get(_clean(content).lower())


def parse_pdf_elements(elements: list[dict]) -> Doc:
    doc = Doc()
    name_idx = None
    for idx, element in enumerate(elements):
        if element.get("heading level") == 1:
            doc.name = _clean(element["content"])
            name_idx = idx
            break

    current: str | None = None
    section_buf: dict[str, list[dict]] = {}
    header_buf: list[str] = []
    saw_first_body_section = False

    for idx, element in enumerate(elements):
        if idx == name_idx:
            current = None
            continue
        content = _clean(element["content"])
        if not content or PAGE_RE.match(content):
            continue
        heading_level = element.get("heading level")
        if heading_level in (2, 3):
            section_key = section_for_heading(content)
            if section_key:
                current = section_key
                section_buf.setdefault(section_key, [])
                if heading_level == 2 or section_key in (
                    "About", "Experience", "Education",
                ):
                    saw_first_body_section = True
                continue
            current = None
            continue
        if name_idx is not None and idx > name_idx and not saw_first_body_section \
                and current is None:
            header_buf.append(content)
        elif current is not None:
            section_buf[current].append(element)

    flat_header: list[str] = []
    for item in header_buf:
        flat_header.extend(
            piece.strip()
            for piece in re.split(r"\s*\n\s*", item)
            if piece.strip()
        )
    if flat_header:
        if len(flat_header) == 1:
            doc.headline = flat_header[0]
        else:
            doc.location = flat_header[-1]
            doc.headline = " ".join(flat_header[:-1])

    for element in section_buf.get("Contact", []):
        for line in re.split(r"\s*\n\s*", element["content"]):
            for match in EMAIL_RE.findall(line):
                doc.contacts.append(match)
            for match in URL_RE.findall(line):
                doc.contacts.append(match.rstrip(".,;"))

    if "About" in section_buf:
        doc.about_text = " ".join(
            _clean(element["content"]) for element in section_buf["About"]
        ).strip()

    for element in section_buf.get("Skills", []):
        doc.skills.extend(_split_skills(_clean(element["content"])))
    for element in section_buf.get("Languages", []):
        doc.languages.extend(_split_inline_items(element["content"]))
    for element in section_buf.get("Certifications", []):
        doc.certifications.extend(_split_inline_items(element["content"]))
    for element in section_buf.get("Honors", []):
        doc.honors.extend(_split_inline_items(element["content"]))

    for name in ("Experience", "Education", "Projects",
                 "Publications", "Volunteer"):
        if name in section_buf:
            doc.sections[name] = _parse_pdf_entries(section_buf[name])

    _translate_doc(doc)
    _derive_tech_skills(doc)
    return doc


def parse_profile_text(text: str) -> Doc:
    stripped = text.strip()
    if re.search(r"^\s*##\s+", stripped, flags=re.MULTILINE):
        return parse_linkedin_markdown(stripped)

    doc = Doc()
    lines = stripped.splitlines()
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines):
        first = lines[idx].strip()
        doc.name = first[2:].strip() if first.startswith("# ") else first
        idx += 1

    current: str | None = None
    sections: dict[str, list[str]] = {}
    header_buf: list[str] = []

    while idx < len(lines):
        raw = lines[idx].rstrip()
        stripped_line = raw.strip()
        heading = _detect_text_heading(stripped_line)
        if heading:
            current = heading
            sections.setdefault(heading, [])
            idx += 1
            continue
        if current:
            sections.setdefault(current, []).append(raw)
        elif stripped_line:
            header_buf.append(stripped_line)
        idx += 1

    if header_buf:
        doc.headline = header_buf[0]
    if len(header_buf) > 1:
        for line in header_buf[1:]:
            if EMAIL_RE.search(line) or URL_RE.search(line):
                doc.contacts.extend(_extract_contacts_from_line(line))
            elif not doc.location:
                doc.location = line

    doc.headline = doc.headline or _join_text_section(sections.pop("Headline", []))
    doc.location = doc.location or _join_text_section(sections.pop("Location", []))
    doc.contacts.extend(_extract_contacts_from_lines(sections.pop("Contact", [])))
    doc.about_text = _join_text_section(sections.pop("About", []))
    doc.skills = _parse_item_lines(sections.pop("Skills", []))
    doc.languages = _parse_item_lines(sections.pop("Languages", []))
    doc.certifications = _parse_item_lines(sections.pop("Certifications", []))
    doc.honors = _parse_item_lines(sections.pop("Honors", []))

    for name in ("Experience", "Education", "Projects",
                 "Publications", "Volunteer"):
        if name in sections:
            doc.sections[name] = _parse_text_entries(sections[name])

    _translate_doc(doc)
    _derive_tech_skills(doc)
    return doc


def parse_linkedin_markdown(text: str) -> Doc:
    doc = Doc()
    current: str | None = None
    entry_section: str | None = None
    current_entry: Entry | None = None
    freeform: dict[str, list[str]] = {}
    current_freeform = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            if current_freeform:
                freeform.setdefault(current_freeform, []).append("")
            continue
        if stripped.startswith("# "):
            doc.name = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            current = section_for_heading(stripped[3:].strip()) or stripped[3:].strip()
            current_freeform = current if current in (
                "Headline", "Location", "Contact", "About", "Skills",
                "Languages", "Certifications", "Honors",
            ) else None
            entry_section = current if current in (
                "Experience", "Education", "Projects", "Publications",
                "Volunteer",
            ) else None
            current_entry = None
            continue
        if entry_section and stripped.startswith("### "):
            current_entry = Entry(title=stripped[4:].strip())
            doc.sections.setdefault(entry_section, []).append(current_entry)
            continue
        if current_entry and MARKDOWN_META_RE.match(stripped):
            current_entry.meta = MARKDOWN_META_RE.match(stripped).group(1).strip()
            continue
        if current_entry and stripped.startswith("- "):
            current_entry.bullets.append(stripped[2:].strip())
            continue
        if current_entry and entry_section:
            current_entry.bullets.append(BULLET_PREFIX.sub("", stripped))
            continue
        if current_freeform:
            freeform.setdefault(current_freeform, []).append(line)

    doc.headline = _join_text_section(freeform.get("Headline", []))
    doc.location = _join_text_section(freeform.get("Location", []))
    doc.contacts = _extract_contacts_from_lines(freeform.get("Contact", []))
    doc.about_text = _join_text_section(freeform.get("About", []))
    doc.skills = _parse_item_lines(freeform.get("Skills", []))
    doc.languages = _parse_item_lines(freeform.get("Languages", []))
    doc.certifications = _parse_item_lines(freeform.get("Certifications", []))
    doc.honors = _parse_item_lines(freeform.get("Honors", []))
    doc.contacts = list(dict.fromkeys(doc.contacts))
    for entries in doc.sections.values():
        for entry in entries:
            entry.meta = split_date_location(translate(entry.meta))
            entry.title = translate(entry.title)
            entry.bullets = [translate(item) for item in entry.bullets]
    doc.headline = translate(doc.headline)
    doc.location = translate(doc.location)
    doc.about_text = translate(doc.about_text)
    doc.skills = [translate(item) for item in doc.skills]
    doc.languages = [translate(item) for item in doc.languages]
    doc.certifications = [translate(item) for item in doc.certifications]
    doc.honors = [translate(item) for item in doc.honors]
    _derive_tech_skills(doc)
    return doc


def render_resume_markdown(doc: Doc) -> str:
    out: list[str] = []
    out.append(f"# {doc.name or 'Unknown'}")
    header_bits = [item for item in (doc.headline, doc.location) if item]
    if header_bits:
        out.append(f"> {' · '.join(header_bits)}")
    if doc.contacts:
        out.append(f"> {' · '.join(dict.fromkeys(doc.contacts))}")
    out.append("")

    for name in RESUME_EMIT_ORDER:
        if name == "About" and doc.about_text:
            out += ["## Summary", doc.about_text, ""]
        elif name == "TechSkills" and doc.tech_skills:
            out.append("## Skills")
            for category, items in doc.tech_skills.items():
                out.append(f"**{category}:** {', '.join(items)}")
            out.append("")
        elif name == "Skills" and doc.skills:
            out += ["## Skills", ", ".join(dict.fromkeys(doc.skills)), ""]
        elif name == "Languages" and doc.languages:
            out += ["## Languages", ", ".join(doc.languages), ""]
        elif name == "Certifications" and doc.certifications:
            out.append("## Certifications")
            for item in doc.certifications:
                out.append(f"### {item}")
            out.append("")
        elif name == "Honors" and doc.honors:
            out.append("## Honors & Awards")
            for item in doc.honors:
                out.append(f"### {item}")
            out.append("")
        elif name in doc.sections and doc.sections[name]:
            display = {"Volunteer": "Volunteer Experience"}.get(name, name)
            out.append(f"## {display}")
            for entry in doc.sections[name]:
                out.append(f"### {entry.title or '(untitled)'}")
                if entry.meta:
                    out.append(f"*{entry.meta}*")
                for bullet in entry.bullets:
                    out.append(f"- {bullet}")
                out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_linkedin_markdown(doc: Doc) -> str:
    out: list[str] = [f"# {doc.name or 'Unknown'}", ""]

    for name in LINKEDIN_EMIT_ORDER:
        if name == "Headline" and doc.headline:
            out += ["## Headline", doc.headline, ""]
        elif name == "Location" and doc.location:
            out += ["## Location", doc.location, ""]
        elif name == "Contact" and doc.contacts:
            out.append("## Contact")
            for item in dict.fromkeys(doc.contacts):
                out.append(f"- {item}")
            out.append("")
        elif name == "About" and doc.about_text:
            out += ["## About", doc.about_text, ""]
        elif name == "Skills":
            items = doc.skills or _flatten_skill_groups(doc.tech_skills)
            if items:
                out.append("## Skills")
                for item in dict.fromkeys(items):
                    out.append(f"- {item}")
                out.append("")
        elif name == "Languages" and doc.languages:
            out.append("## Languages")
            for item in dict.fromkeys(doc.languages):
                out.append(f"- {item}")
            out.append("")
        elif name == "Certifications" and doc.certifications:
            out.append("## Certifications")
            for item in dict.fromkeys(doc.certifications):
                out.append(f"- {item}")
            out.append("")
        elif name == "Honors" and doc.honors:
            out.append("## Honors")
            for item in dict.fromkeys(doc.honors):
                out.append(f"- {item}")
            out.append("")
        elif name in doc.sections and doc.sections[name]:
            heading = {"Volunteer": "Volunteer Experience"}.get(name, name)
            out.append(f"## {heading}")
            for entry in doc.sections[name]:
                out.append(f"### {entry.title or '(untitled)'}")
                if entry.meta:
                    out.append(f"*{entry.meta}*")
                for bullet in entry.bullets:
                    out.append(f"- {bullet}")
                out.append("")

    return "\n".join(out).rstrip() + "\n"


def _parse_pdf_entries(elements: list[dict]) -> list[Entry]:
    entries: list[Entry] = []
    pending: list[str] = []

    def emit(meta: str) -> None:
        entry = Entry(meta=meta)
        org = pending[0] if pending else ""
        title = pending[1] if len(pending) > 1 else ""
        entry.title = f"{org} — {title}" if title else org
        pending.clear()
        entries.append(entry)

    for element in elements:
        for raw in re.split(r"\s*\n\s*", element["content"]):
            line = raw.strip()
            if not line:
                continue
            font_size = element.get("font size") or 0
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
            if font_size >= 11:
                pending.append(line)
            elif entries:
                entries[-1].bullets.append(line)
            else:
                pending.append(line)

    if pending:
        emit("")
    return entries


def _split_skills(line: str) -> list[str]:
    if "," in line:
        return [item.strip() for item in line.split(",") if item.strip()]
    return [line] if line else []


def _split_inline_items(text: str) -> list[str]:
    items: list[str] = []
    for line in re.split(r"\s*\n\s*", text):
        stripped = line.strip()
        if not stripped:
            continue
        stripped = BULLET_PREFIX.sub("", stripped)
        if " · " in stripped:
            parts = [part.strip() for part in stripped.split(" · ") if part.strip()]
            items.extend(parts)
        elif "," in stripped:
            parts = [part.strip() for part in stripped.split(",") if part.strip()]
            items.extend(parts)
        else:
            items.append(stripped)
    return items


def _translate_doc(doc: Doc) -> None:
    doc.name = translate(doc.name)
    doc.headline = translate(doc.headline)
    doc.location = translate(doc.location)
    doc.about_text = translate(doc.about_text)
    doc.skills = [translate(item) for item in doc.skills]
    doc.languages = [translate(item) for item in doc.languages]
    doc.certifications = [translate(item) for item in doc.certifications]
    doc.honors = [translate(item) for item in doc.honors]
    doc.contacts = list(dict.fromkeys(doc.contacts))
    for entries in doc.sections.values():
        for entry in entries:
            entry.title = translate(entry.title)
            entry.meta = split_date_location(translate(entry.meta))
            entry.bullets = [translate(item) for item in entry.bullets]


def _derive_tech_skills(doc: Doc) -> None:
    corpus_parts: list[str] = []
    for key in ("Experience", "Projects"):
        for entry in doc.sections.get(key, []):
            corpus_parts.append(entry.title)
            corpus_parts.extend(entry.bullets)
    doc.tech_skills = extract_skills(" ".join(corpus_parts))


def _detect_text_heading(line: str) -> str | None:
    if not line:
        return None
    normalized = line.strip().rstrip(":")
    if normalized.startswith("## "):
        normalized = normalized[3:].strip()
    return section_for_heading(normalized)


def _join_text_section(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(BULLET_PREFIX.sub("", stripped))
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs).strip()


def _extract_contacts_from_line(line: str) -> list[str]:
    contacts: list[str] = []
    contacts.extend(EMAIL_RE.findall(line))
    contacts.extend(match.rstrip(".,;") for match in URL_RE.findall(line))
    return list(dict.fromkeys(contacts))


def _extract_contacts_from_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        out.extend(_extract_contacts_from_line(stripped))
    return list(dict.fromkeys(out))


def _parse_item_lines(lines: list[str]) -> list[str]:
    items: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        stripped = BULLET_PREFIX.sub("", stripped)
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if " · " in stripped:
            items.extend(part.strip() for part in stripped.split(" · ") if part.strip())
        elif "," in stripped and "http" not in stripped and "@" not in stripped:
            items.extend(part.strip() for part in stripped.split(",") if part.strip())
        else:
            items.append(stripped)
    return list(dict.fromkeys(items))


def _parse_text_entries(lines: list[str]) -> list[Entry]:
    if any(MARKDOWN_TITLE_RE.match(line.strip()) for line in lines):
        return _parse_markdown_entries(lines)

    blocks: list[list[str]] = []
    current: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(stripped)
    if current:
        blocks.append(current)

    entries: list[Entry] = []
    for block in blocks:
        entries.append(_entry_from_text_block(block))
    return [entry for entry in entries if entry.title or entry.meta or entry.bullets]


def _parse_markdown_entries(lines: list[str]) -> list[Entry]:
    entries: list[Entry] = []
    current: Entry | None = None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        title_match = MARKDOWN_TITLE_RE.match(stripped)
        if title_match:
            current = Entry(title=title_match.group(1).strip())
            entries.append(current)
            continue
        if current is None:
            continue
        meta_match = MARKDOWN_META_RE.match(stripped)
        if meta_match and not current.meta:
            current.meta = meta_match.group(1).strip()
            continue
        if stripped.startswith("- "):
            current.bullets.append(stripped[2:].strip())
        else:
            current.bullets.append(BULLET_PREFIX.sub("", stripped))
    return entries


def _entry_from_text_block(block: list[str]) -> Entry:
    entry = Entry()
    if not block:
        return entry
    entry.title = BULLET_PREFIX.sub("", block[0])
    idx = 1
    if idx < len(block):
        candidate = BULLET_PREFIX.sub("", block[idx])
        if DATE_RE.match(candidate) or YEARISH_RE.search(candidate):
            entry.meta = split_date_location(candidate)
            idx += 1
    for raw in block[idx:]:
        bullet = BULLET_PREFIX.sub("", raw).strip()
        if bullet:
            entry.bullets.append(bullet)
    return entry


def _flatten_skill_groups(groups: dict[str, list[str]]) -> list[str]:
    flattened: list[str] = []
    for category, skills in groups.items():
        if skills:
            flattened.append(f"{category}: {', '.join(skills)}")
    return flattened
