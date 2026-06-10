---
name: manager-brief
description: "v2 — Generate a personalized, manager-ready recap brief for ANY scope: a named event (offsite/training/hackathon), a time window ('last week', a sprint), or a specific meeting/project. It checks your emails, Teams chats, meetings, and any event SharePoint site, pulls the running user's own context, confirms forward commitments, and outputs a styled HTML file + a manager email/message draft. Never sends automatically. CLI-agnostic: Scout/Clawpilot, GitHub Copilot CLI, Agency, or any MCP-capable agent."
version: 2
---

# Manager Brief v2 (scope-parameterized, portable)

You generate a personalized "send this to your manager" recap brief for the CURRENT user, for a SCOPE they name. The scope can be:
- **An event** — offsite, training, hackathon, conference (has a SharePoint/Teams site).
- **A time window** — "last week", "this sprint", "the last 2 weeks", a date range.
- **A specific meeting / project** — one recurring meeting, a project, a workstream.

Nothing is hardcoded — you detect the scope type from the user's phrasing and gather from the right sources. Per-user only; never fabricate; never auto-send.

## Step 0 — Get the scope + consent in ONE message
Ask the user (a) what the brief should cover and (b) consent to gather data — in a single prompt. Example:
> "What should this brief cover — a specific event, a time period like 'last week', or a particular meeting/project? Once you confirm, I'll review your relevant emails, Teams chats, meetings (and any event site), then prepare a DRAFT to your manager (I won't send it). OK to proceed?"

Classify the answer into a `SCOPE_TYPE`:
- `event` → has/likely-has a SharePoint site (do Step 2-EVENT).
- `timeframe` → resolve to a concrete date range, e.g. "last week" = previous Mon–Sun (do Step 2-ACTIVITY).
- `meeting` / `project` → a named meeting series or topic (do Step 2-ACTIVITY, filtered to that subject/attendees).

Capture `SCOPE_LABEL` (what to print in the brief, e.g. "last week (Jun 2–6)" or "the Q3 Planning offsite") and any dates. After one confirmation, gather WITHOUT re-asking per source. Pause again only to confirm the brief before drafting.

## Step 1 — Tool selection (read first)
Scan your tools / MCP servers for anything involving **Microsoft Graph, SharePoint, M365, Outlook/mail, Teams/chat, calendar/meetings, or "sites"/"lists"**. Use those as PRIMARY sources. Don't do anonymous `web_fetch`/`curl` against SharePoint (login wall). "Ask the user" is last resort.

## Step 2-ACTIVITY — Summarize from emails, chats & meetings (for `timeframe` / `meeting` / `project`)
Resolve the date range first (for "last week" compute the actual dates from today). Then gather the user's own M365 activity in that window:
- **Meetings** — calendar events in range: `m365_list_events` / `m365_list_meetings`, or Graph `GET /me/calendarView?startDateTime=…&endDateTime=…`. For a named meeting, filter by subject/organizer. Capture key meetings, decisions, and (if a transcript/recording tool exists) takeaways.
- **Emails** — `m365_list_emails` / `m365_search_emails` or Graph `GET /me/messages?$filter=receivedDateTime ge … and le …` (and `sentItems` for what the user drove). Identify threads the user led, decisions, commitments made.
- **Teams chats** — `m365_list_chats` / `m365_list_chat_messages` or Graph chat endpoints, filtered to the range. Pull notable discussions/asks.
- Synthesize into the brief sections: **what I worked on / drove**, **decisions & outcomes**, **what I'm committing to next**, **how my manager can help**, **people I worked with** (frequent collaborators in the window).
- Keep it grounded: summarize only what's actually in the user's mail/chat/calendar. Attribute nothing you can't see. Respect privacy — the user's own items only.

## Step 2-EVENT — Discover the event's SharePoint sources (for `event`)
Goal: find the event's SharePoint site, then its lists/libraries for **team/pod roster**, **connections**, **deliverables**. Discover, don't hardcode.

**A. Find the site**
- If the user gave a site URL → resolve: `GET /sites/{hostname}:/{path}` → `{siteId}`.
- Else search: `GET /sites?search={SCOPE_LABEL}` → pick best match; confirm if ambiguous.

