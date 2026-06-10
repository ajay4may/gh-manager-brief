# gh-manager-brief

A `gh` CLI extension that generates personalized **"send this to your manager"** briefs at the end of a multi-day workshop. Each brief covers:

- What the attendee **learned**
- What they **built**
- What they're **committing to** (next 30 days)
- How the manager can **help**

The goal: turn managers into accountability partners and save attendees an awkward follow-up conversation.

## Install (local, for development)

```bash
gh extension install .
```

From anywhere after install:

```bash
gh manager-brief help
```

## Install (from GitHub, after you push it)

```bash
gh extension install <your-org>/gh-manager-brief
```

> The repo name **must** start with `gh-` for `gh` to recognize it as an extension.

## Usage

```bash
# Generate Markdown briefs into ./out
gh manager-brief generate --input samples/attendees.csv --out ./out --event "AI Bootcamp 2026"

# Also post each brief as a GitHub issue assigned to the attendee
gh manager-brief generate \
  --input samples/attendees.csv \
  --post-issue acme/ai-bootcamp \
  --event "AI Bootcamp 2026"
```

## CSV format

Headers (required, in order):

```
handle,name,manager_email,learned,built,committing,ask
```

Wrap any field containing commas in `"double quotes"`.

## How attendees fill it in

Two options:

1. **Facilitator-driven**: at end of Day 3, hand attendees a Google Form / GitHub Discussion that maps to the CSV columns; export to CSV; run the extension.
2. **Self-service**: ship the CSV template; attendees fill their own row; you concatenate and run once.

## Windows note

The extension is a bash script. On Windows, `gh` runs it via Git Bash (bundled with Git for Windows) — no extra setup needed if you have Git installed.
