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
severity rubric, and critique loop). A review is for **method, philosophy, attribution, and
readability** — the mechanical gates already prove structure, emphasis parity, references, and
line counts, so don't spend a round re-deriving them, and don't report a finding whose whole
content is a preferred synonym. Run the mechanical gate before submitting:
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

**Never assert an unverified universal negative.** "Hegel nowhere explains…", "Spinoza never
wrote…", "no such science existed…" — a negative claim over an author's whole corpus cannot be
settled by reading one chapter, and this project has produced **five**, four of them false or
overstated: §27's organism claim and its historical-geology claim; "Hegel nowhere explains the
choice of title" (he explains it twice, in the Foreword and in the Introduction); §26's "Hegel never
announces the fact" (true of the chapter and of the recapitulation that opens the next Doctrine —
unverifiable beyond them); and one the mirror manufactured on its own at §02, where the English
"a formula he **does not use as the name of his method**" was rendered "a formula Hegel **never
used**". **State the claim at the bound you actually checked, and name the bound** — "not in the
chapter, and not in the recapitulation that opens the Doctrine of the Concept". §25's *omnis
determinatio est negatio* paragraph is the model: the negative is asserted and then paid for, with
the letter, the language, the lost autograph and the competing lines of scholarship. **Sweep both
languages** — the mirror can introduce this defect into a line whose original was clean (`нигде не`,
`никогда не`, `не существовал`). A denylist rule was considered and rejected: any regex blunt enough
to catch the bad cases also fires on the verified ones, which must stay green.

**Check the corpus before the claim — it is usually already settled there.** A finished installment
binds every later one. This round produced **seven** collisions in which a line asserted something
the corpus had already decided against: §09's life-restriction attributed to the *Logic*, against
§27:27, which assigns it to the *Philosophy of Nature*; §09's praxis-grounding presented as Hegel's
own, against §06:33, which flags it as a materialist reconstruction; §05's "no subject who
experiences its contradictions", against §27:23, where the Concept is at work in nature "as blind,
as unaware of itself and unthinking"; §05's law covering "any complex system", against §03:113,
"the direction is not a law"; §05's "precisely Hegel's claim against atomism", against §26:121,
which "validates no emergentist thesis and refutes none"; §05's defective Understanding, against
§27:87, where fixity is "a subjective impotence of reason"; and §09:66's "passes over into the
Object", against §09:9 seven lines above it — and against *Encyclopaedia* §161, which denies
transition to this sphere outright, and §193, whose heading is *realisation*. **Before writing or
repairing a claim about Hegel, grep the corpus for the sibling paragraph that already governs it**,
and cite that sibling in the line.

**When correcting a locus or an attribution, read the whole stretch first.** §27:59 had to be
corrected **twice**: the Kant indictment in "On the Concept in General" does not end where either
earlier reading assumed — Kant is named and rebutted continuously through §1311. A fix written
against the pre-edit sentence instead of against the full passage swaps one false claim for another.

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
