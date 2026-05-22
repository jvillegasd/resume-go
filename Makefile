IMAGE := resume-go
WORK  := $(CURDIR)
# Mount scripts/ and templates/ from the host so edits don't need a rebuild.
MOUNTS := -v $(WORK):/work \
          -v $(WORK)/scripts:/app/scripts \
          -v $(WORK)/templates:/app/templates

.PHONY: build run shell md tex linkedin-source clean

build:
	docker build -t $(IMAGE) .

# Full pipeline: Profile.pdf → build/resume.pdf
run:
	docker run --rm $(MOUNTS) $(IMAGE)

# Step 1 only — stop after build/resume.md so you can hand-edit.
md:
	docker run --rm $(MOUNTS) $(IMAGE) \
		python scripts/pdf_to_md.py --input /work/Profile.pdf --out /work/build/resume.md

# Step 2 only — render + compile an already-edited build/resume.md.
tex:
	docker run --rm $(MOUNTS) $(IMAGE) \
		python scripts/md_to_tex.py --input /work/build/resume.md --out /work/build/resume.tex --compile

# LinkedIn source markdown only — Profile.pdf → build/linkedin_source.md
linkedin-source:
	docker run --rm $(MOUNTS) $(IMAGE) \
		python scripts/profile_to_linkedin_md.py --input-pdf /work/Profile.pdf --out /work/build/linkedin_source.md

shell:
	docker run --rm -it $(MOUNTS) $(IMAGE) bash

clean:
	rm -rf build/
