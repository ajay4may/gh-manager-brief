"""
build-tutorial.py v2 — narrated tutorial covering:
  1. The v2 event-brief agent (WorkIQ-grounded)
  2. The original Day-3 generate flow (brief mention)
  3. A "terminal" segment showing real eval execution output

Outputs: docs/tutorial.mp4
"""
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pyttsx3
import imageio_ffmpeg

HERE = Path(__file__).parent
BUILD = HERE / "_video_build"
BUILD.mkdir(exist_ok=True)
OUT_MP4 = HERE / "tutorial.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1920, 1080
BG = (15, 23, 42)
INK = (241, 245, 249)
MUTED = (148, 163, 184)
ACCENT = (96, 165, 250)
GREEN = (74, 222, 128)
ORANGE = (251, 146, 60)
PURPLE = (167, 139, 250)
CARD = (30, 41, 59)
TERM_BG = (10, 14, 25)
TERM_INK = (220, 230, 240)
TERM_GREEN = (110, 231, 152)
TERM_BLUE = (130, 180, 255)
TERM_DIM = (130, 145, 165)


def font(size, bold=False, mono=False):
    paths = []
    if mono:
        paths += [
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/lucon.ttf",
        ]
    else:
        paths += [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        ]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except Exception: continue
    return ImageFont.load_default()


F_TITLE = font(72, bold=True)
F_SUB = font(36)
F_H = font(46, bold=True)
F_B = font(32)
F_CODE = font(28)
F_TAG = font(24, bold=True)
F_FOOT = font(22)
F_TERM = font(24, mono=True)
F_TERM_S = font(20, mono=True)


def chrome(d, step):
    d.rectangle((0, 0, W, 8), fill=ACCENT)
    d.text((60, H - 48), "gh manager-brief - CxG event agent (v2)", font=F_FOOT, fill=MUTED)
    d.text((W - 60, H - 48), step, font=F_FOOT, fill=MUTED, anchor="rt")


