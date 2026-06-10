"""
event_brief.py — main pipeline for the `event` subcommand.

WorkIQ-grounded: every fact in the brief is sourced from a WorkIQ query.
Local files (transcript, agenda, notes) are optional supplements.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

LIB = Path(__file__).parent
sys.path.insert(0, str(LIB))

from workiq.client import WorkIQClient, WorkIQUnavailable
from workiq import queries as Q
from extractors import attendees as ex_attendees
from extractors import themes as ex_themes
from extractors import actions as ex_actions
from extractors import followups as ex_followups
from renderers.md import render_markdown
from parsers.vtt import parse_vtt
from parsers.local_text import read_text_safe

EVENT_TYPES = ["offsite", "bootcamp", "cab", "training", "workshop", "customer-meeting"]


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="gh manager-brief event",
        description="Generate a WorkIQ-grounded manager brief for an event you attended.",
    )
    p.add_argument("--type", required=True, choices=EVENT_TYPES)
    p.add_argument("--name", required=True, help="Event name (used as anchor for WorkIQ queries).")
    p.add_argument("--from", dest="date_from", required=True, help="Start date YYYY-MM-DD.")
    p.add_argument("--to", dest="date_to", required=True, help="End date YYYY-MM-DD.")
    p.add_argument("--attendee-hint", action="append", default=[], help="Repeatable. Helps WorkIQ resolve who was there.")
    p.add_argument("--keyword", action="append", default=[], help="Repeatable. Topic anchors for WorkIQ.")
    p.add_argument("--transcript", action="append", default=[], help="Optional local .vtt/.txt transcript.")
    p.add_argument("--agenda", help="Optional local agenda file (text/markdown).")
    p.add_argument("--my-notes", dest="my_notes", help="Optional local notes file.")
    p.add_argument("--manager-email", default="")
    p.add_argument("--out", default="./out", help="Output directory.")
    p.add_argument("--format", default="md", choices=["md"], help="Phase 1: Markdown only.")
    p.add_argument("--no-workiq", action="store_true", help="Skip WorkIQ; use local files only.")
    p.add_argument("--workiq-cmd", default=r"C:\Users\ajaysngh\.copilot\bin\workiq.cmd",
                   help="Path to workiq.cmd (Windows) or workiq binary.")
    p.add_argument("--fixture-dir", help="(eval) load WorkIQ responses from a fixture directory instead of calling WorkIQ.")
    return p.parse_args(argv)


def build_brief(args):
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ----- Gather optional local supplements -----
    transcript_text = ""
    for t in args.transcript:
        path = Path(t)
        if not path.exists():
            print(f"warning: transcript not found: {t}", file=sys.stderr)
            continue
        if path.suffix.lower() == ".vtt":
            transcript_text += "\n" + parse_vtt(path)
        else:
            transcript_text += "\n" + read_text_safe(path)

    agenda_text = read_text_safe(Path(args.agenda)) if args.agenda else ""
    notes_text = read_text_safe(Path(args.my_notes)) if args.my_notes else ""

    # ----- WorkIQ client -----
    wq = None
    if not args.no_workiq:
        try:
            wq = WorkIQClient(workiq_cmd=args.workiq_cmd, fixture_dir=args.fixture_dir)
        except WorkIQUnavailable as e:
            print(f"warning: WorkIQ unavailable ({e}). Continuing in --no-workiq mode.", file=sys.stderr)
            wq = None

    # ----- Extractors -----
    ctx = dict(
        event_name=args.name,
        event_type=args.type,
        date_from=args.date_from,
        date_to=args.date_to,
        keywords=args.keyword,
        attendee_hints=args.attendee_hint,
    )
    attendees = ex_attendees.extract(wq, ctx, transcript_text)
    themes = ex_themes.extract(wq, ctx, transcript_text)
    actions = ex_actions.extract(wq, ctx, transcript_text)
    followups = ex_followups.extract(wq, ctx) if wq else []

    # ----- Render -----
    md = render_markdown(
        ctx=ctx,
        manager_email=args.manager_email,
        attendees=attendees,
        themes=themes,
        actions=actions,
        followups=followups,
        agenda=agenda_text,
        notes=notes_text,
        sources=(wq.sources if wq else []),
    )

    # Filename: <type>-<slug>-<date_from>.md
    slug = "".join(c if c.isalnum() else "-" for c in args.name.lower()).strip("-")
    out_path = out_dir / f"{args.type}-{slug}-{args.date_from}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"wrote {out_path}")
    return out_path


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return build_brief(args)


if __name__ == "__main__":
    main()
