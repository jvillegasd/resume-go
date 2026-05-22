# LinkedIn-PDF → ATS resume builder.
# Bundles Python 3.12, JRE 17 (for opendataloader-pdf) and a minimal TeX Live
# install with the packages Jake Gutierrez's template needs.
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jre-headless \
        latexmk \
        texlive-latex-base \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        lmodern \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir opendataloader-pdf jinja2

COPY scripts/ ./scripts/
COPY templates/ ./templates/

# Default: full pipeline on /work/Profile.pdf → /work/build/resume.pdf
# Override by passing your own command: `docker run ... resume-go bash`
CMD ["bash", "-c", "\
    python scripts/pdf_to_md.py --input /work/Profile.pdf --out /work/build/resume.md && \
    python scripts/md_to_tex.py --input /work/build/resume.md --out /work/build/resume.tex --compile \
"]