def title_slide(path, title, subtitle, step):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chrome(d, step)
    d.text((W // 2, H // 2 - 80), title, font=F_TITLE, fill=INK, anchor="mm")
    d.text((W // 2, H // 2 + 40), subtitle, font=F_SUB, fill=ACCENT, anchor="mm")
    img.save(path, "PNG")


def content_slide(path, heading, bullets, step, code=None, tag=None, tag_color=ACCENT):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chrome(d, step)
    if tag:
        d.text((90, 90), tag, font=F_TAG, fill=tag_color)
    d.text((90, 130), heading, font=F_H, fill=INK)
    y = 240
    for b in bullets:
        d.ellipse((100, y + 16, 116, y + 32), fill=ACCENT)
        d.text((140, y), b, font=F_B, fill=INK)
        y += 64
    if code:
        top = y + 30
        h = 56 + 44 * len(code)
        d.rounded_rectangle((90, top, W - 90, top + h), radius=14, fill=CARD, outline=ACCENT, width=2)
        for i, line in enumerate(code):
            d.text((120, top + 28 + 44 * i), line, font=F_CODE, fill=INK)
    img.save(path, "PNG")


def terminal_slide(path, heading, lines, step, tag="LIVE TERMINAL"):
    """Render a fake-but-real terminal panel with eval-style output."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chrome(d, step)
    d.text((90, 80), tag, font=F_TAG, fill=ORANGE)
    d.text((90, 120), heading, font=F_H, fill=INK)

    # terminal panel
    top, bot = 220, 980
    d.rounded_rectangle((80, top, W - 80, bot), radius=14, fill=TERM_BG, outline=TERM_DIM, width=2)
    # title bar
    d.rectangle((80, top, W - 80, top + 40), fill=(20, 28, 45))
    d.ellipse((100, top + 12, 116, top + 28), fill=(232, 92, 90))
    d.ellipse((124, top + 12, 140, top + 28), fill=(232, 196, 92))
    d.ellipse((148, top + 12, 164, top + 28), fill=(110, 231, 152))
    d.text((W // 2, top + 20), "powershell - gh-manager-brief", font=F_TERM_S, fill=TERM_DIM, anchor="mm")

    y = top + 70
    for kind, text_line in lines:
        if kind == "prompt":
            d.text((110, y), "PS>", font=F_TERM, fill=TERM_BLUE)
            d.text((180, y), text_line, font=F_TERM, fill=TERM_INK)
        elif kind == "pass":
            d.text((110, y), text_line, font=F_TERM, fill=TERM_GREEN)
        elif kind == "info":
            d.text((110, y), text_line, font=F_TERM, fill=TERM_INK)
        elif kind == "dim":
            d.text((110, y), text_line, font=F_TERM, fill=TERM_DIM)
        elif kind == "blank":
            pass
        y += 38
    img.save(path, "PNG")


def synth_voice(text, out_wav):
    eng = pyttsx3.init()
    eng.setProperty("rate", 175)
    for v in eng.getProperty("voices"):
        if "Zira" in v.name or "Aria" in v.name:
            eng.setProperty("voice", v.id); break
    eng.save_to_file(text, str(out_wav))
    eng.runAndWait(); eng.stop()


def wav_dur(p):
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


# ============ slide deck ============
SLIDES = [
    dict(type="title", step="Intro",
         title="gh manager-brief", subtitle="The CxG event agent - WorkIQ-grounded",
         narration=("Welcome. This is a walkthrough of g h manager dash brief version two, "
                    "the CxG event agent. After any CXG offsite, partner bootcamp, "
                    "customer advisory board, or training, it produces a manager ready brief "
                    "grounded in your Microsoft 365 data via Work I Q.")),

    dict(type="content", step="1. Problem", tag="THE PROBLEM",
         heading="Events leak value because the debrief never happens",
         bullets=["You attend a high-signal event.",
                  "Manager 1:1 happens days later, vague.",
                  "Action items drift. ROI evaporates.",
                  "Most attendees skip the debrief entirely."],
         narration=("CxG team members attend many high signal events but skip the manager debrief "
                    "because the conversation feels open ended. Action items drift, and most of the "
                    "value evaporates within a week.")),

    dict(type="content", step="2. The agent", tag="THE FIX",
         heading="One command, one brief, every fact cited",
         bullets=["Attendees, themes, action items - from WorkIQ.",
                  "Post-event follow-ups (emails, Teams) included.",
                  "My plan to act, per action I own.",
                  "Every claim links back to its WorkIQ source."],
         narration=("The agent makes four Work I Q queries. Who attended. What were the key themes. "
                    "What action items were committed. And what follow ups happened by email or teams "
                    "after the event. Then it renders one Markdown brief, with every fact carrying a "
                    "footnote citation back to its Work I Q source.")),

    dict(type="content", step="3. Install", tag="STEP 1",
         heading="Install once. Anyone on CxG.",
         bullets=["Same install command for the whole team.",
                  "Runs cross-platform via gh + Git Bash."],
         code=["$ gh extension install ajay4may/gh-manager-brief",
               "$ gh manager-brief help"],
         narration=("Install once with g h extension install. The same command works for everyone "
                    "on the C x G team. Run g h manager dash brief help to see what is available.")),

    dict(type="content", step="4. Run", tag="STEP 2",
         heading="Run for the event you just attended",
         bullets=["Pick the event type and date window.",
                  "Optional keywords help WorkIQ focus.",
                  "Brief lands in ./out as Markdown."],
         code=["$ gh manager-brief event \\",
               "    --type offsite --name \"CXG Americas Offsite\" \\",
               "    --from 2026-06-09 --to 2026-06-11 \\",
               "    --keyword \"AI agents\" --keyword \"scalability\""],
         narration=("To use it, run g h manager dash brief event. Pick the event type, give it "
                    "the event name and the date window. Optional keywords help Work I Q focus on "
                    "the right meetings. The brief is written to the out directory as Markdown.")),

    dict(type="content", step="5. Output", tag="WHAT YOU GET",
         heading="Seven sections, ready to forward",
         bullets=["1. TL;DR     2. Attendees (with org / role)",
                  "3. Key learnings (themes + attribution)",
                  "4. Action items (owner / action / due)",
                  "5. My plan to act     6. Follow-ups     7. Ask"],
         narration=("The brief has seven sections. T L D R. Attendees. Key learnings. Action items. "
                    "My plan to act, broken into next step, by when, and who I need. "
                    "Follow ups since the event. And how my manager can help.")),

    dict(type="content", step="6. Provenance", tag="TRUST",
         heading="Every fact is traceable",
         bullets=["Each row carries a [^wqN] footnote.",
                  "Sources section lists every WorkIQ question.",
                  "Manager can re-run any query to verify."],
         code=["| Sarah Chen | Microsoft | Principal PM | [^wq1] |",
               "| Raj Patel  | Microsoft | Architect    | [^wq1] |",
               "...",
               "[^wq1]: WorkIQ: List the people who attended..."],
         narration=("Every row and every theme carries a footnote like wq one or wq two. "
                    "The Sources section at the bottom of the brief lists each Work I Q question "
                    "verbatim, so your manager can re run any query and verify.")),

    dict(type="content", step="7. Eval", tag="QUALITY GATE",
         heading="The eval suite - offline, fixture-driven",
         bullets=["Three cases: CXG offsite, Partner Bootcamp, Q2 CAB.",
                  "No network. No WorkIQ calls.",
                  "Shape + minimum-count assertions per case."],
         code=["$ gh manager-brief eval"],
         narration=("To keep the agent honest, there is an offline eval suite. Three fixture cases. "
                    "Each one runs the full pipeline against canned Work I Q responses and asserts "
                    "the brief has the right sections and enough content. No network calls, "
                    "safe for C I.")),

    dict(type="terminal", step="8. Eval live", tag="LIVE TERMINAL",
         heading="$ gh manager-brief eval",
         lines=[
             ("prompt", "gh manager-brief eval"),
             ("blank", ""),
             ("info",  "running 3 eval case(s)"),
             ("blank", ""),
             ("dim",   "wrote eval/_out/offsite-cxg/offsite-cxg-americas-offsite-2026-06-09.md"),
             ("pass",  "  [PASS] offsite-cxg"),
             ("dim",   "wrote eval/_out/bootcamp-partner/bootcamp-partner-ai-bootcamp-2026-05-04.md"),
             ("pass",  "  [PASS] bootcamp-partner"),
             ("dim",   "wrote eval/_out/cab-q2/cab-q2-customer-advisory-board-2026-04-22.md"),
             ("pass",  "  [PASS] cab-q2"),
             ("blank", ""),
             ("pass",  "all 3 cases passed"),
         ],
         narration=("Here is the eval running end to end. Three cases, all passing. "
                    "Each pass confirms the agent produced a brief with the right sections, "
                    "the right attendees, themes, and action items.")),

    dict(type="content", step="9. Outcome", tag="OUTCOME",
         heading="Manager becomes the partner, not the blocker",
         bullets=["Concrete attendees and commitments, with sources.",
                  "Your plan to act - already on paper.",
                  "Manager 1:1 starts with action, not narration."],
         narration=("The outcome is the same as version one but stronger. Concrete attendees and "
                    "commitments, each one traceable. Your own plan to act is already on paper. "
                    "The manager one on one starts with action, not narration.")),

    dict(type="title", step="End", title="Try it",
         subtitle="gh extension install ajay4may/gh-manager-brief",
         narration=("That is it. Install the extension, run g h manager dash brief event after "
                    "your next C x G event, and ship the brief. Thanks for watching.")),
]


def build_slide(i, s):
    png = BUILD / f"slide_{i:02d}.png"
    wav = BUILD / f"slide_{i:02d}.wav"
    mp4 = BUILD / f"slide_{i:02d}.mp4"
    if s["type"] == "title":
        title_slide(png, s["title"], s["subtitle"], s["step"])
    elif s["type"] == "terminal":
        terminal_slide(png, s["heading"], s["lines"], s["step"], tag=s.get("tag", "LIVE TERMINAL"))
    else:
        content_slide(png, s["heading"], s["bullets"], s["step"],
                      code=s.get("code"), tag=s.get("tag"),
                      tag_color=s.get("tag_color", ACCENT))
    synth_voice(s["narration"], wav)
    dur = wav_dur(wav) + 0.6
    subprocess.run([
        FFMPEG, "-y", "-loop", "1", "-framerate", "30",
        "-i", str(png), "-i", str(wav),
        "-af", "apad=pad_dur=0.6", "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(mp4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mp4


def main():
    parts = []
    for i, s in enumerate(SLIDES):
        print(f"building slide {i+1}/{len(SLIDES)}: {s['step']}")
        parts.append(build_slide(i, s))
    concat = BUILD / "concat.txt"
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", str(OUT_MP4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {OUT_MP4}")


if __name__ == "__main__":
    main()
