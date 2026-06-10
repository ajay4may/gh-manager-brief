# Manager Brief — Clawpilot Skill

Generates a personalized end-of-Day-3 **CXG Americas Offsite "send this to your manager" brief** for whoever runs it. It pulls *your own* live data (M365 profile + manager, Offsite Hub POD List, your hackathon registration, your pod's mini-hack files) and produces:

1. A styled, CXG-branded **HTML file** in your workspace, and
2. An **Outlook email draft** to your manager (left in Drafts — never auto-sent).

The brief covers: what you learned, what you (and your pod) built, what you're committing to, how your manager can help, and one thing for your next 1:1.

---

## Install (per teammate)

1. Copy the **`manager-brief/`** folder into your Clawpilot skills directory:
   ```
   %USERPROFILE%\.copilot\m-skills\manager-brief\
   ```
   (i.e. `C:\Users\<you>\.copilot\m-skills\manager-brief\SKILL.md` + `template.html`)
2. Restart Clawpilot (or reload skills) so it picks up the new skill.
3. Make sure you're **signed in to M365** in Clawpilot (`/` → sign in if prompted).

## Run

In Clawpilot, type:
```
/manager-brief
```
Then:
- Let it pull your live data (sign in to the Offsite Hub / SharePoint in the browser window if prompted).
- Give it your 2–3 commitments, your manager asks, and a 1:1 talking point.
- Review the generated brief; it saves the HTML and offers to drop an email draft to your manager.
- **You** review the draft in Outlook and hit send.

## Privacy
- Each person runs it as themselves — it only reads *your* private registration plus the shared POD List.
- Nothing is ever sent automatically. The draft sits in your Drafts until you send it.
- Don't share another person's brief; it contains their personal commitments.

## Files
- `SKILL.md` — the skill instructions Clawpilot executes.
- `template.html` — the CXG-branded HTML styling used for the output file.
