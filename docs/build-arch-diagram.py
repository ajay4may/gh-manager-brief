"""Architecture diagram v2 — WorkIQ-grounded event agent."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

OUT = Path(__file__).parent / "architecture-diagram.png"

W, H = 1700, 1000
BG = (250, 250, 252)
INK = (30, 30, 36)
MUTED = (110, 110, 120)
BLUE = (37, 99, 235)
BLUE_S = (219, 234, 254)
GREEN = (16, 163, 74)
GREEN_S = (220, 252, 231)
PURPLE = (124, 58, 237)
PURPLE_S = (237, 233, 254)
ORANGE = (234, 88, 12)
ORANGE_S = (255, 237, 213)
GREY_S = (243, 244, 246)


def font(s, bold=False):
    for c in [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]:
        try: return ImageFont.truetype(c, s)
        except Exception: continue
    return ImageFont.load_default()


def box(d, xy, fill, outline, r=14, w=2):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


def text(d, xy, s, f, fill=INK, anchor="lt"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def arrow(d, x1, y1, x2, y2, color=MUTED, w=3):
    d.line([(x1, y1), (x2, y2)], fill=color, width=w)
    a = math.atan2(y2 - y1, x2 - x1); ah = 14
    p1 = (x2 - ah * math.cos(a - math.pi/7), y2 - ah * math.sin(a - math.pi/7))
    p2 = (x2 - ah * math.cos(a + math.pi/7), y2 - ah * math.sin(a + math.pi/7))
    d.polygon([(x2, y2), p1, p2], fill=color)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

F_T = font(38, bold=True); F_H = font(22, bold=True); F_B = font(17)
F_S = font(14); F_TAG = font(12, bold=True)

text(d, (50, 28), "gh manager-brief - CxG Event Agent (WorkIQ-grounded)", F_T)
text(d, (50, 78), "Every fact in every brief is sourced from Microsoft 365 via WorkIQ. Local files are optional supplements.",
     F_B, MUTED)

# ============ Row 1: inputs ============
# User trigger
box(d, (50, 150, 350, 310), GREEN_S, GREEN)
text(d, (70, 168), "1. TRIGGER", F_TAG, GREEN)
text(d, (70, 190), "CxG attendee runs", F_H)
text(d, (70, 224), "gh manager-brief event", F_B, INK)
text(d, (70, 250), "--type offsite|bootcamp|", F_S, MUTED)
text(d, (70, 270), "        cab|training|...", F_S, MUTED)
text(d, (70, 288), "--name 'CXG Offsite' --from --to", F_S, MUTED)

# Optional locals
box(d, (50, 340, 350, 460), GREY_S, MUTED)
text(d, (70, 358), "OPTIONAL LOCAL", F_TAG, MUTED)
text(d, (70, 380), "Supplements", F_H)
text(d, (70, 412), "- Transcript (.vtt)", F_S)
text(d, (70, 432), "- Agenda (.docx)", F_S)
text(d, (70, 452), "- My notes (.md)", F_S)

# ============ Row 2: agent core ============
box(d, (430, 150, 920, 460), BLUE_S, BLUE, r=16, w=3)
text(d, (450, 168), "2. AGENT", F_TAG, BLUE)
text(d, (450, 190), "Event-brief pipeline (Python)", F_H)

# inner steps
ys = 240
for label, sub in [
    ("Build WorkIQ queries", "attendees / themes / actions / follow-ups"),
    ("Call WorkIQ", "subprocess workiq.cmd ask -q '...'"),
    ("Parse + dedupe", "structured rows; cite per source"),
    ("Render Markdown", "7 sections + footnote provenance"),
]:
    box(d, (450, ys, 900, ys + 50), (255, 255, 255), BLUE, r=10, w=1)
    text(d, (465, ys + 6), label, F_B, INK)
    text(d, (465, ys + 28), sub, F_S, MUTED)
    ys += 60

arrow(d, 350, 230, 430, 230, color=GREEN)
arrow(d, 350, 400, 430, 400, color=MUTED)

# ============ Row 2 right: WorkIQ ============
box(d, (970, 150, 1290, 360), PURPLE_S, PURPLE, w=3)
text(d, (990, 168), "3. WORKIQ", F_TAG, PURPLE)
text(d, (990, 190), "Microsoft 365 grounding", F_H)
text(d, (990, 224), "- Meetings + transcripts", F_S)
text(d, (990, 246), "- Emails (Outlook)", F_S)
text(d, (990, 268), "- Teams chats + channels", F_S)
text(d, (990, 290), "- People graph", F_S)
text(d, (990, 312), "- Docs (OneDrive / SharePoint)", F_S)
text(d, (990, 334), "Inside Microsoft trust boundary.", F_S, MUTED)

arrow(d, 920, 250, 970, 250, color=BLUE)
arrow(d, 970, 290, 920, 290, color=PURPLE)

# Eval block (top right corner)
box(d, (1340, 150, 1650, 290), ORANGE_S, ORANGE)
text(d, (1360, 168), "4. EVAL", F_TAG, ORANGE)
text(d, (1360, 190), "Offline regression", F_H)
text(d, (1360, 222), "gh manager-brief eval", F_B, INK)
text(d, (1360, 250), "Uses eval/fixtures/<case>/", F_S, MUTED)
text(d, (1360, 268), "No WorkIQ calls. CI-ready.", F_S, MUTED)

# ============ Row 3: output ============
box(d, (430, 510, 920, 800), GREY_S, MUTED, r=14)
text(d, (450, 528), "5. OUTPUT", F_TAG, MUTED)
text(d, (450, 550), "Manager brief (Markdown)", F_H)
text(d, (450, 586), "1. TL;DR", F_S)
text(d, (450, 606), "2. Attendees (table, with source)", F_S)
text(d, (450, 626), "3. Key learnings (themes, with source)", F_S)
text(d, (450, 646), "4. Action items (owner / action / due / source)", F_S)
text(d, (450, 666), "5. My plan to act (next step / by when / who)", F_S)
text(d, (450, 686), "6. Follow-ups since the event", F_S)
text(d, (450, 706), "7. How my manager can help", F_S)
text(d, (450, 740), "Every fact: [^wqN] -> WorkIQ query (Sources section)", F_S, BLUE)
text(d, (450, 762), "User reviews + forwards to manager.", F_S, MUTED)

arrow(d, 675, 460, 675, 510, color=BLUE, w=3)

# Manager outcome
box(d, (970, 510, 1650, 800), BLUE_S, BLUE, r=14, w=2)
text(d, (990, 528), "6. OUTCOME", F_TAG, BLUE)
text(d, (990, 550), "Manager as partner", F_H)
text(d, (990, 588), "- Concrete attendees, learnings, commitments.", F_S)
text(d, (990, 612), "- Every claim traceable back to a meeting / email.", F_S)
text(d, (990, 636), "- 'My plan to act' converts each owned action into", F_S)
text(d, (990, 656), "  next step / by when / who I need.", F_S, MUTED)
text(d, (990, 686), "- Pre-frames the ask before manager 1:1.", F_S)
text(d, (990, 710), "- Reusable across the CxG team (same install command).", F_S)
text(d, (990, 750), "gh extension install ajay4may/gh-manager-brief", F_B, BLUE)

arrow(d, 920, 655, 970, 655, color=BLUE, w=3)

# Footer
text(d, (50, 920), "Mode default: WorkIQ on. Use --no-workiq for sensitive events (CAB, customer meetings) to operate on local files only.",
     F_S, MUTED)
text(d, (50, 950), "Privacy: no third-party APIs. Briefs are local files; user always reviews and sends.",
     F_S, MUTED)

img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT}")
