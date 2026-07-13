# resume-go

LinkedIn PDF → ATS-optimized single-column LaTeX resume + LinkedIn profile optimizer.

Uses [Jake Gutierrez's resume template](https://github.com/jakegut/resume) (MIT). Powered by Claude Code skills for AI-assisted tailoring, scoring, and keyword optimization.

## What it does

| Goal | How |
|------|-----|
| LinkedIn PDF → clean resume markdown | `make md` |
| Markdown → compiled PDF resume | `make tex` |
| Score & improve resume content | `/improve-resume` |
| Tailor resume to a job description | `/tailor-resume` |
| Optimize for ATS keyword matching | `/resume-ats-optimize` |
| LinkedIn PDF → optimized LinkedIn copy | `/linkedin-profile-optimize` |

## Quick start (Docker, recommended)

Only Docker required on the host — Python, Java, and TeX Live are bundled in the image.

```bash
make build          # one-time: build the image
make md             # Profile.pdf → build/resume.md  (then hand-edit)
make tex            # build/resume.md → build/resume.pdf
# or in one shot:
make run
```

`make shell` drops you into the container for debugging.

## Local Python alternative

Requires Python 3.10+, Java 11+ JRE, and `latexmk`:

```bash
# macOS prereqs
brew install --cask temurin mactex-no-gui

python -m venv .venv && source .venv/bin/activate
pip install -e .

python scripts/pdf_to_md.py --input Profile.pdf --out build/resume.md
# hand-edit build/resume.md
python scripts/md_to_tex.py --input build/resume.md --out build/resume.tex --compile
```

Final output: `build/resume.pdf`.

### Fedora prerequisites

On Fedora, install Java plus the TeX Live packages used by the resume template:

```bash
sudo dnf install java-latest-openjdk-headless latexmk texlive-pdftex \
  texlive-preprint texlive-enumitem texlive-titlesec texlive-marvosym \
  texlive-fancyhdr texlive-tools texlive-metafont texlive-mfware
```

Then run the local Python commands above.

## Claude Code skills

Install [Claude Code](https://claude.ai/code), then use these slash commands from the project root:

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/improve-resume` | `improve my resume` | Scores resume across 11 dimensions, gives copy-ready suggestions |
| `/tailor-resume` | `tailor for <job>` | Rewrites bullets and skills to match a specific job description |
| `/resume-ats-optimize` | `ats optimize` | Injects missing ATS keywords without changing voice or structure |
| `/linkedin-to-ats` | `linkedin to ats` | Converts LinkedIn PDF to ATS-safe resume markdown |
| `/linkedin-profile-optimize` | `optimize linkedin` | Rewrites LinkedIn sections for discoverability and impact |

All skills work from `build/resume.md`. Run `make md` first if you haven't converted your PDF yet.

## Markdown schema

`scripts/pdf_to_md.py` emits, and `scripts/md_to_tex.py` expects, this shape:

```markdown
# Full Name
> Headline · Location
> email · linkedin.com/in/handle · github.com/handle

## Summary
Free-form paragraph.

## Experience
### Company — Title
*Jan 2022 – Present · Location*
- Bullet one.
- Bullet two.

## Education
### School — Degree
*2016 – 2020*

## Skills
Comma, separated, list.
```

## LinkedIn markdown schema

`scripts/profile_to_linkedin_md.py` emits, and `scripts/normalize_linkedin_md.py` enforces:

```markdown
# Full Name

## Headline
Concise keyword-rich LinkedIn headline.

## Location
City, Country

## About
Short paragraphs tailored to the target role family.

## Experience
### Company — Title
*Jan 2022 – Present · Location*
- Impact-oriented bullet.

## Education
### School — Degree
*2016 – 2020*

## Skills
- Skill cluster
```

`build/` is gitignored — treat these as working artifacts:

- `build/resume.md` — editable resume source
- `build/resume.pdf` — compiled output
- `build/linkedin_source.md` — normalized LinkedIn extraction
- `build/linkedin_optimized.md` — final LinkedIn copy

## License

MIT
