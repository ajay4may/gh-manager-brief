// build-arch-doc.js — generate architecture.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

const here = __dirname;
const diagram = path.join(here, "architecture-diagram.png");
const outFile = path.join(here, "architecture.docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const P = (text, opts = {}) => new Paragraph({ children: [new TextRun({ text, ...opts })], ...opts.paragraph });
const H = (text, level) => new Paragraph({ heading: level, children: [new TextRun({ text, bold: true })] });
const Bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun(text)],
});

const cell = (text, opts = {}) => new TableCell({
  borders,
  width: { size: opts.width || 4680, type: WidthType.DXA },
  shading: opts.header ? { fill: "DBEAFE", type: ShadingType.CLEAR } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({ children: [new TextRun({ text, bold: !!opts.header })] })],
});

const table = (rows, widths) => new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths,
  rows: rows.map((r, i) => new TableRow({
    children: r.map((c, j) => cell(c, { width: widths[j], header: i === 0 })),
  })),
});

const doc = new Document({
  creator: "gh-manager-brief",
  title: "gh manager-brief - Architecture",
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Calibri", color: "1F2937" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Calibri", color: "2563EB" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Calibri", color: "1F2937" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{
        level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }]},
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: { default: new Header({ children: [new Paragraph({
      children: [new TextRun({ text: "gh manager-brief - Architecture", color: "6B7280", size: 18 })],
    })]})},
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "Page ", color: "6B7280", size: 18 }),
        new TextRun({ children: [PageNumber.CURRENT], color: "6B7280", size: 18 }),
      ],
    })]})},
    children: [
      // Title
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 1200, after: 200 },
        children: [new TextRun({ text: "gh manager-brief", bold: true, size: 56, color: "2563EB" })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "Architecture Document", bold: true, size: 36, color: "1F2937" })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 800 },
        children: [new TextRun({ text: "Personalized end-of-Day-3 manager briefs for workshop attendees", italics: true, color: "6B7280", size: 22 })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: `Version 1.0  |  ${new Date().toISOString().slice(0,10)}`, color: "6B7280", size: 20 })],
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // TOC
      H("Table of Contents", HeadingLevel.HEADING_1),
      new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),

      new Paragraph({ children: [new PageBreak()] }),

      // 1. Overview
      H("1. Overview", HeadingLevel.HEADING_1),
      P("gh manager-brief is a GitHub CLI extension that generates a personalized 'send this to your manager' brief for each workshop attendee at the end of Day 3. Each brief is a one-page Markdown document covering four things: what the attendee learned, what they built, what they are committing to over the next 30 days, and how their manager can help."),
      P("The design goal is behavioral, not technical: turn managers into accountability partners rather than obstacles, and save attendees an awkward follow-up conversation they would otherwise skip."),

      H("1.1 Problem", HeadingLevel.HEADING_2),
      Bullet("Multi-day workshops produce excited attendees and vague intentions."),
      Bullet("Attendees rarely follow up with their manager - the conversation feels open-ended and high-effort."),
      Bullet("Managers, lacking specifics, default to 'sounds great' instead of unblocking the next step."),
      Bullet("Workshop ROI evaporates within two weeks."),

      H("1.2 Solution", HeadingLevel.HEADING_2),
      P("A small CLI extension that takes a CSV of attendee responses and emits ready-to-send Markdown briefs. Each brief has a fixed shape (learned / built / committing / ask) so it reads in under two minutes. Optionally, the extension posts each brief as a GitHub issue assigned to the attendee with a 'manager-brief' label, creating a durable 30-day accountability checkpoint."),

      // 2. Architecture
      H("2. Architecture", HeadingLevel.HEADING_1),
      P("The system has four stages: Capture, Generation, Output, and Outcome. The diagram below shows the flow."),

      // Diagram image
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 200 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync(diagram),
          transformation: { width: 600, height: 338 },
          altText: { title: "Architecture diagram", description: "gh manager-brief architecture diagram", name: "ArchitectureDiagram" },
        })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Figure 1: End-to-end flow from attendee response to manager handoff.", italics: true, color: "6B7280", size: 18 })],
      }),

      // 3. Components
      H("3. Components", HeadingLevel.HEADING_1),
      table([
        ["Component", "Type", "Responsibility"],
        ["gh-manager-brief (script)", "Bash entry point", "Parses CLI flags, reads CSV, loops attendees, renders each brief."],
        ["attendees.csv", "Input", "Single source of truth for attendee data. One row per attendee."],
        ["out/<handle>.md", "Output", "One Markdown brief per attendee. Self-contained; safe to email."],
        ["gh issue create", "Optional output", "Posts each brief as a GitHub issue, assigned to attendee, labeled 'manager-brief'."],
        ["GitHub CLI auth", "Dependency", "Reuses existing gh authentication; no token management in the extension."],
      ], [2600, 2200, 4560]),

      // 4. Data Flow
      H("4. Data flow", HeadingLevel.HEADING_1),
      P("Step-by-step:"),
      Bullet("Facilitator collects attendee responses via Form / GitHub Discussion / interview."),
      Bullet("Responses are exported to a CSV with columns: handle, name, manager_email, learned, built, committing, ask."),
      Bullet("Facilitator runs: gh manager-brief generate --input attendees.csv --out ./out"),
      Bullet("The extension iterates rows, rendering one Markdown file per attendee into ./out."),
      Bullet("If --post-issue OWNER/REPO is supplied, each brief is also posted as an issue assigned to the attendee."),
      Bullet("Attendee receives the brief (file or issue notification), forwards it to their manager."),
      Bullet("Manager replies with concrete support; the issue (if used) becomes the 30-day checkpoint."),

      // 5. CSV Schema
      H("5. CSV schema", HeadingLevel.HEADING_1),
      table([
        ["Column", "Type", "Purpose"],
        ["handle", "string", "GitHub username (also used as output filename)."],
        ["name", "string", "Display name for the brief header."],
        ["manager_email", "string", "Listed in the brief so the attendee knows who to send it to."],
        ["learned", "text", "Free-form: what concepts or skills the attendee absorbed."],
        ["built", "text", "Free-form: what artifact the attendee shipped during the workshop."],
        ["committing", "text", "Free-form: 30-day commitment, ideally measurable."],
        ["ask", "text", "Free-form: specific support needed from the manager."],
      ], [1800, 1400, 6160]),
      P("Fields containing commas must be wrapped in double quotes per RFC 4180.", { italics: true }),

      // 6. Distribution
      H("6. Distribution", HeadingLevel.HEADING_1),
      P("The extension is distributed as a GitHub repository named 'gh-manager-brief'. The 'gh-' prefix is required for gh to recognize it as an extension."),
      H("6.1 Install", HeadingLevel.HEADING_2),
      P("gh extension install <org>/gh-manager-brief", { font: "Consolas" }),
      H("6.2 Update", HeadingLevel.HEADING_2),
      P("gh extension upgrade manager-brief", { font: "Consolas" }),
      H("6.3 Uninstall", HeadingLevel.HEADING_2),
      P("gh extension remove manager-brief", { font: "Consolas" }),

      // 7. Security & Privacy
      H("7. Security and privacy", HeadingLevel.HEADING_1),
      Bullet("Attendee data lives only in the CSV and the generated Markdown - no external services, no telemetry."),
      Bullet("When --post-issue is used, briefs become content in the target GitHub repo. Use a private repo for sensitive workshops."),
      Bullet("Manager email addresses are written into the brief body. If the issue path is used, this lands in GitHub - confirm attendees are OK with that."),
      Bullet("The extension inherits gh authentication; no additional secrets are stored."),

      // 8. Extension points
      H("8. Extension points (future)", HeadingLevel.HEADING_1),
      Bullet("--email-via-graph: send each brief directly to manager_email via Microsoft Graph."),
      Bullet("--template <path>: support custom Markdown templates per organization."),
      Bullet("--checkin-days N: auto-create a follow-up issue at day N referencing the original brief."),
      Bullet("--source discussion: pull responses directly from a GitHub Discussion thread instead of CSV."),

      // 9. Operations
      H("9. Operations", HeadingLevel.HEADING_1),
      table([
        ["Concern", "How it's handled"],
        ["Runtime errors", "Bash 'set -euo pipefail' aborts on first failure; partial output remains for inspection."],
        ["Idempotency", "Re-running overwrites Markdown files. Issue posting is NOT idempotent - use a fresh label or dedicated repo per cohort."],
        ["Logging", "Each generated file and posted issue is echoed to stdout."],
        ["Cross-platform", "Runs natively on macOS/Linux. Windows uses Git Bash, which gh invokes automatically."],
      ], [3000, 6360]),

      // 10. Glossary
      H("10. Glossary", HeadingLevel.HEADING_1),
      Bullet("Brief: the one-page Markdown document a single attendee sends to their manager."),
      Bullet("Cohort: a group of attendees from a single workshop run."),
      Bullet("Ask: the concrete unblock or support request made of the manager."),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outFile, buf);
  console.log("wrote", outFile);
});
