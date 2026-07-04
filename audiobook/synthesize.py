"""Generate audiobook MP3s for the synopsis using Azure MAI-Voice-2.

Pipeline per file: clean Markdown -> chunk under the TTS limit -> synthesize each
chunk as PCM via the real-time Speech endpoint (Microsoft Entra / AAD auth) ->
stitch the PCM losslessly with controlled silences -> encode one MP3.

Synthesizing PCM and encoding a single MP3 at the end (rather than concatenating
per-chunk MP3s) avoids MP3 frame-boundary gaps, so the result is seamless.

Authentication uses your Azure login (``az login`` / Azure CLI credential); no
keys are used or stored. The endpoint and voice can be overridden via the
``SOL_TTS_ENDPOINT`` / ``SOL_TTS_VOICE`` environment variables or CLI flags.

Examples
--------
    python synthesize.py --dry-run --all           # inspect text prep, no API
    python synthesize.py --all                      # README (prose) + 01..21
    python synthesize.py ../synopsis/21-*.md        # a single installment
"""

from __future__ import annotations

import argparse
import io
import os
import random
import re
import subprocess
import sys
import time
import wave
import xml.sax.saxutils as saxutils
from pathlib import Path

import requests

from chunk_text import Chunk, chunk_segments
from clean_text import parse_markdown, readme_prose_segments

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNOPSIS_DIR = REPO_ROOT / "synopsis"
README = REPO_ROOT / "README.md"

# The TTS endpoint is user/resource-specific (a fork will use a different Azure
# AI Foundry resource), so it is never hardcoded. It is resolved, in order, from
# an explicit URL, an explicit resource name, $SOL_TTS_ENDPOINT, or
# $SOL_TTS_RESOURCE. See .github/skills/synopsis-audiobook/SKILL.md.
ENDPOINT_TEMPLATE = "https://{resource}.cognitiveservices.azure.com/tts/cognitiveservices/v1"


def resolve_endpoint(resource: str | None = None, endpoint: str | None = None) -> str | None:
    endpoint = endpoint or os.environ.get("SOL_TTS_ENDPOINT")
    if endpoint:
        return endpoint
    resource = resource or os.environ.get("SOL_TTS_RESOURCE")
    if resource:
        return ENDPOINT_TEMPLATE.format(resource=resource)
    return None


ENDPOINT = resolve_endpoint()
VOICE = os.environ.get("SOL_TTS_VOICE", "en-US-Ethan:MAI-Voice-2")
SCOPE = "https://cognitiveservices.azure.com/.default"

PCM_FORMAT = "riff-24khz-16bit-mono-pcm"
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2  # bytes (16-bit)
HEAD_SILENCE_MS = 300
TAIL_SILENCE_MS = 600


# --- authentication ---------------------------------------------------------

def make_token_provider():
    """Return a callable that yields a cached, auto-refreshing AAD token."""
    from azure.identity import AzureCliCredential, DefaultAzureCredential

    try:
        credential = AzureCliCredential(process_timeout=30)
        credential.get_token(SCOPE)  # validate up front
    except Exception:
        credential = DefaultAzureCredential(process_timeout=30)

    cache = {"token": None, "expires": 0.0}

    def get_token() -> str:
        if cache["token"] is None or cache["expires"] - time.time() < 300:
            result = credential.get_token(SCOPE)
            cache["token"] = result.token
            cache["expires"] = result.expires_on
        return cache["token"]

    return get_token


# --- SSML + synthesis -------------------------------------------------------

def build_ssml(text: str, voice: str, rate: str | None) -> str:
    inner = saxutils.escape(text)
    if rate:
        inner = f"<prosody rate={saxutils.quoteattr(rate)}>{inner}</prosody>"
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">'
        f"<voice name={saxutils.quoteattr(voice)}>{inner}</voice></speak>"
    )


def _pcm_from_wav(data: bytes) -> bytes:
    with wave.open(io.BytesIO(data), "rb") as wav:
        if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (
            SAMPLE_RATE, 1, SAMPLE_WIDTH,
        ):
            raise RuntimeError(
                f"unexpected PCM format: {wav.getframerate()}Hz "
                f"{wav.getnchannels()}ch {wav.getsampwidth() * 8}bit"
            )
        return wav.readframes(wav.getnframes())


