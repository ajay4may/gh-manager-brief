"""Extract action items / commitments."""
import re
from typing import List, Optional
from workiq.client import WorkIQClient
from workiq import queries as Q


ACTION_RE = re.compile(
    r"(?P<lead>[-*•]\s+|\d+[.)]\s+)?"
    r"(?P<owner>@?[A-Z][\w\.\-' ]{1,40})?\s*"
    r"(?:to|will|shall|—|->|:)\s+"
    r"(?P<action>[^.\n]{8,200})"
    r"(?:\s+by\s+(?P<due>[^.\n]{3,40}))?",
    re.IGNORECASE,
)


def extract(wq: Optional[WorkIQClient], ctx: dict, transcript_text: str) -> List[dict]:
    items: List[dict] = []
    if wq is not None:
        try:
            text = wq.ask(Q.actions_q(ctx["event_name"], ctx["date_from"], ctx["date_to"]),
                          fixture_key="actions")
            cite = wq.cite()
            items = _parse_actions(text, cite)
        except Exception as e:
            print(f"  WorkIQ actions failed: {e}", file=__import__('sys').stderr)
    if not items and transcript_text:
        items = _regex_actions(transcript_text)
    return items


def _parse_actions(text: str, cite: str) -> List[dict]:
    """Parse WorkIQ's bulleted answer. Handles common shapes."""
    out = []
    for raw in text.splitlines():
        line = raw.strip(" \t-*•").strip()
        if not line:
            continue
        owner, action, due = _split_action_line(line)
        if action:
            out.append({"owner": owner, "action": action, "due": due, "cite": cite})
    return out


def _split_action_line(line: str):
    # Patterns:
    #   "Sarah — pilot the triage agent with two teams (by July 15)"
    #   "Owner: Sarah  Action: pilot triage agent  Due: July 15"
    #   "@sarah to pilot triage agent by July 15"
    #   "Action item: review the bootcamp transcript - Owner: Raj - Due: 2026-06-20"
    line = line.rstrip(".;")
    # Field-style "Owner: X | Action: Y | Due: Z"
    fields = {}
    for token in re.split(r"\s+[|·•·-]\s+|\s{2,}", line):
        m = re.match(r"^(owner|action|task|due|by|deadline)\s*[:\-]\s*(.+)$", token, re.IGNORECASE)
        if m:
            k = m.group(1).lower()
            if k in ("by", "deadline"): k = "due"
            if k == "task": k = "action"
            fields[k] = m.group(2).strip()
    if "action" in fields:
        return fields.get("owner", ""), fields["action"], fields.get("due", "")

    # "Owner — action (by Date)"
    m = re.match(r"^([@\w\.\-' ]+?)\s+[—\-]\s+(.+?)(?:\s+by\s+(.+))?$", line)
    if m:
        owner = m.group(1).strip().lstrip("@")
        action = m.group(2).strip()
        due = (m.group(3) or "").strip()
        return owner, action, due

    # "@name to do thing by date"
    m = re.match(r"^@?([\w\.\-]+)\s+(?:to|will)\s+(.+?)(?:\s+by\s+(.+))?$", line, re.IGNORECASE)
    if m:
        return m.group(1).strip(), m.group(2).strip(), (m.group(3) or "").strip()

    # Bare action
    return "", line, ""


def _regex_actions(text: str) -> List[dict]:
    items = []
    for m in ACTION_RE.finditer(text):
        owner = (m.group("owner") or "").strip().lstrip("@")
        action = (m.group("action") or "").strip()
        due = (m.group("due") or "").strip()
        if action and len(action.split()) >= 3:
            items.append({"owner": owner, "action": action, "due": due, "cite": "[local transcript]"})
    # dedupe by action
    seen = set(); deduped = []
    for it in items:
        k = it["action"].lower()
        if k in seen: continue
        seen.add(k); deduped.append(it)
    return deduped[:20]
