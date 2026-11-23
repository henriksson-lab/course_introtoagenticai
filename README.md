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

Needs [Quarto](https://quarto.org/docs/get-started/). The site is served by
GitHub Pages from `docs/` on `main`.
