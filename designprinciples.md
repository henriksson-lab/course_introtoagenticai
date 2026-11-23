# Design principles

## 1. The agent types, the human judges
We teach delegation and verification, not programming. Code appears only when
reading it helps the participant judge the result.

## 2. Every unit ends in an artifact the participant keeps
A cleaned dataset, a script, a figure, a literature table, a web page, a demo.
Together these form the participant's portfolio.

## 3. Own ideas run through every unit
Each participant keeps one own project for the whole course; there is no
capstone. Every exercise has a worked example on shared data and an "on your own
project" part. Example projects exist for those without an idea.

## 4. Verification is part of every exercise
Each exercise says how to check the result: spot checks, a known answer,
rerunning, a second agent's review, looking up the reference. "It ran without
errors" never counts as checked.

## 5. Show prompts and sessions, not code
Slides show the prompt, what the agent did, and what we checked, with
screenshots of real sessions. Slides must work on their own, whether or not they
are recorded. Agents are non-deterministic, so we tell participants plainly that
their session will look different.

## 6. Tool-agnostic concepts, tool-specific instructions in one place
Each unit has a Claude Code and a Codex column where they differ. Version-specific
details (install commands, menu names, prices) live on one page that we update
each run.

## 7. Privacy by default
Example data is public or synthetic. Every exercise that invites own data has a
one-line reminder of what must not be sent to the cloud.

## 8. Lecture style follows 3MB00A
Each unit folder has a `lec.qmd` (reveal.js, same YAML header and theme as
3MB00A) and an `exercise.qmd`. Every deck has the same shape:

- **Title block.** `title` = the unit name; `subtitle` = "Part N: <part name>";
  `author` = the course name.
- **First slide: "About this lecture".** One short paragraph on the problem and
  why it matters, then 3–5 bullets with the key ideas, then one line saying what
  kind of unit this is and what is deferred to which later unit.
- **Second slide: the concrete problem.** A real task from teaching or research
  (a messy spreadsheet, 40 PDFs, a grant call) before any general concept.
- **Slide titles are claims**, full sentences that say the point ("The agent
  reads your files; a chat window does not"), not topic labels ("File access").
- **A limits slide near the end:** "What the agent does and does not do here" /
  "Where this goes wrong".
- **Last slide: "Summary".** A concept → key fact table, then a
  "**Next (<unit name>):** …" line linking to the following unit.
- **Speaker notes (`::: notes`) on every slide.** They hold what would be said
  aloud, so the deck works whether or not it is recorded.

## 9. Pictures on about half of the slides
Expect about half of the slides to carry an image: a concept figure (SVG,
`figNN-name.svg` in the unit folder, as in 3MB00A) or a real one (a screenshot
of a session, a terminal, a GitHub page, a result plot). Screenshots are
annotated (arrows, highlighted boxes) so that the eye lands on the point.

## 10. Quality over quantity in decks
There is no page limit. A deck may have up to about 40 slides when the topic
needs it. One topic per deck still holds: if a deck covers two topics, split it
rather than cut good material.

## 11. One font size on every slide
Text size never changes between slides: no `{.smaller}`, `.r-fit-text`, inline
`font-size` or similar. When a slide does not fit, make the **image smaller**
first, then cut or move text, then split the slide (e.g. "Summary" and
"Summary (continued)"). Check fit by rendering the deck and looking at it, or
with the overflow check described in README.md.
