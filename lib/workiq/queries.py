"""Question templates for each extraction. Keeps prompts in one place."""
from typing import List


def attendees_q(event_name: str, date_from: str, date_to: str, hints: List[str]) -> str:
    base = (
        f"List the people who attended meetings titled or about '{event_name}' "
        f"between {date_from} and {date_to}. "
        f"For each person give their name, organization, and role if known. "
        f"Return a clean bulleted list, one person per line."
    )
    if hints:
        base += f" Known attendees include: {', '.join(hints)}."
    return base


def themes_q(event_name: str, date_from: str, date_to: str, keywords: List[str]) -> str:
    base = (
        f"Summarize the 5 to 8 most important topics discussed in meetings about "
        f"'{event_name}' between {date_from} and {date_to}. "
        f"For each topic, give a short heading and a one-sentence insight, "
        f"and note who raised it if clear."
    )
    if keywords:
        base += f" Pay special attention to: {', '.join(keywords)}."
    return base


def actions_q(event_name: str, date_from: str, date_to: str) -> str:
    return (
        f"List the action items, decisions, and commitments from meetings about "
        f"'{event_name}' between {date_from} and {date_to}. "
        f"For each item, give: owner (name), action (one sentence), due date if mentioned. "
        f"Return as a bulleted list."
    )


def followups_q(event_name: str, date_to: str) -> str:
    return (
        f"After {date_to}, find emails and Teams messages that reference '{event_name}' "
        f"and contain new commitments, follow-up actions, or updates to action items. "
        f"For each, summarize in one line: who, what, and when it's due."
    )
