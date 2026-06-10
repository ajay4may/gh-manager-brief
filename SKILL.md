---
name: "manager-brief"
description: "Generate a personalized end-of-Day-3 CXG Offsite \"send this to your manager\" brief by pulling the running user's OWN live data (M365 profile/manager, Offsite Hub POD List, hackathon registration, pod mini-project). Default output: a styled CXG-branded HTML file PLUS an Outlook email draft to the manager. Never auto-sends."
---

You generate a personalized CXG Americas Offsite "send this to your manager" brief for the CURRENT signed-in user. This runs per-user and pulls each person's OWN live data — NEVER hardcode another person's values. Every attendee who installs this skill gets THEIR brief from THEIR signals.

# Goal
A one-screen (~250–350 word) manager brief with 6 sections: (1) What I learned, (2) What I built, (3) What I'm committing to, (4) How you (manager) can help, (5) One thing for our next 1:1, plus a signature.

**Default output (always do both):**
1. A styled, CXG-branded **HTML file** saved to the workspace.
2. An **Outlook email draft** addressed to the user's manager (via `m365_create_draft`), left in Drafts for review.

NEVER auto-send. The user reviews and sends themselves.

# Step 1 — Gather the user's OWN live signals (don't ask for what you can fetch)
Run in parallel where possible:
- `m365_get_my_profile` → name, role / jobTitle.
- `m365_get_my_manager` → manager name + email.
- **Pod / assigned project / teammates / mini-hack project** — read with the Browser Control (Playwright) tools, signed in as the current user:
  - **Offsite Hub app** → open **"POD List"**, find the pod whose member list contains the current user; capture pod name, assigned project, teammates.
    `https://apps.powerapps.com/play/e/6e170e38-a716-e023-8347-d840e57a851e/app/04ecb430-68d3-45d1-8e28-ba3da4da8d2a?tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47`
  - **Hackathon PODs SharePoint library** → open the user's pod folder; the files (pitch deck, videos) reveal the actual mini-hack project name + who contributed what.
    `https://microsoft.sharepoint-df.com/teams/CXGAmericasOffsite-June2026/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FCXGAmericasOffsite%2DJune2026%2FShared%20Documents%2FGeneral%2FHackathon%20PODs`
  - The user's **AI toolkit + hackathon goal** are in their own registration ("Sign up for Hack Project" → Register, choices pre-loaded). Only the signed-in user can see their own.
- **"What I learned"** — derive 3 concrete Day-1 takeaways from the Americas Offsite recordings/transcripts via WorkIQ (`workiq.cmd ask -q "..."`), or use grounded offsite themes (AI-first mindset; agents act, not just chat; speed/experimentation over perfection). Make them specific, not generic.

If a browser sign-in wall appears, ask the user to complete sign-in, then continue. If a field truly can't be fetched, ask the user concisely for just that field.

# Step 2 — Confirm the forward-looking parts (only the user can author these)
Ask the user for: 2–3 time-bound commitments, 2–3 concrete low-friction manager asks, one 1:1 talking point. Offer AI-drafted suggestions they can edit. Do NOT invent commitments as if they were facts.

# Step 3 — Grounding rules
- Write in first person as the user.
- Only state accomplishments backed by fetched data. If something (e.g. a recording mention) can't be verified, don't assert it — frame as the user's own contribution or leave it out.
- Confident, specific, short.

# Step 4 — Generate output
1. Build the brief text (template below).
2. Save a **styled HTML file** to the workspace named `CXG-Manager-Brief-<FirstNameLastName>.html`. Use `template.html` in this skill folder as the exact styling/structure — substitute the brief content into it. It is CXG-branded (deep crimson `#A4262C` accent, navy→crimson gradient header, "Segoe UI" font) and includes the Clawpilot theme-detection script + CSS variables so it renders in light/dark.
3. Create an **email draft** to the manager via `m365_create_draft` — subject `"My CXG Offsite recap — and one ask for your help"`, body = the plain-text brief. Confirm recipient + content with the user first. NEVER call any send tool.
4. Show the user the HTML file path and confirm the draft is in their Drafts folder.

# Reference: the 6-section template
Subject: My CXG Offsite recap — and one ask for your help
Intro: "Hi <ManagerFirstName> — I just wrapped three days at the CXG Americas Offsite (June 9–11, Redmond). Here's a quick brief on what I took away and where I'd value your support."
- **WHAT I LEARNED** — bullets
- **WHAT I BUILT** — pod name + assigned project theme + mini-hack project + the user's specific contribution + tools used
- **WHAT I'M COMMITTING TO** — bullets
- **HOW YOU CAN HELP** — bullets
- **FOR OUR NEXT 1:1** — one line
- Signature: name + role

Always confirm the final brief with the user before creating any draft.
