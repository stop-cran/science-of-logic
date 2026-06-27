# Review checklist & critique loop — *science-of-logic*

Operational companion to `.github/copilot-instructions.md`. **Single source of truth** for two
roles: the **author** self-checking *before submitting*, and the **`synopsis-reviewer-claude`** +
**`synopsis-reviewer-gpt`** agents (a two-vendor review pair).
Run it every round.

## The critique loop

1. **Author** drafts/edits an installment, runs the mechanical checker, submits.
2. **Reviewer** — ideally a *different model*; cross-model rounds reliably catch what a single
   model misses — critiques against this file.
3. **Author** applies genuine fixes *with judgment*, **holds** the rest *with explicit rationale*,
   propagates any canon change to earlier installments, re-runs the checker, and **verifies**.
4. Repeat until a round is **clean**: no Blocker / High / Medium findings and all mechanical
   gates green. **Stop condition:** once a round yields only **Low / Optional single-word polish**,
   the piece is *settled* — don't spin further rounds chasing taste (diminishing returns).
5. Author authorizes → translate in **nauka-logiki** → run the same loop there.

Never batch ahead of the author's authorization.

**Rotate reviewer models across rounds.** Use at least two *different vendors* (e.g. Claude + GPT +
Gemini) over a piece's review life. Observed division of labour: a **cross-model** pass catches canon
and grammar errors a same-model pass tends to *rationalize away*; a **same-model regression** pass
catches consistency drift introduced by the previous round's own edits. Run reviewers at high/xhigh
reasoning with long context (the full installment + every cross-referenced sibling + both READMEs at
once — that is what surfaces retrofit ripples). Enforce routing operationally where the interface
supports it (e.g. Copilot CLI `/subagents` and `/model`); otherwise treat rotation as a manual discipline.

**At least one reviewer ≠ author model.** On a first-review breadth pass, at least one reviewer must
differ from the model the installment was *drafted* with; a same-vendor reviewer still earns its keep
as a **regression / supplemental** pass (it catches drift the previous round's own edits introduced).
The committed Claude + GPT pair guarantees this for any GPT-, Claude-, or Gemini-authored draft:
whichever vendor the author used, at least one of the two reviewers differs. Routing is the **single
source of truth** in `.github/copilot/settings.json` under `subagents.agents.<name>` —
`synopsis-reviewer-claude` (Opus) and `synopsis-reviewer-gpt` (GPT-5.5), both at `xhigh` +
`long_context`. They divide labour — Claude tends to catch structure, canon propagation, and regression
drift; GPT tends to catch idiom and precision/quality — so run **both** on first review (a parallel
breadth pass), then a single-vendor **regression** pass after the author's edits, until the round is
clean. Add a Gemini-pinned third agent for a tie-breaker / a guaranteed cross-model pass even when the
author is on GPT or Claude.

## How to review (discipline)

- Review the **current** file, not a remembered one. Prefer a **word-diff against the
  last-reviewed commit**: `git --no-pager diff --word-diff=plain <prev>..HEAD -- <file>` — so
  nothing is judged from a stale snapshot. (This bit us once: a "deviation" note was raised
  against EN text that had already been changed.)
- After the author applies fixes, **re-read** the changed spans and **verify** — don't assume.
- Tier every finding by severity; mark each a **fix** or a **hold (rationale)**.
- You are **review-only**: report; the author edits.

## 1 — Mechanical gates (must be green)

Run from the repo root:

```
npx -y -p markdown-it@14 node tools/check-synopsis.js
```

For every Section III installment (NN ≥ 10) it checks:

- **Abstract renders as a *single outer* `<em>` span** — the house-style trap. A trailing
  `**bold**` term or a stray `*` that drops outside the span is the usual cause.
- Section skeleton present: `## I.` … and a `## Coda`.
- **No LaTeX math** (`$…$`, `\(…\)`) — math is italic-plain.
- A **README entry** links the file.
- **Canon denylist** — locked-terminology violations in `tools/canon-denylist.json` fail
  mechanically (e.g. a stray `ℏ`); the installments **and** the README are scanned.

Don't eyeball anything the script can prove. Wire it to run automatically with a pre-commit hook —
`git config core.hooksPath .githooks` (the committed `.githooks/pre-commit` runs the checker) — or as
a Copilot CLI hook.

## 2 — Consistency & canon propagation

- **Cross-references are accurate.** Verify deferral threads (e.g. §15 → §16 → §17), ordinal
  counts ("the *fourth* appearance of the bad infinite"), and "secured / located / first" claims
  by *reading the cited installments* — not from memory.
- **Retrofit ripple.** A change here may expose or create an inconsistency in an
  already-committed installment or either README. If so, **propagate the fix backwards** and
  name the file/line. (History: ℏ→h, real-vs-realized, Engels-vs-Hegel attribution,
  отношение-степеней, home/seat→средоточие.)
- **Categorial-not-empirical guardrail** present wherever a natural-science example appears: the
  Logic supplies the *form*, not the constants — "it does not deduce them."

## 3 — Fidelity to Hegel

- The installment's architecture tracks the corresponding stretch of the *Logic*; deliberate
  compressions are **defensible and flagged**, not silent re-orderings.
- Physics examples are precise *under the guardrail* (e.g. Proust = definite vs Dalton = multiple
  proportions; "at ordinary pressure"; no anachronism asserted as Hegel's own).

## 4 — House style

Defer to `.github/copilot-instructions.md` (don't duplicate): dense register, `**bold**` key
terms, `(*German*)` glosses, `§NN` cross-references, italic-plain math.

## Severity rubric

- **Blocker** — breaks a mechanical gate, or a factually wrong claim.
- **High** — fidelity error, broken cross-reference, guardrail missing where physics appears.
- **Medium** — terminology drift, imprecision, inconsistency with a sibling installment.
- **Low** — idiom, grammar, polish.
- **Optional** — taste; offer, don't press.

## Review output format

1. **Verdict** — publishable? any blockers?
2. **Verified ✓** — the gates and spot-checks you actually ran.
3. **Findings** — grouped by severity, each marked *fix* or *hold (rationale)*.
4. **Questions** — design/judgment calls for the author.
5. **Handoff** — the author applies the agreed fixes; offer to re-review the next iteration.
