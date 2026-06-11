---
name: tailor-resume
description: >
  Tailors build/resume.md for a specific job offer by injecting JD keywords,
  reordering skills, and refocusing bullets — without modifying the canonical resume.
  Outputs a separate build/resume_{slug}.md and renders build/resume_{slug}.pdf.
  Triggers on: "tailor my resume for", "optimize for this job", "customize resume for",
  "create a version for [company]", "tailor for this offer", "match my resume to this JD".
  Use when the user has a specific job description to target. For general improvements
  use /improve-resume. For generic ATS optimization use /resume-ats-optimize.
---

# tailor-resume

## Goal

Produce a job-specific version of the canonical resume that maximizes keyword match
and relevance for a single job description — without ever modifying `build/resume.md`.
Each tailored version lives as its own file so the user can apply to multiple companies
simultaneously, each with a dedicated optimized PDF.

---

## Step 1 — Input Collection

1. Read `build/resume.md` as the source of truth. **Never write to this file.**
2. If the user has not pasted a job description, ask:
   > "Please paste the full job description — title, responsibilities, and requirements."
3. Ask for the output slug:
   > "What slug should I use for the output file? (e.g. `stripe` → `build/resume_stripe.md`) — or skip to auto-derive from the company name."
   - If skipped, derive a lowercase, hyphen-separated slug from the company name in the JD (e.g. "Quantum Lending Solutions" → `quantum-lending`).

---

## Step 2 — JD Analysis

Parse the job description and extract:

| Signal | What to look for |
|---|---|
| **Required skills** | "must have", "required", "you have", "you bring" sections |
| **Preferred skills** | "nice to have", "bonus", "preferred", "ideally" |
| **Seniority** | Senior, Staff, Lead, Principal, IC4/5/6, "5+ years" |
| **Domain focus** | fintech, platform, infra, ML, payments, lending, etc. |
| **Key action verbs** | verbs the JD uses for the role (own, scale, drive, ship, design) |
| **High-weight keywords** | any term that appears 2+ times in the JD |

Produce an internal summary (not shown to user):
```
Required: [list]
Preferred: [list]
High-weight: [list]
Gaps (in JD but missing from resume): [list]
Strong matches (in both): [list]
Off-topic bullets (in resume but irrelevant to JD): [list]
```

---

## Step 3 — Gap Analysis

Compare JD signals against `build/resume.md`:

- **Injection candidates**: JD keywords absent from resume that the user genuinely has (based on their experience bullets, not invented).
- **Deprioritize**: Skills in resume not mentioned in JD — keep them but move to end of their category.
- **Promote**: Bullets that align well with JD focus — move to top of role's bullet list.
- **Trim**: Bullets with zero relevance to this JD — move to bottom or remove if space is tight.

---

## Step 4 — Generate Tailored Resume

Write `build/resume_{slug}.md` with these targeted changes:

### Headline (`>` line 1)
Rewrite to reflect the target role title and JD domain language.
- Original: `> Backend Engineer @ Quantum Lending Solutions | Python + AWS | ...`
- Tailored: `> Senior Backend Engineer | Python + AWS + [JD tech] | [JD domain phrase]`

### Skills Section
- Reorder categories so JD-relevant ones appear first.
- Within each category, move JD-matching items to the front.
- Inject missing JD keywords that are truthful — only add skills the user demonstrably has based on their experience bullets.
- Do not remove any existing skills; only reorder and add.

### Experience Bullets (per role, max 2 rewrites per role)
- Front-load JD-relevant verbs and keywords into the first clause.
- Mirror JD language where truthful (e.g. JD says "own" → replace "built" with "owned and shipped").
- Keep all metrics intact — never alter numbers.
- Move the most JD-relevant bullet to position 1 in each role if it isn't already.
- Never invent responsibilities, tools, or scope.

### Summary
Skip — not exported in the current build pipeline.

### What NOT to change
- Job titles, company names, dates, locations.
- Metrics (percentages, volumes, time savings).
- Education section.
- Honors & Awards.

---

## Step 5 — Render

Run the Docker render command targeting the new slug file:

```bash
docker run --rm \
  -v /Users/linkrs/Desktop/projects/resume-go:/work \
  -v /Users/linkrs/Desktop/projects/resume-go/scripts:/app/scripts \
  -v /Users/linkrs/Desktop/projects/resume-go/templates:/app/templates \
  resume-go \
  python scripts/md_to_tex.py \
    --input /work/build/resume_{slug}.md \
    --out /work/build/resume_{slug}.tex \
    --compile
```

Then open the PDF:
```bash
open /Users/linkrs/Desktop/projects/resume-go/build/resume_{slug}.pdf
```

Verify `build/resume.md` is unchanged after render.

---

## Step 6 — Output Summary

After writing and rendering, show:

```
## Tailored Resume — {slug}
> build/resume_{slug}.md → build/resume_{slug}.pdf

### Keywords injected
- [keyword] added to [Skills category]
- [keyword] added to [Skills category]

### Headline updated
- Before: [original]
- After:  [tailored]

### Bullets rewritten
**[Company]** bullet 1:
- Before: [original]
- After:  [tailored]

### Skills reordered
- [Category]: [new order]

### Gaps (in JD but not in your background — not injected)
- [keyword]: [why it wasn't added]

build/resume.md — unchanged ✓
```

---

## Guardrails

- **Never write to `build/resume.md`** — it is read-only for this skill.
- **Never invent metrics, promotions, titles, tools, or scope.**
- If a JD keyword is missing from the resume AND genuinely absent from the user's background, list it as a gap — never inject it.
- Bullets must stay ≤ 2 lines; prefer 1.
- Do not add new roles, education, or sections — tailoring is content-only.
- Unicode arrows (`→`) are ATS-unsafe — use "to" instead.
- If the tailored resume exceeds 2 pages, flag it and suggest which bullets to trim.
- Maximum 2 bullet rewrites per role to avoid over-engineering older, less relevant positions.
- All injected keywords must be verifiable in the user's existing experience bullets or skills — no hallucination.
