---
name: linkedin-to-ats
description: Convert a LinkedIn-exported Profile.pdf into an ATS-optimized
  single-column LaTeX resume using Jake Gutierrez's template. Use when the
  user says "linkedin to resume", "make my resume", "ATS resume", "convert
  my linkedin profile", or drops a Profile.pdf in this project root.
---

# LinkedIn → ATS Resume

Two-stage offline pipeline. No LLM, no API keys.

```
Profile.pdf  ──(opendataloader-pdf, Java)──▶  build/resume.md
                                                    │
                                          user hand-edits
                                                    │
build/resume.tex  ◀──(jinja2 + Jake template)── build/resume.md
       │
       ▼ latexmk -pdf
   build/resume.pdf
```

## Prerequisites — check before running

**Preferred: Docker** (bundles Java + TeX, host only needs Docker):

```bash
docker --version
make build    # builds the resume-go image the first time
```

**Alternative: local install** (only if Docker isn't available):

```bash
java -version        # must be 11+
latexmk --version    # required only for --compile
python -c "import opendataloader_pdf"
```

If missing: `brew install --cask temurin mactex-no-gui` then `pip install -e .`.

## Workflow (Docker)

1. `make md` → `build/resume.md`. Read it and surface anything off.
2. Pause for the user to edit `build/resume.md`.
3. `make tex` → `build/resume.pdf`.

`make run` does steps 1 and 3 back-to-back (skip if the user wants to edit).

## Workflow (local Python)

1. **Extract.** Default input is `Profile.pdf` in the project root.
   ```bash
   python scripts/pdf_to_md.py --input Profile.pdf --out build/resume.md
   ```
   Read the generated `build/resume.md` and surface anything that looks wrong
   (split job titles, missing dates, mangled bullets) — common LinkedIn-export
   quirks are noted in the troubleshooting section below.

2. **Pause for edits.** Tell the user the markdown is ready and invite them
   to edit `build/resume.md` before LaTeX rendering. Do NOT skip this — the
   markdown is the canonical, human-friendly intermediate.

3. **Render & compile.**
   ```bash
   python scripts/md_to_tex.py --input build/resume.md \
       --out build/resume.tex --compile
   ```
   Result: `build/resume.pdf`.

## Canonical resume.md schema

Both scripts speak this exact shape. Preserve it when editing.

```markdown
# Full Name
> Headline · Location
> email · linkedin.com/in/handle · github.com/handle

## Summary
Free-form paragraph.

## Experience
### Company — Title
*Jan 2022 – Present · Location*
- Bullet.
- Bullet.

## Education
### School — Degree
*2016 – 2020*

## Skills
Comma, separated, list.
```

Section names recognized by the LaTeX renderer: `Summary`, `Experience`,
`Education`, `Projects`, `Skills`, `Certifications`, `Languages`. Unknown
`##` sections are parsed but not rendered — add them to the template if
you need them.

## Troubleshooting

- **No JSON produced** → Java not on PATH. opendataloader-pdf needs JRE 11+.
- **First job title duplicated into name** → header heuristic misfired; edit
  `build/resume.md` directly.
- **Dates missing from a role** → LinkedIn occasionally puts dates above the
  role title rather than below; reorder in the markdown.
- **LaTeX compile error on `&` or `%`** → the renderer escapes these, but if
  you hand-edit and introduce raw special chars in `build/resume.tex`, fix
  them or re-run step 3 from `build/resume.md`.
- **Resume spills to two pages** → trim bullets, shorten the Skills line, or
  drop older roles. Jake's template is tuned for one page.
