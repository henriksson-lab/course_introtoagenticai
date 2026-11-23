# Content plan: Introduction to agentic AI

A working draft. Weeks will shift, merge and split. See [audience.md](audience.md)
for who we teach and [designprinciples.md](designprinciples.md) for how we build
material. Open questions are marked **[?]**.

## The course in one sentence

Participants learn to **delegate real work to a coding agent (Claude Code and
Codex), check the result, and keep it organised, reproducible and shareable**,
without having to become programmers first.

Code is a by-product. The skills we teach are: describing a task well, giving
the agent the right context, judging the output, and keeping a project in order.

## Evaluation of the initial idea list

| Idea | Verdict | Notes |
|------|---------|-------|
| Motivating intro lecture | **Keep, core** | Open with a live build: an empty folder becomes a plot, a web page and a literature table in about 15 minutes. Then explain what an agent is: an LLM in a loop with tools (read files, run commands, search). |
| CLI basics | **Keep, but reframe** | The goal is to *read* the terminal, not to type commands. They need folders, paths, `cd`/`ls`/`pwd`, starting the agent, and reading what it wants to run before they approve it. One short unit. The agent can explain any command it proposes. |
| R scripts for plots (reproducible code) | **Keep, core** | This is the clearest example of why an agent beats a chat window: the script stays on disk, can be rerun and can be shared. Add a Python variant for engineers. |
| Literature review on a gene set | **Keep, core** | High value, but high risk: invented references. The unit must be about verification (PMIDs/DOIs checked against PubMed, a structured table, a BibTeX/Zotero export). Generalise it to "literature review on a set of X" for non-biologists. |
| Parallel workers, Claude vs Codex | **Keep, later** | Teach three ideas: (1) two agents in two folders or terminals at once, (2) the same task given to both and the results compared, (3) one agent reviewing the other's work. Subagents come in here. Too advanced for week 1. |
| Directory organisation for large projects | **Keep, core. Possibly the most important unit** | `CLAUDE.md` / `AGENTS.md`, README, `data/raw` (read-only), `results/`, `notes/`, plan files. This is how the agent finds things across sessions and how a colleague can pick the project up. Codex reads `AGENTS.md`, Claude reads `CLAUDE.md`: teach one file that both read. |
| Course page on GitHub Pages | **Keep** | Quarto website, as in 3MB00A. Builds directly on git/GitHub. Teachers will want this. |
| Make an interactive demo | **Keep, capstone-shaped** | Self-contained HTML/JS (no build step: the 3MB00A TypeScript/esbuild setup is too heavy for this audience). Participants pick their own topic and embed the result in their course page. |
| Basic RNA-seq analysis by LLM alone | **Keep as a track** | Good for biologists and medical faculty: counts → QC → DESeq2 → volcano plot → enrichment → link back to the literature review. Not for everyone. |
| Basic FEM simulation | **Keep as a track, broaden** | Narrow audience, and hard to verify without domain knowledge. Make it a "simulation" track: FEM (heat diffusion or beam bending with scikit-fem), ODE models (SIR epidemic, pharmacokinetics), or agent-based models. Verify against a known analytic solution. |
| Git and GitHub | **Keep, after they have something worth saving** | Present git first as an **undo button and lab notebook**, and only then as a way to share. The agent does the typing ("commit this with a good message", "show me what changed since yesterday"). |

### Gaps in the initial list (should be added)

1. **Privacy, data protection and ethics.** This is the first thing a teacher or
   clinician will get wrong. What may be sent to a cloud LLM: patient data,
   student data, unpublished results, exam questions, peer-review manuscripts?
   University policy, GDPR, AI disclosure in papers and theses. **Must be core.**
2. **How LLMs fail.** Hallucination, confident errors, sycophancy, non-determinism,
   context limits, and silent "simplifications" (for example, an agent that drops
   failing rows to make a script run). Verification is taught as a skill.
3. **Safety of the agent itself.** Permission modes, what "allow always" means,
   working in a copy, git as a safety net, never pointing the agent at your home
   folder.
4. **Cost, accounts and installation.** Subscriptions, usage limits, Windows vs Mac,
   institutional licences. This needs a setup clinic before day 1 (see below).
