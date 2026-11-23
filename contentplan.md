# Content plan: Introduction to agentic AI

A working draft. Units will shift, merge and split. See [audience.md](audience.md)
for who we teach and [designprinciples.md](designprinciples.md) for how we build
material. Open questions are marked **[?]**.

The course language is **English**. Scheduling, credits, cost and help sessions
are out of scope for this plan.

## The course in one sentence

Participants learn to **delegate real work to a coding agent (Claude Code and
Codex), check the result, and keep it organised, reproducible and shareable**,
without having to become programmers first.

Code is a by-product. The skills we teach are: describing a task well, giving
the agent the right context, judging the output, and keeping a project in order.

## Own ideas run through the whole course (no capstone)

There is no separate final project. Instead, each participant chooses **their own
project** in the first block and keeps one project folder for the whole course.
Every exercise has two parts:

1. **Worked example.** A shared task on example data, so everyone has a
   reference result and something to compare with.
2. **On your own project.** The same skill applied to the participant's own
   topic: their data, their course, their research question.

For those without an idea, we keep a list of example projects (see the end of
this file). A participant may also swap projects partway through.

## Accounts and licences

Participants need accounts for the tools below. **Give pointers, not prices**:
plans and limits change often, so link to the official pages and keep this list
on **one** page of the site that we update before each run.

