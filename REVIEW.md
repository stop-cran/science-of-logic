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

**Additions to settled prose restart the loop.** A late insertion into an installment that has
already gone clean — a gloss, a citation, a paragraph written to answer one of the author's
questions — is **presumptively broken** and must go through the reviewer pair before it lands.
This is the most reliable defect source the project has: of four additions drafted for §25 in a
single round, one was cut outright and three were substantially rewritten over two further
rounds, and every §25 defect found after the installment first went clean had entered this way.
The characteristic failure is not a false claim but a **collision**: the addition restates a
point the settled text already makes later and better, and the two then disagree about the
*character*, the *cause*, or the *level* of the same move. Three symptoms worth watching for — the
addition asserts something the neighbouring settled line denies (e.g. "already has a content" four
lines after "no content has entered"); it pre-empts a motor the next section supplies; or it routes
a figure *down* the ladder where the settled text routes it *up* (a later §25 draft sent absolutized
chance down into formal necessity, where the section close and the Coda take it up into absolute
necessity). **Prefer cutting to patching**: if the settled text already carries the point, the
addition's only job was to point at it, and a forward reference does that without risk.

**A correct objection does not entail new prose.** The strongest version of this failure is an
addition that is philosophically *right* and still unpublishable, because the objection it answers
was already discharged elsewhere in the installment. Before drafting, search the file for the
answer; if it is there, the whole remedy is one clause pointing at it. Check too that the addition
is not smuggling in a coinage where the settled text already has a bolded term for the same thing —
a term with exactly one corpus occurrence, and that one your own, is the tell.

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
`synopsis-reviewer-claude` (Claude Opus 5) and `synopsis-reviewer-gpt` (GPT-5.6 Sol), both at `xhigh` +
`long_context`. They divide labour — Claude tends to catch structure, canon propagation, and regression
drift; GPT tends to catch idiom and precision/quality — so run **both** on first review (a parallel
breadth pass), then a single-vendor **regression** pass after the author's edits, until the round is
clean. Add a Gemini-pinned third agent for a tie-breaker / a guaranteed cross-model pass even when the
author is on GPT or Claude.

Foundry-served external reviewers (for example DeepSeek or xAI, invoked through
`synopsis-foundry-review`) are **supplemental fresh-vendor passes** and count toward vendor
diversity; triage their findings under the same severity and clean-round stop rules. They do not
replace the default Claude + GPT first-review breadth pair unless the author explicitly changes that
round's routing.

## The reviewer panel — what to parallelize, and what not to

Reviewers may be run in parallel, but **only the procedural layer may be split by facet.**
The judgment layer must stay whole and must stay duplicated.

**Two or more generalists on *identical* whole-file prompts.** This layer is load-bearing and is
never faceted. Its value is not coverage but **adjudicable disagreement**: two reviewers given the
same file and the same instructions, disagreeing about the same line, is the single most productive
event in this project's history. The §22/§25 condition-totality reversal — the most consequential
correction the corpus has had — surfaced exactly this way, from two reviewers contradicting each
other on a line that had already survived two Claude passes and two GPT passes. Faceting eliminates
overlap **by construction**, and overlap is the only place such disagreement can occur. Keep at
least one generalist whose vendor differs from the author model.

**Facet agents, run alongside.** These are for work where a checklist beats a disposition and
where overlap genuinely adds nothing:

- **Quotation verifier** — extract *every* quoted span, including fragments inside the abstract,
  and check each verbatim against the primary source. Exhaustive, not sampled. This exists because
  the corpus once shipped a fabricated attribution; a generalist asked to also do everything else
  will sample.
- **Propagation sweeper** — body ↔ abstract ↔ README ↔ the prior installment's forward-pointers,
  plus every claim the new file makes *about* a sibling installment. The characteristic defect is a
  fix applied in the body and not in the abstract or the README.
- **Corpus-lock auditor** — terminology, gloss format, heading skeleton, typography, against the
  established 26 files rather than against taste.

**Faceting is a division of labour, not of authority.** A facet agent reports; it does not
adjudicate. Splits are still settled against the primary source, never by preferring a reviewer.

**Two failure modes the split introduces, and their countermeasures.** First, defects fall in the
**seams** between facets — so the generalists' prompts stay unrestricted, and the seams are their
responsibility. Second, a pure parallel fan-out loses the **regression pass**: in the §26 round the
second reviewer read the file *after* the first reviewer's fixes had landed, verified them verbatim,
and on that basis withdrew eleven of its own candidate findings. Preserve this — after fixes, run
one **sequential whole-file pass** on the amended text.