def synth_pcm(
    ssml: str,
    get_token,
    session: requests.Session,
    max_retries: int = 8,
) -> bytes:
    """Synthesize one SSML chunk to raw PCM, with backoff on transient errors.

    The MAI-Voice-2 preview endpoint occasionally returns transient 502/503
    gateway errors ("upstream connect error … protocol error") for tens of
    seconds, so retries use capped exponential backoff with jitter to ride out
    a multi-minute blip rather than failing the whole file.
    """
    headers = {
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": PCM_FORMAT,
        "User-Agent": "science-of-logic-audiobook",
    }
    body = ssml.encode("utf-8")
    for attempt in range(max_retries):
        headers["Authorization"] = "Bearer " + get_token()
        transient = False
        detail = ""
        try:
            resp = session.post(ENDPOINT, headers=headers, data=body, timeout=180)
        except requests.RequestException as exc:
            transient, detail = True, f"network error: {exc}"
        else:
            if resp.status_code == 200:
                return _pcm_from_wav(resp.content)
            transient = resp.status_code in (408, 429, 500, 502, 503, 504)
            detail = f"{resp.status_code} {resp.text[:300]}"
            if not transient:
                raise RuntimeError(f"TTS request failed: {detail}")
            retry_after = resp.headers.get("Retry-After")
        if attempt == max_retries - 1:
            raise RuntimeError(f"TTS request failed after {max_retries} attempts: {detail}")
        # `retry_after` is only assigned on the HTTP-response path; the
        # `not detail.startswith("network")` guard must come first so we never
        # read it on the network-exception path (where it is unset).
        base = float(retry_after) if (not detail.startswith("network") and retry_after) else min(2 ** attempt, 45)
        time.sleep(base * (0.8 + 0.4 * random.random()))
    raise RuntimeError("exhausted retries")


def _silence(ms: int) -> bytes:
    return b"\x00\x00" * int(SAMPLE_RATE * ms / 1000)


def _wrap_wav(pcm: bytes) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)
    return buffer.getvalue()


def _pcm_seconds(pcm: bytes) -> float:
    return len(pcm) / (SAMPLE_RATE * SAMPLE_WIDTH)


# --- encoding ---------------------------------------------------------------

def _ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def encode_mp3(wav_bytes: bytes, out_path: Path, bitrate: str = "128k") -> None:
    # Encode to a temp file and atomically rename on success, so an interrupted
    # encode never leaves a truncated MP3 at the resumable output path (which the
    # skip-if-exists resume logic would then treat as a completed file forever).
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    cmd = [
        _ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "wav", "-i", "pipe:0",
        "-codec:a", "libmp3lame", "-b:a", bitrate,
        str(tmp_path),
    ]
    proc = subprocess.run(cmd, input=wav_bytes, capture_output=True)
    if proc.returncode != 0:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='replace')[:400]}")
    os.replace(tmp_path, out_path)


# --- per-file driver --------------------------------------------------------

def load_chunks(md_path: Path, prose_only: bool) -> list[Chunk]:
    segments = parse_markdown(md_path.read_text(encoding="utf-8"))
    if prose_only:
        segments = readme_prose_segments(segments)
    return chunk_segments(segments)


