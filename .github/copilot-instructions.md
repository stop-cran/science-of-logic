# Copilot instructions — *science-of-logic*

## What this repository is

A long-form **English synopsis of G. W. F. Hegel's *Science of Logic***, written as a
method-driven close reading. The emphasis is Hegel's **method of investigation** and its
contribution to the scientific paradigm and scientific method — not an encyclopedic
paraphrase. Section III proceeds installment by installment in `synopsis/NN-*.md`, each a
focused close reading of one stretch of the *Logic*. The Russian translation lives in the
sibling repository **nauka-logiki** and must mirror this one.

## Workflow (do not skip or reorder)

1. Write the English installment in `synopsis/`.
2. Submit it for external-agent review; expect **multiple rounds**, often cross-model.
3. Apply feedback **with judgment** (see below); answer the author's philosophical questions.
4. Translate into Russian in the **nauka-logiki** repository.
5. Review the Russian (its own rounds).
6. Commit and push each part, GPG-signed.

The author reviews each piece before authorizing the next — **never batch ahead** without a
check-in.

**Review process.** Authors self-check and reviewers critique against `REVIEW.md` (the checklist,
severity rubric, and critique loop). Run the mechanical gate before submitting:
`npx -y -p markdown-it@14 node tools/check-synopsis.js`. The `synopsis-reviewer-claude` and
`synopsis-reviewer-gpt` custom agents in
`.github/agents/` encode the review-only reviewer role (a two-vendor pair).

## Handling review feedback

Apply genuine fixes (idiom, grammar, precision, consistency), but **hold** suggestions that
conflict with fidelity to Hegel or with established house style — **always with an explicit
rationale**. Principled, reasoned holds are preferred over blanket acceptance.

**Additions to settled prose go back through review.** Anything inserted into an installment that
has already gone clean — a gloss, a citation, a paragraph answering one of the author's questions —
is presumptively broken until the reviewer pair has seen it. It is this project's single most
reliable defect source, and the typical fault is a *collision* with settled text later in the same
file rather than a false claim. Prefer cutting to patching. See `REVIEW.md`.

**Re-read after a fix batch — the defects no reviewer can see.** Edits in a batch are each written
against the *pre-batch* text and none of them sees the others, so a batch reliably manufactures its
own contradictions: a hedge that collides with a concession made elsewhere, a formulation struck at
one site and left standing at another, a framing removed by one fix and reinstated by the next, a
reversed verdict whose paragraph still ends on the old one. In the §27 round a single sequential pass
over the amended file returned **eight MAJOR findings of exactly these shapes** — after five reviewers
had already been run and applied. After any fix batch: **grep the whole file for every phrase the
batch deleted or reversed**, re-read each amended paragraph to its **last sentence**, then re-run the
checker. See `REVIEW.md`.

**Settle reviewer disagreements against the primary source.** When the pair splits on what Hegel or
a cited edition says, read the text rather than picking a reviewer — each is usually half right.

## House style

- **Abstract**: the paragraph directly under the `#` title is wrapped in a **single `*…*`
  italic span**, with `**bold**` key terms and `(*German*)` glosses nested inside it.
  (Verify it renders as one `<em>` span before committing.)
- **Section skeleton**: `## I.`–`## N` contiguous Roman-numeral sections (N varies per installment),
  then `## Coda`. Recurring
  sections include *Three Misreadings, Answered Directly*, *What the Method Did Here —
  Observations*, and *What Comes Next*.
- **Math**: italic plain text (e.g. *y = x²*, *a · b = k*, *s ∝ t²*, *h*) — **not** LaTeX
  `$…$`.
- **Cross-references**: cite earlier installments as `§13`, `§16`, etc.
- **Quotations from Hegel are verified against the text** before an argument leans on them, and
  carry no emphasis the source lacks. A section **heading** is often the strongest warrant
  available — check whether Hegel has already *titled* the point before reconstructing it. Where a
  reading is yours rather than his, mark it as a reading.