**Migrate downward whenever possible.** The three facets above are procedural by design, which
means each is a candidate for `tools/check-synopsis.js` and `tools/canon-denylist.json`. An agent
that greps is an expensive grep. Every round, ask the corpus-lock auditor to propose denylist
entries that would have caught its findings mechanically, and require it to verify each proposed
pattern produces **zero matches against the already-settled files** before it is added.

### The §27 round — the doctrine's first live confirmation, and one correction to it

The §27 panel was the first run under the rules above, and it produced three results worth keeping.

**The duplicated generalists earned their cost.** Two generalists received **byte-identical**
whole-file prompts on different vendors. They converged on two sibling-misdescriptions — §27 had
attributed to §03 the opposite of what §03 says, and had attributed to §06 a warning §06 never
issues — which the propagation facet found independently, giving triple agreement and no need for
adjudication. They then **flatly contradicted each other** on the section handling the sciences:
one cleared it explicitly, in terms ("factually sound and do not overreach"), while the other
returned six blockers in the same paragraphs — a false genealogy for modern logic, an
impossibility claim the text does not support, an overreached cladistics parallel, an
attribution of periodicity to nuclear charge alone, and a claim that the *impotence of nature*
passage was detachable when the next sentences in Miller ground it systematically. Every one was
upheld against the primary source. Had the clearing reviewer run alone, the section would have
shipped. **Coverage would not have caught this; only overlap could.**

**A narrow facet can be weaker than a generalist at its own facet.** The quotation verifier
returned 52 of 54 spans verified and one genuine alteration. The generalist, not assigned to
quotations at all, found four further quotation defects the facet had passed: a dropped
parenthetical inside a quoted sentence, and three German glosses placed inside quotation marks,
one of them a word **not in Miller at all**. The cause is instructive — the facet checked whether
the *words* were Hegel's and
stopped there, while the generalist also checked the punctuation, the brackets, and the silent
elisions. Widen the quotation verifier's brief accordingly: **a quotation is altered if anything
inside the quotation marks is not in the source, including brackets, commas, and glosses, and if
anything is dropped from the middle without an ellipsis.** This does not weaken the case for
facets; it shows a facet is only as good as the definition of its facet.

**Two settled conventions, so that reviewers stop spending findings on them.** First, **bold inside
a quotation is the synopsis's own emphasis.** It is applied throughout the corpus to mark the
load-bearing words of a cited passage, it is deliberate and uniform, and it makes no claim about
emphasis in the source. It is not an alteration and should not be reported as one. Second, and
conversely, **a German gloss belongs outside the quotation marks**, in the synopsis's own voice and
in parentheses — `the **soul** (*Seele*)`, not `"the **soul** [*Seele*]"`. The glosses are ours, not
the translator's; inside the quotation marks they are an alteration, and square brackets falsely
imply the translator supplied them.

**Check a facet's scope before believing its negative.** The verifier's single NOT FOUND was an
artifact of the page range *the prompt* assigned it: the quoted phrase is verbatim Miller, on a
page the prompt had not listed. A facet's negative finding is a claim about its search space
first and about the corpus second.

**The sequential regression pass is where the round's remaining defects were.** Five reviewers — two
generalists and three facets — had been run and every finding applied. A single sequential pass over
the **amended** file then returned **eight further MAJOR findings, every one of them created by the
repairs themselves**, and none of them visible to any reviewer who read the file before the fixes
landed. They fell into four recurring shapes, and the shapes matter more than the instances:

- **A hedge collides with a concession made elsewhere.** One fix conceded that Hegel does allow the
  three moments to be counted "if one insists"; a paragraph four sections away still said counting
  them was "forbidden outright."
- **A struck formulation survives at a second site.** A sentence deleted from §III for overclaiming —
  "the method can describe itself only when it has a result to describe" — was still standing, word
  for word, in the Coda.
- **A fix re-imports the framing another fix removed.** "Explanation" had just been struck from the
  *Merkmal* passage as the wrong criterion; a repair three paragraphs later reinstated it verbatim
  ("the later one *explains the earlier*, which is what having a principle means").
- **A reversed verdict leaves its old closing sentence standing.** The *impotence of nature* paragraph
  was rewritten to argue the passage is load-bearing, and still ended by calling it "a badly-expressed
  observation."

The common cause is that a batch of edits is applied blind: each edit is written against the text as
it stood *before* the batch, and none of them sees the others. The countermeasure is **mechanical, not
judgmental** — after applying a fix batch, grep the whole file for every formulation the batch deleted
or reversed, and re-read each amended paragraph **to its last sentence**, which is where a reversed
verdict characteristically survives. No gate in `tools/` catches any of this, and no parallel reviewer
can: the defects did not exist when they read. Budget for this pass; it is not a formality.

### The §27 regression rounds — five further results