def synthesize_file(
    md_path: Path,
    out_path: Path,
    get_token,
    voice: str,
    rate: str | None,
    prose_only: bool = False,
    limit_chunks: int | None = None,
) -> float:
    chunks = load_chunks(md_path, prose_only)
    if limit_chunks:
        chunks = chunks[:limit_chunks]
    session = requests.Session()
    pcm = bytearray(_silence(HEAD_SILENCE_MS))
    for index, chunk in enumerate(chunks, 1):
        if chunk.pre_pause_ms:
            pcm += _silence(chunk.pre_pause_ms)
        ssml = build_ssml(chunk.text, voice, rate)
        pcm += synth_pcm(ssml, get_token, session)
        print(
            f"    chunk {index}/{len(chunks)} "
            f"({'title' if chunk.is_title else 'para'}, {len(chunk.text)} chars) ok",
            flush=True,
        )
    pcm += _silence(TAIL_SILENCE_MS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    encode_mp3(_wrap_wav(bytes(pcm)), out_path)
    return _pcm_seconds(bytes(pcm))


# --- narration lint (keeps one-time corpus audits live as the corpus grows) --

_SLASH_RE = re.compile(r"(?<=\w)/(?=\w)")


def narration_lint(chunks) -> tuple[int, int]:
    """Return (stray-pipe chunk count, literal-slash count) for narrated chunks.

    A `|` surviving into a narrated chunk means a prose pipe slipped past
    table-stripping (should be 0). A word/word `/` (e.g. dy/dx, whole/parts) is
    vocalized literally as "slash". These counts anchor a regression trip-wire:
    an unexplained delta vs the SKILL.md baseline means a corpus/code change
    touched narration in a way that should be reviewed. Warnings, not failures.
    """
    pipes = sum(1 for c in chunks if "|" in c.text)
    slashes = sum(len(_SLASH_RE.findall(c.text)) for c in chunks)
    return pipes, slashes


def dry_run_file(md_path: Path, out_path: Path, prose_only: bool) -> tuple[int, int, int, int]:
    chunks = load_chunks(md_path, prose_only)
    total_chars = sum(len(c.text) for c in chunks)
    # Rough planning estimate, calibrated from the measured full-corpus render
    # (~783 narrated characters per minute of audio at this voice and pacing).
    est_minutes = total_chars / 783.0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path = out_path.with_suffix(".txt")
    with txt_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            prefix = "## " if chunk.is_title else ""
            handle.write(prefix + chunk.text + "\n\n")
    pipes, slashes = narration_lint(chunks)
    print(
        f"  {md_path.name}: {len(chunks)} chunks, {total_chars} chars, "
        f"~{est_minutes:.1f} min  ->  {txt_path.name}"
    )
    if pipes:
        print(f"    WARN: {pipes} narrated chunk(s) contain a stray '|' (prose pipe / unstripped table)")
    return len(chunks), total_chars, pipes, slashes


# --- input selection --------------------------------------------------------

def resolve_inputs(args) -> list[tuple[Path, Path, bool]]:
    """Return (source_md, output_mp3, prose_only) triples to process."""
    out_dir = Path(args.out_dir)
    jobs: list[tuple[Path, Path, bool]] = []
    if args.all or not args.inputs:
        jobs.append((README, out_dir / "00-readme.mp3", True))
        for md in sorted(SYNOPSIS_DIR.glob("[0-9][0-9]-*.md")):
            jobs.append((md, out_dir / (md.stem + ".mp3"), False))
    else:
        for pattern in args.inputs:
            for md in sorted(Path().glob(pattern)) or [Path(pattern)]:
                prose = md.name.lower() == "readme.md"
                stem = "00-readme" if prose else md.stem
                jobs.append((md, out_dir / (stem + ".mp3"), prose))
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", help="Markdown files/globs (default: --all)")
    parser.add_argument("--all", action="store_true", help="README (prose) + all installments")
    parser.add_argument("--out-dir", default=str(Path(__file__).resolve().parent / "out"))
    parser.add_argument("--voice", default=VOICE)
    parser.add_argument("--resource", default=None, help="Foundry custom-domain resource name (e.g. romanko-exp); or set $SOL_TTS_RESOURCE")
    parser.add_argument("--endpoint", default=None, help="full TTS endpoint URL; or set $SOL_TTS_ENDPOINT")
    parser.add_argument("--rate", default=None, help='prosody rate; pass with = to avoid argparse, e.g. --rate=-5%% or --rate=0.95')
    parser.add_argument("--dry-run", action="store_true", help="clean+chunk only; write .txt, no API calls")
    parser.add_argument("--limit-chunks", type=int, default=None, help="synthesize only the first N chunks (smoke test)")
    parser.add_argument("--force", action="store_true", help="re-render even if the output MP3 already exists")
    args = parser.parse_args()

    global ENDPOINT
    ENDPOINT = resolve_endpoint(args.resource, args.endpoint)
    jobs = resolve_inputs(args)

    if args.dry_run:
        print(f"Dry run — {len(jobs)} file(s), endpoint {ENDPOINT or '(unset — set SOL_TTS_RESOURCE for a real run)'}, voice {args.voice}")
        n_files = t_chunks = t_chars = t_pipes = t_slashes = 0
        for md_path, out_path, prose in jobs:
            if not md_path.exists():
                print(f"  MISSING: {md_path}")
                continue
            nc, nch, npipe, nsl = dry_run_file(md_path, out_path, prose)
            n_files += 1
            t_chunks += nc
            t_chars += nch
            t_pipes += npipe
            t_slashes += nsl
        # Anchor + regression trip-wire. The corpus IS the entire production
        # distribution, so these totals are exhaustive, not a sample. After any
        # clean_text.py/chunk_text.py change, compare against the SKILL.md anchor:
        # a delta for files you did not intend to touch is a regression.
        print(
            f"\nTotals: {n_files} files, {t_chunks} chunks, {t_chars} chars, ~{t_chars / 783 / 60:.1f} h audio"
        )
        print(
            f"Narration lint: {t_pipes} stray-pipe chunk(s), {t_slashes} literal '/' (read as 'slash')"
        )
        print(
            "Regression: compare the two lines above to the SKILL.md anchor; an unexplained "
            "delta after a cleaner/chunker change means narration shifted for files you did not touch."
        )
        return 0

    if not ENDPOINT:
        parser.error(
            "No TTS endpoint configured. Set the environment variable SOL_TTS_RESOURCE to your "
            "Azure AI Foundry custom-domain name (e.g. 'romanko-exp'), or SOL_TTS_ENDPOINT to the "
            "full URL, or pass --resource/--endpoint. See .github/skills/synopsis-audiobook/SKILL.md."
        )

    get_token = make_token_provider()
    print(f"Synthesizing {len(jobs)} file(s) with {args.voice}\n  endpoint {ENDPOINT}")
    failures: list[str] = []
    for md_path, out_path, prose in jobs:
        if not md_path.exists():
            print(f"  MISSING: {md_path}")
            continue
        if out_path.exists() and not args.force and not args.limit_chunks:
            print(f"  skip (exists): {out_path.name}")
            continue
        print(f"  {md_path.name} -> {out_path.name}")
        try:
            seconds = synthesize_file(
                md_path, out_path, get_token, args.voice, args.rate,
                prose_only=prose, limit_chunks=args.limit_chunks,
            )
            print(f"  done: {out_path.name} ({seconds / 60:.1f} min)")
        except Exception as exc:  # keep going; report at the end
            failures.append(f"{md_path.name}: {exc}")
            print(f"  FAILED: {md_path.name}: {exc}")
    if failures:
        print(f"\n{len(failures)} file(s) failed:")
        for line in failures:
            print(f"  {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
