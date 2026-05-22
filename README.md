# resume-go

Turn a LinkedIn-exported `Profile.pdf` into an ATS-optimized single-column
LaTeX resume (Jake Gutierrez's template, MIT).

## Run (Docker, recommended)

Bundles Python, Java 17, and a minimal TeX Live — only Docker is needed on the host.

```bash
make build          # one-time: build the image
make md             # Profile.pdf → build/resume.md  (then hand-edit)
make tex            # build/resume.md → build/resume.pdf
# or in one shot:
make run
```

`make shell` drops you into the container if you want to poke around.

## Run (local Python, alternative)

Requires Python 3.10+, Java 11+ JRE, and `latexmk`:

```bash
# macOS prereqs
brew install --cask temurin mactex-no-gui

python -m venv .venv && source .venv/bin/activate
pip install -e .

python scripts/pdf_to_md.py --input Profile.pdf --out build/resume.md
# (optional) hand-edit build/resume.md
python scripts/md_to_tex.py --input build/resume.md --out build/resume.tex --compile
```

Final output: `build/resume.pdf`.

## Markdown schema

`scripts/pdf_to_md.py` emits, and `scripts/md_to_tex.py` expects, this exact
shape — edit between the two steps as needed:

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
