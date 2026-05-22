---
name: linkedin-profile-optimize
description: Generate an optimized LinkedIn-profile markdown file from a local Profile.pdf or pasted/exported profile text in this repo. Use when the user says "optimize my LinkedIn profile", "turn this profile into LinkedIn markdown", "improve this LinkedIn copy", or asks for build/linkedin_optimized.md from Profile.pdf or pasted profile content.
---

# LinkedIn Profile Optimize

Use this skill to create `build/linkedin_optimized.md`, optimized for the
LinkedIn profile itself rather than an ATS resume.

## Inputs

Supported v1 sources:

- local `Profile.pdf`
- pasted/exported LinkedIn profile text

Direct LinkedIn URL scraping is **out of scope** for this skill.

## Output files

- `build/linkedin_source.md` — normalized source content
- `build/linkedin_optimized.md` — final optimized profile copy

## Workflow

1. Detect the input type.
   - If `Profile.pdf` is available, generate source markdown with:
     `python scripts/profile_to_linkedin_md.py --input-pdf Profile.pdf --out build/linkedin_source.md`
   - If the user pasted profile text, save it to a temporary text file and run:
     `python scripts/profile_to_linkedin_md.py --input-text <file> --out build/linkedin_source.md`
2. Read `build/linkedin_source.md` and identify weak or missing areas:
   - headline too generic
   - about section too thin or too resume-like
   - experience bullets that are duty-based, tool-dumps, or unclear
   - missing keyword coverage for the target role family
3. Rewrite the profile into LinkedIn-oriented copy:
   - stronger headline
   - clearer About section
   - concise, outcome-oriented experience bullets
   - tighter skills list
4. Save the draft, then normalize and validate it:
   `python scripts/normalize_linkedin_md.py --input build/linkedin_optimized.draft.md --out build/linkedin_optimized.md`

## Canonical optimized markdown shape

```md
# Full Name

## Headline
...

## Location
...

## Contact
- linkedin.com/in/handle

## About
...

## Experience
### Company — Title
*Jan 2022 - Present · Location*
- Bullet

## Education
...

## Skills
- Skill cluster
```

`Headline` and `About` are required in the final file. Empty optional sections
should be omitted.

## Rewrite rules

- Do not invent titles, promotions, ownership, or metrics.
- Keep the copy truthful, stronger, and more specific.
- Optimize for LinkedIn readability and searchability, not LaTeX resume layout.
- Use standard role keywords naturally.
- Prefer concise bullets and short paragraphs.

## If the user actually wants an ATS resume

If the request is about resume generation or ATS formatting, use:

- `linkedin-to-ats` for PDF → resume markdown
- `resume-ats-optimize` for post-parse resume rewriting
