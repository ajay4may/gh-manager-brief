# Manager Brief — portable agent skill

A CLI-agnostic skill that generates a personalized "send this to your manager" recap brief after any event, offsite, training, or hackathon. It gathers the running user's own context (identity, manager, project, contribution) using whatever tools the host agent offers, confirms forward commitments with the user, and outputs:

1. A styled **HTML file** in the working directory, and
2. A **draft** email/message to the manager (never sent automatically).

Works in **GitHub Copilot CLI**, **Agency**, **Clawpilot**, or any MCP-capable agent. It degrades gracefully: if a tool isn't available it asks the user or reads a file you point it at.

---

## Install

The skill is the `manager-brief/` folder (`SKILL.md` + `template.html` + this `README.md`). Drop it into each host's skills location below.

### Microsoft Scout / Clawpilot
1. Copy the folder to your skills directory:
   ```
   %USERPROFILE%\.copilot\m-skills\manager-brief\         (Windows)
   ~/.copilot/m-skills/manager-brief/                      (macOS/Linux)
   ```
   You should end up with `…/m-skills/manager-brief/SKILL.md`.
2. Restart Scout/Clawpilot (or reload skills) so it indexes the new skill.
3. Sign in to M365 in the app (the `/` menu → sign in) so the built-in `m365_*` tools + signed-in browser are available.
4. Run `/manager-brief`.
   - Data source here: built-in `m365_*` tools + the Playwright browser signed in as you (reads the POD List / SharePoint lists directly).

### GitHub Copilot CLI (ghcp)
1. Copy the folder to the Copilot CLI skills directory:
   ```
   %USERPROFILE%\.copilot\skills\manager-brief\           (Windows)
   ~/.copilot/skills/manager-brief/                        (macOS/Linux)
   ```
   (Note: `skills`, not `m-skills`.)
2. Start a new `copilot` session (skills load at startup), then run `/manager-brief` or say "use the manager-brief skill".
3. ghcp has no built-in M365 auth. For auto-lookup, either:
   - add a **Microsoft Graph MCP server** to `~/.copilot/mcp-config.json` (then the skill's Graph endpoints work), or
   - just answer the skill's prompts — it falls back to asking you for pod/manager/connections and still produces the HTML + draft text.

### Agency (or any MCP-capable agent)
1. Place `manager-brief/` where Agency loads skills/prompts (or paste `SKILL.md` contents as a skill/system prompt).
2. **Ensure the Microsoft Graph / SharePoint MCP is enabled** in Agency. The skill auto-detects it and uses these Graph calls:
   - `GET /sites/microsoft.sharepoint-df.com:/teams/CXGAmericasOffsite-June2026` → `{siteId}`
   - `GET /sites/{siteId}/lists/{PODs list}/items?$expand=fields` (pod assignment)
   - `GET /sites/{siteId}/lists/{OffsiteConnectionLists_Activity}/items?$expand=fields` (connections, both directions)
   - `GET /users/{email}?$select=displayName,jobTitle,department` (resolve names)
3. Run the skill. With the Graph MCP present it resolves pod + connections directly — no "which POD were you on?" prompt. (If you see that prompt, the agent isn't routing to the Graph MCP — confirm the MCP is enabled and that `SKILL.md`'s "TOOL-SELECTION RULE" is intact.)

### Quick verification (any host)
After install, `/manager-brief` should: ask for consent **once** → pull your profile/manager/pod/connections → ask only for your commitments → output an HTML file + a manager draft. If it jumps straight to asking which pod you're on, the host has no Graph/SharePoint access wired up (see the host's section above).

---

## What it needs (and fallbacks)
| Input | Best source | Fallback |
|---|---|---|
| Name, role, manager | Graph/M365 tool or `GET /me`, `/me/manager` | ask the user |
| Event + project + contribution | notes/repo/deck the user points to | ask the user |
| Learnings | transcript/notes search | user-provided bullets |
| Commitments / asks / 1:1 topic | — | always asked (only the user can author) |

## Guardrails
- Per-user only; never fabricates accomplishments.
- Never sends/posts automatically — always leaves a draft for review.
- Keeps the brief to one screen (~250–350 words).

## Files
- `SKILL.md` — the portable skill instructions.
- `template.html` — neutral-branded HTML output (override `--accent` for org colors, e.g. CXG crimson `#a4262c`).
