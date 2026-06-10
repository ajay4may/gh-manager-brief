"""Generate the architecture diagram PNG for gh-manager-brief."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).parent / "architecture-diagram.png"

W, H = 1600, 900
BG = (250, 250, 252)
INK = (30, 30, 36)
MUTED = (110, 110, 120)
ACCENT = (37, 99, 235)
ACCENT_SOFT = (219, 234, 254)
GREEN = (16, 163, 74)
GREEN_SOFT = (220, 252, 231)
ORANGE = (234, 88, 12)
ORANGE_SOFT = (255, 237, 213)
GREY_SOFT = (243, 244, 246)


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def rounded_box(draw, xy, fill, outline, radius=14, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, s, font, fill=INK, anchor="lt"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def arrow(draw, x1, y1, x2, y2, color=MUTED, width=3):
    import math
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    ah = 14
    p1 = (x2 - ah * math.cos(angle - math.pi / 7), y2 - ah * math.sin(angle - math.pi / 7))
    p2 = (x2 - ah * math.cos(angle + math.pi / 7), y2 - ah * math.sin(angle + math.pi / 7))
    draw.polygon([(x2, y2), p1, p2], fill=color)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

f_title = load_font(40, bold=True)
f_h = load_font(22, bold=True)
f_b = load_font(18)
f_s = load_font(15)
f_tag = load_font(13, bold=True)

text(d, (60, 40), "gh manager-brief - Architecture", f_title, INK)
text(d, (60, 92), "End-of-Day-3 personalized manager briefs, generated and optionally posted as GitHub issues.",
     f_b, MUTED)

# Capture
rounded_box(d, (60, 170, 360, 320), GREEN_SOFT, GREEN)
text(d, (80, 188), "1. CAPTURE", f_tag, GREEN)
text(d, (80, 212), "Attendee responses", f_h)
text(d, (80, 248), "- Google Form / Discussion", f_s)
text(d, (80, 270), "- Self-service CSV template", f_s)
text(d, (80, 292), "- Facilitator interview", f_s)

# CSV
rounded_box(d, (430, 200, 700, 290), GREY_SOFT, MUTED)
text(d, (445, 215), "attendees.csv", f_h)
text(d, (445, 248), "handle, name, manager_email,", f_s, MUTED)
text(d, (445, 268), "learned, built, committing, ask", f_s, MUTED)

arrow(d, 360, 245, 430, 245, color=GREEN)

# Extension
rounded_box(d, (770, 170, 1180, 360), ACCENT_SOFT, ACCENT, radius=16, width=3)
text(d, (790, 188), "2. EXTENSION", f_tag, ACCENT)
text(d, (790, 212), "gh manager-brief", f_h)

rounded_box(d, (790, 252, 970, 332), (255, 255, 255), ACCENT, radius=10, width=1)
text(d, (805, 265), "Parse CSV", f_s, INK)
text(d, (805, 287), "(bash entry script)", f_s, MUTED)
text(d, (805, 309), "Per-attendee loop", f_s, INK)

rounded_box(d, (985, 252, 1165, 332), (255, 255, 255), ACCENT, radius=10, width=1)
text(d, (1000, 265), "Render brief", f_s, INK)
text(d, (1000, 287), "(Markdown heredoc)", f_s, MUTED)
text(d, (1000, 309), "Inject event + date", f_s, INK)

arrow(d, 700, 245, 770, 245, color=ACCENT)

# Local output
rounded_box(d, (60, 480, 470, 700), GREY_SOFT, MUTED, radius=14, width=2)
text(d, (80, 498), "3a. LOCAL OUTPUT", f_tag, MUTED)
text(d, (80, 522), "out/<handle>.md", f_h)
text(d, (80, 558), "One Markdown brief per attendee:", f_s, MUTED)
text(d, (80, 582), "- What I learned", f_s)
text(d, (80, 604), "- What I built", f_s)
text(d, (80, 626), "- What I'm committing to", f_s)
text(d, (80, 648), "- How my manager can help", f_s)
text(d, (80, 672), "Attendee forwards to manager.", f_s, MUTED)

# Issues
rounded_box(d, (530, 480, 940, 700), ORANGE_SOFT, ORANGE, radius=14, width=2)
text(d, (550, 498), "3b. OPTIONAL: --post-issue", f_tag, ORANGE)
text(d, (550, 522), "GitHub Issues", f_h)
text(d, (550, 558), "Posts each brief as an issue:", f_s, MUTED)
text(d, (550, 582), "- Assigned to attendee (@handle)", f_s)
text(d, (550, 604), "- Labeled 'manager-brief'", f_s)
text(d, (550, 626), "- Tracked in event repo", f_s)
text(d, (550, 648), "Becomes a 30-day accountability", f_s, MUTED)
text(d, (550, 670), "checkpoint with the manager.", f_s, MUTED)

# Outcome
rounded_box(d, (1000, 480, 1530, 700), ACCENT_SOFT, ACCENT, radius=14, width=2)
text(d, (1020, 498), "4. OUTCOME", f_tag, ACCENT)
text(d, (1020, 522), "Manager as partner", f_h)
text(d, (1020, 558), "- Concrete commitments, not vague", f_s)
text(d, (1020, 580), "  'I learned a lot'.", f_s, MUTED)
text(d, (1020, 608), "- Specific ask manager can act on.", f_s)
text(d, (1020, 636), "- 30-day check-in is pre-scheduled,", f_s)
text(d, (1020, 658), "  not awkward.", f_s, MUTED)

arrow(d, 870, 360, 270, 480, color=MUTED)
arrow(d, 975, 360, 735, 480, color=ORANGE)
arrow(d, 940, 590, 1000, 590, color=ACCENT, width=2)

# gh API note
rounded_box(d, (1220, 200, 1530, 290), GREY_SOFT, MUTED, radius=12)
text(d, (1240, 215), "gh issue create", f_h)
text(d, (1240, 248), "Calls GitHub REST API via gh", f_s, MUTED)
text(d, (1240, 268), "auth (no token wrangling).", f_s, MUTED)
arrow(d, 1180, 245, 1220, 245, color=ACCENT)

text(d, (60, 830), "Built as a 'gh extension' (script-based, bash). Cross-platform via Git Bash on Windows.",
     f_s, MUTED)
text(d, (60, 855), "Distribution: push to GitHub as 'gh-manager-brief' repo, then: gh extension install <org>/gh-manager-brief",
     f_s, MUTED)

img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT}")
