---
name: synopsis-audiobook
description: >-
    Generate or troubleshoot the spoken-audio (audiobook) version of the science-of-logic
    English synopsis using Azure MAI-Voice-2 text-to-speech. Use when the user wants to
    narrate or produce MP3 audio for the README or synopsis installments, run or fix
    audiobook/synthesize.py, change the narration voice/rate, or diagnose TTS
    authentication, character-limit, or transient 502 errors.
user-invocable: true
---

# Synopsis audiobook — MAI-Voice-2 narration

Reusable pipeline in the **science-of-logic** repo (`audiobook/`) that turns the English
synopsis Markdown into a seamless MP3 audiobook — one file for the README and one per
Section III installment — using the **MAI-Voice-2** neural TTS model served through Azure
AI Speech (Foundry Tools).

## What it does

- Cleans synopsis Markdown for narration (`clean_text.py`): strips emphasis, headings,
  bullets, links, and rules; spells out symbols a TTS engine would mangle — `§NN` →
  "section NN", `§17–§20` → "section 17 to 20", parenthetical Roman numerals `(VIII)` →
  "part 8", plain-text math (`A = A` → "A equals A", `+A`/`−A` → "plus A"/"minus A",
  `T² ∝ r³` → "T squared is proportional to r cubed", `→` → "to").
- Chunks text (`chunk_text.py`) to stay under the endpoint's 2,000-char / 10-min limit,
  splitting **only at sentence boundaries** (never mid-sentence) and keeping whole
  paragraphs together when they fit; each chunk carries a structural pause hint.
- Synthesizes each chunk to PCM via the Azure Speech real-time SSML endpoint with
  **Microsoft Entra (AAD)** auth, stitches the PCM losslessly with controlled silences
  between paragraphs/sections, and encodes **one seamless MP3 per file** (bundled `ffmpeg`
  from `imageio-ffmpeg`; no system install, no format-conversion step — the join is
  gapless because there is a single encode at the end).
- Is **resumable and fault-tolerant**: skips files whose MP3 already exists, and continues
  past per-file errors, reporting failures at the end.
- README audio narrates prose only (title, intro, "How to Read"); the TOC and essay lists
  are skipped.

## What it does NOT do

- Does **not** commit audio. `out/`, `*.mp3`, `*.wav`, and dry-run `*.txt` are git-ignored;
  only the scripts are versioned. Never `git add` rendered audio.
- Does **not** use API keys. Auth is AAD only (your `az login`). No secrets are stored.
- Does **not** produce the Russian (nauka-logiki) audiobook. English only for now; the RU
  corpus would need `xml:lang="ru-RU"` and a Russian voice (e.g. `ru-RU-Lev:MAI-Voice-2`)
  plus a Cyrillic-aware cleaner review.
- Does **not** narrate essays (`essays/`) — only README + `synopsis/NN-*.md`.
- Does **not** use SSML expressive styles, multi-speaker, or voice-prompting/cloning.
- Does **not** deduce pronunciation of German glosses, `dx/dy`-style slashes, or unusual
  symbols beyond the handled set; new symbols may need a `clean_text.py` rule.
- Is **not** a batch/long-audio job — it uses the real-time endpoint chunk-by-chunk.

## How to use

From `audiobook/` (Windows PowerShell):

```powershell
pip install -r requirements.txt          # azure-identity, requests, imageio-ffmpeg
az login                                  # need "Cognitive Services Speech User" on the resource

python synthesize.py --dry-run --all      # inspect prepared text (writes out/*.txt), no API calls
python synthesize.py ../synopsis/21-*.md --limit-chunks 2   # smoke test one file
python synthesize.py --all                # README (prose) + installments 01..21 -> out/*.mp3
```

Outputs: `out/00-readme.mp3`, `out/01-….mp3`, … `out/21-….mp3`.
Re-running `--all` **resumes** (skips existing MP3s); add `--force` to re-render.

## Configuration

