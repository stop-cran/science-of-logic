# English audiobook

The shared engine and operating skill now live in
[stop-cran/book-skills](https://github.com/stop-cran/book-skills/tree/main/.github/skills/audiobook-from-markdown).
This repository owns only `book.json` and the thin `synthesize.py` compatibility launcher.
Do not restore local copies of the cleaner, chunker, transport, or dependencies.

**English production is awaiting an approved spoken AI/synopsis disclosure.** This
migration preserves the existing text profile but does not approve new English front
matter or regenerate English audio. A README-free 1-29 album needs a bounded profile
whose first track carries that approved opening; adding it only to catalog track 00
would not cover a selection excluding the README.

Set `BOOK_SKILLS_ROOT` to that checkout. From this directory:

```powershell
python .\synthesize.py --dry-run --chapters 1-29
python .\synthesize.py --resource '<your-resource>' --probe-max-chars --chapters 1-29
python .\synthesize.py --resource '<your-resource>' --limit-chunks 2 01-from-school-logic-to-dialectic
```

The project preserves `en-US-Ethan:MAI-Voice-2`, `SOL_TTS_*` environment variables,
README prose selection, scientific notation, and recap-table omission. `--all` still
includes the README and every current installment; use an exact range when requested.
Configured source paths and globs are accepted. The English profile also preserves
explicit essay-path narration through `allow_external_inputs`; such files receive track
numbers after the configured catalog. A partial glob cannot silently drop an unknown file.
These ad-hoc numbers are per invocation; declare `additional_sources` or a separate
project for stable essay-album ordering. Extras do not change existing catalog totals.
External files are forbidden with `--chapters` or a chapter-bounded project, so the Russian
1-29 selection cannot expand accidentally. Use a separate profile for a separate album.

Read and follow the shared skill for authentication, probing, preview approval, resumption,
and verification. Dependencies are declared in its `reference\requirements.txt`, not here.
Existing MP3s have no new completion manifests and are not assumed current: choose another
output directory or explicitly regenerate with `--force`. Audio and caches remain ignored.

The migration deliberately fixes duplicated "section section" narration for `§§`,
strips quotation markers while retaining quote text, and removes box-drawing decoration
from the three recap diagrams. Roman references are spoken as parts, distinct from
Arabic installment references. Balanced
URL parentheses no longer leak URL tails into narration. A diagram's words remain in document order; its graphical
topology is not inferred. Mathematical subscripts are preserved. Table omission is this
book's policy, not a general assumption about Markdown.

The Russian project has its own configuration in `nauka-logiki\audiobook\book.json`.
No English audio is regenerated as part of the Russian-only §§1-29 run.

`--force` rebuilds an output using verified PCM checkpoints; interrupted replacements
can resume. Only `--force --refresh-cache` deliberately repeats all selected TTS calls.
