# Audiobook generation

Reusable scripts that turn the English synopsis into an audiobook using the
**MAI-Voice-2** neural text-to-speech model, served through Azure AI Speech
(Foundry Tools). One MP3 is produced for the README and one per Section III
installment.

> Rendered audio is **not** committed. `out/`, `*.mp3`, `*.wav` and the dry-run
> `*.txt` transcripts are git-ignored.

## How it works

1. **`clean_text.py`** — strips Markdown (emphasis, headings, bullets, links, rules, and
   whole tables) and spells out symbols that would otherwise be vocalized: `§NN`
   -> "section NN", `§17–§20` -> "section 17 to 20", parenthetical Roman
   numerals `(VIII)` -> "part 8", and plain-text math (`A = A` -> "A equals A",
   `+A`/`−A` -> "plus A"/"minus A"). Returns title/paragraph segments.
2. **`chunk_text.py`** — keeps whole paragraphs together when they fit under a
   conservative budget (1,800 chars, below the endpoint's 2,000-char / 10-min
   limit) and otherwise splits them **at sentence boundaries only**, so no chunk
   is cut mid-sentence. Each chunk carries a structural pause hint.
3. **`synthesize.py`** — authenticates with Microsoft Entra (your `az login`),
   synthesizes each chunk to PCM, stitches the PCM losslessly with controlled
   silences between paragraphs/sections, and encodes a single seamless MP3 per
   file (a bundled `ffmpeg` from `imageio-ffmpeg` does the WAV->MP3 encode).

## Prerequisites

```powershell
pip install -r requirements.txt
az login   # your account needs the "Cognitive Services Speech User" role on the resource
$env:SOL_TTS_RESOURCE = "<your-foundry-resource-name>"   # user-specific; not baked into the repo
```

Authentication is **AAD only** (no keys). Token scope
`https://cognitiveservices.azure.com/.default`. The Foundry resource/endpoint is
**user-specific** (a fork uses a different resource), so it is never hardcoded — set
`SOL_TTS_RESOURCE` (custom-domain name) or `SOL_TTS_ENDPOINT` (full URL).

## Usage

```powershell
# Inspect the prepared narration text without calling the API (writes out/*.txt):
python synthesize.py --dry-run --all

# Smoke test: synthesize only the first 2 chunks of one installment:
python synthesize.py ../synopsis/21-*.md --limit-chunks 2

# Full run: README (prose sections only) + installments 01..21 -> out/*.mp3
python synthesize.py --all
```

Outputs: `out/00-readme.mp3`, `out/01-from-school-logic-to-dialectic.mp3`, ...

## Configuration

| Variable / flag        | Default                                                              |
| ---------------------- | ------------------------------------------------------------------- |
| `SOL_TTS_RESOURCE` / `--resource` | Foundry custom-domain name; endpoint URL is built from it (required for a real run) |
| `SOL_TTS_ENDPOINT` / `--endpoint` | Full TTS endpoint URL (overrides `--resource`)          |
| `SOL_TTS_VOICE` / `--voice` | `en-US-Ethan:MAI-Voice-2`                                      |
| `--rate`               | (unset) e.g. `--rate=-5%` or `--rate=0.95` to slow the delivery      |
| `--out-dir`            | `audiobook/out`                                                     |

Other MAI-Voice-2 en-US voices: `en-US-Olivia` (F), `en-US-Harper` (F),
`en-US-Grant` (M), `en-US-Iris` (F), `en-US-Jasper` (M).

An agent playbook for this pipeline (what it does / does not do, troubleshooting,
future-improvement guidelines) lives at
`.github/skills/synopsis-audiobook/SKILL.md` and is auto-discovered by Copilot CLI when
working in this repo.

## Notes

- MAI-Voice-2 is in **public preview**; expect preview quotas. The synthesizer
  retries with backoff on `429`/`5xx` and honors `Retry-After`.
- The README audio narrates the prose only (title, intro, "How to Read") and
  skips the table-of-contents and essay lists.
- **Verifying a cleaner/chunker change:** `--dry-run --all` prints grand-total
  `Totals` and `Narration lint` lines — the corpus is the whole production
  distribution, so this is an exhaustive regression check. Compare against the
  anchor in `SKILL.md` (1,232 chunks / 478,268 chars / 0 pipes / 30 slashes as of
  §21); an unexplained delta after a code change is a regression. Prosody and
  pronunciation are audible-only — also render and **listen to one affected chunk**.
