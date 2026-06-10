# Manager Brief v2 — event-parameterized, portable agent skill

Generate a personalized "send this to your manager" recap brief for **any scope** — a named event (offsite, training, hackathon, conference), a **time window** ("last week", "this sprint"), or a **specific meeting/project**. v2 detects what you mean and pulls from the right places: your **emails, Teams chats, meetings**, and any **event SharePoint site**.

It pulls the running user's own context, confirms forward commitments, and outputs:
1. A styled **HTML file** in the working directory, and
2. A **draft** email/message to the manager — never sent automatically.

CLI-agnostic: **Scout / Clawpilot**, **GitHub Copilot CLI**, **Agency**, or any MCP-capable agent.

---

## What's new in v2
- **Scope as a parameter** — works for three kinds of input:
  - *Event*: "the CXG Americas Offsite" → discovers its SharePoint site/lists (roster, connections, deliverables) dynamically.
  - *Timeframe*: "last week", "the last 2 weeks", a date range → summarizes your emails, Teams chats, and meetings in that window.
  - *Meeting/project*: "the Q3 Planning sync" → filters activity to that subject/attendees.
- **Email + chat + meeting summarization** — for timeframe/meeting scopes it reads your calendar, mail (incl. Sent), and Teams chats and synthesizes what you drove, decisions, and collaborators.
- **Dynamic SharePoint discovery** (event scope) — `GET /sites?search=…`, enumerate lists, match roster/connections/deliverables by name heuristics; auto-map list columns by content.
- **Event presets** — known events (e.g. CXG Americas Offsite) as an optional shortcut, still verified via Graph.

---

## Install

The skill is the `manager-brief/` folder (`SKILL.md` + `template.html` + this `README.md`).

### Microsoft Scout / Clawpilot
```
%USERPROFILE%\.copilot\m-skills\manager-brief\     (Windows)
~/.copilot/m-skills/manager-brief/                  (macOS/Linux)
```
Restart the app, sign in to M365, then run `/manager-brief`. Uses built-in `m365_*` tools + the signed-in browser.

### GitHub Copilot CLI (ghcp)
```
%USERPROFILE%\.copilot\skills\manager-brief\        (Windows)
~/.copilot/skills/manager-brief/                     (macOS/Linux)
```
Start a new `copilot` session, run `/manager-brief`. For auto-lookup, add a Microsoft Graph MCP to `~/.copilot/mcp-config.json`; otherwise it asks you for the inputs.

### Agency (or any MCP agent)
Place `manager-brief/` where Agency loads skills (or paste `SKILL.md` as a skill prompt). **Enable the Microsoft Graph / SharePoint MCP** — the skill auto-detects it and discovers the event's site/lists via Graph. Run the skill and name your event.

> If the skill jumps straight to "which team were you on?", the host has no Graph/SharePoint access wired up — enable the MCP or sign into the browser.

---

## Usage
1. Run `/manager-brief`.
2. Tell it what to cover — and confirm consent (once):
   - An **event**: *"the CXG Americas Offsite – June 2026"* (optionally paste the site link)
   - A **time window**: *"last week"*, *"the last 2 weeks"*, *"this sprint"*
   - A **meeting/project**: *"the Q3 Planning sync"*, *"the Contoso migration"*
3. It gathers the right sources — SharePoint site (events) and/or your emails, Teams chats, and meetings (timeframe/meeting).
4. Give it your commitments, manager asks, and a 1:1 topic.
5. Review the generated HTML + the manager draft (in Drafts). You send it.

## Guardrails
- Per-user only — never includes other people's private rows.
- Never auto-sends; always leaves a draft.
- One consent up front; one final confirmation before drafting.

## Files
- `SKILL.md` — v2 skill instructions (event-parameterized, dynamic discovery).
- `template.html` — neutral-branded HTML output (override `--accent` for org colors).
