"""make-data.py: synthetic course-evaluation export for the track
"Survey and tabular data" (Introduction to agentic AI).

Everything here is invented: the course, the students, the teachers and the
comments. Any resemblance to real people is accidental.

What it makes (in the folder of this script):
  course-evaluation-export.xlsx  the messy export the participant gets
                                 (via course-evaluation-export.csv and
                                 LibreOffice; the CSV is kept as well)
  truth-clean.csv                the 120 real respondents, items coded 1-5
                                 as worded (NOT reverse-coded), NA = blank
  truth-comments.csv             every free-text answer with its true theme
  answer-key.md                  the known answers used on the exercise page

The export imitates a Microsoft Forms / Google Forms download that a course
coordinator has extended by hand:
  - 107 online rows: 105 real students, 1 test response made by the
    teacher before the survey opened, 1 double submission (identical
    answers one minute apart)
  - 15 paper forms from the last lab session, typed in by a teaching
    assistant below the online rows: Likert answers as numbers 1-5,
    programme names typed freely, no timestamps
  - 12 Likert items; items 5 and 9 are negatively worded (reverse-coded)
  - item 3 has a "Not applicable" option
  - about 3 % of answers left blank at random, and one student who stopped
    after item 6
  - two free-text questions, some answers in Swedish, three of them naming
    a teaching assistant, one naming a lecturer, and one that identifies a
    student through a disability
  - small groups: 4 exchange students, 3 non-binary students, 2 who prefer
    not to say their gender

Run:  python3 make-data.py     (needs numpy and scipy; LibreOffice for .xlsx)
"""
import csv
import subprocess
import shutil
import tempfile
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(20260611)

ITEMS = [
    "The learning outcomes of the course were clear to me.",
    "The lectures helped me learn.",
    "The recorded lectures helped me learn.",
    "The lab sessions helped me understand the theory.",
    "The workload was unreasonably high.",
    "The course literature was useful.",
    "I received useful feedback on my lab reports.",
    "The feedback came in time for me to use it.",
    "I often felt unsure about what was expected of me.",
    "The exam matched what we practised in the course.",
    "The teachers were approachable.",
    "Overall, I am satisfied with the course.",
]
REVERSED = {5, 9}          # item numbers (1-based) that are negatively worded
LABELS = ["Strongly disagree", "Disagree", "Neither agree nor disagree",
          "Agree", "Strongly agree"]
NA_LABEL = "Not applicable (I did not use them)"
Q_WELL = "What worked well in the course?"
Q_IMPROVE = "What should be improved for next year?"
Q_PROG = "Which programme are you enrolled in?"
Q_MODE = "How did you mainly take the course?"
Q_AGE = "Age group"
Q_GENDER = "Gender"

# ---- the 120 real respondents ------------------------------------------------
N_ONLINE, N_PAPER = 105, 15
N = N_ONLINE + N_PAPER

programme = (["Biomedicine"] * 52 + ["Biotechnology"] * 38 + ["Medicine"] * 16
             + ["Exchange student"] * 4 + ["Other / single-subject course"] * 10)
mode = ["Campus"] * 84 + ["Distance"] * 36
gender = ["Woman"] * 70 + ["Man"] * 45 + ["Non-binary"] * 3 + ["Prefer not to say"] * 2
age = ["18-21"] * 41 + ["22-25"] * 49 + ["26-30"] * 18 + ["31 or older"] * 12
for lst in (programme, mode, gender, age):
    rng.shuffle(lst)
# paper forms come from the last campus lab session: make the last 15 campus
mode = np.array(mode)
dist_idx = [i for i in range(N_ONLINE, N) if mode[i] == "Distance"]
camp_idx = [i for i in range(N_ONLINE) if mode[i] == "Campus"]
for a, b in zip(dist_idx, camp_idx):
    mode[a], mode[b] = mode[b], mode[a]
mode = list(mode)
# exchange students take the course on campus
for i in range(N):
    if programme[i] == "Exchange student" and mode[i] == "Distance":
        j = next(k for k in range(N_ONLINE) if mode[k] == "Campus"
                 and programme[k] != "Exchange student")
        programme[i], programme[j] = programme[j], programme[i]

