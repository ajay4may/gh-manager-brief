"""Extract attendee list — WorkIQ first, transcript speakers as fallback."""
import re
from typing import List, Optional
from workiq.client import WorkIQClient
from workiq import queries as Q


def extract(wq: Optional[WorkIQClient], ctx: dict, transcript_text: str) -> List[dict]:
    results: List[dict] = []
    citation = None
    if wq is not None:
        try:
            text = wq.ask(Q.attendees_q(ctx["event_name"], ctx["date_from"],
                                        ctx["date_to"], ctx["attendee_hints"]),
                          fixture_key="attendees")
            citation = wq.cite()
            results = _parse_attendees(text, citation)
        except Exception as e:
            print(f"  WorkIQ attendees failed: {e}", file=__import__('sys').stderr)

    if not results and transcript_text:
        speakers = _speakers_from_vtt(transcript_text)
        results = [{"name": s, "org": "", "role": "", "cite": "[local transcript]"} for s in speakers]

    if not results and ctx["attendee_hints"]:
        results = [{"name": h.strip(), "org": "", "role": "", "cite": "[user hint]"}
                   for h in ctx["attendee_hints"]]
    return results


def _parse_attendees(text: str, cite: str) -> List[dict]:
    rows = []
    for raw in text.splitlines():
        line = raw.strip(" \t-*•").strip()
        if not line:
            continue
        # try to split "Name — Org, Role" or "Name (Org, Role)" or "Name - Org - Role"
        m = re.match(r"^([^—\-(\[]+?)\s*[—\-]\s*(.+)$", line)
        if m:
            name = m.group(1).strip()
            rest = m.group(2).strip()
            parts = [p.strip() for p in re.split(r",|/|·", rest, maxsplit=1)]
            org = parts[0] if parts else ""
            role = parts[1] if len(parts) > 1 else ""
            rows.append({"name": name, "org": org, "role": role, "cite": cite})
        else:
            rows.append({"name": line, "org": "", "role": "", "cite": cite})
    # dedupe by name (case-insensitive)
    seen = set(); deduped = []
    for r in rows:
        key = r["name"].lower()
        if key in seen: continue
        seen.add(key); deduped.append(r)
    return deduped


def _speakers_from_vtt(text: str) -> List[str]:
    speakers = []
    for line in text.splitlines():
        m = re.match(r"^\s*<v\s+([^>]+)>", line) or re.match(r"^([A-Z][\w\s\.\-']{1,40}):\s", line)
        if m:
            name = m.group(1).strip()
            if name not in speakers:
                speakers.append(name)
    return speakers
