"""Extract key learnings / themes."""
import re
from typing import List, Optional
from workiq.client import WorkIQClient
from workiq import queries as Q


def extract(wq: Optional[WorkIQClient], ctx: dict, transcript_text: str) -> List[dict]:
    if wq is not None:
        try:
            text = wq.ask(Q.themes_q(ctx["event_name"], ctx["date_from"],
                                     ctx["date_to"], ctx["keywords"]),
                          fixture_key="themes")
            cite = wq.cite()
            themes = _parse_themes(text, cite)
            if themes:
                return themes
        except Exception as e:
            print(f"  WorkIQ themes failed: {e}", file=__import__('sys').stderr)
    return _heuristic_themes(transcript_text)


def _parse_themes(text: str, cite: str) -> List[dict]:
    """Parse a WorkIQ response into theme dicts.
    Accepts bullets, numbered lists, or 'Heading: insight' blocks."""
    themes = []
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        # Match a heading-style line: "**Title**" or "## Title" or "1. Title:"
        m = re.match(r"^\s*(?:[-*•]\s+|\d+[.)]\s+)?\**(.+?)\**\s*[:—]\s*(.+)$", line)
        if m:
            heading = m.group(1).strip().strip("*#")
            insight = m.group(2).strip()
            if heading and insight:
                themes.append({"heading": heading, "insight": insight, "cite": cite})
                continue
        # plain bullet
        m2 = re.match(r"^\s*[-*•]\s+(.+)$", line)
        if m2:
            themes.append({"heading": "", "insight": m2.group(1).strip(), "cite": cite})
            continue
        # numbered
        m3 = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if m3:
            themes.append({"heading": "", "insight": m3.group(1).strip(), "cite": cite})
            continue
        # plain line — treat as continuation of last or new insight
        if themes and not themes[-1]["insight"]:
            themes[-1]["insight"] = line.strip()
        else:
            themes.append({"heading": "", "insight": line.strip(), "cite": cite})
    return themes[:8]


def _heuristic_themes(text: str) -> List[dict]:
    """Very simple offline fallback: pick first/middle/last meaningful sentences."""
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    sents = [s.strip() for s in sents if len(s.strip()) > 40]
    if not sents:
        return []
    picks = []
    for idx in [0, len(sents)//4, len(sents)//2, 3*len(sents)//4, len(sents)-1]:
        if 0 <= idx < len(sents) and sents[idx] not in [p["insight"] for p in picks]:
            picks.append({"heading": "", "insight": sents[idx], "cite": "[local transcript]"})
    return picks[:5]