# Item means on the 1-5 scale (as worded) for campus students; distance
# students differ on items 3 (recordings, higher) and 4 (labs, lower).
base = np.array([3.9, 3.6, 3.5, 4.0, 3.6, 3.3, 3.2, 2.4, 2.6, 3.0, 4.2, 3.7])
dist_shift = np.zeros(12)
dist_shift[2] = +0.8
dist_shift[3] = -1.1
loading = np.array([1, 1, .6, .8, -.8, .6, .9, .8, -1, .8, .7, 1.2])

latent = rng.normal(0, 0.7, N)
X = np.zeros((N, 12))
for i in range(N):
    mu = base + loading * latent[i] + (dist_shift if mode[i] == "Distance" else 0)
    X[i] = np.clip(np.rint(mu + rng.normal(0, 0.65, 12)), 1, 5)
X = X.astype(float)

# one straight-liner: "Strongly agree" everywhere, even on the reversed items
straight = 17
X[straight] = 5

# item 3: not applicable for some campus students
na3 = [i for i in range(N) if mode[i] == "Campus" and rng.random() < 0.14]
NA_CODE = -1.0
X[na3, 2] = NA_CODE

# random blanks (about 3 %), never on the straight-liner
mask = rng.random(X.shape) < 0.03
mask[straight] = False
X[mask] = np.nan
# one student stopped after item 6
stopper = 63
X[stopper, 6:] = np.nan

