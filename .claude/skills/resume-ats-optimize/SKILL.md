---
name: resume-ats-optimize
description: Optimize an already-parsed resume in this project for ATS and recruiter best practices by rewriting build/resume.md into a stronger backend/platform-oriented resume. Use when the user says "optimize my resume", "make this ATS friendly", "improve my CV bullets", "rewrite my parsed resume", "improve job descriptions", or when build/resume.md already exists and needs post-parse content improvement.
---

# Resume ATS Optimize

Use this skill **after** the resume has already been parsed into `build/resume.md`.
If `build/resume.md` does not exist yet and the user is starting from a LinkedIn PDF,
use the `linkedin-to-ats` skill first.

## Goal

Turn the parsed markdown resume into a recruiter-friendly, ATS-safe resume by
improving the **content**, not the extraction pipeline. Focus on summary,
experience bullets, skill taxonomy, and section usefulness.

## Intake first

Before rewriting, collect the minimum facts needed to avoid a generic or
misleading resume:

- target role family (for example: backend, platform, fintech backend)
- master resume vs one specific job description
- page-length target
- whether to use verified metrics only, directional impact, or placeholders
- any must-keep or must-remove sections

If the user gives little direction, default to a **master backend/platform
resume** with truthful, directional-impact wording.

## Source of truth

- Read `build/resume.md` first.
- Preserve the markdown schema expected by this repo.
- Edit the markdown, not the PDF.
- Keep standard section headings so ATS parsing remains simple.

Expected schema:

```markdown
# Full Name
> headline/location line may exist
> contact line

## Summary
...

## Experience
### Company — Title
*Jan 2022 - Present · Location*
- Bullet

## Education
...

## Skills
...
```

## Optimization workflow

1. **Assess the current resume**
   - Identify weak LinkedIn-export phrasing.
   - Flag bullets that are only duties, tool dumps, or generic team membership.
   - Check whether recent roles carry the narrative and older roles are too detailed.
   - Check whether the summary and skills reflect the target role.

2. **Rewrite for ATS + recruiters**
   - Add or tighten a short Summary section near the top.
   - Prioritize recent, relevant experience.
   - Compress older roles when they do not add much signal.
   - Use standard, searchable terminology naturally.
   - Keep formatting plain and machine-readable.

3. **Improve bullets**
   - Start with a strong action verb.
   - Lead with outcome or business/technical impact when known.
   - Add scope and systems context.
   - Mention tools naturally instead of in long parenthetical stacks.
   - Remove filler like "worked with", "member of the team", or
     "responsible for" unless truly necessary.
   - Prefer concise bullets over long paragraphs.

4. **Strengthen ATS keyword coverage**
   - Mirror the target job's language when a JD is available.
   - For backend/platform resumes, prefer terms like:
     backend, platform, microservices, APIs, distributed systems,
     event-driven architecture, AWS, Python, FastAPI, Django, testing,
     observability, integrations, cloud infrastructure.
   - Do not keyword-stuff; keep terms in real context.

## Rewrite rules

- Do **not** invent metrics, scope, promotions, or ownership.
- If metrics are missing, use directional impact honestly.
- Preserve truthful job titles unless the user explicitly confirms a better one.
- Keep section names standard: Summary, Experience, Education, Skills,
  Projects, Certifications, Languages.
- Prefer 4-6 bullets for recent roles, fewer for older roles.
- Remove low-value repetition across roles.
- If space is tight, cut weaker old bullets before trimming strong recent ones.

## Output contract

When using this skill:

1. Briefly summarize the main ATS/content issues found.
2. Produce the revised `build/resume.md` content or apply the rewrite directly,
   depending on the user's request.
3. If useful, call out 2-5 follow-up facts the user could provide later to make
   the resume stronger (for example: metrics, scale, latency, revenue impact,
   team size, volume handled).

## Guardrails

- This skill is for **post-parse optimization**, not PDF extraction.
- Prefer content improvements over template/layout changes.
- If the user later asks for job-specific tailoring, reuse the optimized master
  resume and then align keywords and summary to that job description.
