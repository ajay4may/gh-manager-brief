"""Scan WorkIQ for post-event emails/chats that confirm or amend action items."""
from typing import List
from workiq.client import WorkIQClient
from workiq import queries as Q


def extract(wq: WorkIQClient, ctx: dict) -> List[dict]:
    try:
        text = wq.ask(Q.followups_q(ctx["event_name"], ctx["date_to"]),
                      fixture_key="followups")
        cite = wq.cite()
    except Exception as e:
        # Missing fixture in eval mode is fine — followups are optional.
        return []
    out = []
    for raw in text.splitlines():
        line = raw.strip(" \t-*•").strip()
        if not line:
            continue
        out.append({"summary": line, "cite": cite})
    return out[:15]