# ---- free-text answers -------------------------------------------------------
IMPROVE = {
    "workload": [
        "Weeks 3 and 4 were far too heavy, two lab reports and a quiz in the same week.",
        "Too much at once in the middle of the course.",
        "The workload in week 3 was not realistic next to the other course.",
        "Spread out the deadlines. Week 4 was a nightmare.",
        "Less reading in the first half, it piled up.",
        "Two reports due on the same day should not happen.",
        "Heavy workload, I worked every weekend.",
        "Please move one of the lab reports to a later week.",
        "The middle weeks were stressful because everything was due at once.",
        "It felt like 20 credits of work for a 15 credit course.",
        "Workload. Too many small assignments.",
        "Fewer hand-ins in week 3-4 would help a lot.",
        "I liked the content but the pace in weeks 3 and 4 was too fast.",
        "Reduce the number of quizzes when lab reports are due.",
        "The schedule in the middle of the course left no time to read.",
        "För mycket på en gång under vecka 3 och 4.",
    ],
    "late feedback": [
        "Feedback on lab report 1 came after report 2 was due, so I could not use it.",
        "Faster feedback on the lab reports please.",
        "We got our reports back three weeks later.",
        "The feedback was good but came too late to help.",
        "Lab report feedback should come before the next report.",
        "I never knew if I was on the right track because feedback took so long.",
        "Return the graded reports sooner.",
        "Feedback was slow.",
        "It would help to get comments on the first report earlier.",
        "The comments on my report were useful, but I got them after the exam.",
        "Quicker turnaround on lab reports.",
        "Some kind of feedback during the lab, not only weeks afterwards.",
        "Feedbacken på labbrapporterna kom alldeles för sent.",
    ],
    "recordings": [
        "The sound in the recorded lectures was often bad.",
        "Some recordings were missing the slides.",
        "Upload the recordings the same day, not a week later.",
        "Lecture 7 was never recorded.",
        "The microphone did not pick up the students' questions.",
        "Better audio in the recordings.",
        "Recordings should be split into shorter parts.",
    ],
    "exam alignment": [
        "The exam had calculation questions we never practised.",
        "The exam did not match the seminars.",
        "More old exams to practise on.",
        "The exam focused on details from the literature that were not in the lectures.",
        "Make the exam more like the quizzes.",
        "The exam questions were worded differently from anything we had seen.",
    ],
    "distance lab week": [
        "As a distance student the lab week on campus was too compressed.",
        "Five lab days in a row on campus was exhausting for those of us travelling.",
        "Distance students should get the lab instructions earlier so we can prepare.",
        "The compressed lab week meant I did not understand what we were doing.",
        "Spread the campus labs over two visits for distance students.",
    ],
    "lab accessibility": [
        "As the only wheelchair user in the group, the lab benches in room B214 were too high for me.",
    ],
    "complaint about a named lecturer": [
        "Lecturer Anna Berg was dismissive when I asked a question in the seminar in week 5.",
    ],
    "other": [
        "The lecture hall was cold.",
        "Schedule changes were announced at very short notice.",
        "Rooms changed twice without warning.",
        "More practice problems with solutions.",
        "More worked examples in the lectures.",
        "The textbook is expensive, a library copy would help.",
        "The Canvas page was confusing, hard to find the lab instructions.",
        "Organise Canvas by week.",
        "Longer breaks in the three-hour lectures.",
        "Nothing really.",
    ],
}
WELL = {
    "labs": [
        "The labs were the best part of the course.",
        "Hands-on lab work made the theory click.",
        "I liked the cell culture lab a lot.",
        "Labs! Finally doing real experiments.",
        "The microscopy lab was great.",
        "The lab sessions connected well to the lectures.",
        "Working in the lab in small groups.",
        "Lab work was well organised.",
        "The labs, especially the western blot.",
        "Practical work in the lab.",
        "I learned most from the labs.",
        "The lab supervisors explained things well during the labs.",
        "Good labs with clear instructions.",
        "The lab where we designed our own experiment.",
        "Labs were fun and useful.",
        "Seeing the cells under the microscope myself.",
        "The labs made the course worth it.",
        "Labbarna var bäst!",
    ],
    "quizzes": [
        "The weekly quizzes kept me on track.",
        "Quizzes were a good way to check my understanding.",
        "I liked the short quizzes after each lecture.",
        "The online quizzes helped me revise.",
        "Quizzes with instant feedback.",
        "The quizzes made me study every week instead of at the end.",
        "Good quizzes.",
        "The practice quizzes before the exam.",
        "Weekly quizzes, please keep them.",
        "Quizzes helped me see what was important.",
        "The quiz questions were good preparation.",
    ],
    "approachable teachers": [
        "The teachers were friendly and easy to ask.",
        "Erik in the lab was always willing to explain again.",
        "Teachers answered questions on the forum quickly.",
        "Approachable teachers.",
        "The TA Erik was very helpful.",
        "The teaching team clearly cared about us.",
        "Easy to get help during the labs.",
        "I felt I could ask anything.",
        "Erik's extra help session before the exam.",
        "Friendly and engaged teachers.",
    ],
    "recordings": [
        "Having recorded lectures made it possible for me to work alongside studying.",
        "Recordings meant I could rewatch the hard parts.",
        "The recorded lectures were essential as a distance student.",
        "I could study in the evenings thanks to the recordings.",
        "Being able to pause and rewatch the lectures.",
        "The recordings were well structured.",
        "Recorded lectures.",
        "The recordings saved me when I was ill.",
    ],
    "other": [
        "Group work in the seminars.",
        "The seminars with case discussions.",
        "Working with other students in the group project.",
        "The study guide for each week.",
        "The study guide made it clear what to read.",
        "Good course overall.",
        "Everything.",
        "Interesting topic.",
    ],
}


def assign(pool_dict, prefer, n_answer_rate):
    """Give comments to respondents. prefer(theme) returns a score per
    respondent; higher = more likely to have written that comment."""
    used = {stopper, straight}
    out = {}
    for theme, texts in pool_dict.items():
        score = prefer(theme) + rng.normal(0, 0.6, N)
        order = [i for i in np.argsort(-score) if i not in used]
        for text, i in zip(texts, order):
            out[i] = (text, theme)
            used.add(i)
    return out


def x(i, item):
    v = X[i, item - 1]
    return 3.0 if np.isnan(v) or v < 0 else v


