# Content plan: Introduction to agentic AI

A working draft. Units will shift, merge and split. See [audience.md](audience.md)
for who we teach and [designprinciples.md](designprinciples.md) for how we build
material. Open questions are marked **[?]**.

The course language is **English**. Scheduling, total time, credits, cost and
help sessions are out of scope for this plan. We aim for content of good quality
first and fit it to a time frame later.

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
| **Free software** | Git, R (+ RStudio, optional), Python, Quarto. Installed with the agent's help in *Terminal survival kit* where possible. | [git-scm.com](https://git-scm.com) · [cran.r-project.org](https://cran.r-project.org) · [quarto.org](https://quarto.org) |

**[?]** Do we require both Claude Code and Codex? The *Parallel workers* unit
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
| Grant results: collect and analyse | **Add (new)** | See *Collecting and analysing grant results*. |
| Likely reviewers for an upcoming grant | **Add (new)** | See *Likely reviewers*. |
| Shiny apps | **Add (new)** | See *Shiny apps*. |
| Extracting data from PDFs | **Add (new)** | See *Extracting data from PDFs*. |
| Basic Python image analysis | **Add (new)** | Track C. |

## Course order

Each unit = a slide deck that stands on its own (recorded or not) + an exercise
with a worked example and an "on your own project" part. Units are referred to
by **name**, not number, so they can be reordered without breaking links.

### Ordering rules
These rules decide the order. Check any reordering against them.

1. **Motivation before installation.** People put up with a painful install only
   once they have seen why it is worth it.
2. **A first success before theory.** Participants do something useful with the
   agent before we explain how LLMs work. The explanation then refers to things
   they have just seen go right or wrong.
3. **Privacy before own data.** The own project is chosen only after the privacy
   unit, so nobody's first own-data session sends patient or student data to
   the cloud.
4. **Safety net before heavy editing.** Git comes right after the project folder
   exists, before the agent starts changing participants' own files at scale.
5. **Each unit leans on the one before.** Git → GitHub → page → demo/Shiny (all
   hosted on the page). Literature review → PDF extraction (from the papers just
   found) → grant data → reviewer profiles (built from the same literature
   databases).
6. **Sharing comes early.** Once the project page exists, every later result
   (the literature table, the grant analysis, the extracted data) is published
   on it. Participants practise the git → GitHub loop again in every unit
   instead of once.
7. **Scaling up comes last.** Parallel agents, custom skills and reading other
   people's code all pay off only once participants have repeated a workflow
   often enough to want to automate it.

### Part 1: Getting started (example data only)
1. **Why agentic AI?** Live build: an empty folder becomes a plot, a web page and
   a literature table. Chat vs agent; what it changes for teaching and research.
2. **Accounts and installation.** The table above; install Claude Code and/or
   Codex; first "hello" in the terminal.
3. **Terminal survival kit.** Files, folders, paths; starting Claude Code and
   Codex; reading and approving what the agent wants to do; permission modes;
   letting the agent install R/Python/git for you.
4. **First delegations.** Organise a messy folder; clean an Excel file; summarise
   a few PDFs into a table. Example data only. Verify by spot checks.
5. **How LLMs and agents work, and how they fail.** Tokens, context, tools, the
   agent loop; hallucination, sycophancy, silent shortcuts; why we verify. Uses
   examples from what went wrong in *First delegations*.
6. **Privacy, ethics and safety.** What data may be sent to a cloud LLM; GDPR and
   university policy; AI disclosure in papers and theses; never pointing the
   agent at your whole home folder; working in a copy. **Ends with: choose your
   own project** (or pick one from the list).

### Part 2: A project that lasts
7. **Delegating well.** Goal, context, constraints, acceptance criteria; plan
   mode; "interview me first"; iterating; when to start over.
8. **Organising a project for an agent.** `CLAUDE.md`/`AGENTS.md`, README, folder
   layout, plan and notes files, memory; making it shareable. *The own-project
   folder gets this structure now.*
9. **Git as undo button and lab notebook.** Snapshots, history, "what changed",
   going back. The agent does the typing.
10. **Reproducible figures.** From CSV to a publication-quality plot with an R
    script (Python variant); rerun on new data; pin package versions. Commit
    the result.

### Part 3: Sharing
11. **GitHub.** Repositories, push, collaborators, issues; public vs private.
    *Peer exercise:* swap repositories with another participant; use your own
    agent to understand and critique theirs. This tests *Organising a project*
    directly.
