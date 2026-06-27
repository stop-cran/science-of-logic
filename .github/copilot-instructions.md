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

## Handling review feedback

Apply genuine fixes (idiom, grammar, precision, consistency), but **hold** suggestions that
conflict with fidelity to Hegel or with established house style — **always with an explicit
rationale**. Principled, reasoned holds are preferred over blanket acceptance.

## House style

- **Abstract**: the paragraph directly under the `#` title is wrapped in a **single `*…*`
  italic span**, with `**bold**` key terms and `(*German*)` glosses nested inside it.
  (Verify it renders as one `<em>` span before committing.)
- **Section skeleton**: `## I.`–`## IX.` Roman-numeral sections, then `## Coda`. Recurring
  sections include *Three Misreadings, Answered Directly*, *What the Method Did Here —
  Observations*, and *What Comes Next*.
- **Math**: italic plain text (e.g. *y = x²*, *a · b = k*, *s ∝ t²*, *ℏ*) — **not** LaTeX
  `$…$`.
- **Cross-references**: cite earlier installments as `§13`, `§16`, etc.
- Keep the dense, weighty register; do not loosen it for readability unless a sentence is
  genuinely over-literal.
- Claims about physics are **categorial, not empirical**: the Logic supplies the *form*, not
  the constants. Keep the "categorial, not a piece of physics — it does not deduce them"
  guardrail wherever natural-science examples appear.
- `README.md` carries a one-entry-per-installment index; **keep it parallel with the Russian
  README** (the two are mirrors of each other).

## Commits

- **GPG-sign every commit** (`-S`). Signing program: `C:/Program Files/GnuPG/bin/gpg.exe`.
- Author: `Roman Konstantinovskiy <stop-cran@list.ru>`.
- Append the trailer: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
- Stage only `.md` / `README.md`; **do not** stage build artifacts (`node_modules/`,
  `synopsis.html`, `synopsis.pdf`, `build-pdf.js`, etc.).
- Use the literal `§` character in commit messages.
- Verify after committing: `git log --pretty="%h %G? %s" -1` should show `G` (good signature).
