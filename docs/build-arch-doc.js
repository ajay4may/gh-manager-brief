// build-arch-doc.js — architecture document v2 (CxG event agent, WorkIQ-grounded)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

const here = __dirname;
const diagram = path.join(here, "architecture-diagram.png");
const outFile = path.join(here, "architecture.docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const P = (text, opts = {}) => new Paragraph({ children: [new TextRun({ text, ...opts })] });
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
  title: "gh manager-brief - Architecture (v2, CxG Event Agent)",
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
      children: [new TextRun({ text: "gh manager-brief - Architecture (v2)", color: "6B7280", size: 18 })],
    })]})},
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "Page ", color: "6B7280", size: 18 }),
        new TextRun({ children: [PageNumber.CURRENT], color: "6B7280", size: 18 }),
      ],
    })]})},
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 1200, after: 200 },
        children: [new TextRun({ text: "gh manager-brief", bold: true, size: 56, color: "2563EB" })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: [new TextRun({ text: "Architecture Document - v2", bold: true, size: 36, color: "1F2937" })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { after: 800 },
        children: [new TextRun({ text: "CxG event-brief agent, grounded in WorkIQ", italics: true, color: "6B7280", size: 22 })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: `Version 2.0  |  ${new Date().toISOString().slice(0,10)}`, color: "6B7280", size: 20 })],
      }),

      new Paragraph({ children: [new PageBreak()] }),

      H("Table of Contents", HeadingLevel.HEADING_1),
      new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),

      new Paragraph({ children: [new PageBreak()] }),

      // 1. Overview
      H("1. Overview", HeadingLevel.HEADING_1),
      P("gh manager-brief is a GitHub CLI extension and reusable CxG-team agent that produces a manager-ready brief for any event a CxG team member attends - CXG Offsite, Partner Bootcamp, Customer Advisory Board (CAB), training, workshop, or customer meeting."),
      P("Every fact in every brief is grounded in WorkIQ - Microsoft 365 data (meetings, transcripts, emails, Teams chats, people, docs). Local files (transcripts, agendas, notes) are optional supplements, never the primary source."),

      H("1.1 Why this exists", HeadingLevel.HEADING_2),
      Bullet("CxG team members attend many high-signal events but skip the manager debrief because the conversation feels open-ended."),
      Bullet("Workshop and event ROI evaporates without a structured handoff."),
      Bullet("Managers need attendees, learnings, action items, and a concrete plan to act - all with provenance they can trust."),

      H("1.2 What it produces", HeadingLevel.HEADING_2),
      P("A Markdown brief with seven sections:"),
      Bullet("TL;DR (3 bullets)"),
      Bullet("Attendees (table: name, org, role, source)"),
      Bullet("Key learnings (5-8 themes with attribution)"),
      Bullet("Action items (owner, action, due, source)"),
      Bullet("My plan to act (next step, by when, who I need - for actions you own)"),
      Bullet("Follow-ups since the event (post-event emails/chats from WorkIQ)"),
      Bullet("How my manager can help (your specific ask)"),
      P("Every claim ends with a footnote like [^wq1] linking to the exact WorkIQ query in the Sources section."),

      // 2. Architecture
      H("2. Architecture", HeadingLevel.HEADING_1),
      P("Six logical components, illustrated below."),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 200 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync(diagram),
          transformation: { width: 600, height: 353 },
          altText: { title: "Architecture v2", description: "WorkIQ-grounded event agent", name: "ArchV2" },
        })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Figure 1: WorkIQ-grounded event-brief agent flow.", italics: true, color: "6B7280", size: 18 })],
      }),

      H("2.1 Components", HeadingLevel.HEADING_2),
      table([
        ["#", "Component", "Responsibility"],
        ["1", "Trigger (CLI)", "User runs gh manager-brief event with type/name/date window."],
        ["2", "Agent (event_brief.py)", "Orchestrates queries, parsing, rendering. Pure Python, no LLM dependency in Phase 1."],
        ["3", "WorkIQ grounding", "Primary data source. Queried via subprocess workiq.cmd ask."],
        ["4", "Eval suite", "Offline regression. Fixture-driven, no network calls."],
        ["5", "Output (Markdown)", "Manager-ready brief, 7 sections, with provenance footnotes."],
        ["6", "Manager outcome", "Concrete attendees, commitments, plan to act - all traceable."],
      ], [600, 2500, 6260]),

      // 3. Data flow
      H("3. Data flow", HeadingLevel.HEADING_1),
      Bullet("User runs the event subcommand with --type, --name, --from, --to."),
      Bullet("Agent builds four WorkIQ queries (attendees, themes, action items, follow-ups)."),
      Bullet("Each query is dispatched via workiq.cmd ask -q '...' (subprocess). Response captured verbatim."),
      Bullet("Per-domain extractors parse responses into structured rows and tag each with a provenance ID."),
      Bullet("Optional local files (.vtt, .docx, .md) are folded in as supplements, not as primary sources."),
      Bullet("Markdown renderer emits the brief with footnotes; Sources section lists every WorkIQ query verbatim."),
      Bullet("User reviews and forwards to manager. Never auto-sent."),

      // 4. WorkIQ queries
      H("4. WorkIQ query templates", HeadingLevel.HEADING_1),
      P("All four queries are pure natural language - WorkIQ handles retrieval and summarization."),
      table([
        ["Domain", "Question shape"],
        ["Attendees", "List people who attended meetings titled or about '{event}' between {from}-{to}, with name, org, role."],
        ["Themes", "Summarize 5-8 most important topics in meetings about '{event}' between {from}-{to}, with attribution."],
        ["Action items", "List action items, owners, and due dates from meetings about '{event}' between {from}-{to}."],
        ["Follow-ups", "After {to}, find emails/Teams messages referencing '{event}' with new commitments or updates."],
      ], [2200, 7160]),

      // 5. Provenance
      H("5. Provenance model", HeadingLevel.HEADING_1),
      Bullet("Each WorkIQ call gets a sequential source ID (wq1, wq2, ...)."),
      Bullet("Every fact rendered from that call carries the marker [^wqN]."),
      Bullet("Sources section at the bottom of the brief lists each marker with the exact WorkIQ question."),
      Bullet("A manager can re-run any question in WorkIQ to verify."),
      Bullet("Local supplements are tagged [local transcript] or [user hint] - clearly not WorkIQ-grounded."),

      // 6. Privacy
      H("6. Privacy and trust boundary", HeadingLevel.HEADING_1),
      Bullet("WorkIQ stays inside the Microsoft trust boundary; no third-party APIs are called."),
      Bullet("For sensitive events (CAB, customer 1:1), use --no-workiq to operate on local files only."),
      Bullet("Briefs are written to local disk only; the agent never auto-sends."),
      Bullet("Generated briefs may carry the sensitivity of the underlying transcripts - label them before sharing."),

      // 7. Reuse model
      H("7. CxG team reuse model", HeadingLevel.HEADING_1),
      P("The extension is the same install command for everyone on CxG:"),
      P("gh extension install ajay4may/gh-manager-brief", { font: "Consolas" }),
      P("Per-user state (manager email, display name) can be passed at the command line or set as environment variables. Phase 3 will add a config file."),

      // 8. Eval
      H("8. Eval suite", HeadingLevel.HEADING_1),
      P("Offline, fixture-driven. Three cases ship in the repo: CXG offsite, Partner Bootcamp, Q2 CAB."),
      P("Run with: gh manager-brief eval", { font: "Consolas" }),
      P("Each case provides plain-text WorkIQ response fixtures (attendees.txt, themes.txt, actions.txt, followups.txt). The agent's --fixture-dir flag loads these instead of calling WorkIQ. The eval validates the generated brief against shape checks (section presence) and minimum counts (attendees, themes, actions)."),
      P("Add a new case by dropping a folder into eval/fixtures/<case>/ and appending an entry to CASES in eval/run_evals.py."),

      // 9. Extension points
      H("9. Future work", HeadingLevel.HEADING_1),
      Bullet("LLM-assisted clustering of themes via Microsoft-internal endpoint."),
      Bullet("DOCX output (manager-friendly Word doc)."),
      Bullet("Auto-create follow-up issue at day 30 referencing the original brief."),
      Bullet("Email the brief via Microsoft Graph (with explicit user confirmation)."),
      Bullet("Per-user config file (~/.config/gh-manager-brief/config.yml)."),
      Bullet("MIP sensitivity propagation: stamp brief filename + header with highest sensitivity encountered."),

      // 10. File layout
      H("10. File layout", HeadingLevel.HEADING_1),
      P("gh-manager-brief", { font: "Consolas" }),
      P("├── gh-manager-brief            # bash entry, dispatches subcommands", { font: "Consolas" }),
      P("├── lib/", { font: "Consolas" }),
      P("│   ├── event_brief.py          # main pipeline", { font: "Consolas" }),
      P("│   ├── workiq/                 # client + question templates", { font: "Consolas" }),
      P("│   ├── extractors/             # attendees / themes / actions / followups", { font: "Consolas" }),
      P("│   ├── parsers/                # vtt + plain text", { font: "Consolas" }),
      P("│   └── renderers/md.py         # Markdown with provenance", { font: "Consolas" }),
      P("├── eval/", { font: "Consolas" }),
      P("│   ├── run_evals.py            # eval runner", { font: "Consolas" }),
      P("│   └── fixtures/               # WorkIQ response fixtures per case", { font: "Consolas" }),
      P("├── samples/attendees.csv       # CSV template for 'generate'", { font: "Consolas" }),
      P("└── docs/                       # this document, diagram, tutorial video", { font: "Consolas" }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outFile, buf);
  console.log("wrote", outFile);
});