| Variable / flag              | Default                                                                     |
| ---------------------------- | --------------------------------------------------------------------------- |
| `SOL_TTS_ENDPOINT`           | `https://romanko-exp.cognitiveservices.azure.com/tts/cognitiveservices/v1`  |
| `SOL_TTS_VOICE` / `--voice`  | `en-US-Ethan:MAI-Voice-2`                                                   |
| `--rate`                     | (unset); e.g. `-5%` or `0.95` to slow delivery                              |
| `--out-dir`                  | `audiobook/out`                                                             |
| `--limit-chunks N`           | smoke-test only the first N chunks                                          |
| `--force`                    | re-render even if the MP3 exists                                            |

Other en-US voices: `en-US-Olivia` (F), `en-US-Harper` (F), `en-US-Grant` (M),
`en-US-Iris` (F), `en-US-Jasper` (M). The endpoint is a custom-domain Azure AI Services
(Foundry) resource; AAD token scope is `https://cognitiveservices.azure.com/.default`.

## Troubleshooting

- **`AzureCliCredential … Failed to invoke the Azure CLI` / timeout** — the default 10 s
  subprocess timeout expires when `az` is cold on Windows. The script already sets
  `process_timeout=30`; if it still fails, run `az account get-access-token --resource
  https://cognitiveservices.azure.com` once to warm the CLI, and confirm `az login`.
- **401 / 403** — your identity lacks the **Cognitive Services Speech User** role on the
  resource (generic "Cognitive Services User" is not enough for Speech), or the resource
  has no custom domain. Assign the role; verify the endpoint host ends in
  `.cognitiveservices.azure.com`.
- **404 Resource not found** — wrong path; the AAD real-time TTS path is
  `/tts/cognitiveservices/v1` (not `/cognitiveservices/v1`).
- **Transient 502/503 "upstream connect error … protocol error"** — a preview-endpoint
  gateway blip, sometimes lasting tens of seconds. The script retries with jittered backoff
  (up to 8 attempts, ~2.5 min). If a whole file still fails, just re-run `--all` — it
  resumes and retries only the missing files.
- **400 on a specific chunk** — likely malformed SSML or an over-limit chunk; check the
  `--dry-run` transcript (`out/<stem>.txt`) for that file and any new unhandled symbol.
- **Robotic pacing / wrong intonation** — a paragraph was split badly; confirm chunks split
  only at sentence boundaries (`chunk_text.py`), or lower the budget / add `--rate`.
- **`ffmpeg failed`** — `imageio-ffmpeg` binary missing; `pip install -r requirements.txt`.

## Guidelines for future improvements

- **Batch synthesis (long-audio) API** would cut ~1,300 sequential requests to a handful of
  async jobs — check whether it supports MAI-Voice-2 (preview) before switching.
- **Bounded parallelism** (e.g. 2–4 workers) with rate-limit handling would speed the full
  run, if preview quota allows.
- **ID3 tags + chapter metadata** (title/track/album per installment) for player UX.
- **Russian audiobook**: parameterize `xml:lang`/voice, add a Cyrillic cleaner pass, mirror
  in nauka-logiki.
- **Per-section SSML `<break>`** or mild expressive `style`/`styledegree` if the plain
  delivery feels flat; keep it subtle for philosophy narration.
- **Symbol coverage**: extend `clean_text.py` only for symbols that actually appear (audit
  the corpus first, as was done for `² ³ · × ∝ →`); avoid ambiguous global rules (e.g. do
  not convert `/`, which means "and" in `whole/parts` but division in `dy/dx`).
- Keep the **categorial-not-empirical** guardrail intact — cleaning must never alter meaning,
  only remove decoration and vocalize symbols.

## Key facts / constraints

- Endpoint: `…cognitiveservices.azure.com/tts/cognitiveservices/v1`; SSML `Content-Type
  application/ssml+xml`; MP3 via `X-Microsoft-OutputFormat`. PCM used internally
  (`riff-24khz-16bit-mono-pcm`) for gapless stitching.
- Hard limits: **2,000 characters and 10 minutes of audio per request** → chunking is
  mandatory (budget 1,800 chars).
- The full synopsis is ~22 files / ~1,300 chunks / ~3.7 h of audio.
