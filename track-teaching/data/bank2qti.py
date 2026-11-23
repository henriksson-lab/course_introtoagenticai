#!/usr/bin/env python3
"""
bank2qti.py: turn a question bank in a simple Markdown format into a quiz
that Canvas can import.

Example for the track "Teaching materials" (Introduction to agentic AI).
Uses only the Python standard library: nothing to install.

Usage:
    python3 bank2qti.py question-bank.md
    python3 bank2qti.py question-bank.md --title "Describing data, week 2"

Writes, next to the bank file:
    <name>-qti.zip       QTI 1.2 package (Canvas flavour). Import it in Canvas:
                         Course > Settings > Import Course Content >
                         Content Type "QTI .zip file".
    <name>-key.md        answer key with the reason for every choice, for you
                         and your co-teachers. Keep it private.

Supports two question types: multiple choice with exactly one correct answer
(with feedback per choice, so students see why a distractor is wrong), and
numeric answers with an allowed margin. The bank format is described at the
top of question-bank.md.

Before writing anything the script checks the bank and stops with a list of
problems (no correct choice, two correct choices, a choice without a reason,
a numeric question without an answer, duplicate ids). Fix them and rerun.

The QTI layout follows the files Canvas itself exports for Classic Quizzes,
in the same way as the canvas-quiz/build.py pipeline of the sister course
(Quantitative biology, 3MB00A). Canvas can convert the import to New Quizzes
if your institution has turned that option on.
"""

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


# ---------------------------------------------------------------- reading