**Vendor verdicts split, and the minority vendor was right every time.** Round 1: one vendor
returned *not publishable* with two Blockers while two others certified the file clean; every
Blocker held. Round 2, over the amended file, reproduced the split **exactly** — the two
certifying vendors again returned "publishable, no Blockers" on *both* their facets, while the
minority vendor returned "not yet publishable" on both, and all four of its findings were then
verified true against the sibling installments and applied. Round 3 reproduced it a **third**
time: the fast vendor certified "publishable, no Blockers" and its sole Medium asked for
something the paragraph's last sentence already contained, while the minority vendor returned
2 High and 2 Medium — every one of which was verified true and applied. Round 4 reproduced it a
**fourth** time, and more sharply: the fast vendor's generalist facet returned **no findings at
any severity**, while the minority vendor returned 2 High and 1 Medium on the generalist facet
and 2 Medium and 2 Low on style — all seven verified true and applied, and the Medium (a
cross-reference pointing at §VII for a result used only in §VIII) provably so. **Do not vote-count
across vendors.** A majority certification is not evidence; adjudicate every finding against the
siblings and the primary source. The fast, cheap vendor has now four times certified a file
containing real defects, and twice returned findings the text already satisfied.

Round 5 reproduced the split a **fifth** time, with the same polarity: the fast vendor certified
*publishable* on both facets, its generalist again returning **no findings at any severity**, while
the minority vendor returned *not yet publishable* on both. Its leading finding is the sharpest
evidence yet for the rule below. The round-4 fix had rewritten the abstraction argument at `:97` to
locate the defeat in **what abstraction keeps**, expressly denying that the omitted differences
survive — but five paragraphs earlier `:65` still said the abstract universal has content "only by
borrowing it back from what it stripped," which is that denied reading verbatim. The fix had
contradicted a passage it did not touch. That passage *had* been checked against the rewrite in the
same session and cleared as consistent; the author's own re-reading missed it, and only the next
round's outside eye caught it. **An author cannot certify his own fix batch, and neither can the
vendor that has already passed the file.**

Round 6 held the split a **sixth** time and closed the argument. The fast vendor returned
*publishable* on both facets with its fidelity pass reporting **zero findings**, and its three
generalist findings all failed on inspection — one of them proposing a "tighter" citation that
would have relocated *Macht* to a transition later than the one where §26 actually establishes it,
i.e. a correction that would have **introduced** the error it claimed to prevent. The minority
vendor, meanwhile, returned three Mediums that every one verified, two of them in the dominant
class: an **opponent-scope overreach** — the chapter arguing against "the tradition" where its own
coda, its README entry and §09 all name the narrower *school logic*, so that Aristotle and the
scholastics were being charged with the empiricists' doctrine — and a **retrofit ripple** in which
§27's new guardrail ("neither uniform nor ever quite finished", "the Logic does not certify any
such transition") contradicted §03's surviving "the historical pattern is **invariant**", "every
advance in the empirical sciences", and "every successful scientific theory". §03 had *already*
been amended by this installment on a different point, which is precisely why the residue survived:
**a sibling corrected once reads as a sibling checked.** It is not.

**The abstract is a propagation site, and it is the one that gets missed.** The scope fix touched
five places; four were found by reading, and the fifth — the installment's own opening abstract —
only by the mandatory grep for the deleted formulation. The abstract restates the whole argument in
a single very long line, so the eye slides over it and `view` truncates it. **Grep it explicitly by
its own text after every substantive change.** This is the third consecutive fix batch in which the
countermeasure grep caught a live residue that re-reading had passed.

**A fix can trade one imprecision for another, and the same paragraph can be right to flag
twice.** §27's abstraction argument was flagged by the same vendor in two consecutive rounds for
**opposite** reasons. Round 3 objected that "the product is itself a singular" equivocates on
type and token; the rewrite that removed the equivocation produced "carries over the very content
the operation set out to strip," which round 4 objected to as a straw man — retaining the common
content is precisely what abstraction *intends*. The correct formulation was a **third** thing,
neither of the two errors: what abstraction retains is itself one determinate content among
others, so universality is reached only *in* individual content. **A fix batch is not
self-certifying.** When a fix rewrites an argument rather than correcting a reference, the
rewrite is new text and earns a fresh pass. Re-review after substantive rewrites, and do not
treat a paragraph as settled merely because it was amended in response to a verified finding.

**A reviewer's line citation can be wrong while its finding is right.** Round 3's first High
cited a sibling at lines that are blank. The substance was nonetheless correct, and was
confirmed by grep against the sibling's headings. **Verify the claim, not the coordinates** —
and do not dismiss a finding because its pointer misses.

**A requested facet can fail silently.** Round 3's launcher requested two facets from the
minority vendor; only one report appeared at first, with a zero-byte stderr log — the second
arrived late. Check for *missing outputs*, not only for errors, and re-check before concluding
a facet failed.

