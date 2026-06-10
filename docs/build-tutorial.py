"""
build-tutorial.py - generate a narrated tutorial MP4 for gh-manager-brief.

Pipeline:
  1. Define N slides (title + bullets + narration text).
  2. For each slide:
     - Render PNG using PIL.
     - Synthesize narration WAV using pyttsx3 (Windows SAPI).
  3. Use ffmpeg (from imageio_ffmpeg) to:
     - Build per-slide MP4 (image x narration duration + audio).
     - Concatenate all per-slide MP4s into tutorial.mp4.
"""
import os
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
BG = (15, 23, 42)         # slate-900
INK = (241, 245, 249)     # slate-100
MUTED = (148, 163, 184)   # slate-400
ACCENT = (96, 165, 250)   # blue-400
GREEN = (74, 222, 128)
ORANGE = (251, 146, 60)
CARD = (30, 41, 59)       # slate-800


def font(size, bold=False):
    for c in [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = font(72, bold=True)
F_SUB = font(36)
F_H = font(46, bold=True)
F_B = font(32)
F_CODE = font(28)
F_TAG = font(24, bold=True)
F_FOOT = font(22)


def draw_chrome(d, step_label):
    # top bar
    d.rectangle((0, 0, W, 8), fill=ACCENT)
    # footer
    d.text((60, H - 48), "gh manager-brief - end-of-Day-3 manager briefs",
           font=F_FOOT, fill=MUTED)
    d.text((W - 60, H - 48), step_label, font=F_FOOT, fill=MUTED, anchor="rt")


def render_title_slide(path, title, subtitle, step_label):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d, step_label)
    d.text((W // 2, H // 2 - 80), title, font=F_TITLE, fill=INK, anchor="mm")
    d.text((W // 2, H // 2 + 40), subtitle, font=F_SUB, fill=ACCENT, anchor="mm")
    img.save(path, "PNG")


def render_content_slide(path, heading, bullets, step_label, code=None, tag=None, tag_color=ACCENT):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d, step_label)

    if tag:
        d.text((90, 90), tag, font=F_TAG, fill=tag_color)
    d.text((90, 130), heading, font=F_H, fill=INK)

    y = 240
    for b in bullets:
        d.ellipse((100, y + 16, 116, y + 32), fill=ACCENT)
        d.text((140, y), b, font=F_B, fill=INK)
        y += 64

    if code:
        # code card
        card_top = y + 30
        card_h = 56 + 44 * len(code)
        d.rounded_rectangle((90, card_top, W - 90, card_top + card_h),
                            radius=14, fill=CARD, outline=ACCENT, width=2)
        for i, line in enumerate(code):
            d.text((120, card_top + 28 + 44 * i), line, font=F_CODE, fill=INK)

    img.save(path, "PNG")


# ---------- Slide deck ----------
SLIDES = [
    {
        "type": "title",
        "title": "gh manager-brief",
        "subtitle": "Turn workshop attendees into accountable owners",
        "step": "Intro",
        "narration": (
            "Welcome. This is a quick walkthrough of g h manager dash brief, "
            "a GitHub CLI extension that generates personalized end of day three briefs "
            "for every workshop attendee to send to their manager."
        ),
    },
    {
        "type": "content",
        "tag": "THE PROBLEM",
        "heading": "Why managers don't help",
        "bullets": [
            "Attendees leave excited but vague.",
            "The follow-up chat feels open-ended.",
            "Managers default to 'sounds great'.",
            "ROI from the workshop evaporates in two weeks.",
        ],
        "step": "1. Problem",
        "narration": (
            "Multi day workshops produce excited attendees and vague intentions. "
            "The conversation with their manager feels open ended, so most attendees skip it, "
            "and the value from the workshop evaporates within two weeks."
        ),
    },
    {
        "type": "content",
        "tag": "THE FIX",
        "heading": "A one-page brief, generated for them",
        "bullets": [
            "What I learned",
            "What I built",
            "What I'm committing to (next 30 days)",
            "How my manager can help",
        ],
        "step": "2. Solution",
        "narration": (
            "The extension generates a one page brief with a fixed shape. "
            "What I learned, what I built, what I am committing to over the next thirty days, "
            "and exactly how my manager can help. "
            "It reads in under two minutes and removes the awkwardness."
        ),
    },
    {
        "type": "content",
        "tag": "STEP 1",
        "heading": "Install the extension",
        "bullets": [
            "Pushed to GitHub as 'gh-manager-brief'.",
            "Anyone installs with one command.",
        ],
        "code": [
            "$ gh extension install your-org/gh-manager-brief",
            "$ gh manager-brief help",
        ],
        "step": "3. Install",
        "narration": (
            "To install, push the extension as a repo named g h dash manager dash brief, "
            "then anyone runs g h extension install with your org slash that repo. "
            "From then on it is available as a g h subcommand."
        ),
    },
    {
        "type": "content",
        "tag": "STEP 2",
        "heading": "Collect attendee responses into a CSV",
        "bullets": [
            "Columns: handle, name, manager_email,",
            "         learned, built, committing, ask.",
            "Source: form, discussion, or interview.",
        ],
        "code": [
            "ajay4may,Ajay Singh,manager@example.com,",
            "\"How RAG works\",\"Triage agent\",",
            "\"Pilot with 2 teams\",\"Intro to SalesOps lead\"",
        ],
        "step": "4. Capture",
        "narration": (
            "At the end of day three, capture responses from each attendee into a simple CSV. "
            "Seven columns: handle, name, manager email, learned, built, committing, and ask. "
            "Use a form, a GitHub Discussion, or a quick interview, whatever fits your workshop."
        ),
    },
    {
        "type": "content",
        "tag": "STEP 3",
        "heading": "Generate the briefs",
        "bullets": [
            "One Markdown file per attendee.",
            "Drops into ./out by default.",
            "Re-runnable; safe to edit and re-run.",
        ],
        "code": [
            "$ gh manager-brief generate \\",
            "    --input attendees.csv \\",
            "    --out ./out \\",
            "    --event \"AI Bootcamp 2026\"",
        ],
        "step": "5. Generate",
        "narration": (
            "Then run g h manager dash brief generate, pointing at the CSV. "
            "The extension writes one Markdown brief per attendee into the out directory, "
            "ready to forward to their manager."
        ),
    },
    {
        "type": "content",
        "tag": "STEP 4 (optional)",
        "heading": "Post each brief as a GitHub issue",
        "bullets": [
            "Issue is assigned to the attendee.",
            "Labeled 'manager-brief'.",
            "Becomes a 30-day accountability checkpoint.",
        ],
        "code": [
            "$ gh manager-brief generate \\",
            "    --input attendees.csv \\",
            "    --post-issue acme/ai-bootcamp",
        ],
        "step": "6. Post issues",
        "tag_color": ORANGE,
        "narration": (
            "Optionally, add post dash issue with a repo name. "
            "Each brief is also created as a GitHub issue assigned to the attendee "
            "and labeled manager dash brief. "
            "That issue becomes a durable thirty day accountability checkpoint "
            "the manager can drop into at any time."
        ),
    },
    {
        "type": "content",
        "tag": "OUTCOME",
        "heading": "Manager becomes the partner, not the blocker",
        "bullets": [
            "Concrete commitments, not vague intent.",
            "Specific ask the manager can act on.",
            "No awkward conversation - it's already on paper.",
        ],
        "step": "7. Outcome",
        "narration": (
            "The outcome is simple. Managers see concrete commitments and a specific ask they can act on. "
            "The attendee skips an awkward conversation because the structure is already there. "
            "Managers become accountability partners instead of obstacles."
        ),
    },
    {
        "type": "title",
        "title": "Try it",
        "subtitle": "gh extension install your-org/gh-manager-brief",
        "step": "End",
        "narration": (
            "That is it. Install the extension, point it at your attendee CSV, and ship the briefs. "
            "Thanks for watching."
        ),
    },
]


def synth_voice(text, out_wav):
    """Use pyttsx3 (SAPI) to write a narration WAV."""
    eng = pyttsx3.init()
    eng.setProperty("rate", 175)
    # prefer a female voice if available, else default
    for v in eng.getProperty("voices"):
        if "Zira" in v.name or "Aria" in v.name:
            eng.setProperty("voice", v.id)
            break
    eng.save_to_file(text, str(out_wav))
    eng.runAndWait()
    eng.stop()


def wav_duration_seconds(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def build_slide(i, slide):
    png = BUILD / f"slide_{i:02d}.png"
    wav = BUILD / f"slide_{i:02d}.wav"
    mp4 = BUILD / f"slide_{i:02d}.mp4"

    if slide["type"] == "title":
        render_title_slide(png, slide["title"], slide["subtitle"], slide["step"])
    else:
        render_content_slide(
            png, slide["heading"], slide["bullets"], slide["step"],
            code=slide.get("code"),
            tag=slide.get("tag"),
            tag_color=slide.get("tag_color", ACCENT),
        )

    synth_voice(slide["narration"], wav)

    # Pad WAV duration: add 0.5s silence at end via ffmpeg apad
    dur = wav_duration_seconds(wav) + 0.6
    # Build per-slide MP4: still image for duration, with WAV audio padded
    subprocess.run([
        FFMPEG, "-y", "-loop", "1", "-framerate", "30",
        "-i", str(png),
        "-i", str(wav),
        "-af", "apad=pad_dur=0.6",
        "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(mp4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mp4


def main():
    parts = []
    for i, s in enumerate(SLIDES):
        print(f"building slide {i+1}/{len(SLIDES)}: {s['step']}")
        parts.append(build_slide(i, s))

    concat_file = BUILD / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.as_posix()}'\n")

    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(OUT_MP4),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"wrote {OUT_MP4}")


if __name__ == "__main__":
    main()
