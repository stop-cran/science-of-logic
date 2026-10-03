---
name: synopsis-audiobook
description: Generate or troubleshoot this English synopsis's audiobook using the shared book-skills engine and the local book configuration.
user-invocable: true
---

# English synopsis audiobook adapter

Read `audiobook/README.md` and `audiobook/book.json`, then load the canonical
`audiobook-from-markdown/SKILL.md` from the checkout named by `BOOK_SKILLS_ROOT`.
Its repository is https://github.com/stop-cran/book-skills.

The shared skill and engine own preparation, probing, authentication, caching,
completion manifests, metadata, preview approval, and error handling. Do not duplicate
them here. `audiobook/synthesize.py` delegates to that engine without copying it.

This book owns its English voice, notation policy, and README selection. `--all`
includes the README and all installments, including later ones; use the exact requested
range. Do not change settled manuscripts for TTS. Audio stays out of Git.
Before any future English production render, obtain an approved spoken AI/synopsis
disclosure and ensure it belongs to the selected album's first track; the migration
profile is awaiting that step. See the local README, especially for README-free ranges.
Russian narration uses the separate `nauka-logiki` configuration, not this one.

For pipeline defects use the shared skill's feedback channel; project-content
disagreements remain in this repository's author-review workflow.
