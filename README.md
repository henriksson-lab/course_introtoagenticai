# Introduction to agentic AI: course site sources

Teacher information. This file is not part of the published site.

Planning documents (not published): [contentplan.md](contentplan.md) (unit order
and the reasons for it), [audience.md](audience.md),
[designprinciples.md](designprinciples.md).

## Layout

One folder per unit, named after the topic (never renamed; order lives in the
sidebar in `_quarto.yml`). Each unit has `lec.qmd` (reveal.js slides with
speaker notes), `exercise.qmd`, figures `figNN-name.svg`, and sometimes
`data/` with example files plus the script that generated them.

## Building

```bash
make           # render the site to docs/
make preview   # live-reload preview
make clean     # delete docs/ and the Quarto cache
```

Needs [Quarto](https://quarto.org/docs/get-started/) (1.7.30, same as CI).

**Publishing:** every push to `main` triggers `.github/workflows/publish.yml`,
which renders the site and deploys it to GitHub Pages
(<https://henriksson-lab.github.io/course_introtoagenticai/>). `docs/` is
gitignored: render locally only to check slides (`make preview`, or
`quarto render <unit>/lec.qmd` and open `docs/<unit>/lec.html`).

**Slide overflow check:** after rendering, `python3 tools/check-overflow.py <unit> ...`
measures every slide in headless Chrome and lists slides taller than 720 px.
Rule (designprinciples §11): one font size everywhere; shrink images or split
slides instead.

Note: the *A course or project page* unit teaches participants the simpler
"commit `docs/`" approach on purpose; this repo uses Actions to keep history small.
