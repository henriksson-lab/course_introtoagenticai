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

## 8. Keep decks small
Same rule as 3MB00A: one topic per deck, about 15 slides at most. Split decks
rather than cut them.