12. **A course or project page.** Quarto website on GitHub Pages. The figures
    from *Reproducible figures* are its first content.
13. **Interactive demos.** One self-contained HTML page that explains a concept
    from your own field; embed it in your page.
14. **Shiny apps.** An interactive app for exploring your own data (filters,
    plots, tables), in R Shiny or Shiny for Python. Run it locally first, then
    publish it: [Shinylive](https://shiny.posit.co/py/docs/shinylive.html) runs
    the app in the browser and can be hosted on the same GitHub Pages site. Use
    [shinyapps.io](https://www.shinyapps.io) or a university server when the
    app needs a real R/Python server. Discuss what data becomes public when you
    publish an app.

### Part 4: Literature, documents and the web
15. **Literature review on a gene (or topic) set.** Search, structured table,
    verified references, BibTeX/Zotero export. Publish the table on your page.
16. **Extracting data from PDFs.** Tables, numbers and text from a folder of
    papers, reports or old lab protocols into one tidy spreadsheet.
    - Worked example: extract one reported quantity (sample sizes, effect sizes,
      or measured values) from the open-access papers found in the literature
      review, into one table with a "source page" column.
    - Teach the difference between PDFs with real text and scanned images
      (OCR), and tables that come apart when extracted.
    - Verification: the agent records page and table numbers; the participant
      checks a random sample by hand; a second agent extracts independently and
      the two are compared.
17. **Collecting and analysing grant results.** APIs vs scraping; checking terms
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
18. **Likely reviewers for an upcoming grant, and mock reviews.**
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

### Part 5: Scaling up
19. **Parallel workers: Claude and Codex.** Two agents at once; the same task to
    both and a comparison; cross-review; subagents; strengths of each tool.
20. **Making the agent yours.** Slash commands, skills, MCP connectors (PubMed,
    Zotero); a reusable "house style" for figures or reports.
21. **Reading other people's code.** Explain, document, port (MATLAB → R/Python)
    and test that the results match.
### Part 6: The wider picture
These units need little hands-on agent skill. They sit in Part 6 for now; each
notes where it could move later.

22. **Choosing a model: families, sizes and benchmarks.**
    - The landscape: the main providers and their model families (Anthropic
      Claude, OpenAI GPT, Google Gemini) and the main open-weights families
      (Llama, Qwen, DeepSeek, Mistral, gpt-oss). Within a family, large /
      medium / small tiers trade capability against speed, cost and usage
      limits. Reasoning ("thinking") settings. Context length. How to switch
      model inside Claude Code and Codex, and when it is worth it (hard
      analysis vs bulk file chores).
    - Model names change every few months: teach how to read a model name
      and a release note, not a fixed list. Keep the current list on the single
      version-specific page (see designprinciples §6).
    - Benchmarks, what they measure and how the results are normalised. Redraw
      a few published graphs (with credit) rather than make our own claims:
      - *Score on a fixed test* over time: e.g. SWE-bench Verified (fixing real
        code bugs), Terminal-Bench (agent work in a terminal), GPQA Diamond
        (expert science questions), Humanity's Last Exam. Show saturation:
        tests that went from near 0 to near 100 % within a year or two.
      - *Normalised by human task length*: METR's "time horizon", the length
        of task (in human working time) a model completes half the time, and
        how it has doubled roughly every 7 months (Kwa et al. 2025, METR).
        **Probably the most intuitive graph for this audience.**
      - *Normalised across many benchmarks*: composite indices such as Epoch
        AI's Capabilities Index or the Artificial Analysis Intelligence Index.
      - *Normalised by cost*: score per dollar, or the cost of reaching a given
        score falling over time (Epoch AI; Stanford AI Index report).
      - *Human preference*: LMArena-style rankings from blind side-by-side
        votes (Elo-like scores), and what they reward (style, length).
      - Closed vs open-weights gap over time (Epoch AI, Stanford AI Index).
    - Caveats, at a basic level: test questions leaking into training data;
      providers choosing which benchmarks to report; scores on a test vs
      usefulness on *your* task. Conclusion for participants: try two models on
      a small sample of your own task and compare (links to *Parallel workers*).
    - Sources to take figures from (**[?]** check licences and fetch current
      versions before writing): [METR time horizons](https://metr.org),
      [Epoch AI data hub](https://epoch.ai/data),
      [Stanford AI Index](https://hai.stanford.edu/ai-index),
      [Artificial Analysis](https://artificialanalysis.ai),
      [LMArena](https://lmarena.ai), [SWE-bench](https://www.swebench.com).
    - Placement: Part 6 for now. Alternative later: right after *How LLMs and
      agents work*, or before *Parallel workers*.
23. **Open-weights models and data privacy.** Closed models (Claude, GPT) vs
    open-weights models (e.g. Llama, Qwen, Mistral, gpt-oss) that anyone can
    download and run. Where the data goes in each case: the provider's cloud,
    a university- or nationally hosted service, or your own computer.
    [SciLifeLab OpenLLM](https://openllm.scilifelab.se/about/) as the Swedish
    example of a hosted service for research. What open-weights models make
    possible (sensitive data that may not leave the institution) and what they
    cost (weaker models, less capable agents, hardware). Connecting an agent
    harness to an open model. Builds directly on *Privacy, ethics and safety*.
    Placement: Part 6 for now (decided 2026-11-23). Alternative later: here (needs comfort with the tools), or right after
    *Privacy, ethics and safety* for participants whose own project involves
    sensitive data. *Privacy, ethics and safety* should point forward to it
    either way.
24. **Labelling AI-generated content: the EU rules, watermarks and detection.**
    No maths; pictures and small worked examples only.
    - The rules: the EU AI Act's transparency obligations (Article 50).
      Providers must mark AI-generated content in a machine-readable way;
      people who publish deepfakes or AI-written text meant to inform the
      public must disclose it. The EU code of practice on marking and labelling
      AI-generated content. **[?]** Check current dates and status before
      writing; they were being phased in during 2026.
    - What it means for participants: course pages, figures, slides and press
      texts they publish; their own university's disclosure rules.
    - How marking works, at a basic level:
      - *Metadata labels* (e.g. C2PA "content credentials"): a signed note
        attached to the file. Easy to read, easy to strip by taking a
        screenshot.
      - *Invisible watermarks in images and audio* (e.g. Google's SynthID):
        a pattern hidden in the pixels, invisible to the eye but detectable by
        a program that knows the key. Survives some editing, not all.
      - *Watermarks in text*: the model is nudged to prefer certain words
        slightly more often. A detector that knows the rule counts them; with
        enough text the excess is very unlikely to be chance. Show it as a
        coin-flip analogy, not a formula. Paraphrasing or translating weakens
        it, and short texts carry too little signal.
    - "AI detectors" for student texts that use no watermark: why they are
      unreliable, with false accusations especially against non-native
      writers. Important for teachers: a detector score is not evidence.
    - Exercise idea: inspect the content credentials of an AI-generated image;
      run a toy text-watermark demo (a coin-flip simulation in a self-contained
      HTML page) to see how much text a detector needs.
    - Placement: Part 6 for now (decided 2026-11-23). Alternative later: near *Privacy, ethics and safety*, or before *A course
      or project page* (the first time participants publish content).
25. **Guardrails and safety levels.** Participants will hit guardrails of
    several kinds, often without knowing which one stopped them. This unit
    names them, shows what each looks like, and explains the safety levels
    behind the strictest ones. (**[?]** Check every provider page and level
    name below against current versions before writing.)
    - **Kinds of guardrail**, each with an illustrative example of what the
      user sees and what to do:
      - *Content refusals in the model*: the model declines (harmful content,
        weapons, self-harm, sexual content, hateful content). Usually a polite
        refusal in the reply.
      - *Safety classifiers around the model*: a separate system that blocks
        input or output in high-risk areas (biological and chemical weapons,
        some cyber-attack help). Can trigger on legitimate research; may stop
        an answer midway or end a session. Bio deep dive in the next unit.
      - *Dual-use computing and security work*: requests that look like
        hacking (scanning networks, cracking passwords, malware analysis) may
        be refused even for legitimate IT or security research.
      - *Personal data and people*: reluctance to compile profiles of named
        private individuals, find addresses, or identify people in photos.
        Relevant to *Likely reviewers for an upcoming grant*: stay with
        public professional information.
      - *Copyright*: refusing to reproduce long passages of books, lyrics or
        paywalled articles (links to *Copyright, memorisation and credit*).
      - *Medical, legal and financial caution*: extra caveats, referral to a
        professional, or a vaguer answer.
      - *Agent-level guardrails in the harness*, not the model: permission
        prompts, sandboxing, network access switched off, protected folders
        (taught in *Terminal survival kit* and *Privacy, ethics and safety*).
        These are settings the user controls.
      - *Account-level enforcement*: warnings, restricted features or a banned
        account for repeated policy violations, under the provider's usage
        policy.
      - Not guardrails, but often mistaken for them: usage and rate limits
        ("you have reached your limit"), context running out, network errors.
    - **Recognising which one you hit**: refusal in the reply vs a system
      message vs a task stopping vs a permission prompt. A small decision
      table.
    - **What to do**: if the request is legitimate, give context (who you are,
      what the task is for) and ask for the safe parts; split out the part that
      is genuinely restricted and handle it through normal channels. Do not try
      to trick the model past a guardrail: it breaks the usage policy and can
      cost you the account. False positives can be reported to the provider.
    - **Safety levels** behind the strictest guardrails, at a basic level:
      providers test each new model for dangerous capabilities before release
      and switch on stronger protections when a model crosses a threshold.
      - Anthropic's Responsible Scaling Policy: AI Safety Levels (ASL-2,
        ASL-3, ...), modelled loosely on biosafety levels (BSL). A comparison
        biologists will recognise at once.
      - OpenAI's Preparedness Framework: tracked risk categories (biological
        and chemical, cybersecurity, AI self-improvement) with "High" and
        "Critical" capability thresholds.
      - Google DeepMind's Frontier Safety Framework: "critical capability
        levels".
      - The EU AI Act's obligations for general-purpose models with
        "systemic risk" (brief).
      - Why this matters to participants: the most capable models carry the
        strictest classifiers, so a stronger model can refuse something a
        weaker one would do; open-weights models (*Open-weights models and
        data privacy*) have fewer outside guardrails, which shifts the
        responsibility to the user and the institution.
    - Placement: Part 6 for now. Alternative later: a short version in
      *How LLMs and agents work, and how they fail*, since participants may hit
      guardrails as early as *First delegations*.
26. **Limits of AI for biological research: safety guardrails.**
    Deep dive for life sciences and medicine, building on *Guardrails and
    safety levels*.
    - Why they exist: providers block help that could make biological
      weapons or dangerous pathogens easier to produce (dual-use concern).
      Anthropic and OpenAI both run extra safeguards for biology in their most
      capable models. **[?]** Check each provider's current public policy pages
      before writing.
    - When they occur: mostly around pathogens and toxins, such as enhancing
      transmissibility or virulence, synthesis or acquisition routes for select
      agents and toxins, or detailed protocols for working with them. Legitimate
      work can trigger them too (virology, toxin biology, some protein design,
      biosecurity research itself).
    - What they look like: a refusal; a partial or vaguer answer than usual; a
      warning message; in an agent, a task that stops partway or a session that
      ends. Show real-looking (illustrative) examples of each.
    - What to do: recognise it as a policy limit, not a bug; do not try to get
      around it; use the provider's channels for legitimate research access
      where they exist, your institution's biosafety officer, and ordinary
      literature and colleagues. Never paste restricted or dual-use protocols
      into a cloud model.
    - Other limits for biologists, beyond safety guardrails: protocols the model
      invents or gets subtly wrong (chemical hazards, concentrations, missing
      safety steps), medical questions, and the gap between plausible text and
      what actually works at the bench.
    - Relevant for Track A (RNA-seq) and anyone in life sciences or medicine.
      Placement: Part 6 for now (decided 2026-11-23). Alternative later: a unit here, or a section of *How LLMs and agents
      work, and how they fail*.

### Pending additions to existing units
- *How LLMs and agents work*: add a high-level slide on **how each token
  depends on all the earlier ones** (the model reads the whole context each
  time it produces the next token; earlier tokens shape later ones), linking the
  token, next-token and context-window slides into one picture.
- *How LLMs and agents work*: **likely, not new.** The model picks among the
  most probable next tokens, so by default it gives the typical answer, not the
  most original one. Novelty is low unless you push for it (ask for
  alternatives, unusual angles, critiques of the obvious answer) and judge the
  result yourself. Consequences: good at standard analyses and conventional
  text, weak at original research ideas; ideas it presents as new may already
  be in the literature. Point to *Copyright, memorisation and credit* for the
  Navier–Stokes case, which shows the other side: with search, verification and
  heavy compute, agents can produce new results.
- *How LLMs and agents work*: tie **hallucination** to the same mechanism.
  The model produces what is *plausible* given the context, not what is
  *true*. A plausible but non-existent reference or function comes out of the
  same process as a correct one, which is why it sounds just as confident.

### Part 6 (continued)
27. **Copyright, memorisation and credit.**
    - Current legal state, briefly and without legal advice: training on
      copyrighted material and whether outputs infringe are being decided in
      court case by case. Examples to present (**[?]** check the status of each
      before writing):
      - *GEMA v OpenAI* (Munich, 2025): song lyrics memorised by the model
        judged to infringe. An EU example.
      - *Bartz v Anthropic* (US, 2025): settlement over books from pirate
        sites.
      - *New York Times v OpenAI and Microsoft* (US, ongoing).
      - *Getty Images v Stability AI* (UK, 2025).
    - Memorisation: models can sometimes reproduce training material word for
      word or image for image: long passages of books, song lyrics, code with
      its licence comments, near-copies of training images. Research has
      extracted such material on purpose. Rare text that appears many times
      online is memorised most.
    - What it means for participants: their AI-generated text, code or
      figures could contain someone else's material without them knowing;
      licence of the code an agent writes; what to check before publishing a
      course page or a paper; the EU AI Act's copyright-related duties for
      model providers (brief).
    - Credit and novelty, with the **OpenAI Navier–Stokes controversy**
      (September 2026) as the case: OpenAI claimed its model produced a solution
      to a Navier–Stokes Millennium Prize problem. Mathematicians questioned
      whether it solved the problem experts actually mean (a forcing term,
      a loophole), the result is not peer-reviewed, and there is a dispute over
      credit to human mathematicians whose work it built on. There are also
      allegations, which OpenAI denies, about the use of a mathematician's notes
      stored in a Codex session. Use it to discuss who gets credit when AI is
      involved, why verification by experts still matters, and, linking back to
      *Privacy, ethics and safety*, what happens to unpublished ideas you give
      a cloud agent. Present the allegations as allegations; sources:
      [Scientific American](https://scientificamerican.com/article/did-openai-solve-the-wrong-navier-stokes-problem),
      [MIT Technology Review](https://www.technologyreview.com/2026/09/08/1143747/what-openais-latest-controversy-tells-us-about-the-future-of-math),
      [Axios](https://axios.com/2026/09/08/openai-math-solution-navier-stokes-credit).
      **[?]** Check for later developments before writing.
    - Placement: Part 6 for now (decided 2026-11-23). Alternative later: in Part 6, or split so that copyright goes before *A
      course or project page* (when participants first publish) and the credit
      case goes with the novelty slide in *How LLMs and agents work*.

### Tracks (pick one or more; all teach the same agent skills on different data)
A track can start once *Reproducible figures* is done. The recommended point is
after Part 4, so the track's results go on the page and RNA-seq can build on the
literature review.

- **A. Bulk RNA-seq.** Counts → QC → DESeq2 → volcano → enrichment → link back to
  the literature table from *Literature review*.
- **B. Simulation.** FEM heat or elasticity (scikit-fem), ODE models, or
  agent-based models; validate against an analytic solution.
- **C. Image analysis in Python.** Basic Python scripts (scikit-image, with
  numpy/pandas) to segment, count and measure objects, for example nuclei in
  microscopy images, colonies on plates, or particles in materials images.
  Batch-process a folder; save measurements to CSV; plot them. Verification:
  overlay the detected outlines on the images and count a few by hand. This is
  also the course's gentle introduction to Python.
- **D. Survey and tabular data.** Questionnaire or course-evaluation data;
  descriptive statistics, plots, a report.
- **E. Teaching materials.** Question bank → Canvas (reuse 3MB00A's
  `canvas-quiz/`), exercise variants with answer keys, slides as Quarto/reveal.js.

## Example own projects (for those without an idea)
- A course page for one of your own courses, with one interactive demo.
- A literature map of 20 genes, proteins or materials from your field, with a
  verified reference table.
- The funding landscape of your research area in Sweden or the EU (extends a unit above).
- Preparing your next grant application: reviewer profiles and mock reviews
  (extends a unit above).
- Making an old analysis reproducible: one script, pinned versions, a README.
- A cleaned and documented dataset ready for deposit (Zenodo, FAIR).
- A Shiny app for your lab's data, published next to your course page
  (extends a unit above).
- A spreadsheet of values extracted from the papers in your field (extends a unit above).
- An automated weekly report, for example from instrument logs.

## More candidate material
- Bulk file chores: rename images from a metadata sheet; convert formats.
- A data management plan for a new project.
- Checking a manuscript's statistics against its own tables.
- Schematic figures as SVG for slides and papers.
- Scheduled and recurring agent tasks.

## Open questions
- **[?]** Require both Claude Code and Codex, or one plus the other for *Parallel workers*
  only?
- **[?]** Which grant funders to use as the main example: Swecris (Swedish
  audience), or NIH RePORTER (best API, international)?
