#!/bin/sh
# make-data.sh: example files for the track "Teaching materials".
#
# question-bank.md and lecture-outline.md are written by hand (no personal
# data; the questions are invented for this course). This script
#   1. converts the bank to a Canvas QTI zip and an answer key (bank2qti.py,
#      Python standard library only), and
#   2. packs the files participants download into teaching-example.zip.
# Run it from anywhere:  sh make-data.sh
set -e
here=$(dirname "$0")
python3 -I "$here/bank2qti.py" "$here/question-bank.md"
rm -f "$here/teaching-example.zip"
python3 -I - "$here" <<'PY'
import sys, zipfile, pathlib
d = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(d / "teaching-example.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in ("question-bank.md", "bank2qti.py", "lecture-outline.md"):
        z.write(d / name, f"teaching-example/{name}")
print("wrote teaching-example.zip")
PY