def parse_bank(text):
    """Return a list of question dicts from the Markdown bank."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # drop comments
    blocks = re.split(r"(?m)^## ", text)[1:]             # one block per question
    questions = []
    for block in blocks:
        lines = block.rstrip().split("\n")
        m = re.match(r"\s*([\w-]+)\s*:\s*(.+)", lines[0])
        if not m:
            raise SystemExit(f"Cannot read question heading: '## {lines[0]}'")
        q = {"id": m.group(1), "title": m.group(2).strip(), "choices": [],
             "stem_lines": [], "explanation": ""}
        current = None  # the choice that a "why:" line belongs to
        for line in lines[1:]:
            meta = re.match(r"-\s*(type|topic|difficulty)\s*:\s*(.+)", line)
            choice = re.match(r"(\*?)([A-H])\)\s+(.+)", line)
            why = re.match(r"\s+why\s*:\s*(.+)", line)
            kv = re.match(r"(answer|margin|explanation)\s*:\s*(.+)", line)
            if meta:
                q[meta.group(1)] = meta.group(2).strip()
            elif choice:
                current = {"letter": choice.group(2), "text": choice.group(3).strip(),
                           "correct": choice.group(1) == "*", "why": ""}
                q["choices"].append(current)
            elif why and current is not None:
                current["why"] = why.group(1).strip()
            elif kv:
                q[kv.group(1)] = kv.group(2).strip()
            elif not q["choices"]:
                q["stem_lines"].append(line)
        q["stem"] = "\n".join(q.pop("stem_lines")).strip()
        questions.append(q)
    return questions


def check_bank(questions):
    """Return a list of problems; empty if the bank is fine."""
    problems, seen = [], set()
    for q in questions:
        where = f"{q['id']} ({q['title']})"
        if q["id"] in seen:
            problems.append(f"{where}: the id is used twice")
        seen.add(q["id"])
        if not q["stem"]:
            problems.append(f"{where}: no question text")
        qtype = q.get("type")
        if qtype == "mc":
            n_correct = sum(c["correct"] for c in q["choices"])
            if len(q["choices"]) < 2:
                problems.append(f"{where}: fewer than two choices")
            if n_correct != 1:
                problems.append(f"{where}: {n_correct} choices marked correct (need exactly 1)")
            for c in q["choices"]:
                if not c["why"]:
                    problems.append(f"{where}: choice {c['letter']} has no 'why:' line")
        elif qtype == "numeric":
            for key in ("answer", "margin"):
                try:
                    float(q.get(key, ""))
                except ValueError:
                    problems.append(f"{where}: '{key}:' is missing or not a number")
        else:
            problems.append(f"{where}: type must be mc or numeric, not '{qtype}'")
    return problems


# ---------------------------------------------------------------- QTI output

def para_html(text):
    """Plain text -> HTML paragraphs; *word* -> <em>word</em>."""
    out = []
    for p in re.split(r"\n\s*\n", text.strip()):
        p = html.escape(p)
        p = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", p)
        out.append("<p>" + p.replace("\n", "<br/>") + "</p>")
    return "".join(out)


def mattext(fragment):
    # Canvas expects the HTML escaped inside <mattext texttype="text/html">
    return f'<material><mattext texttype="text/html">{html.escape(fragment)}</mattext></material>'


def item_metadata(qtype, points=1.0):
    return ("<itemmetadata><qtimetadata>"
            f"<qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>{qtype}</fieldentry></qtimetadatafield>"
            f"<qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>{points}</fieldentry></qtimetadatafield>"
            "</qtimetadata></itemmetadata>")


def general_feedback(q):
    """(condition that shows it, the feedback block); empty if none."""
    if not q.get("explanation"):
        return "", ""
    show = ('<respcondition continue="Yes"><conditionvar><other/></conditionvar>'
            '<displayfeedback feedbacktype="Response" linkrefid="general_fb"/></respcondition>')
    block = (f'<itemfeedback ident="general_fb"><flow_mat>{mattext(para_html(q["explanation"]))}'
             "</flow_mat></itemfeedback>")
    return show, block


SCORE_DECL = '<outcomes><decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/></outcomes>'
FULL_SCORE = '<setvar action="Set" varname="SCORE">100</setvar>'


def qti_item(q):
    head = f'<item ident="{q["id"]}" title="{html.escape(q["title"])}">'
    show_general, general_block = general_feedback(q)
    stem = mattext(para_html(q["stem"]))

    if q["type"] == "numeric":
        a, m = float(q["answer"]), float(q["margin"])
        presentation = ("<presentation>" + stem +
                        '<response_str ident="response1" rcardinality="Single">'
                        '<render_fib fibtype="Decimal"><response_label ident="answer1"/></render_fib>'
                        "</response_str></presentation>")
        correct = ('<respcondition continue="No"><conditionvar><or>'
                   f'<varequal respident="response1">{a}</varequal>'
                   f'<and><vargte respident="response1">{a - m}</vargte>'
                   f'<varlte respident="response1">{a + m}</varlte></and>'
                   f"</or></conditionvar>{FULL_SCORE}</respcondition>")
        return (head + item_metadata("numerical_question") + presentation +
                "<resprocessing>" + SCORE_DECL + show_general + correct + "</resprocessing>" +
                general_block + "</item>")

    # multiple choice: one response label per choice, feedback per choice
    ids = [f'{q["id"]}_{c["letter"]}' for c in q["choices"]]
    labels = "".join(f'<response_label ident="{i}">{mattext(html.escape(c["text"]))}</response_label>'
                     for i, c in zip(ids, q["choices"]))
    presentation = ("<presentation>" + stem +
                    '<response_lid ident="response1" rcardinality="Single">'
                    f"<render_choice>{labels}</render_choice></response_lid></presentation>")
    per_choice = "".join(
        f'<respcondition continue="Yes"><conditionvar><varequal respident="response1">{i}</varequal>'
        f'</conditionvar><displayfeedback feedbacktype="Response" linkrefid="{i}_fb"/></respcondition>'
        for i in ids)
    right = next(i for i, c in zip(ids, q["choices"]) if c["correct"])
    correct = (f'<respcondition continue="No"><conditionvar><varequal respident="response1">{right}</varequal>'
               f"</conditionvar>{FULL_SCORE}</respcondition>")
    choice_blocks = "".join(
        f'<itemfeedback ident="{i}_fb"><flow_mat>{mattext("<p>" + html.escape(c["why"]) + "</p>")}'
        "</flow_mat></itemfeedback>"
        for i, c in zip(ids, q["choices"]))
    return (head + item_metadata("multiple_choice_question") + presentation +
            "<resprocessing>" + SCORE_DECL + show_general + per_choice + correct + "</resprocessing>" +
            general_block + choice_blocks + "</item>")


def write_qti(questions, title, out_zip):
    quiz_id = re.sub(r"[^A-Za-z0-9_]", "_", out_zip.stem)
    items = "\n".join(qti_item(q) for q in questions)
    assessment = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 '
        'http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">\n'
        f'<assessment ident="{quiz_id}" title="{html.escape(title)}"><qtimetadata>'
        "<qtimetadatafield><fieldlabel>cc_maxattempts</fieldlabel><fieldentry>1</fieldentry></qtimetadatafield>"
        f'</qtimetadata><section ident="root_section">\n{items}\n</section></assessment></questestinterop>\n')
    description = html.escape(f"<p>{len(questions)} questions. Feedback is shown after you submit.</p>")
    meta = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<quiz identifier="{quiz_id}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 '
        'https://canvas.instructure.com/xsd/cccv1p0.xsd">'
        f"<title>{html.escape(title)}</title><description>{description}</description>"
        "<shuffle_answers>true</shuffle_answers><scoring_policy>keep_highest</scoring_policy>"
        f"<quiz_type>practice_quiz</quiz_type><points_possible>{float(len(questions))}</points_possible>"
        "<allowed_attempts>1</allowed_attempts><show_correct_answers>true</show_correct_answers>"
        "<available>false</available></quiz>\n")
    manifest = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<manifest identifier="{quiz_id}_manifest" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1">'
        "<metadata><schema>IMS Content</schema><schemaversion>1.1.3</schemaversion></metadata>"
        "<organizations/><resources>"
        f'<resource identifier="{quiz_id}" type="imsqti_xmlv1p2"><file href="{quiz_id}/{quiz_id}.xml"/>'
        f'<dependency identifierref="{quiz_id}_meta"/></resource>'
        f'<resource identifier="{quiz_id}_meta" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
        f'href="{quiz_id}/assessment_meta.xml"><file href="{quiz_id}/assessment_meta.xml"/></resource>'
        "</resources></manifest>\n")
    # The XML must be well formed, or Canvas rejects the whole package.
    for name, doc in (("manifest", manifest), ("assessment", assessment), ("meta", meta)):
        try:
            ET.fromstring(doc.encode("utf-8"))
        except ET.ParseError as err:
            raise SystemExit(f"Internal error: {name} XML is not well formed: {err}")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("imsmanifest.xml", manifest)
        z.writestr(f"{quiz_id}/{quiz_id}.xml", assessment)
        z.writestr(f"{quiz_id}/assessment_meta.xml", meta)


# ---------------------------------------------------------------- answer key

def write_key(questions, title, out_md):
    lines = [f"# {title}: answer key (PRIVATE: do not publish)", ""]
    for n, q in enumerate(questions, 1):
        lines += [f"## {n}. {q['title']}  [{q['id']}; {q.get('topic', '')}; {q.get('difficulty', '')}]", "",
                  q["stem"], ""]
        if q["type"] == "numeric":
            lines += [f"**Answer:** {q['answer']} (margin {q['margin']})", ""]
        else:
            for c in q["choices"]:
                mark = "**correct**" if c["correct"] else "wrong"
                lines += [f"- {c['letter']}) {c['text']}: {mark}. {c['why']}"]
            lines += [""]
        if q.get("explanation"):
            lines += [f"*Feedback:* {q['explanation']}", ""]
    out_md.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("bank", type=Path, help="the question bank (.md)")
    ap.add_argument("--title", help="quiz title in Canvas (default: from the bank's first heading)")
    args = ap.parse_args()

    text = args.bank.read_text(encoding="utf-8")
    first = re.search(r"(?m)^# (.+)", text)
    title = args.title or (first.group(1).replace("Question bank:", "").strip().capitalize()
                           if first else args.bank.stem)
    questions = parse_bank(text)
    problems = check_bank(questions)
    if problems:
        print(f"{len(problems)} problem(s) in {args.bank.name}; nothing written:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    out_zip = args.bank.with_name(args.bank.stem + "-qti.zip")
    out_key = args.bank.with_name(args.bank.stem + "-key.md")
    write_qti(questions, title, out_zip)
    write_key(questions, title, out_key)

    n_mc = sum(q["type"] == "mc" for q in questions)
    print(f"Read {len(questions)} questions ({n_mc} multiple choice, {len(questions) - n_mc} numeric).")
    print("Correct answer position:", ", ".join(
        next(c["letter"] for c in q["choices"] if c["correct"]) for q in questions if q["type"] == "mc"))
    print("wrote", out_zip.name)
    print("wrote", out_key.name, "(private)")


if __name__ == "__main__":
    main()