def prefer_improve(theme):
    s = np.zeros(N)
    for i in range(N):
        if theme == "workload":
            s[i] = x(i, 5)
        elif theme == "late feedback":
            s[i] = 6 - x(i, 8)
        elif theme == "recordings":
            s[i] = 6 - x(i, 3) + (2 if mode[i] == "Distance" else 0)
        elif theme == "exam alignment":
            s[i] = 6 - x(i, 10)
        elif theme == "distance lab week":
            s[i] = 50 if mode[i] == "Distance" and i < N_ONLINE else -50
    return s


def prefer_well(theme):
    s = np.zeros(N)
    for i in range(N):
        if theme == "labs":
            s[i] = x(i, 4)
        elif theme == "approachable teachers":
            s[i] = x(i, 11)
        elif theme == "recordings":
            s[i] = x(i, 3) + (3 if mode[i] == "Distance" else 0)
    return s


improve = assign(IMPROVE, prefer_improve, 0.5)
well = assign(WELL, prefer_well, 0.45)
# (the straight-liner and the student who stopped early write nothing)

# ---- timestamps for online rows ----------------------------------------------
start = np.datetime64("2026-06-08T09:00")
mins = np.sort(rng.integers(0, 60 * 24 * 14, N_ONLINE))


def ts(m, extra):
    t = start + np.timedelta64(int(m), "m") + np.timedelta64(int(extra), "s")
    return str(t).replace("T", " ")


# ---- build the export rows ---------------------------------------------------
PAPER_PROG = {"Biomedicine": ["Biomed", "biomedicine", "BMA", "Biomedicine"],
              "Biotechnology": ["Biotech", "biotechnology", "Bioteknik"],
              "Medicine": ["Medicine", "med", "Läkarprogrammet"],
              "Other / single-subject course": ["fristående kurs", "other"],
              "Exchange student": ["Exchange"]}

header = (["ID", "Start time", "Completion time", "Email", "Name",
           Q_PROG, Q_MODE, Q_AGE, Q_GENDER]
          + [f"{k+1}. {t}" for k, t in enumerate(ITEMS)] + [Q_WELL, Q_IMPROVE])


def online_row(rid, i, m):
    r = [rid, ts(m, 0), ts(m, 240 + rng.integers(0, 600)), "anonymous", "",
         programme[i], mode[i], age[i], gender[i]]
    for k in range(12):
        v = X[i, k]
        r.append("" if np.isnan(v) else NA_LABEL if v < 0 else LABELS[int(v) - 1])
    r += [well.get(i, ("", ""))[0], improve.get(i, ("", ""))[0]]
    return r


rows = []
test = (["1", "2026-06-05 16:02:11", "2026-06-05 16:03:40", "anonymous", "",
         "Biomedicine", "Campus", "31 or older", "Prefer not to say"]
        + [LABELS[2]] * 12 + ["test", "test test - delete me"])
rows.append(test)
rid = 2
dup_of = 40
for i in range(N_ONLINE):
    rows.append(online_row(str(rid), i, mins[i]))
    rid += 1
    if i == dup_of:
        r = online_row(str(rid), i, mins[i] + 1)
        r[3:] = rows[-1][3:]
        done = np.datetime64(rows[-1][2].replace(" ", "T")) + np.timedelta64(60, "s")
        r[2] = str(done).replace("T", " ")
        rows.append(r)
        dup_row_id = rid
        dup_first_id = rid - 1
        rid += 1
paper_ids = []
for n, i in enumerate(range(N_ONLINE, N), start=1):
    pid = f"paper-{n:02d}"
    paper_ids.append(pid)
    choices = PAPER_PROG[programme[i]]
    r = [pid, "", "", "paper", "", choices[rng.integers(len(choices))],
         "campus", age[i], gender[i]]
    for k in range(12):
        v = X[i, k]
        r.append("" if np.isnan(v) else "N/A" if v < 0 else str(int(v)))
    r += [well.get(i, ("", ""))[0], improve.get(i, ("", ""))[0]]
    rows.append(r)

csv_path = HERE / "course-evaluation-export.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)

