---
name: manager-brief
description: Generate a personalized, manager-ready recap brief after an event, offsite, training, or hackathon. Pulls the running user's own context where tools allow (identity, manager, project/team), confirms forward commitments with the user, and outputs a styled HTML file plus a ready-to-send email/message draft. Never sends automatically. Designed to be CLI-agnostic — works in GitHub Copilot CLI, Agency, Clawpilot, or any MCP-capable agent.
---

# Manager Brief (portable)

You generate a personalized "send this to your manager" recap brief for the CURRENT user. This skill is **host-agnostic**: it runs in GitHub Copilot CLI, Agency, Clawpilot, or any agent runtime. Adapt to whatever tools the host provides — do NOT assume a specific vendor tool exists.

## Output (always both)
1. A styled **HTML file** saved to the working directory: `manager-brief-<firstname>-<yyyymmdd>.html` (use `template.html` from this skill folder; substitute the `{{TOKENS}}`).
2. A **draft message** to the user's manager (email or chat), left for the user to review and send. **NEVER send automatically.**

## The brief: 6 sections (~250–350 words, one screen)
1. **What I learned** — 3–4 specific takeaways (not generic).
2. **What I built / did** — project/team + the user's concrete contribution + tools used.
3. **What I'm committing to** — 2–3 time-bound commitments.
4. **How my manager can help** — 2–3 concrete, low-friction asks.
5. **One thing for our next 1:1** — a single seeded talking point.
6. **Signature** — name + role.

---

