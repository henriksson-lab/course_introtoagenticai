#!/usr/bin/env python3
"""
make-data.py: example data for the unit "Likely reviewers for an upcoming grant,
and mock reviews".

Creates three files and a zip file holding them:

  proposal-draft.md          a synthetic draft research plan (soil drought ecology)
  panel-fictional.csv        a FICTIONAL review panel: 8 invented people
  publications-fictional.csv invented publication records for the panel members,
                             shaped like what ORCID/OpenAlex would return
  reviewer-prep.zip          the three files above, for download

Everything is invented: the people, the universities, the journals, the papers
and the proposal. Any resemblance to real people is accidental. The course never
uses real named people in its worked examples.

The draft contains deliberate weaknesses that a panel should find. They are
listed in WEAKNESSES below and in the collapsed "Expected outcome" boxes in
exercise.qmd. Do not give this script to the agent during the exercise: it
gives away the answers.

The publications file contains one deliberate trap: two different people called
Jonas Ekbacka (an ecologist and a historian). A careful profile keeps only the
ecologist, identified by the identifier and affiliation in panel-fictional.csv.

Needs: Python 3 standard library only. Run from anywhere:

    python3 make-data.py
"""

import csv
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

WEAKNESSES = [
    "Pseudoreplication: 3 roofs and 3 controls, but 20 cores per plot are analysed as 120 independent samples.",
    "No power analysis or justification of the number of plots.",
    "Overstated novelty: 'the first study of drought legacies in soil microbes' (there is a literature on this).",
    "Carbon use efficiency (CUE): method not stated (e.g. 18O-water or 13C labelling).",
    "Soil moisture measured only at sampling; no continuous sensors, so the drought treatment is not verified.",
    "Single field site, no backup if roofs fail or the site is disturbed.",
    "Time plan: all sequencing and analysis in year 4; no slack for a failed season.",
    "'Microbial memory' is not defined or operationalised; no clear hypothesis that could be rejected.",
    "Data management: 'data available on request' only; no repository, no plan for sequence data.",
    "Jargon not explained: CUE, ASV, PLFA, Birch effect, rhizodeposition, legacy effect, beta diversity.",
    "Merits of the applicant cannot be judged from the research plan alone (no CV in the draft).",
]

PROPOSAL = """\
# Drought legacies in boreal forest soils: do microbial communities remember?

*Synthetic example draft for the course "Introduction to agentic AI".
The project, the applicant and all references are invented.*

## 1. Purpose and aims

Summer droughts are becoming more frequent and more severe in Scandinavian
boreal forests. Soils in these forests store more carbon than the trees
themselves, and much of the exchange of carbon between soil and atmosphere is
controlled by soil microorganisms. We will carry out the first study of drought
legacies in soil microbes, and test whether microbial communities that have
experienced one drought respond differently to the next.

Aims:

1. To determine whether a summer drought leaves a legacy effect in the soil
   microbial community that persists for at least one year.
2. To test whether this microbial memory changes carbon use efficiency (CUE)
   and CO2 release during a second drought.
3. To link changes in community composition (ASVs, beta diversity) to changes
   in soil carbon fluxes.

## 2. State of the art

Drought affects soil microbes directly through water stress and indirectly
through reduced rhizodeposition. On rewetting, a pulse of CO2 is released (the
Birch effect). Studies in grasslands have shown shifts in PLFA profiles after
drought (Example et al. 2019), but no study has followed the same soil through
repeated droughts in a boreal forest. Whether microbial communities "remember"
earlier stress is therefore unknown.

## 3. Significance

If microbial memory makes soils release more carbon in repeated droughts, current
carbon models underestimate future CO2 emissions from boreal forests. Our results
will be directly relevant to climate policy and forestry.

## 4. Preliminary results

In a pilot in 2025 we sampled soil under two rainfall-exclusion roofs and two
control plots once, after an eight-week drought. 16S amplicon sequencing showed
a lower relative abundance of Acidobacteria under the roofs (Figure 1, not
included in this draft). CO2 release was 30 % higher in drought soil after
rewetting in the laboratory.

## 5. Project description

**Site and design.** The experiment is placed in one Norway spruce stand at a
field station in central Sweden. We will build three rainfall-exclusion roofs
(10 x 10 m) and keep three control plots without roofs. Roofs will exclude all
rain for eight weeks in summer 2027 (drought 1) and again in summer 2029
(drought 2). In 2028 there is no drought, to measure the legacy.

**Sampling.** In each plot we take 20 soil cores at each of six sampling
occasions per year, giving 6 plots x 20 cores x 6 occasions = 720 samples per
year and about 1,440 samples in total over the drought years. Soil moisture is
measured gravimetrically on each core at sampling.

**Analyses.** Microbial community composition by 16S and ITS amplicon
sequencing (ASVs). Microbial biomass and PLFA. Carbon use efficiency (CUE) in
laboratory incubations. Soil CO2 efflux in the field with a portable chamber at
each sampling occasion.

**Statistics.** We will compare drought and control soils with t-tests and
ANOVA, using all 120 cores per occasion as independent samples, which gives high
statistical power. Community composition will be analysed with ordination and
PERMANOVA.

**Time plan.**

| Year | Activity |
|---|---|
| 2027 | Build roofs; drought 1; sampling |
| 2028 | Legacy year; sampling |
| 2029 | Drought 2; sampling |
| 2030 | Sequencing of all samples; data analysis; writing |

**Risks.** The roofs have been used before in the pilot and are robust. We do
not foresee major risks.

## 6. Data management

Data will be stored on the university server and will be available from the
principal investigator on request.

## 7. Independent line of research

The applicant has worked on soil carbon for ten years and this project builds a
new line of research on microbial ecology.

## 8. Collaboration

We will collaborate informally with colleagues working on carbon models.

## 9. Budget (summary)

Salary for one postdoc (100 %, 4 years) and the applicant (20 %). Sequencing of
1,440 samples. Roof materials. Travel to the field station.
"""