5. **Reusable workflows.** Custom slash commands and skills ("/make-figure in our
   lab style"), MCP connectors (PubMed, Zotero, Google Drive). This is where
   productivity compounds.
6. **Reading other people's code.** "My former PhD student left 3000 lines of
   MATLAB." Explain it, document it, port it to R or Python, test that the
   results match. Very common, very valuable.

## More ideas (candidates for units, tracks or capstones)

**For everyone**
- Clean a messy Excel sheet into tidy data, with a script that does it again next
  time. Probably the most common real task.
- Bulk file chores: rename 400 microscopy images from a metadata sheet, convert
  formats, sort downloads.
- Extract tables and numbers from a folder of PDFs into one spreadsheet, and
  check a sample by hand.
- Build a small Shiny or Streamlit app or dashboard for your own data.
- A personal or lab website (same machinery as the course page).
- Automate a recurring report, for example a weekly summary of instrument logs.
- Turn a methods section into a runnable pipeline, or check a paper's statistics
  against its own tables.
- Make figures and diagrams as SVG: schematic figures for slides and papers.

**For teachers**
- Generate a question bank and export it to Canvas (3MB00A already has
  `canvas-quiz/`, which we can reuse).
- Exercise variants with randomised numbers plus answer keys.
- Lecture slides as Quarto/reveal.js from an outline; accessibility (alt text,
  captions).
- Rubric drafting. Do *not* upload student work without checking the privacy
  rules first; this is a good discussion case.
- Course page plus an interactive demo of a concept from your own course.

**For researchers**
- A data management plan and README for a dataset you are about to publish
  (FAIR, Zenodo).
- Make an old analysis reproducible: pinned package versions (`renv`), a single
  "run everything" script.
- Image analysis: count nuclei or measure areas (Python/scikit-image, or an
  ImageJ macro).
- Grant and manuscript support, kept within ethical limits: structure, consistency
  checks, reference formatting. Not writing your science.

**Agent skills worth a unit of their own**
- Plan mode: let the agent propose a plan, edit it, then execute.
- "Interview me": have the agent ask you questions before it starts.
- Acceptance criteria: tell the agent how *you* will check the result, so it can
  check too.
- Cross-review: Codex reviews Claude's analysis, or the reverse.
- Scheduled/recurring tasks (later, optional).

## Proposed structure

The course is modular, so it can run as 2, 3, 4 or 5 weeks (see "Length
options" below). Each unit = short recorded lecture (screen recording of a real
session) + an exercise that ends in an **artifact the participant keeps**.

### Week 0: Setup clinic (before the course)
- Accounts (Claude, ChatGPT/Codex, GitHub), installation, first "hello" in the
  terminal. Drop-in Zoom session.
- Fallback for those who cannot install: **[?]** GitHub Codespaces or a university
  VM with both agents preinstalled.

### Week 1: Foundations, first useful results
1. **Why agentic AI?** Live build; chat vs agent; what it changes for teaching
   and research. (Motivation lecture.)
2. **How LLMs and agents work, and how they fail.** Tokens, context, tools, the
   agent loop; hallucination; why we verify.
3. **Terminal survival kit.** Files, folders, paths; starting Claude Code and
   Codex; reading and approving what the agent wants to do; permission modes.
4. **First delegations.** Organise a messy folder; clean an Excel file; summarise
   a folder of PDFs into a table. Verify by spot checks.
5. **Privacy, ethics, cost.** What data may go where; university policy; AI
   disclosure; subscriptions and limits.

### Week 2: Working like a professional
6. **Delegating well.** Goal, context, constraints, acceptance criteria; plan
   mode; iterating; when to start over.
7. **Organising a project for an agent.** `CLAUDE.md`/`AGENTS.md`, README, folder
   layout, plan and notes files, memory; making it shareable. *Artifact: a
   template project folder they reuse for the rest of the course.*
8. **Reproducible figures.** From CSV to a publication-quality plot with an R
   script (Python variant); rerun on new data; pin versions.
9. **Literature review on a gene (or topic) set.** Search, structured table,
   verified references, BibTeX/Zotero export.
10. **Git as undo button and lab notebook.** Snapshots, history, "what changed",
    going back. The agent does the typing.

### Week 3: Sharing and scaling
11. **GitHub.** Repositories, push, collaborators, issues; public vs private.
12. **A course or project page.** Quarto website on GitHub Pages.
13. **Interactive demos.** One self-contained HTML page that explains a concept
    from your field; embed it in your page.
14. **Parallel workers: Claude and Codex.** Two agents at once; the same task to
    both and a comparison; cross-review; subagents; strengths of each tool.
15. **Making the agent yours.** Slash commands, skills, MCP connectors (PubMed,
    Zotero).

### Week 4: Tracks (pick one; all teach the same agent skills on different data)
- **A. Bulk RNA-seq.** Counts → QC → DESeq2 → volcano → enrichment → link back to
  unit 9's literature table.
- **B. Simulation.** FEM heat or elasticity (scikit-fem), ODE models, or
  agent-based models; validate against an analytic solution.
- **C. Image analysis.** Microscopy: segment, count, measure; batch processing.
- **D. Survey and tabular data.** Questionnaire or course-evaluation data;
  descriptive stats, plots, a report. (Teachers outside the life sciences.)
- **E. Teaching materials.** Quiz bank → Canvas, exercise variants, slides.
- **F. Inherited code.** Understand, document, port and test a legacy script.

### Week 5: Capstone
- Own project, chosen in week 2 so it can grow through the course. Example list
  for those without an idea.
- Peer review: swap repositories; the reviewer uses *their* agent to understand
  and critique the other's project. This tests unit 7 directly.
- Short presentation of the result and of *how* it was built (prompts, dead
  ends, what was verified and how).

### Length options
| Format | Content |
|--------|---------|
| 2 weeks | Week 1 + units 6–10, mini capstone |
| 3 weeks | Weeks 1–2 + units 11–12 + capstone |
| 4 weeks | Weeks 1–3 + one track, capstone merged into the track |
| 5 weeks | Everything above |

Recommendation: **4 weeks at half pace** (participants are working staff), with
the capstone running alongside weeks 3–4.

## Assessment [?]
A portfolio of the artifacts from each unit plus a capstone with a presentation
and a peer review. No written exam: the learning outcome is "can do", not "can
recall".

## Open questions
- **[?]** Credits, and is this a formal course (ECTS, syllabus) or staff
  development? Half-time or full-time?
- **[?]** Who pays for subscriptions? Is there an institutional licence (Claude for
  Education / ChatGPT Edu)? Does the university approve these tools for the data
  participants will use?
- **[?]** Do we require both Claude Code and Codex, or one plus a taster of the
  other? Requiring both doubles the cost and setup work.
- **[?]** Language: Swedish or English?
- **[?]** Campus sessions or fully recorded? This audience benefits a lot from live
  help sessions ("my terminal says…").
- **[?]** Tools change monthly. Keep all version-specific instructions (install
  commands, menu names, prices) on **one** page so they can be updated each run.