**A facet's certification is not evidence of absence.** Round 1's second Blocker — a quotation
headed "Second, to §25" whose backward link was in fact **§26** — was returned by the **style**
facet, and missed by *both* dedicated fidelity facets, one of which had explicitly "verified" the
attribution as correct. Facets of one model are correlated (one finding appeared in three of four
facets from the same vendor), so **multiple facets are not a substitute for a second vendor**, and
a non-fidelity facet must be kept in every round.

**The dominant defect class is cross-sibling contradiction, not local error.** Every round-2
finding had the same shape: a claim in the new installment contradicted by a sibling's committed
text — "at no point importing an external standard" against §25's recorded limit that *the repair
is the critic's*; "without announcing it" against §23 and §24, which name immanent critique
outright; a placement in §06 in tension with what §27 reports Hegel saying about a **calculus**.
Local prose is comparatively safe; **the sentences that assert what the corpus elsewhere does are
the ones to audit**, and the fix belongs wherever the contradiction is — three of these were
repaired by amending the *sibling*, not the new file.

**Check the round log before acting on a re-flagged finding.** Two round-1 findings had already
been adjudicated in an earlier round and recorded above; reviewers see the rubric, not the
adjudication history, and will raise them again. Read this file's round log first — otherwise a
settled ruling is silently reversed by the next round's "fix".

## How to review (discipline)

- Review the **current** file, not a remembered one. Prefer a **word-diff against the
  last-reviewed commit**: `git --no-pager diff --word-diff=plain <prev>..HEAD -- <file>` — so
  nothing is judged from a stale snapshot. (This bit us once: a "deviation" note was raised
  against EN text that had already been changed.)
- After the author applies fixes, **re-read** the changed spans and **verify** — don't assume.
- When introducing a **new rendering of a recurring phrase**, check how the **settled siblings**
  already render it (the mirror of retrofit-ripple): e.g. "the claim is categorial" was settled as
  «утверждение … категориальное» in §18, so §19 had to match it, not invent «притязание».
- An optional **cold / no-context reviewer pass** (a reviewer given only the installment, no project
  framing) is worth running once per piece: it reliably catches scholarly-provenance slips, over-reach,
  and false friends that the project-anchored reviewers read past.
- **Independent convergence is the certainty signal.** When both reviewers, given no shared
  context, flag the *same span*, treat it as established and fix it rather than re-arguing it.
  Every convergent finding so far has been genuine — including the verdicts to **cut**: on §25 both
  independently returned "not publishable, cut both edits, use at most a forward pointer", in
  near-identical words, and each had caught a decisive defect the other missed.
- **Adjudicate a reviewer split against the primary source or against the corpus — never by
  preferring a reviewer.**
  When the pair disagrees about what Hegel (or a cited edition) actually says, go read it; one
  fetch usually settles it. When they disagree about **house style**, count the corpus: a §23
  emphasis split was decided by ten instances showing philosopher names bolded on first appearance
  and plain thereafter, which made one reviewer's stated premise simply false. Expect each reviewer
  to be *half* right. On §25 one reviewer had the
  correct Russian section heading and the wrong Spinoza wording while the other had the reverse,
  and the verified answer matched **neither** proposal in full — it also dissolved a mirror-vs-
  citation conflict both had reported as a forced choice. A split is therefore a signal to
  *check*, not to arbitrate. The remedy may also be neither reviewer's: a proposed Russian
  hyphenated calque for *that-it-is* was rejected because its first word is a homonym of an
  interrogative, inverting *Dass-sein* into *Was-sein*.
- **Verify a quotation before an argument leans on it.** Quote from the text, not from memory or
  from a reviewer's paraphrase, and confirm that any emphasis in the quotation is the source's
  own rather than silently supplied. A section *heading* is often the strongest available
  warrant — check whether the point is already titled before reconstructing it.
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

**What the checker cannot see.** It proves structure, not prose. Check these by hand every round:

- **Repetition across paragraphs** — the same figure, example, or cross-reference deployed twice
  in one installment. An n-gram sweep over the file catches what re-reading misses. (Beware
  fixed-width context regexes such as `.{130}pat.{130}` — they silently skip matches near line
  boundaries.)
- **An addition that contradicts a later section** — only a reader tracking the argument end to
  end will catch it; see *Additions to settled prose* above.
- **Smuggled canon violations.** Transition language is the recurring one: `§06` assigns
  *Übergehen* to Being, so a phrase like "must take in an *other*" is a category error inside the
  Doctrine of Essence, however natural it reads. When an addition describes a move, name the
  move's kind and check it against `§06`'s typology.
- **EN↔RU divergence** — run the mirror-parity audit documented in the Russian repo's `REVIEW.md`.

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
