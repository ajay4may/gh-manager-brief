"""Render the manager brief as Markdown, with provenance footnotes."""
from datetime import date
from pathlib import Path
from typing import List


HERE = Path(__file__).parent
TEMPLATES = HERE.parent / "templates"


# event-type → intro line shown right under the title
TYPE_INTRO = {
    "offsite":          "team offsite",
    "bootcamp":         "partner / customer bootcamp",
    "cab":              "Customer Advisory Board session",
    "training":         "training session",
    "workshop":         "hands-on workshop",
    "customer-meeting": "customer meeting",
}


def render_markdown(*, ctx, manager_email, attendees, themes, actions, followups,
                    agenda, notes, sources):
    title = ctx["event_name"]
    et_intro = TYPE_INTRO.get(ctx["event_type"], ctx["event_type"])
    date_range = ctx["date_from"] if ctx["date_from"] == ctx["date_to"] \
                 else f"{ctx['date_from']} – {ctx['date_to']}"

    md = []
    md.append(f"# Event Brief — {title}")
    md.append(f"_{et_intro} · {date_range}_")
    md.append("")
    md.append(f"**To:** {manager_email or '<your manager>'}  |  **Prepared:** {date.today().isoformat()}  |  **Grounded in:** WorkIQ")
    md.append("")
    md.append("> A manager-ready recap: who was there, what came out of it, what I'm doing about it.")
    md.append("")

    # 1. TL;DR
    md.append("## 1. TL;DR")
    tldr = _tldr(themes, actions)
    if tldr:
        md.extend(f"- {t}" for t in tldr)
    else:
        md.append("- _(not enough signal yet — run with WorkIQ enabled or attach a transcript)_")
    md.append("")

    # 2. Attendees
    md.append(f"## 2. Attendees ({len(attendees)})")
    if attendees:
        md.append("| Name | Org | Role | Source |")
        md.append("| --- | --- | --- | --- |")
        for a in attendees[:50]:
            md.append(f"| {a['name']} | {a.get('org','')} | {a.get('role','')} | {a.get('cite','')} |")
    else:
        md.append("_None resolved._")
    md.append("")

    # 3. Key learnings
    md.append("## 3. Key learnings")
    if themes:
        for t in themes:
            head = t.get("heading") or ""
            ins = t.get("insight") or ""
            cite = t.get("cite", "")
            if head:
                md.append(f"### {head}")
                md.append(f"{ins} {cite}".rstrip())
            else:
                md.append(f"- {ins} {cite}".rstrip())
    else:
        md.append("_None resolved._")
    md.append("")

    # 4. Action items
    md.append("## 4. Action items")
    if actions:
        md.append("| Owner | Action | Due | Source |")
        md.append("| --- | --- | --- | --- |")
        for a in actions:
            md.append(f"| {a.get('owner','') or '_unassigned_'} | {a['action']} | {a.get('due','')} | {a.get('cite','')} |")
    else:
        md.append("_None captured._")
    md.append("")

    # 5. My plan to act
    md.append("## 5. My plan to act")
    md.append("_For each action I own, my concrete next step:_")
    my_actions = [a for a in actions if a.get("owner", "").strip().lower().startswith(("i ", "me", "my", "ajay"))]
    if not my_actions and actions:
        # if owner detection didn't find self, prompt user to fill in
        md.append("- **Action:** _<fill in the one(s) you own>_")
        md.append("  - **Next step (this week):** _…_")
        md.append("  - **By when:** _…_")
        md.append("  - **Who I need:** _…_")
    elif my_actions:
        for a in my_actions:
            md.append(f"- **Action:** {a['action']}")
            md.append(f"  - **Next step (this week):** _…_")
            md.append(f"  - **By when:** {a.get('due') or '_…_'}")
            md.append(f"  - **Who I need:** _…_")
    else:
        md.append("- _No action items resolved._")
    md.append("")

    # 6. Follow-ups (WorkIQ post-event signal)
    if followups:
        md.append("## 6. Follow-ups since the event")
        for f in followups:
            md.append(f"- {f['summary']} {f.get('cite','')}".rstrip())
        md.append("")

    # 7. How my manager can help
    md.append("## 7. How my manager can help")
    md.append("- _<the specific unblock you want from your manager>_")
    md.append("")

    # Optional supplements (agenda, notes)
    if agenda.strip():
        md.append("---")
        md.append("<details><summary>Agenda (attached)</summary>")
        md.append("")
        md.append(agenda.strip())
        md.append("")
        md.append("</details>")
        md.append("")

    if notes.strip():
        md.append("---")
        md.append("<details><summary>My notes (attached)</summary>")
        md.append("")
        md.append(notes.strip())
        md.append("")
        md.append("</details>")
        md.append("")

    # Sources / footnotes
    if sources:
        md.append("---")
        md.append("### Sources")
        for s in sources:
            md.append(f"[^wq{s.sid}]: {s.label}")
        md.append("")

    md.append("---")
    md.append("_Generated by `gh manager-brief event` — review and edit before sending._")
    return "\n".join(md) + "\n"


def _tldr(themes, actions):
    bullets = []
    if themes:
        first = themes[0]
        head = first.get("heading") or first.get("insight", "")
        bullets.append(f"Top theme: {head}")
    if len(themes) > 1:
        sec = themes[1]
        head = sec.get("heading") or sec.get("insight", "")
        bullets.append(f"Also: {head}")
    if actions:
        bullets.append(f"{len(actions)} action item(s) captured — see section 4.")
    return bullets
