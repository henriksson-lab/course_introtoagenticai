# make-data.py: example data for the unit "Open-weights models and data privacy".
#
# Writes:
#   methods-snippets.txt  eight short, made-up "methods" paragraphs from several fields
#   answer-key.csv        the correct extraction for each paragraph (for checking)
#   methods-snippets.zip  the snippets file only (what participants download)
#
# All text is synthetic: the studies, numbers and places are invented for teaching.
# Several paragraphs contain small traps (units to convert, a total to add up,
# a value that is not stated, a distracting second number) so that a weaker
# model makes visible mistakes. Run with:  python3 make-data.py

import csv
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

SNIPPETS = [
    ("S1",
     "Seedlings of Arabidopsis thaliana (Col-0) were grown on agar plates at 22 °C "
     "under long-day conditions. Three plates of 15 seedlings each were used per "
     "treatment, and root length was measured after 10 days. Two seedlings were "
     "lost to contamination and excluded."),
    ("S2",
     "We surveyed 412 first-year engineering students at two campuses about study "
     "habits. The questionnaire was open for three weeks in October. Of the 412 "
     "invited, 287 completed it; only complete responses were analysed. Room "
     "temperature was not relevant to this study."),
    ("S3",
     "Zebrafish larvae (Danio rerio, AB strain) were kept at 28.5 °C and exposed to "
     "the compound from 2 to 5 days post-fertilisation. In total 96 larvae were "
     "imaged (48 treated, 48 controls)."),
    ("S4",
     "Steel coupons (n = 24) were cycled in a salt-spray chamber held at 35 °C for "
     "a period of six weeks, after which mass loss was recorded. A second batch of "
     "12 coupons, kept dry, served as a reference and is reported elsewhere."),
    ("S5",
     "Soil cores were collected from 9 sites along a 40 km transect and incubated "
     "in the dark for 72 hours before respiration was measured. Incubation "
     "temperature was kept constant."),
    ("S6",
     "Escherichia coli K-12 cultures were grown overnight in LB medium at 37 °C, "
     "diluted 1:100 and grown for a further 3 hours. Each condition was run in "
     "biological triplicate across four conditions."),
    ("S7",
     "Interviews were held with 18 hospital pharmacists between March and May; "
     "each lasted 40 to 60 minutes. Transcripts were coded by two researchers."),
    ("S8",
     "Daphnia magna were cultured at 20 °C (68 °F) in groups of 10 animals per "
     "beaker, with 6 beakers per treatment and 3 treatments. Survival was "
     "recorded daily for 21 days."),
]

# organism_or_material, sample_size, temperature_C, duration_days
# "not stated" where the paragraph does not give the value.
ANSWERS = [
    ("S1", "Arabidopsis thaliana", "43", "22", "10",
     "3 x 15 = 45 seedlings, minus 2 excluded = 43"),
    ("S2", "first-year engineering students", "287", "not stated", "21",
     "287 analysed, not 412 invited; three weeks = 21 days; no temperature"),
    ("S3", "Danio rerio (zebrafish)", "96", "28.5", "3",
     "exposed from day 2 to day 5 = 3 days"),
    ("S4", "steel coupons", "24", "35", "42",
     "six weeks = 42 days; the 12 reference coupons are not part of this study"),
    ("S5", "soil", "9", "not stated", "3",
     "72 hours = 3 days; temperature 'constant' but no value given"),
    ("S6", "Escherichia coli K-12", "12", "37", "not stated",
     "triplicate x 4 conditions = 12; 'overnight + 3 hours' is not a stated number of days"),
    ("S7", "hospital pharmacists", "18", "not stated", "not stated",
     "March to May is the data collection period, not a study duration in days"),
    ("S8", "Daphnia magna", "180", "20", "21",
     "10 animals x 6 beakers x 3 treatments = 180; use the Celsius value"),
]


def main():
    txt = os.path.join(HERE, "methods-snippets.txt")
    with open(txt, "w", encoding="utf-8") as f:
        f.write("Eight short methods paragraphs (synthetic, for teaching)\n\n")
        for sid, text in SNIPPETS:
            f.write(f"[{sid}] {text}\n\n")

    with open(os.path.join(HERE, "answer-key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "organism_or_material", "sample_size", "temperature_C",
                    "duration_days", "note"])
        w.writerows(ANSWERS)

    with zipfile.ZipFile(os.path.join(HERE, "methods-snippets.zip"), "w",
                         zipfile.ZIP_DEFLATED) as z:
        z.write(txt, arcname="methods-snippets.txt")


if __name__ == "__main__":
    main()