- **What counts as an altered quotation.** Anything inside the quotation marks that is not in
  Miller is an alteration — not only substituted words, but added commas, added glosses, and
  material dropped from the middle without an ellipsis. Two specific traps, both of which have
  reached a draft: Miller writes **"Notion"**, so `Concept` must never appear inside a quotation
  even though our own prose says *Concept*; and Miller's own German glosses are in **square**
  brackets (`[*Seele*]`, `[*begrifflos*]`, `[*das Eins*]`), so a **parenthesised** gloss inside
  quotation marks is always ours and always wrong. Our prose uses `English (*German*)`; quotations
  reproduce Miller's brackets verbatim. Unescaped `[*…*]` is safe for the checker; `\[` is not.
- Keep the dense, weighty register; do not loosen it for readability unless a sentence is
  genuinely over-literal.
- Claims about physics are **categorial, not empirical**: the Logic supplies the *form*, not
  the constants. Keep the "categorial, not a piece of physics — it does not deduce them"
  guardrail wherever natural-science examples appear.
- `README.md` carries a one-entry-per-installment index; **keep it parallel with the Russian
  README** (the two are mirrors of each other).

## Environment and tooling (Windows / PowerShell 5.1)

- **`>` and `Out-File` write UTF-16LE.** Never use them to capture binary or to inspect a file's
  encoding — they will invent a BOM that is not there. Capturing `git cat-file blob` this way once
  made every file in this repo appear to be UTF-16 and nearly triggered a needless repo-wide
  re-encoding. Use `& $env:ComSpec /c "git cat-file blob <id> > out.bin"` for byte-exact capture.
- **.NET static calls ignore `Set-Location`.** `[System.IO.File]::ReadAllText("README.md")` resolves
  against the process start directory, not the current one. Always pass absolute paths.
- **`Set-Location` does not persist between tool calls**; each call starts fresh.
- **`npx` is blocked by execution policy** — use `& npx.cmd`. Checker command:
  `Set-Location C:\Users\romanko\Documents\science-of-logic; & npx.cmd -y -p markdown-it@14 node tools/check-synopsis.js`
- **After any `create`/`edit`**, re-normalize to CRLF + UTF-8-no-BOM, then re-run the checker.
- **The `edit` tool has twice duplicated a blank line in `README.md`.** Prefer a PowerShell
  array-splice for that file, and always inspect `git diff` for stray blank lines afterwards.

## Line endings — a repo-specific trap

`core.autocrlf=true`, but the stored blobs are **not uniform**: `README.md` is committed with
**CRLF**, while every `synopsis/*.md`, `REVIEW.md`, and `tools/*` blob is committed with **LF**.
Staging everything the same way therefore produces a spurious whole-file diff on one side or the
other. Stage in two commands:

```
git -c core.autocrlf=false add -- README.md
git -c core.autocrlf=true  add -- REVIEW.md synopsis/ tools/
```

Confirm before committing that `git diff --cached --stat` shows only the lines actually edited. A
79-line diff on `README.md` means the EOL handling was wrong, not that the file changed.

## Commits

- **GPG-sign every commit** (`-S`). Signing program: `C:/Program Files/GnuPG/bin/gpg.exe`.
- Author: `Roman Konstantinovskiy <stop-cran@list.ru>`.
- Append the trailer: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
- Stage only `.md` / `README.md`; **do not** stage build artifacts (`node_modules/`,
  `synopsis.html`, `synopsis.pdf`, `build-pdf.js`, etc.).
- Use the literal `§` character in commit messages.
- For multi-paragraph messages, write the temp file **inside `.git/`** (e.g. `.git/COMMIT_MSG_27.txt`)
  so it can never be staged by accident, and delete it after committing.
- Verify after committing: `git log --pretty="%h %G? %s" -1` should show `G` (good signature).