UNI = {
    "TU": "Tallmark University (fictional)",
    "KU": "Kustby University (fictional)",
    "FAU": "Fjällby Agricultural University (fictional)",
    "AU": "University of Aldenburg (fictional)",
    "VP": "Vester Polytechnic (fictional)",
    "PU": "University of Pohjala (fictional)",
}

# name, role, affiliation, identifier, keywords for the profile
PANEL = [
    ("Maren Holmqvist", "chair", UNI["TU"], "fictional-id-0001", "soil carbon; biogeochemistry; stable isotopes"),
    ("Jonas Ekbacka", "member", UNI["KU"], "fictional-id-0002", "microbial ecology; amplicon sequencing; bioinformatics"),
    ("Liv Sandström-Okafor", "member", UNI["FAU"], "fictional-id-0003", "forest ecology; drought experiments; tree physiology"),
    ("Piet van Ommeren", "member", UNI["AU"], "fictional-id-0004", "statistics for ecology; mixed models; experimental design"),
    ("Aiko Brandt", "member", UNI["VP"], "fictional-id-0005", "soil hydrology; soil moisture sensors; modelling"),
    ("Rosa Lindgren-Matu", "member", UNI["KU"], "fictional-id-0006", "plant-microbe interactions; mycorrhiza; root exudates"),
    ("Samuel Varga", "member", UNI["TU"], "fictional-id-0007", "climate science; remote sensing; carbon budgets"),
    ("Henna Kivelä", "member", UNI["PU"], "fictional-id-0008", "animal ecology; population dynamics; generalist"),
]

J = {
    "SE": "Journal of Example Soil Ecology",
    "BG": "Example Biogeochemistry Letters",
    "ME": "Microbial Example Reviews",
    "FE": "Forest Example Research",
    "ST": "Example Methods in Ecology",
    "HY": "Example Journal of Hydrology",
    "CL": "Example Climate Dynamics",
    "AN": "Example Animal Ecology",
    "HI": "Example Review of Agrarian History",
}

