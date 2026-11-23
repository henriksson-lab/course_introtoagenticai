#!/bin/sh
# make-reference.sh (teacher-only; needs octave-cli and python3)
# 1. Produce growth-legacy/gr_out_0312.txt by running the UNCHANGED legacy
#    script gr_calc.m in GNU Octave. It stands in for the output the former
#    student saved.
# 2. Pack growth-legacy/ into growth-legacy.zip for participants.
# Run after make-data.py.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/growth-legacy" && octave-cli --no-gui --quiet --eval "gr_calc"
cd "$HERE" && python3 -c "
import zipfile, os
with zipfile.ZipFile('growth-legacy.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir('growth-legacy')):
        z.write(os.path.join('growth-legacy', f), 'growth-legacy/' + f)
"