## Step 0 — Ask for consent ONCE, up front
Before gathering anything, tell the user in a single message what you'll access and do, and get one confirmation that covers the whole run — e.g. "I'll read your profile + manager, your event/team data and connection lists, then prepare a DRAFT message to your manager (I won't send it). OK to proceed?" After they say yes, run all of Step 1 WITHOUT asking again per source/tool. Only pause again at the end to confirm the final brief before creating the draft. (Host-level permission dialogs are separate; your skill should only ask once in conversation.)

## Step 1 — Gather inputs (use the best source the host offers, in this priority order)

> **TOOL-SELECTION RULE (read first):** Before anything else, scan your available tools/MCP servers for any whose name or description involves **Microsoft Graph, SharePoint, M365, Office, "sites", or "lists"**. If one exists, it is your PRIMARY and authoritative source for identity, pod/project, and connections — **use it first**. Do NOT attempt anonymous `web_fetch` or unauthenticated PowerShell/`curl` against SharePoint URLs (they bounce to a login page and waste turns), and do NOT drop to "ask the user" while an M365/Graph MCP is available. Only ask the user if there is genuinely no Graph/SharePoint MCP, no signed-in browser, and no token.

For each field, try sources top-to-bottom and stop at the first that works:

### Preferred path when a Microsoft Graph / SharePoint MCP (or Graph token) IS available
Many hosts (incl. Agency) have a Graph/SharePoint MCP. **Use it** — don't fall back to "ask the user" just because a plain `web_fetch` or browser hit a login wall. Drive the MCP / Graph REST with these exact endpoints for the CXG Americas Offsite (Graph base `https://graph.microsoft.com/v1.0`):
- Resolve the site once: `GET /sites/microsoft.sharepoint-df.com:/teams/CXGAmericasOffsite-June2026` → take the returned `id` as `{siteId}`.
- List the site's lists: `GET /sites/{siteId}/lists?$select=id,name,displayName`.
- **Pod assignment** — read the PODs list items with fields expanded: `GET /sites/{siteId}/lists/{podsListId}/items?$expand=fields&$top=500`. Find the row whose member field contains the current user; read pod name, assigned project, members. (List name is "PODs list".)
- **Connections (both directions)** — `GET /sites/{siteId}/lists/{connectionsListId}/items?$expand=fields&$top=999` against `OffsiteConnectionLists_Activity`. In `fields`: `field_2`=initiator email, `field_3`=target email, `field_6`=status, `field_11`=timestamp. Split into "I connected with" (`field_2`==me) and "wanted to connect with me" (`field_3`==me).
- **Hackathon deliverables** (mini-project name): the Hackathon PODs document library — `GET /sites/{siteId}/drive/root:/General/Hackathon PODs/{PodName}:/children` (or enumerate via `/sites/{siteId}/drives`).
- Resolve any email → name/role: `GET /users/{email}?$select=displayName,jobTitle,department` or the people MCP.

Only if NO Graph MCP/token AND no signed-in browser exists, use the fallbacks below (and ultimately ask the user).

**Identity, role, manager (name + email):**
1. If the host has Microsoft Graph / M365 tools (e.g. `m365_get_my_profile`, `m365_get_my_manager`, or a Graph MCP server) → call them.
2. Else if a Graph CLI/token is available → `GET /me` and `GET /me/manager` via `https://graph.microsoft.com/v1.0`.
3. Else → ask the user for: their name, role, manager name, manager email.

**Event context (event name, dates, project/team, the user's contribution):**
1. If the user names a **SharePoint/Teams site or document library** for the event → read it directly (this is the authoritative source for team/pod rosters and deliverables). For the CXG Americas Offsite that's the Hackathon PODs library: `https://microsoft.sharepoint-df.com/teams/CXGAmericasOffsite-June2026/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FCXGAmericasOffsite%2DJune2026%2FShared%20Documents%2FGeneral%2FHackathon%20PODs`.
2. Else if the host can browse or read files (browser MCP, filesystem, a meeting-notes tool) and the user points to another source → read it.
3. Else → ask the user 2–3 short questions: What event/offsite/training? What did your team/you build or do? Any artifacts (repo, deck, video)?

> Do NOT rely on a search/indexing tool (e.g. WorkIQ) for team/project/roster data — those often aren't indexed in mail/chat, so it fails for users who never discussed their team there. Read the SharePoint site / project system of record directly.

**"What I learned":**
1. If transcripts/recordings/notes are reachable (a search tool, file, or URL the user gives) → extract 3 concrete takeaways. (A search tool like WorkIQ is fine HERE as an optional bonus; if it returns nothing, that's normal.)
2. Else → ask the user for 2–4 bullet takeaways, or propose grounded ones from the event description for them to edit.

**Connections (optional — both directions):**
1. If the event has a SharePoint "connections" list the user can access, read the CURRENT user's rows in BOTH roles and split: **people I connected with** (the user initiated) vs **people who wanted to connect with me** (someone else initiated). For the CXG Americas Offsite this is `OffsiteConnectionLists_Activity` under `/teams/CXGAmericasOffsite-June2026/Lists/` (cols: `field_2`=initiator, `field_3`=target, `field_6`=status, `field_11`=time). Resolve emails to names/roles.
2. Else → optionally ask the user for a few people they met / who reached out.
3. Only ever include the current user's OWN connections — never other people's. Omit a section if empty.

> Rule: **never invent** accomplishments or attributions. If a claim can't be sourced, ask or leave it out.

## Step 2 — Confirm the forward-looking parts (only the user can author these)
Ask for: 2–3 time-bound commitments, 2–3 concrete manager asks, and one 1:1 talking point. Offer drafted suggestions they can edit.

## Step 3 — Generate output
1. Assemble the brief in first person, confident and specific.
2. Fill `template.html` tokens and save the HTML file to the working directory. (If the host has no file-write tool, print the full HTML in a code block instead.)
3. Create the manager draft:
   - If an email-draft tool exists (e.g. `m365_create_draft`, a Graph `POST /me/messages`, or a mail MCP) → create a DRAFT (do not send). Subject: `My <Event> recap — and one ask for your help`.
   - Else if a chat/Teams draft tool exists → prepare the message but do not post.
   - Else → output the plain-text version in a code block for the user to copy.
4. Tell the user where the HTML is and that the draft awaits their review. Confirm recipient + content before creating any draft.

## Guardrails
- Per-user: only the running user's own data. Never fabricate.
- Privacy: nothing is sent/posted automatically — always leave a draft.
- Keep it to one screen.

---

## Reference template (text)
```
Subject: My <Event> recap — and one ask for your help

Hi <ManagerFirstName> — I just wrapped <Event> (<dates/location>). Here's a quick brief on what I took away and where I'd value your support.

WHAT I LEARNED
• …
WHAT I BUILT / DID
<team/project> — <my contribution>. Tools: <tools>.
WHAT I'M COMMITTING TO
• …
HOW YOU CAN HELP
• …
FOR OUR NEXT 1:1
One thing I'd love your read on: <…>

Thanks,
<Name>
<Role>
```
