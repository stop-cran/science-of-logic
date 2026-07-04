"""Split cleaned narration segments into TTS-sized chunks.

The Azure real-time text-to-speech endpoint caps each request at 2,000
characters and 10 minutes of audio, so long paragraphs must be split — but
*never* mid-sentence, which would corrupt intonation. This module keeps whole
paragraphs together when they fit under a conservative budget, and otherwise
splits them at sentence boundaries, packing sentences greedily.

Each :class:`Chunk` carries a ``pre_pause_ms`` hint so the synthesizer can insert
a natural silence before it (longer before a section title, shorter between the
sub-parts of one paragraph).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from clean_text import Segment

# Conservative budget: well under the 2,000-character hard limit, leaving room
# for the fact that a budget-sized chunk is still only ~2 minutes of audio.
DEFAULT_BUDGET = 1800

DEFAULT_PAUSES = {
    "title": 700,  # before a section heading
    "para": 350,   # before a new paragraph
    "cont": 140,   # between the sub-parts of one split paragraph
}

# Abbreviations that end in a period but do not end a sentence.
_ABBREV = {
    "mr", "mrs", "ms", "dr", "st", "vs", "etc", "e.g", "i.e", "cf", "no",
    "fig", "ch", "pp", "vol", "al", "jr", "sr", "ca", "cap", "esp",
}


@dataclass
class Chunk:
    text: str
    pre_pause_ms: int
    is_title: bool


# A sentence boundary is whitespace after terminal punctuation, optionally
# followed by a closing quote/paren/bracket. Python's re has no variable-width
# lookbehind, so two fixed-width lookbehinds are alternated — this catches
# boundaries like `..." But` where the char before the space is the quote, not
# the period (a recurring pattern here: quoted objection followed by a rebuttal).
_SENTENCE_END_RE = re.compile(
    r"(?:(?<=[.!?])|(?<=[.!?][\"'\u2019\u201d)\]\u00bb]))\s+"
)


def _looks_like_nonfinal(fragment: str) -> bool:
    """True if ``fragment`` ends in a period that is not a sentence end."""
    if fragment.endswith(("!", "?")):
        return False
    tokens = fragment.split()
    if not tokens:
        return False
    last = tokens[-1]
    core = last.rstrip('.!?"”»)\'')
    lower = core.lower()
    if lower in _ABBREV:
        return True
    # Single-letter initial ("G.", "W.", "F.") or a trailing digit (decimal).
    if re.fullmatch(r"[A-Za-z]", core):
        return True
    if re.search(r"\d$", core):
        return True
    return False


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, rejoining abbreviation/initial false splits."""
    fragments = _SENTENCE_END_RE.split(text.strip())
    out: list[str] = []
    for frag in fragments:
        if not frag:
            continue
        if out and _looks_like_nonfinal(out[-1]):
            out[-1] = out[-1] + " " + frag
        else:
            out.append(frag)
    return out


def _hard_split(text: str, budget: int) -> list[str]:
    """Last-resort split of an over-long sentence at a word boundary."""
    pieces: list[str] = []
    while len(text) > budget:
        cut = text.rfind(" ", 0, budget)
        if cut <= 0:
            cut = budget
        pieces.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        pieces.append(text)
    return pieces


def split_paragraph(text: str, budget: int = DEFAULT_BUDGET) -> list[str]:
    """Split one paragraph into <=budget parts without breaking sentences."""
    if len(text) <= budget:
        return [text]
    parts: list[str] = []
    current = ""
    for sentence in split_sentences(text):
        for piece in (_hard_split(sentence, budget) if len(sentence) > budget else [sentence]):
            if not current:
                current = piece
            elif len(current) + 1 + len(piece) <= budget:
                current += " " + piece
            else:
                parts.append(current)
                current = piece
    if current:
        parts.append(current)
    return parts


def chunk_segments(
    segments: list[Segment],
    budget: int = DEFAULT_BUDGET,
    pauses: dict | None = None,
) -> list[Chunk]:
    """Turn segments into synthesis chunks with structural pause hints."""
    pauses = pauses or DEFAULT_PAUSES
    chunks: list[Chunk] = []
    first = True
    for seg in segments:
        if seg.kind == "title":
            chunks.append(Chunk(seg.text, 0 if first else pauses["title"], True))
        else:
            parts = split_paragraph(seg.text, budget)
            for idx, part in enumerate(parts):
                if idx == 0:
                    pre = 0 if first else pauses["para"]
                else:
                    pre = pauses["cont"]
                chunks.append(Chunk(part, pre, False))
        first = False
    return chunks