# ---- truth files ---------------------------------------------------------------
resp_ids = []
rid = 2
for i in range(N_ONLINE):
    resp_ids.append(str(rid))
    rid += 1
    if i == dup_of:
        rid += 1
resp_ids += paper_ids

with open(HERE / "truth-clean.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["respondent", "source", "programme", "mode", "age_group",
                "gender"] + [f"q{k+1:02d}" for k in range(12)])
    for i in range(N):
        vals = ["" if np.isnan(v) else "NA" if v < 0 else str(int(v))
                for v in X[i]]
        w.writerow([resp_ids[i], "online" if i < N_ONLINE else "paper",
                    programme[i], mode[i], age[i], gender[i]] + vals)

with open(HERE / "truth-comments.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["respondent", "question", "theme", "text"])
    for qname, d in (("worked_well", well), ("improve", improve)):
        for i in sorted(d):
            w.writerow([resp_ids[i], qname, d[i][1], d[i][0]])

# ---- answer key ----------------------------------------------------------------
def valid(col):
    return col[~np.isnan(col) & (col > 0)]


lines = ["# Answer key: course-evaluation-export.xlsx", "",
         "Generated by make-data.py. All data is synthetic.", "",
         "## Rows", "",
         f"- The export has {len(rows)} data rows below the header.",
         "- Remove 2: the test response (ID 1, dated 5 June, before the survey "
         "opened on 8 June, free text 'test'), and the double submission "
         f"(ID {dup_row_id} repeats ID {dup_first_id} one minute later, every "
         "answer identical).",
         f"- **{N} respondents remain**: {N_ONLINE} online and {N_PAPER} on paper.",
         "- 164 students were registered, so the response rate is "
         f"{N}/164 = {100*N/164:.0f} %.",
         f"- Respondent {resp_ids[stopper]} stopped after item 6 (items 7-12 "
         "blank). Keep them: their first six answers count.",
         f"- Respondent {resp_ids[straight]} answered 'Strongly agree' to all "
         "12 items, including the two negatively worded ones. Flag, do not "
         "silently remove; report with and without.", "",
         "## Groups (after cleaning)", ""]
for name, lst in ((Q_PROG, programme), (Q_MODE, mode), (Q_GENDER, gender),
                  (Q_AGE, age)):
    vals, cnt = np.unique(lst, return_counts=True)
    lines.append(f"- {name}: " + ", ".join(f"{v} {c}" for v, c in zip(vals, cnt)))
lines += ["",
          "Paper rows spell programmes freely (Biomed, BMA, Bioteknik, "
          "Läkarprogrammet = Medicine, fristående kurs = Other / single-subject "
          "course, Exchange) and write mode as 'campus'.", "",
          "Groups smaller than 5 that must not be reported on their own: "
          "Exchange student (4), Non-binary (3), Prefer not to say (2). "
          "Combine them (for example 'Other or not stated') or leave them out "
          "of breakdowns. Cross-tabulations (programme x mode x gender) "
          "create many more small cells.", "",
          "## Items (as worded, 1 = Strongly disagree ... 5 = Strongly agree)", "",
          "Items 5 and 9 are negatively worded. For a scale score, reverse them "
          "(6 - answer). Item 3 has 'Not applicable', which is not a scale "
          "value: treat it as missing for the item statistics, and report the "
          "count.", "",
          "| Item | n answered | not applicable | blank | % agree (4-5) | "
          "% disagree (1-2) | median | mean |",
          "|---|---|---|---|---|---|---|---|"]
for k in range(12):
    col = X[:, k]
    v = valid(col)
    lines.append(
        f"| {k+1}{' (R)' if k+1 in REVERSED else ''} {ITEMS[k]} | {len(v)} | "
        f"{int(np.sum(col < 0))} | {int(np.sum(np.isnan(col)))} | "
        f"{100*np.mean(v >= 4):.0f} | {100*np.mean(v <= 2):.0f} | "
        f"{np.median(v):g} | {v.mean():.2f} |")

Xr = X.copy()
Xr[Xr < 0] = np.nan
for k in REVERSED:
    Xr[:, k - 1] = 6 - Xr[:, k - 1]
score = np.nanmean(Xr, axis=1)
complete = Xr[~np.isnan(Xr).any(axis=1)]
kk = complete.shape[1]
alpha = kk / (kk - 1) * (1 - complete.var(axis=0, ddof=1).sum()
                         / complete.sum(axis=1).var(ddof=1))
Xwrong = X.copy()
Xwrong[Xwrong < 0] = np.nan
cw = Xwrong[~np.isnan(Xwrong).any(axis=1)]
alpha_wrong = kk / (kk - 1) * (1 - cw.var(axis=0, ddof=1).sum()
                               / cw.sum(axis=1).var(ddof=1))
lines += ["",
          "## Scale score", "",
          "Course experience score = mean of the 12 items after reversing "
          "items 5 and 9, over the items each person answered.", "",
          f"- Mean score over {N} respondents: **{np.mean(score):.2f}** "
          f"(SD {np.std(score, ddof=1):.2f}).",
          f"- Cronbach's alpha (respondents with all 12 items answered, "
          f"n = {complete.shape[0]}): **{alpha:.2f}** with items 5 and 9 "
          f"reversed; **{alpha_wrong:.2f}** if someone forgets to reverse them. "
          "A drop like this is a sign that reverse-coding was missed.", ""]

camp = np.array(mode) == "Campus"
lines += ["## Campus vs distance", "",
          "| Item | campus % agree (n) | distance % agree (n) | "
          "Mann-Whitney p |", "|---|---|---|---|"]
for k in range(12):
    a, b = valid(X[camp, k]), valid(X[~camp, k])
    p = mannwhitneyu(a, b).pvalue
    lines.append(f"| {k+1} | {100*np.mean(a>=4):.0f} ({len(a)}) | "
                 f"{100*np.mean(b>=4):.0f} ({len(b)}) | {p:.3g} |")
lines += ["",
          "Built into the data: distance students rate item 3 (recordings) "
          "higher and item 4 (labs) lower. Those two are the real differences. "
          "With 12 tests, about one in twenty would reach p < 0.05 by chance "
          "alone if there were no differences at all; any other 'significant' "
          "item should be treated with care.", "",
          "## Free text", "",
          f"- '{Q_WELL}': {len(well)} answers.",
          f"- '{Q_IMPROVE}': {len(improve)} answers.",
          "- Paper rows write 'N/A' for not applicable on item 3.",
          "- Three answers are in Swedish (one workload, one late feedback, "
          "one labs).", "",
          "Themes used to generate the comments (a human coder may reasonably "
          "differ by one or two per theme):", ""]
for qname, d in ((Q_WELL, well), (Q_IMPROVE, improve)):
    themes, cnt = np.unique([t for _, t in d.values()], return_counts=True)
    lines.append(f"- {qname} " + "; ".join(f"{t}: {c}" for t, c in
                                         sorted(zip(themes, cnt),
                                                key=lambda z: -z[1])))
lines += ["",
          "Comments that must not be quoted in a report:", "",
          "- three comments name the teaching assistant 'Erik' (positive, but "
          "still personal data about a staff member);",
          "- one names a lecturer, 'Anna Berg', with a complaint: handle "
          "through the normal channels, not in a report to the programme "
          "board;",
          "- one identifies a student as 'the only wheelchair user in the "
          "group': health data, and identifying. Report the issue (lab bench "
          "height in B214) without the quote.", "",
          "Every quote in a report must appear word for word in the export. "
          "truth-comments.csv lists every comment with its theme."]
(HERE / "answer-key.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ---- xlsx via LibreOffice -------------------------------------------------------
soffice = shutil.which("soffice")
if soffice:
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([soffice, f"-env:UserInstallation=file://{prof}",
                        "--headless", "--infilter=CSV:44,34,76,1",
                        "--convert-to", "xlsx", "--outdir", str(HERE),
                        str(csv_path)], check=True, capture_output=True)
    print("wrote course-evaluation-export.xlsx")
else:
    print("LibreOffice not found: only the CSV was written")
print(f"{len(rows)} export rows, {N} real respondents")