# name, identifier, affiliation, year, title, journal, keywords
PUBS = [
    ("Maren Holmqvist", "fictional-id-0001", UNI["TU"], 2025, "Carbon use efficiency of boreal soil microbes measured with 18O-labelled water", J["BG"], "carbon use efficiency; 18O; boreal"),
    ("Maren Holmqvist", "fictional-id-0001", UNI["TU"], 2024, "Rewetting pulses and the Birch effect: a meta-analysis of 312 experiments", J["BG"], "Birch effect; rewetting; meta-analysis"),
    ("Maren Holmqvist", "fictional-id-0001", UNI["TU"], 2022, "Drought legacies in soil carbon cycling: a review", J["SE"], "drought legacy; review; soil carbon"),
    ("Maren Holmqvist", "fictional-id-0001", UNI["TU"], 2020, "Stable isotope tracing of root-derived carbon in podzols", J["BG"], "13C; rhizodeposition; podzol"),
    ("Maren Holmqvist", "fictional-id-0001", UNI["TU"], 2018, "Soil organic matter stocks across a Swedish climate gradient", J["SE"], "soil organic carbon; climate gradient"),

    ("Jonas Ekbacka", "fictional-id-0002", UNI["KU"], 2025, "Amplicon sequence variants versus OTUs in soil fungal surveys", J["ME"], "ASV; ITS; bioinformatics"),
    ("Jonas Ekbacka", "fictional-id-0002", UNI["KU"], 2023, "Microbial community memory after repeated drying-rewetting cycles in the laboratory", J["ME"], "microbial memory; drought; 16S"),
    ("Jonas Ekbacka", "fictional-id-0002", UNI["KU"], 2021, "Relic DNA inflates diversity estimates in dry soils", J["SE"], "relic DNA; diversity; sequencing bias"),
    ("Jonas Ekbacka", "fictional-id-0002", UNI["KU"], 2019, "A pipeline for reproducible amplicon analysis", J["ST"], "pipeline; reproducibility; amplicon"),
    # trap: a different person with the same name
    ("Jonas Ekbacka", "fictional-id-0901", "Norrvik University, Department of History (fictional)", 2024, "Tithe records and harvest failure in eighteenth-century Sweden", J["HI"], "agrarian history; drought; tithes"),
    ("Jonas Ekbacka", "fictional-id-0901", "Norrvik University, Department of History (fictional)", 2021, "Peasant memory of the famine years 1771-1773", J["HI"], "famine; memory; rural history"),

    ("Liv Sandström-Okafor", "fictional-id-0003", UNI["FAU"], 2025, "Throughfall exclusion roofs: lessons from ten years in boreal forests", J["FE"], "rainfall exclusion; field methods; drought"),
    ("Liv Sandström-Okafor", "fictional-id-0003", UNI["FAU"], 2023, "Spruce fine-root dynamics during and after summer drought", J["FE"], "Norway spruce; fine roots; drought"),
    ("Liv Sandström-Okafor", "fictional-id-0003", UNI["FAU"], 2020, "Edge effects under experimental roofs bias soil moisture", J["FE"], "edge effects; soil moisture; roofs"),

    ("Piet van Ommeren", "fictional-id-0004", UNI["AU"], 2024, "Pseudoreplication in field ecology, twenty years on", J["ST"], "pseudoreplication; experimental design"),
    ("Piet van Ommeren", "fictional-id-0004", UNI["AU"], 2022, "Power analysis for mixed models with few experimental units", J["ST"], "power analysis; mixed models"),
    ("Piet van Ommeren", "fictional-id-0004", UNI["AU"], 2019, "PERMANOVA with nested designs: a practical guide", J["ST"], "PERMANOVA; nested design; community data"),

    ("Aiko Brandt", "fictional-id-0005", UNI["VP"], 2025, "Low-cost soil moisture sensor networks for field experiments", J["HY"], "soil moisture; sensors; field experiments"),
    ("Aiko Brandt", "fictional-id-0005", UNI["VP"], 2022, "Lateral water flow under rain-exclusion shelters", J["HY"], "lateral flow; rain exclusion; hydrology"),
    ("Aiko Brandt", "fictional-id-0005", UNI["VP"], 2020, "Modelling soil water in podzolised forest soils", J["HY"], "soil water model; podzol"),

    ("Rosa Lindgren-Matu", "fictional-id-0006", UNI["KU"], 2024, "Ectomycorrhizal fungi buffer spruce seedlings against drought", J["SE"], "ectomycorrhiza; drought; seedlings"),
    ("Rosa Lindgren-Matu", "fictional-id-0006", UNI["KU"], 2021, "Root exudate composition changes during water stress", J["FE"], "root exudates; rhizodeposition; water stress"),

    ("Samuel Varga", "fictional-id-0007", UNI["TU"], 2025, "Satellite detection of drought stress in Nordic forests", J["CL"], "remote sensing; drought; forest"),
    ("Samuel Varga", "fictional-id-0007", UNI["TU"], 2023, "How large is the boreal soil carbon feedback? Model uncertainty", J["CL"], "carbon budget; Earth system models; uncertainty"),

    ("Henna Kivelä", "fictional-id-0008", UNI["PU"], 2024, "Vole population cycles and winter climate", J["AN"], "population dynamics; voles; climate"),
    ("Henna Kivelä", "fictional-id-0008", UNI["PU"], 2021, "Long-term monitoring of forest birds in a warming north", J["AN"], "birds; monitoring; climate change"),
]


def main():
    paths = {}
    p = os.path.join(HERE, "proposal-draft.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(PROPOSAL)
    paths["proposal-draft.md"] = p

    p = os.path.join(HERE, "panel-fictional.csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "role", "affiliation", "identifier", "panel", "source", "date_collected", "note"])
        for name, role, aff, ident, _kw in PANEL:
            w.writerow([name, role, aff, ident,
                        "Panel E-SOIL: Ecology, soil and biogeochemistry (fictional)",
                        "https://example.org/fictional-funder/panels/e-soil",
                        "2026-11-23",
                        "FICTIONAL PERSON for a course exercise"])
    paths["panel-fictional.csv"] = p

    p = os.path.join(HERE, "publications-fictional.csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["author_name", "author_identifier", "affiliation", "year", "title", "journal", "keywords"])
        for row in PUBS:
            w.writerow(row)
    paths["publications-fictional.csv"] = p

    z = os.path.join(HERE, "reviewer-prep.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, path in paths.items():
            zf.write(path, arcname="reviewer-prep/" + name)

    print("wrote", ", ".join(paths), "and reviewer-prep.zip")
    print(f"{len(PANEL)} panel members, {len(PUBS)} publication rows "
          f"({sum(1 for r in PUBS if r[1] == 'fictional-id-0901')} belong to the namesake)")
    print(f"{len(WEAKNESSES)} deliberate weaknesses:")
    for i, w_ in enumerate(WEAKNESSES, 1):
        print(f"  {i}. {w_}")


if __name__ == "__main__":
    main()
