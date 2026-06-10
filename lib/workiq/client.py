"""WorkIQ client — wraps `workiq.cmd ask` and tracks provenance per query."""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class WorkIQUnavailable(Exception):
    pass


@dataclass
class Source:
    """A WorkIQ provenance record — one per call."""
    sid: int          # short id used as footnote ref
    label: str        # human-readable: "WorkIQ: <question>"
    response: str     # full response text


class WorkIQClient:
    def __init__(self, workiq_cmd: str, fixture_dir: Optional[str] = None, timeout: int = 90):
        self.workiq_cmd = workiq_cmd
        self.fixture_dir = Path(fixture_dir) if fixture_dir else None
        self.timeout = timeout
        self.sources: List[Source] = []
        self._next_sid = 1

        if self.fixture_dir:
            if not self.fixture_dir.exists():
                raise WorkIQUnavailable(f"fixture dir not found: {self.fixture_dir}")
            return
        # real WorkIQ — verify the binary exists
        if not Path(self.workiq_cmd).exists():
            raise WorkIQUnavailable(f"workiq cmd not found at {self.workiq_cmd}")

    def ask(self, question: str, fixture_key: Optional[str] = None) -> str:
        """Run a WorkIQ query (or load a fixture) and record the source."""
        if self.fixture_dir is not None:
            key = fixture_key or _slug(question)
            fpath = self.fixture_dir / f"{key}.txt"
            if not fpath.exists():
                raise WorkIQUnavailable(f"fixture not found: {fpath}")
            text = fpath.read_text(encoding="utf-8")
        else:
            try:
                proc = subprocess.run(
                    [self.workiq_cmd, "ask", "-q", question],
                    capture_output=True, text=True, timeout=self.timeout,
                    shell=False,
                )
            except FileNotFoundError as e:
                raise WorkIQUnavailable(str(e))
            except subprocess.TimeoutExpired:
                raise WorkIQUnavailable(f"WorkIQ query timed out after {self.timeout}s")
            text = (proc.stdout or "").strip()
            if proc.returncode != 0 and not text:
                err = (proc.stderr or "").strip()[:300]
                raise WorkIQUnavailable(f"workiq exit {proc.returncode}: {err}")

        src = Source(sid=self._next_sid, label=f"WorkIQ: {question}", response=text)
        self.sources.append(src)
        self._next_sid += 1
        return text

    def cite(self) -> str:
        """Footnote marker for the most recent source."""
        if not self.sources:
            return ""
        return f"[^wq{self.sources[-1].sid}]"


def _slug(s: str) -> str:
    s = "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")
    return s[:80]