**B. Enumerate lists + libraries**
- `GET /sites/{siteId}/lists?$select=id,name,displayName,list` and `GET /sites/{siteId}/drives`.
- Match by display name (case-insensitive): roster→`pod|team|roster|group|squad|table|cohort`; connections→`connection|connect|network|met|quest`; registration→`registration|signup|attendee`; deliverables→a doc library with per-team folders.
- If multiple matches, list them and let the user pick.

**C. Read matched lists** with `?$expand=fields&$top=999` (page via `@odata.nextLink`):
- **Team/pod**: row whose member field contains the user → team, project/theme, teammates.
- **Connections (both directions)**: inspect first row's `fields` to map email/status/timestamp columns by content (don't assume `field_2`/`field_3`). Split into **people I connected with** (initiator==me) vs **people who wanted to connect with me** (target==me).
- **Deliverables**: `GET /sites/{siteId}/drive/root:/{libraryPath}/{TeamName}:/children` → infer mini-project name + the user's contribution.
- Resolve email → name/role: `GET /users/{email}?$select=displayName,jobTitle,department` or a people MCP.
- You may ALSO run Step 2-ACTIVITY over the event dates to enrich "what I learned/did".

## Step 2-COMMON — Identity + manager + learnings
- **Identity/manager**: `m365_get_my_profile`/`m365_get_my_manager`, else Graph `GET /me`, `GET /me/manager`, else ask.
- **"What I learned"**: optional search/recording tool (e.g. WorkIQ) over the scope; if nothing, ask or propose grounded takeaways.

> Fallback ladder everywhere: Graph/M365 MCP → signed-in browser → ask the user. Never invent.

## Step 3 — Confirm forward-looking parts (only the user can author)
Ask for 2–3 time-bound commitments, 2–3 concrete manager asks, one 1:1 talking point. Offer drafts to edit.

## Step 4 — Generate output (always both)
1. Brief in first person, confident + specific, ~250–350 words.
2. Save a styled **HTML file**: `manager-brief-<firstname>-<scope-slug>-<yyyymmdd>.html` using `template.html` (set `{{EVENT}}`=SCOPE_LABEL, `{{EVENT_META}}`=dates/context; omit empty sections). If no file-write tool, print HTML in a code block.
3. Create a **manager draft** (don't send): `m365_create_draft` / Graph `POST /me/messages` / chat-draft tool. Subject: `My {{EVENT}} recap — and one ask for your help`. Confirm recipient + content first.
4. Report the file path + that the draft awaits review.

## Brief structure (use what fits the scope; omit empty sections)
Subject: `My {{EVENT}} recap — and one ask for your help`
Intro: "Hi <ManagerFirstName> — here's a quick recap of {{EVENT}} ({{EVENT_META}}) and where I'd value your support."
- WHAT I WORKED ON / LEARNED — bullets (event takeaways, or the week's focus areas)
- KEY OUTCOMES / WHAT I BUILT OR DROVE — decisions, deliverables, project/theme + my contribution + tools
- WHAT I'M COMMITTING TO — bullets
- HOW YOU CAN HELP — bullets
- PEOPLE I CONNECTED WITH / WORKED WITH — (optional) names/roles I engaged
- PEOPLE WHO WANTED TO CONNECT WITH ME — (optional, event scope) who reached out
- FOR OUR NEXT 1:1 — one line
- Signature: name + role

## Guardrails
- Per-user only; never include other people's private data.
- Never auto-send — always leave a draft.
- One consent up front; one final confirmation before drafting.

---
### Reference: known event presets (optional shortcut for `event` scope)
If the user names one of these, you already know its site (still verify via Graph):
- **CXG Americas Offsite — June 2026**: site `https://microsoft.sharepoint-df.com/teams/CXGAmericasOffsite-June2026`; lists: `PODs list` (roster), `OffsiteConnectionLists_Activity` (connections), `Checkin`, `Hack Registrations`; deliverables library: `Shared Documents/General/Hackathon PODs/<Team>`.

