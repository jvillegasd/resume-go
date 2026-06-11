---
name: improve-resume
description: >
  Evaluates a resume holistically across 11 dimensions and proposes structured,
  prioritized improvements with copy-ready suggestions per company/section.
  Supports deep-dive mode to rewrite any role's bullets point-by-point.
  Triggers on: "improve my resume", "review my resume", "evaluate my resume",
  "give me resume feedback", "audit my resume", "score my resume",
  "analyze my resume", "improve this experience", "drill into this role".
  Use AFTER /linkedin-to-ats has produced build/resume.md, or when the user
  pastes resume content directly. For ATS keyword optimization use /resume-ats-optimize.
---

# improve-resume

## Goal

Act as a resume coach. Read the resume, evaluate it across 11 quality dimensions,
and output structured improvement suggestions grouped by priority (alta / media / baja).
Each analysis is independent — improving the CV may surface new points, and the
score can shift between iterations. After the analysis, offer to drill into any
single role or section point-by-point.

---

## Step 1 — Input Detection

Check for the resume in this order:
1. Read `build/resume.md` if it exists.
2. If not found, ask the user to either paste their resume content or run `/linkedin-to-ats` first to extract it.

Before evaluating, ask one optional scoping question:
> "What role or specialization are you targeting? (e.g. Senior Backend Engineer, Staff Platform Engineer — or skip to evaluate as-is)"

Use the target role to weight the Technical Skills Hierarchy and Specialization Consistency dimensions. If the user skips, evaluate generically.

---

## Step 2 — Evaluation

Evaluate the resume against all 11 dimensions below. For each dimension, assign a priority:
- **Alta** — critical gap; hurts ATS pass rate or recruiter impression significantly
- **Media** — noticeable weakness; worth fixing before submitting
- **Baja** — polish; nice to have but won't block a callback

### Dimensions

**1. Achievement Quantification**
Check every bullet in every role. Is the outcome expressed with at least one of: number, %, time saved, cost reduced, scale (users, requests/sec, services)?
- Alta if 3+ roles are missing quantification entirely.
- Media if some roles have it but recent roles don't.
- Baja if only older or peripheral roles are missing it.

**2. Results-Focused Language**
Check for task-description language ("Designed and developed X", "Responsible for Y", "Worked on Z") vs. impact language ("Reduced", "Scaled", "Enabled", "Delivered", "Cut", "Improved").
- Alta if >50% of bullets describe tasks rather than outcomes.
- Media if recent roles use task language.
- Baja if only peripheral bullets are affected.

**3. Technical Skills Hierarchy**
Are the skills listed in order of relevance to the target role (if provided)? Core languages and frameworks first, tooling and utilities last. Do skills in the Skills section match what's emphasized in Experience bullets?
- Alta if core tech for the target role appears buried or missing.
- Media if order is suboptimal but the content is present.
- Baja if it's mostly fine with minor reordering needed.

**4. Specialization Consistency**
Does the narrative across all roles reinforce a single clear specialization (e.g. backend, platform, MLOps, fintech)? Or does it scatter focus across unrelated domains?
- Alta if roles contradict each other or signal unclear career direction.
- Media if one role is an outlier that weakens the narrative.
- Baja if the narrative is consistent with minor drift.

**5. Bullet Consistency**
Uniform punctuation (all end with period or none do), consistent capitalization, similar line length, same tense (past for past roles, present for current), consistent indentation across all roles.
- Alta if multiple rules are violated across 3+ companies.
- Media if isolated violations exist.
- Baja if only one or two minor inconsistencies.

**6. Section Header Structure**
Headers like "Experience", "Education", "Skills" must be plain text, parseable by ATS. No decorative characters (emojis, lines, symbols). Dates and locations must follow a consistent format.
- Alta if decorative chars are present or headers would break ATS parsing.
- Media if format is inconsistent but parseable.
- Baja if headers are fine with minor formatting tweaks needed.

**7. Certifications**
Is there a Certifications section? If certifications are mentioned inline in bullets or skills, they should have their own section with verification IDs.
- Alta if certifications exist in bullets/skills but no dedicated section.
- Media if section exists but IDs are missing.
- Baja if section is absent and it's genuinely unknown whether certs exist.

