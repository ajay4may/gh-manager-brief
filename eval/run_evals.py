"""
run_evals.py — offline eval suite for the event brief agent.

Runs the pipeline against fixture WorkIQ responses and validates the brief
against shape/content checks. Exit code 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
OUT = HERE / "_out"

sys.path.insert(0, str(ROOT / "lib"))
from event_brief import main as run_event  # noqa: E402


CASES = [
    {
        "id": "offsite-cxg",
        "fixture": "cxg-offsite",
        "args": [
            "--type", "offsite",
            "--name", "CXG Americas Offsite",
            "--from", "2026-06-09", "--to", "2026-06-11",
            "--keyword", "AI agents", "--keyword", "scalability",
        ],
        "expect": {
            "min_attendees": 3,
            "min_themes": 3,
            "min_actions": 2,
            "must_have_sections": ["TL;DR", "Attendees", "Key learnings",
                                   "Action items", "My plan to act",
                                   "How my manager can help", "Sources"],
            "must_have_substrings": ["WorkIQ"],
            "must_have_followups": True,
        },
    },
    {
        "id": "bootcamp-partner",
        "fixture": "partner-bootcamp",
        "args": [
            "--type", "bootcamp",
            "--name", "Partner AI Bootcamp",
            "--from", "2026-05-04", "--to", "2026-05-05",
        ],
        "expect": {
            "min_attendees": 2,
            "min_themes": 2,
            "min_actions": 1,
            "must_have_sections": ["Attendees", "Action items", "Sources"],
            "must_have_followups": False,
        },
    },
    {
        "id": "cab-q2",
        "fixture": "cab-q2",
        "args": [
            "--type", "cab",
            "--name", "Q2 Customer Advisory Board",
            "--from", "2026-04-22", "--to", "2026-04-22",
        ],
        "expect": {
            "min_attendees": 2,
            "min_themes": 2,
            "min_actions": 1,
            "must_have_sections": ["Attendees", "Key learnings", "Action items"],
            "must_have_followups": False,
        },
    },
]


def run_case(case):
    fixture_dir = FIXTURES / case["fixture"]
    out_dir = OUT / case["id"]
    if out_dir.exists():
        for p in out_dir.glob("*"):
            try: p.unlink()
            except Exception: pass
    out_dir.mkdir(parents=True, exist_ok=True)

    argv = case["args"] + [
        "--out", str(out_dir),
        "--fixture-dir", str(fixture_dir),
    ]
    run_event(argv)

    # Find the generated file
    files = list(out_dir.glob("*.md"))
    if not files:
        return False, f"no brief written in {out_dir}"
    text = files[0].read_text(encoding="utf-8")

    failures = []
    exp = case["expect"]

    for section in exp.get("must_have_sections", []):
        if section.lower() not in text.lower():
            failures.append(f"missing section: '{section}'")

    for sub in exp.get("must_have_substrings", []):
        if sub not in text:
            failures.append(f"missing substring: '{sub}'")

    # Count attendees rows (between Attendees header and next ##)
    n_att = _count_table_rows(text, "## 2. Attendees")
    if n_att < exp.get("min_attendees", 0):
        failures.append(f"attendees={n_att} < min {exp['min_attendees']}")

    n_themes = _count_theme_blocks(text)
    if n_themes < exp.get("min_themes", 0):
        failures.append(f"themes={n_themes} < min {exp['min_themes']}")

    n_actions = _count_table_rows(text, "## 4. Action items")
    if n_actions < exp.get("min_actions", 0):
        failures.append(f"actions={n_actions} < min {exp['min_actions']}")

    if exp.get("must_have_followups"):
        if "## 6. Follow-ups" not in text:
            failures.append("missing follow-ups section")

    return (len(failures) == 0), failures or "ok"


def _count_table_rows(md_text, section_header):
    """Count data rows in the table directly under a section header."""
    lines = md_text.splitlines()
    try:
        i = next(idx for idx, ln in enumerate(lines) if ln.strip().startswith(section_header))
    except StopIteration:
        return 0
    # find table data rows: lines starting with '|' but not the header/separator
    count = 0
    header_seen = False
    sep_seen = False
    for ln in lines[i+1:]:
        s = ln.strip()
        if s.startswith("## "):
            break
        if s.startswith("|"):
            if not header_seen:
                header_seen = True; continue
            if not sep_seen and re.match(r"^\|\s*-+", s):
                sep_seen = True; continue
            if header_seen and sep_seen:
                count += 1
    return count


def _count_theme_blocks(md_text):
    """Count themes under '## 3. Key learnings' — either '### Heading' lines or '- bullet' lines."""
    lines = md_text.splitlines()
    try:
        i = next(idx for idx, ln in enumerate(lines) if ln.strip().startswith("## 3. Key learnings"))
    except StopIteration:
        return 0
    count = 0
    for ln in lines[i+1:]:
        s = ln.strip()
        if s.startswith("## "):
            break
        if s.startswith("### "):
            count += 1
        elif s.startswith("- "):
            count += 1
    return count


def main():
    print(f"running {len(CASES)} eval case(s)\n")
    fails = 0
    for c in CASES:
        ok, details = run_case(c)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {c['id']:24s}  {details if not ok else ''}")
        if not ok:
            fails += 1
    print()
    if fails:
        print(f"{fails} of {len(CASES)} FAILED")
        sys.exit(1)
    print(f"all {len(CASES)} cases passed")


if __name__ == "__main__":
    main()
