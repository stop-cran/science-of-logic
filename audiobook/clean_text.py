"""Convert a synopsis Markdown file into clean narration text.

The synopsis installments use a dense Markdown vocabulary: a single-``*…*``
abstract with nested ``**bold**`` terms and ``(*German*)`` glosses, Roman-numeral
section headings, ``§NN`` cross-references, en-dash ranges, plain-text math
(``*A = A*``, ``*+A*``, ``*−A*``), bullet lists, and ``[text](url)`` links.

This module strips all of that decoration and spells out the handful of symbols
that a text-to-speech engine would otherwise vocalize awkwardly, so the audio
never contains stray ``*``, ``#``, ``-``, ``§`` or a mispronounced Roman numeral.

The public entry point is :func:`parse_markdown`, which returns an ordered list
of :class:`Segment` objects (``kind`` is ``"title"`` or ``"para"``). Keeping the
title/paragraph structure lets the chunker insert structural pauses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Segment:
    """A narration unit: a heading (``title``) or a body paragraph (``para``)."""

    kind: str  # "title" | "para"
    text: str


# --- Roman numerals (section references such as "(VIII)") -------------------

_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_to_int(s: str) -> int | None:
    """Return the integer value of a Roman numeral, or ``None`` if invalid."""
    s = s.upper()
    if not s or any(ch not in _ROMAN_VALUES for ch in s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        val = _ROMAN_VALUES[ch]
        total += -val if val < prev else val
        prev = max(prev, val)
    # Reject non-canonical forms (e.g. "IIII") by round-tripping.
    return total if 1 <= total <= 39 else None


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_HR_RE = re.compile(r"^\s*([-*_])\1{2,}\s*$")
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
_ROMAN_PREFIX_RE = re.compile(r"^[IVXLCDM]+\.\s+", re.IGNORECASE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_IMG_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_PAREN_ROMAN_RE = re.compile(r"\(([IVXLCDM]+)\)")


def _spell_paren_roman(match: re.Match) -> str:
    n = _roman_to_int(match.group(1))
    return f"part {n}" if n is not None else match.group(0)


def clean_inline(text: str) -> str:
    """Strip inline Markdown and spell out symbols within a single string."""
    # Images before links (image alt text is dropped entirely).
    text = _IMG_RE.sub("", text)
    text = _LINK_RE.sub(r"\1", text)
    # Emphasis and code markers. The corpus uses * and ** (never _ emphasis),
    # so removing every * and backtick is safe and also clears *A = A*, *+A*.
    text = text.replace("**", "").replace("*", "").replace("`", "")
    # Section sign: ranges first ("§17–§20" -> "section 17 to 20"), then singles.
    text = re.sub(r"§\s*(\d+)\s*[–—-]\s*§\s*(\d+)", r"section \1 to \2", text)
    text = re.sub(r"§\s*(\d+)", r"section \1", text)
    text = text.replace("§", "section ")
    # Parenthetical Roman-numeral references, e.g. "(VIII)" -> "part 8".
    text = _PAREN_ROMAN_RE.sub(_spell_paren_roman, text)
    # Plain-text math used in the corpus.
    text = text.replace("²", " squared").replace("³", " cubed")
    text = text.replace("·", " times ").replace("×", " times ")
    text = text.replace("∝", " is proportional to ")
    text = text.replace("→", " to ")
    text = re.sub(r"\s=\s", " equals ", text)
    text = re.sub(r"(?<![A-Za-z0-9])\+(?=[A-Za-z])", "plus ", text)
    text = re.sub(r"(?<![A-Za-z0-9])[−–-](?=[A-Za-z]\b)", "minus ", text)
    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_heading(text: str) -> str:
    """Drop a leading Roman-numeral enumerator from a section heading."""
    return clean_inline(_ROMAN_PREFIX_RE.sub("", text))


def parse_markdown(md: str) -> list[Segment]:
    """Parse synopsis Markdown into an ordered list of narration segments."""
    segments: list[Segment] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            para = clean_inline(" ".join(buffer))
            if para:
                segments.append(Segment("para", para))
            buffer.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if _HR_RE.match(line):
            flush()
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            body = heading.group(2)
            text = clean_inline(body) if level == 1 else _clean_heading(body)
            if text:
                segments.append(Segment("title", text))
            continue
        bullet = _BULLET_RE.match(line)
        ordered = _ORDERED_RE.match(line)
        if bullet or ordered:
            flush()
            item = (bullet or ordered).group(1)
            text = clean_inline(item)
            if text:
                segments.append(Segment("para", text))
            continue
        buffer.append(line.strip())

    flush()
    return segments


def readme_prose_segments(segments: list[Segment]) -> list[Segment]:
    """Keep only the narratable prose of the README.

    Retains the top-level title, the introductory paragraph(s) before the first
    section heading, and the "How to Read" heading with its paragraph(s). Skips
    the Section I/II/III headings, the numbered table-of-contents entries, and
    the "Essays" list — all of which are link catalogues, not prose.
    """
    out: list[Segment] = []
    i = 0
    n = len(segments)

    # Title + intro paragraphs, up to the first non-intro heading.
    if i < n and segments[i].kind == "title":
        out.append(segments[i])
        i += 1
    while i < n and segments[i].kind == "para":
        out.append(segments[i])
        i += 1

    # "How to Read" heading and its paragraphs.
    for j in range(i, n):
        if segments[j].kind == "title" and segments[j].text.lower().startswith("how to read"):
            out.append(segments[j])
            k = j + 1
            while k < n and segments[k].kind == "para":
                out.append(segments[k])
                k += 1
            break

    return out
