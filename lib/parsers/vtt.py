"""Minimal Teams .vtt parser — flattens to '<speaker>: <text>' per cue."""
import re
from pathlib import Path


_TS = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")


def parse_vtt(path: Path) -> str:
    out = []
    speaker = ""
    text_buf = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line == "WEBVTT" or _TS.match(line) or line.isdigit():
            if text_buf:
                out.append(f"{speaker + ': ' if speaker else ''}{' '.join(text_buf).strip()}")
                text_buf = []
                speaker = ""
            continue
        m = re.match(r"^<v\s+([^>]+)>(.*)$", line)
        if m:
            speaker = m.group(1).strip()
            rest = m.group(2).strip()
            if rest:
                text_buf.append(re.sub(r"</?v[^>]*>", "", rest))
        else:
            text_buf.append(re.sub(r"</?v[^>]*>", "", line))
    if text_buf:
        out.append(f"{speaker + ': ' if speaker else ''}{' '.join(text_buf).strip()}")
    return "\n".join(out)
