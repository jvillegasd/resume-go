# resume-go

Turn a LinkedIn-exported `Profile.pdf` into an ATS-optimized single-column
LaTeX resume (Jake Gutierrez's template, MIT).

This repo also supports generating an **optimized LinkedIn-profile markdown**
artifact from either `Profile.pdf` or pasted/exported LinkedIn profile text.

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

## LinkedIn profile optimization

Generate a LinkedIn-oriented source markdown file from the PDF:

```bash
make linkedin-source
# or locally:
python scripts/profile_to_linkedin_md.py \
  --input-pdf Profile.pdf \
  --out build/linkedin_source.md
```

Generate the same source markdown from pasted/exported text:

```bash
python scripts/profile_to_linkedin_md.py \
  --input-text profile.txt \
  --out build/linkedin_source.md
```

After rewriting the copy into an optimized draft, normalize it into the
canonical final file:

```bash
python scripts/normalize_linkedin_md.py \
  --input build/linkedin_optimized.draft.md \
  --out build/linkedin_optimized.md
```

The project-local skill
`.claude/skills/linkedin-profile-optimize/SKILL.md`
orchestrates the full source → optimize → normalize workflow.

When the extracted source misses important business context, edit
`build/linkedin_source.md` first, then rerun the optimization flow. This is
the best place to add clarifications such as project purpose, decision logic,
domain context, or the human/business meaning of a system's output.

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

## LinkedIn markdown schema

`scripts/profile_to_linkedin_md.py` emits, and
`scripts/normalize_linkedin_md.py` enforces, this shape:

```markdown
# Full Name

## Headline
Concise keyword-rich LinkedIn headline.

## Location
City, Country

## Contact
- linkedin.com/in/handle

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

Because `build/` is gitignored, treat these markdown files as working artifacts:

- `build/linkedin_source.md` — normalized extraction you can refine
- `build/linkedin_optimized.draft.md` — rewritten draft before validation
- `build/linkedin_optimized.md` — final normalized LinkedIn copy
