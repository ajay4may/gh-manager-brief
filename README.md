# gh-manager-brief

A `gh` CLI extension and reusable **CxG-team agent** for manager-ready briefs.

Two flows, one extension:

| Subcommand | Use it when… |
|---|---|
| `gh manager-brief event` | You attended a CxG **event** (CXG Offsite, Partner Bootcamp, Customer Advisory Board, training, customer meeting) and need a brief for your manager. **Grounded in [WorkIQ](https://aka.ms/workiq).** |
| `gh manager-brief generate` | You ran a **Day-3 workshop** and want a personalized brief per attendee from a CSV. |
| `gh manager-brief eval` | Run the offline eval suite against built-in fixtures. |

Every brief covers what was learned, what's getting done about it, and how the manager can help — so managers become accountability partners, not obstacles.

---

## Install

```bash
gh extension install ajay4may/gh-manager-brief
gh manager-brief help
```

`gh-` prefix is required for `gh` to recognize a repo as an extension. Windows users: extension runs via Git Bash (already bundled with Git for Windows).

---

## `event` — WorkIQ-grounded event brief

Generate a manager-ready brief for an event you attended, grounded in your Microsoft 365 corpus via WorkIQ.

```bash
gh manager-brief event \
  --type offsite \
  --name "CXG Americas Offsite" \
  --from 2026-06-09 --to 2026-06-11 \
  --keyword "AI agents" --keyword "scalability" \
  --manager-email your.manager@microsoft.com
```

### What it does
1. Queries **WorkIQ** for the event window:
   - Who attended (meetings, names, orgs, roles)
   - What was discussed (top 5–8 themes with attribution)
   - Action items, owners, due dates
   - Follow-up emails / Teams chats sent after the event
2. Renders a Markdown brief with **7 sections**:
   1. TL;DR
   2. Attendees (table)
   3. Key learnings
   4. Action items (table)
   5. **My plan to act** (for actions you own)
   6. Follow-ups since the event
   7. How my manager can help
3. **Every fact carries a provenance footnote** (`[^wq1]`, `[^wq2]`, …) linking back to the WorkIQ query — your manager can verify any claim.

### Supported event types
`offsite` · `bootcamp` · `cab` · `training` · `workshop` · `customer-meeting`

### Optional local supplements
You can attach files even when WorkIQ is on — they're folded into the brief:

```bash
gh manager-brief event --type bootcamp --name "Partner AI Bootcamp" \
  --from 2026-05-04 --to 2026-05-05 \
  --transcript day1.vtt --transcript day2.vtt \
  --agenda agenda.docx \
  --my-notes my-notes.md
```

### Offline / no-WorkIQ mode
Use `--no-workiq` to fall back to local files only — useful for sensitive content (e.g., CAB) you don't want WorkIQ to touch:

```bash
gh manager-brief event --type cab --name "Q2 CAB" \
  --from 2026-04-22 --to 2026-04-22 \
  --transcript cab.vtt --no-workiq
```

### Examples by event type

```bash
# CXG offsite
gh manager-brief event --type offsite --name "CXG Americas Offsite" \
  --from 2026-06-09 --to 2026-06-11

# Partner Bootcamp
gh manager-brief event --type bootcamp --name "Partner AI Bootcamp" \
  --from 2026-05-04 --to 2026-05-05

# Customer Advisory Board
gh manager-brief event --type cab --name "Q2 CAB" \
  --from 2026-04-22 --to 2026-04-22

# Internal training
gh manager-brief event --type training --name "Foundry Models 201" \
  --from 2026-03-12 --to 2026-03-12

# 1:1 customer meeting
gh manager-brief event --type customer-meeting --name "Acme Q3 review" \
  --from 2026-06-05 --to 2026-06-05 --attendee-hint "Linda Park, Brian Cole"
```

---

## `generate` — Day-3 workshop briefs (original flow)

Generate one Markdown brief per attendee from a CSV.

```bash
gh manager-brief generate --input samples/attendees.csv --out ./out --event "AI Bootcamp 2026"

# Also post each brief as a GitHub issue assigned to the attendee
gh manager-brief generate --input samples/attendees.csv \
  --post-issue acme/ai-bootcamp --event "AI Bootcamp 2026"
```

CSV headers (required, in order):

```
handle,name,manager_email,learned,built,committing,ask
```

Wrap fields containing commas in `"double quotes"`.

---

## `eval` — offline eval suite

```bash
gh manager-brief eval
```

Runs 3 cases (CXG offsite, Partner Bootcamp, Q2 CAB) against fixture WorkIQ responses, then validates each generated brief against shape + content checks. Exits non-zero on any failure. **Never makes network calls.** Use this as a regression gate before merging changes.

Add your own case in `eval/run_evals.py` and a fixture directory in `eval/fixtures/<your-case>/` with `attendees.txt`, `themes.txt`, `actions.txt`, and optional `followups.txt`.

---

## Architecture & docs

- [Architecture document](docs/architecture.docx) — full system overview
- [Architecture diagram](docs/architecture-diagram.png)
- [Tutorial video (1m59s)](docs/tutorial.mp4) — walks through the original Day-3 `generate` flow

---

## Privacy

- WorkIQ stays inside the Microsoft trust boundary; no third-party APIs are called.
- For sensitive events (CAB, customer meetings), use `--no-workiq` if you'd rather not query the corpus at all.
- Generated briefs are written to your local disk only — the extension never auto-sends them. You always review and forward.

---

## Repository layout

```
gh-manager-brief
├── gh-manager-brief            # bash entry; dispatches subcommands
├── lib/
│   ├── event_brief.py          # main event pipeline
│   ├── workiq/                 # WorkIQ client + queries
│   ├── extractors/             # attendees / themes / actions / followups
│   ├── parsers/                # vtt + plain text
│   └── renderers/md.py         # Markdown renderer w/ provenance
├── eval/
│   ├── run_evals.py            # eval runner
│   └── fixtures/               # WorkIQ response fixtures per case
├── samples/attendees.csv       # CSV template for `generate`
└── docs/                       # architecture doc, diagram, tutorial video
```