**8. Education Detail**
Is the education section present and correctly formatted (school, degree, dates)? Are any relevant academic projects, theses, or honors missing that could strengthen the narrative?
- Alta if education section is absent or malformed.
- Media if present but missing relevant projects.
- Baja if format is correct and nothing obvious is missing.

**9. Link Optimization**
Are LinkedIn and GitHub URLs present? Are they formatted as clean URLs (not raw redirects or profile IDs)?
- Alta if links are absent entirely.
- Media if links are present but not in clickable/clean format.
- Baja if minor formatting improvements are possible.

**10. Contact & Location**
Is there a city/region of residence? Is all contact info on one or two lines in the header? Is the email professional?
- Alta if contact info is missing or hard to parse.
- Media if location is absent.
- Baja if minor formatting improvements are possible.

**11. Space & Density**
Does the resume fit within 1-2 pages? Is whitespace used well? Are there underused sections that could hold stronger content, or bloated sections that dilute quality?
- Alta if resume exceeds 2 pages without justification.
- Media if there's significant whitespace that could hold more impact.
- Baja if it's within limits with minor optimization possible.

---

## Step 3 — Output Format

```
## Resume Improvement Analysis
> Each analysis is independent — improving the CV may surface new points. Score may shift between iterations.

---

### 🔴 Alta — [Dimension Name]

- **[Company/Section]**: [specific, copy-ready suggestion]
- **[Company/Section]**: [specific, copy-ready suggestion]

### 🟡 Media — [Dimension Name]

- [specific suggestion]
- [specific suggestion]

### 🟢 Baja — [Dimension Name]

- [specific suggestion]

---
**Summary:** X alta · Y media · Z baja improvements found.

Want me to drill into a specific role point-by-point? Just say "drill into [Company]" or "improve [role]".
```

Rules for suggestions:
- Name the specific company or section affected — never generic "in your resume".
- Make each suggestion self-contained and actionable without additional context.
- If a metric is needed but unknown, write: "Add the [metric type] — e.g. 'reduced X by Y%' — once you have the data."
- Maximum 3 suggestions per dimension; pick the highest-impact ones.
- Skip dimensions with no issues — don't force suggestions.

---

## Step 4 — Deep-Dive Mode

Triggered when the user says: "drill into [Company]", "improve [role]", "go point by point on [section]".

Process bullets **one at a time**, interactively. Do NOT show all bullets at once.

For each bullet, show:

```
**Bullet X of N — [Company]**

**Original:**
> [exact original bullet text]

**Proposed:**
> [rewritten bullet — stronger verb, impact framing, quantification if data available]

**Why:** [one sentence explaining the improvement]

⚠️ *Needs data: [what metric or fact is required to complete the rewrite]*  ← omit if no data needed

Apply this bullet? (yes / no / edit)
```

If the proposed bullet has a `⚠️ Needs data` flag, **do not show the apply prompt yet**. Instead, ask the specific question directly:

```
⚠️ Before applying: [specific question about the missing data — e.g. "What did these microservices handle — loan servicing, credit scoring, payments?"]
```

Wait for the user's answer, fold it into the proposed bullet, show the updated version, then ask:

```
Apply this bullet? (yes / no / edit)
```

Then wait for the user's response before showing the next bullet.

- **yes** — mark as accepted, move to next bullet
- **no** — keep original, move to next bullet
- **edit** — user provides a correction; incorporate it, show the updated version, and ask again

After all bullets are reviewed, show a summary:

```
**Deep-Dive Complete — [Company]**
X bullets accepted · Y kept as-is · Z edited

Apply all accepted bullets to build/resume.md? (yes / no)
```

Only write to `build/resume.md` after the final confirmation.

---

## Guardrails

- **Never invent metrics, percentages, scope, promotions, or ownership claims.**
- If a metric is missing, use directional language ("significantly reduced", "meaningfully improved") or explicitly flag it as needing real data.
- Preserve all truthful claims — only improve framing and language.
- Do not change job titles, company names, or dates.
- Bullets must stay ≤ 2 lines; prefer 1.
- Do not restructure the resume layout — this skill is content-only.
- For ATS keyword injection or full rewrites, recommend `/resume-ats-optimize`.