| Tool | What participants need | Where |
|------|------------------------|-------|
| **Claude Code** | A paid Claude plan: Pro or higher (Max, Team, Enterprise). The free plan does *not* include Claude Code. Pay-as-you-go API billing via the Claude Console also works. | [claude.com/pricing](https://claude.com/pricing) · [docs: Claude Code setup](https://docs.claude.com/en/docs/claude-code/setup) |
| **Codex** | A ChatGPT account. The Codex CLI works with all ChatGPT plans, including Free and Go, but with low usage limits; Plus or higher is realistic for the course. | [chatgpt.com/pricing](https://chatgpt.com/pricing) · [Codex help article](https://help.openai.com/en/articles/11369540-codex) · [Codex pricing](https://developers.openai.com/codex/pricing) |
| **Institutional plans** | Claude for Education, Claude Team/Enterprise and ChatGPT Edu/Enterprise may include the agents. Whether they do depends on the institution's workspace settings, so participants should ask their IT department. | Local IT |
| **GitHub** | A free personal account. Educators can apply for GitHub Education benefits. | [github.com/signup](https://github.com/signup) · [GitHub Education](https://github.com/education) |
| **Free software** | Git, R (+ RStudio, optional), Python, Quarto. Installed with the agent's help in unit 3 where possible. | [git-scm.com](https://git-scm.com) · [cran.r-project.org](https://cran.r-project.org) · [quarto.org](https://quarto.org) |

**[?]** Do we require both Claude Code and Codex? The parallel-workers unit (16)
needs both. All other units can be done with either.

## Evaluation of the initial idea list

| Idea | Verdict | Notes |
|------|---------|-------|
| Motivating intro lecture | **Keep, core** | Open with a live build: an empty folder becomes a plot, a web page and a literature table. Then explain what an agent is: an LLM in a loop with tools (read files, run commands, search the web). |
| CLI basics | **Keep, but reframe** | The goal is to *read* the terminal, not to type commands. They need folders, paths, `cd`/`ls`/`pwd`, starting the agent, and reading what it wants to run before they approve it. The agent can explain any command it proposes. |
| R scripts for plots (reproducible code) | **Keep, core** | The clearest example of why an agent beats a chat window: the script stays on disk, can be rerun and can be shared. Add a Python variant. |
| Literature review on a gene set | **Keep, core** | High value, but high risk: invented references. The unit must be about verification (PMIDs/DOIs checked against PubMed, a structured table, a BibTeX/Zotero export). Generalise it to "a set of X" for non-biologists. |
| Parallel workers, Claude vs Codex | **Keep, later** | Teach three ideas: (1) two agents in two folders or terminals at once, (2) the same task given to both and the results compared, (3) one agent reviewing the other's work. Subagents come in here. |
| Directory organisation for large projects | **Keep, core. Possibly the most important unit** | `CLAUDE.md` / `AGENTS.md`, README, `data/raw` (read-only), `results/`, `notes/`, plan files. This is how the agent finds things across sessions and how a colleague can pick the project up. Teach one file that both tools read. |
| Course page on GitHub Pages | **Keep** | Quarto website, as in 3MB00A. |
| Make an interactive demo | **Keep** | Self-contained HTML/JS (no build step: the 3MB00A TypeScript/esbuild setup is too heavy for this audience). Participants choose their own topic and embed the demo in their page. |
| Basic RNA-seq analysis by LLM alone | **Keep as a track** | Counts → QC → DESeq2 → volcano plot → enrichment → link back to the literature review. |
| Basic FEM simulation | **Keep as a track, broaden** | A "simulation" track: FEM (heat diffusion or beam bending with scikit-fem), ODE models (SIR epidemic, pharmacokinetics), or agent-based models. Verify against a known analytic solution. |
| Git and GitHub | **Keep, after they have something worth saving** | Present git first as an **undo button and lab notebook**, and only then as a way to share. The agent does the typing. |
| Grant results: collect and analyse | **Add (new)** | See unit 13. |
| Likely reviewers for an upcoming grant | **Add (new)** | See unit 14. |

## Proposed structure

Each unit = a slide deck that stands on its own (recorded or not) + an exercise
with a worked example and an "on your own project" part. Blocks are groupings by
theme, not weeks.

### Block 0: Before you start
0. **Accounts and installation.** The table above; install Claude Code and/or
   Codex; first "hello" in the terminal.

### Block 1: Foundations
1. **Why agentic AI?** Live build; chat vs agent; what it changes for teaching
   and research. *Choose your own project* (or pick from the list).
2. **How LLMs and agents work, and how they fail.** Tokens, context, tools, the
   agent loop; hallucination, sycophancy, silent shortcuts; why we verify.
3. **Terminal survival kit.** Files, folders, paths; starting Claude Code and
   Codex; reading and approving what the agent wants to do; permission modes;
   letting the agent install R/Python/git for you.
4. **First delegations.** Organise a messy folder; clean an Excel file; summarise
   a folder of PDFs into a table. Verify by spot checks.
5. **Privacy, ethics and safety.** What data may be sent to a cloud LLM; GDPR and
   university policy; AI disclosure in papers and theses; never pointing the
   agent at your whole home folder; working in a copy.

### Block 2: Working like a professional
6. **Delegating well.** Goal, context, constraints, acceptance criteria; plan
   mode; "interview me first"; iterating; when to start over.
7. **Organising a project for an agent.** `CLAUDE.md`/`AGENTS.md`, README, folder
   layout, plan and notes files, memory; making it shareable. *The own-project
   folder gets this structure now.*
8. **Reproducible figures.** From CSV to a publication-quality plot with an R
   script (Python variant); rerun on new data; pin package versions.
9. **Literature review on a gene (or topic) set.** Search, structured table,
   verified references, BibTeX/Zotero export.
10. **Git as undo button and lab notebook.** Snapshots, history, "what changed",
    going back. The agent does the typing.

### Block 3: Sharing
11. **GitHub.** Repositories, push, collaborators, issues; public vs private.
    *Peer exercise:* swap repositories with another participant; use your own
    agent to understand and critique theirs. This tests unit 7 directly.
12. **A course or project page.** Quarto website on GitHub Pages.
13. **Interactive demos.** One self-contained HTML page that explains a concept
    from your own field; embed it in your page.

### Block 4: Data from the web, with grants as the example
14. **Collecting and analysing grant results.** APIs vs scraping; checking terms
    of use and `robots.txt`; storing raw downloads separately from analysis.
    - Sources: [Swecris](https://www.vr.se/english/swecris.html) (Swedish funders,
      2008 onwards, with an [API](https://www.vr.se/english/swecris/swecris-api.html)),
      [NIH RePORTER](https://reporter.nih.gov) (API),
      [CORDIS](https://cordis.europa.eu) (EU projects, open data),
      [ERC funded projects](https://erc.europa.eu/projects-statistics/funded-projects).
    - Analyses: money over time per field and university; success by call;
      topic trends from abstracts (keywords → clusters); "who funds work like
      mine?"; where your own topic sits on the map.
    - Verification: totals checked against the funder's published statistics.
15. **Likely reviewers for an upcoming grant, and mock reviews.**
    - Collect the published panel and reviewer lists for a call (for example
      the Swedish Research Council's review panels, or ERC panel members from
      earlier rounds).
    - Build an expertise profile for each panel member from public sources
      (ORCID, OpenAlex, PubMed); match the profiles against your draft
      proposal: which parts will an expert find thin, and which terms will a
      non-expert not know?
    - Have the agent write **mock reviews** from several reviewer perspectives,
      using the funder's own assessment criteria.
    - Ethics discussion (required): this is personal data, even if public;
      keep it for your own preparation; never contact or lobby reviewers;
      panels change between rounds.

### Block 5: Scaling up
16. **Parallel workers: Claude and Codex.** Two agents at once; the same task to
    both and a comparison; cross-review; subagents; strengths of each tool.
17. **Making the agent yours.** Slash commands, skills, MCP connectors (PubMed,
    Zotero); a reusable "house style" for figures or reports.
18. **Reading other people's code.** Explain, document, port (MATLAB → R/Python)
    and test that the results match.

### Tracks (pick one or more; all teach the same agent skills on different data)
- **A. Bulk RNA-seq.** Counts → QC → DESeq2 → volcano → enrichment → link back to
  unit 9's literature table.
- **B. Simulation.** FEM heat or elasticity (scikit-fem), ODE models, or
  agent-based models; validate against an analytic solution.
- **C. Image analysis.** Microscopy: segment, count, measure; batch processing.
- **D. Survey and tabular data.** Questionnaire or course-evaluation data;
  descriptive statistics, plots, a report.
- **E. Teaching materials.** Question bank → Canvas (reuse 3MB00A's
  `canvas-quiz/`), exercise variants with answer keys, slides as Quarto/reveal.js.

## Example own projects (for those without an idea)
- A course page for one of your own courses, with one interactive demo.
- A literature map of 20 genes, proteins or materials from your field, with a
  verified reference table.
- The funding landscape of your research area in Sweden or the EU (unit 14
  extended).
- Preparing your next grant application: reviewer profiles and mock reviews
  (unit 15 extended).
- Making an old analysis reproducible: one script, pinned versions, a README.
- A cleaned and documented dataset ready for deposit (Zenodo, FAIR).
- A small Shiny or Streamlit dashboard for your lab's data.
- An automated weekly report, for example from instrument logs.

## More candidate material
- Extract tables and numbers from a folder of PDFs into one spreadsheet.
- Bulk file chores: rename images from a metadata sheet; convert formats.
- A data management plan for a new project.
- Checking a manuscript's statistics against its own tables.
- Schematic figures as SVG for slides and papers.
- Scheduled and recurring agent tasks.

## Open questions
- **[?]** Require both Claude Code and Codex, or one plus the other for unit 16
  only?
- **[?]** Which grant funders to use as the main example: Swecris (Swedish
  audience), or NIH RePORTER (best API, international)?
