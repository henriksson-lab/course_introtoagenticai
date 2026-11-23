"""
make-data.py: example files for the exercise in the unit
"Choosing a model: families, sizes and benchmarks" (Part 6).

All text is synthetic: the methods excerpts are made up. Run with:

    python3 make-data.py

It writes, next to this script:
  methods-snippets.txt  12 short methods excerpts (the "test set")
  answers.csv           the answer key (sample size analysed, unit, test)
  model-test.zip        both files, in model-test/snippets/ and model-test/key/

The traps (for the teacher): exclusions (1, 6, 9), pilot numbers (7),
technical vs biological replicates (8), nested units (3, 5), numbers in
words (2, 9), a total that must be computed (11), no test (10) and a missing
sample size (12).
"""
import csv
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

ITEMS = [
    ("We enrolled 48 participants; 6 withdrew before the second visit, leaving 42 for the analysis. "
     "Groups were compared with a two-sided Welch t-test.", "42", "participants", "Welch t-test"),
    ("Twenty-four mice (twelve per group) were weighed weekly. Final weights were compared between "
     "groups with a Mann-Whitney U test.", "24", "mice", "Mann-Whitney U test"),
    ("Soil cores were taken at 15 sites, three cores per site, giving 45 cores. Nitrate content was "
     "analysed with a linear mixed model with site as a random effect.", "45", "cores (from 15 sites)",
     "linear mixed model"),
    ("A total of 312 students answered the survey (response rate 41 %). Associations between "
     "programme and answer were tested with a chi-squared test of independence.", "312", "students",
     "chi-squared test"),
    ("We analysed 1,204 images from 8 donors. Because images from the same donor are not independent, "
     "donor means were compared with a nested ANOVA.", "8", "donors (1,204 images)", "nested ANOVA"),
    ("Of the 90 plants sown, 81 germinated and were measured at day 21. Heights were compared with a "
     "one-way ANOVA followed by Tukey's HSD.", "81", "plants", "one-way ANOVA with Tukey's HSD"),
    ("Pilot data from 10 volunteers, reported elsewhere, motivated this study, in which 64 volunteers "
     "were measured before and after training. We used a paired t-test.", "64", "volunteers",
     "paired t-test"),
    ("Each condition had n = 3 biological replicates, each measured in technical triplicate. "
     "Conditions were compared with an unpaired t-test on the replicate means.", "3",
     "biological replicates per condition", "unpaired t-test"),
    ("Two hundred and six patient records were screened, of which 150 met the inclusion criteria and "
     "were analysed. Survival was modelled with a Cox proportional hazards model.", "150",
     "patient records", "Cox proportional hazards model"),
    ("Seventeen classrooms took part. No statistical test was performed; the results are "
     "descriptive.", "17", "classrooms", "none"),
    ("We recruited 30 participants in each of the three arms. Outcomes were compared across arms with "
     "a Kruskal-Wallis test.", "90", "participants", "Kruskal-Wallis test"),
    ("Samples from treated and untreated plots were classified as infected or not, and the "
     "proportions were compared with Fisher's exact test.", "not stated", "samples", "Fisher's exact test"),
]

with open(os.path.join(HERE, "methods-snippets.txt"), "w") as f:
    f.write("Methods excerpts, one per item. Synthetic examples.\n\n")
    for i, (text, *_rest) in enumerate(ITEMS, 1):
        f.write(f"[{i}] {text}\n\n")

with open(os.path.join(HERE, "answers.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "n_analysed", "unit", "test"])
    for i, (_t, n, unit, test) in enumerate(ITEMS, 1):
        w.writerow([i, n, unit, test])

with zipfile.ZipFile(os.path.join(HERE, "model-test.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(HERE, "methods-snippets.txt"), "model-test/snippets/methods-snippets.txt")
    z.write(os.path.join(HERE, "answers.csv"), "model-test/key/answers.csv")
print("wrote methods-snippets.txt, answers.csv, model-test.zip")
