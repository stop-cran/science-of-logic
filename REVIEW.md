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

Round 7 turned the panel on **§03 itself** — a file amended twice by later installments but never
reviewed on its own — and held the split a **seventh** time, with the first *falsification* of a
certifying verdict. The fast vendor returned *publishable* on both facets; its fidelity pass
reported **zero findings** on the stated premise that the target contains "no direct quotations with
quotation marks present," so that the quotation-integrity check was "vacuously clean." §03 contained
four quoted spans. The premise was checkable and false, and the same vendor affirmatively certified
as "explicitly presented… the guardrails are in place" the very line that proved to be the round's
worst error: "this is precisely the sequence Hegel reconstructs in the Philosophy of Nature," where
the *Philosophy of Nature* proceeds **Mechanics–Physics–Organics** (§04), **mechanism–chemism–
teleology** is *logical* Objectivity (§27), and §03's own list was a third triad. The minority
vendor returned 3 Blockers, 5 Highs, 2 Mediums; **every one verified against the text, and none was
wrong.** Where earlier rounds showed a certification to be *unreliable*, this one shows one resting
on a false statement of fact about the file. That is the end of the argument for vote-counting.

**A narrowing retrofit must be checked against the whole file, not the lines it edited.** Round 6
carried §27's guardrail back into §03 at four lines. Round 7 found the retrofit *defeated three
lines away*: surviving universals — "every actual act of cognition," "the advance of any science,"
"precisely the sequence," "has had to learn the hard way" — simply overrode it. A disclaimer
standing beside an unrestricted assertion does not neutralize it. **Prefer cutting the universal to
adding another qualifier**, and after a narrowing pass grep the file for the quantifiers themselves,
not only for the deleted formulation.

**An early installment is the corpus's weakest point, and the panel has never seen it.** §03 was
written before §16, §17, §26 and §27 existed; each of those later fixed a result §03 had stated
loosely, and §03 kept the loose statement. Its three Blockers were all of this kind — a calculus
claim superseded by §16/§17, a move "beyond reciprocity" that §26 explicitly calls an empty mode of
representing, and a Nature-sequence attribution §04 and §27 jointly refute. **Schedule a regression
round on the early installments as the later ones land**; being cited by a newer file is not being
checked against it.

**The abstract is a propagation site, and it is the one that gets missed.** The scope fix touched
five places; four were found by reading, and the fifth — the installment's own opening abstract —
only by the mandatory grep for the deleted formulation. The abstract restates the whole argument in
a single very long line, so the eye slides over it and `view` truncates it. **Grep it explicitly by
its own text after every substantive change.** This is the third consecutive fix batch in which the
countermeasure grep caught a live residue that re-reading had passed.

Round 8 re-ran the panel on the repaired §03 and held the split an **eighth** time, with a **second
falsified certification** — and this one falsified on a *verification claim* rather than a countable
fact. The fast vendor's fidelity facet returned **zero findings at every severity** and certified
that "every forward/backward claim about §04, §06, §26, §27 [was] verified against the supplied
sibling text." The round's single Blocker was precisely a backward claim about §26. Round 7 showed a
certification resting on a false premise about the file; round 8 shows one resting on a false report
of work performed. The minority vendor raised the Blocker on all three facets independently — which
is **within-vendor correlation, not three confirmations**, and was treated as one finding — and was
**3-for-3** on every externally checkable claim it made.

**A retrofit ripples in both directions, and the countermeasure grep must cover the whole deleted
span.** The round-8 Blocker was manufactured by the round-7 repair. After rewriting §03's causality
paragraph, the grep ran on the *formula that motivated the fix* ("each substance is at once cause
and effect of every other") and cleared the corpus. It did not run on the other distinctive phrases
in the same deleted span — and §26 was quoting two of them verbatim, so that §26 now made a checkably
false statement about §03's text. Two rules follow. First: **when a fix deletes or rewrites a span,
grep every distinctive phrase in the span, not only the one that motivated the fix** — a sibling may
be quoting the part you did not think you were changing. Second: **the ripple runs both ways.** Ask
not only what the edited file quotes, but *who quotes the edited file*; grep the corpus for the
edited installment's own number and read every hit. Applying that rule in round 8 turned up a second
live ripple in §01 that reading had missed. A sibling that cites you is a sibling you can break.

Round 9 re-ran the panel on the twice-repaired §03 and produced a **third** void certification, the
first outright conflict between two facets, and the discovery that the repairs had themselves become
a defect. Nine fixes were accepted across §03 and §04; the minority vendor found all of them.

**Verify the check before declaring a round dead.** Round 9 was diagnosed as having died in flight
because `Get-Process python` returned nothing, and its output was wiped and the round relaunched. The
process is named **`python3.13`**; the check had been wrong for several rounds, and the original run
was very likely healthy and merely slow. Match on a pattern —
`Get-Process | Where-Object { $_.ProcessName -match 'python' }` — and before destroying any output,
read the `.log.out` files and count the reports on disk. A panel that looks dead is usually just
slow. Launch panels **detached**, so that a session teardown can never be what kills them.

**A certification that presupposes access the panel does not have is void, whether or not it happens
to be false.** The fast vendor's fidelity facet returned zero findings and certified that every
direct quotation had been "extracted and compared for verbatim fidelity." No edition of the primary
text is in the panel's context. The minority vendor stated that limit explicitly and **declined to
certify**, which is the correct behaviour. Three consecutive rounds have now produced a failed
certification: round 7 on a false premise about the file, round 8 on a false report of work
performed, round 9 on work that was not possible. Read what a certification claims to have *done*,
and ask whether the panel could have done it.

**A style facet can attack a fidelity repair, and a load-bearing hedge looks like accretion from the
outside.** The fast vendor's style facet proposed restoring, at `:19`, the exact unrestricted
universal that round 8's fidelity findings had forced out — offered as tightening flabby prose.
Before accepting any stylistic proposal, **check the line against the last two rounds' rulings on
it**; a qualification that reads as defensive throat-clearing may be the entire result of a previous
round. Conversely, the same facet was right that §03 asserted its ownership of the reconstruction
three separate times in one paragraph. Both observations are stylistic; only the history
distinguishes them.

**Repairs accrete, and a pile of disclaimers is itself a defect.** Rounds 7 and 8 answered scope
findings by adding qualifications, and by round 9 the paragraph introducing the four procedures
carried three overlapping statements that the reconstruction was the synopsis's own — which reads as
a review response left inside the essay. The standing rule to **prefer cutting a universal to adding
a disclaimer** has a corollary: when disclaimers have already accumulated, consolidate them into one
that carries every limit rather than adding a fourth. The same edit dropped a categorical negative
about Hegel for which no warrant could be found; an unsourced denial is a claim like any other.

**A correction ripples to whoever cites the corrected claim, not only to whoever quotes the corrected
words.** §27 established that fixed determinations are not the Understanding's fault but reason's
failure to go on, and §03 was amended to say so. §04 still credited §03 with "the characteristic
product of the Understanding" — a claim §03 now explicitly refuses, in a sentence sharing no
distinctive phrase with anything that had been edited. Phrase-grep cannot find this. **After changing
what an installment asserts, grep the corpus for its number and read what each citation says it
holds.**

### Round 10 — §02, with a ripple into §10

**Verify a suspected fabrication before dismissing it.** A reviewer grounded a complaint on §28. The
corpus has twenty-seven installments, and the finding was very nearly rejected as invention — but
§27 does forward-reference a §28 at four places, booking there the residue of a debt it only
half-discharges. The fact was sound; only the proposed remedy was misplaced. **A reference to an
installment not yet written is legitimate in this corpus, and the cheapest check — does the file
exist — is the wrong one.** The disposition that follows is now a standing category of its own:
**accept the fact, reject the remedy.** A reviewer can be right about what is wrong and wrong about
where to repair it, and the two judgements must be taken separately.

**A sibling can contradict itself, and the target inherits the contradiction.** §02 called *Dasein*
the "first concrete category" on §10's authority. §10 says so at :118 — and at :82 says Becoming
"is more concrete than either," then compares *Dasein* only to Being and Nothing, stepping around
Becoming. The defect was never §02's; it was §10 disagreeing with itself, and §02 faithfully
reproducing one side. Repairing the target alone would have preserved the error at its source.
**Checking an installment against its sibling is not enough; the sibling must be checked against
itself.** The fix — *the first concrete determination that stands*, the first result that *remains*
— was written into both files at once.

**A style facet attacked a fidelity repair for the second consecutive round.** One vendor's style
report proposed sharpening the very sentence another had ruled must be cut, and lightening a
qualification another had explicitly filed a Hold to preserve. Neither reviewer could see the
other's report; both were doing their assigned job. This is not vendor error but a structural
property of a facet panel, and it is now predictable rather than surprising. **Check every style
proposal against the last two rounds' rulings on the same line before acting on it.**

**Within-vendor correlation is not confirmation.** One model flagged the same line on all three
facets and the "first concrete" claim on two. That is one finding each, not three and not two. Both
were accepted — but on verification against §10 and against the named-philosopher list, never
because reports agreed. **The panel supplies candidates; the corpus supplies warrants.**

**Detect a file's conventions; do not carry them forward as an assumption.** This corpus was
believed to use typographic apostrophes, and exact-string edits were being defended against a hazard
that does not exist here: a full non-ASCII inventory of §02 returned em dashes, one section sign,
two en dashes and one umlaut — every apostrophe and quotation mark plain ASCII. **Inventory the
non-ASCII codepoints of the file you are about to edit.** It costs one command and it retires a
whole class of imagined risk — while revealing the real one, which is the em dash.

**The mechanical gate does not check that text is *sane*, only that it is well-formed — and a
generated script is a file PowerShell must first decide how to read.** An edit script written as
BOM-less UTF-8 was parsed as the ANSI codepage; every em dash, section sign and umlaut it carried
was double-encoded into the corpus, and the gate returned PASS on all twenty-seven files, because
mojibake is still valid UTF-8. The damage was visible only on re-reading the prose. **After any
scripted edit, re-read the changed lines as text, and audit for the double-encoding signature
(`\u00C2`, `\u00C3`, `\u00E2\u0080`) before staging.** Repair by reinterpretation must be applied
per line and guarded against the replacement character: a line mixing sound and corrupt characters
cannot be reinterpreted wholesale and has to be rebuilt from character codes. **A passing gate is
not evidence that an edit landed correctly; it is evidence of nothing more than what it measures.**

**A detached launcher reports its own sleep, never the panel's completion.** Waiting on the
notification wastes the interval; the interval is where the target file should be read in full, so
that adjudication rests on one's own reading rather than on the panel's account of it.

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

### Round 11 — §02 again, and a defect that no panel could have seen

The round-10 batch rewrote arguments rather than wording, which by the rule above earns a fresh
panel; round 11 was that panel. Five findings were accepted, six declined. The accepted five are
worth less than the three lessons the round produced about *how the ledger was read*.

**A reviewer's line numbers were right and the author's recollection was wrong.** The previous
round's log recorded that this vendor's citations "run about two low," and the first reflex was to
discount its numbering. A direct read of the file disproved that: the citations were exact. The
standing instruction — verify a cited line against the file before ruling — must be applied
symmetrically. **Treat your own memory of a line number as no more reliable than the reviewer's**,
and never carry a claim about a reviewer's accuracy forward as if it were a property of the vendor.

**A line number is not a stable key for a protection.** "§02:86 is protected" had been carried
over from round 10. It was false in the way that matters: :86 was the one consequence round 10 had
*not* narrowed, and it was the correct target. Protections must be keyed to the **claim or
sentence**, never to its address, because every accepted edit can move the address.

**An unnarrowed sibling in a numbered list is itself evidence.** Round 10 narrowed consequences 2
and 3 and left consequence 1 a bare universal. That asymmetry, noticed only on re-reading,
independently corroborated the reviewer. It is the practical form of the older rule that a
narrowing propagates by claim and not by phrase: after narrowing one member of a list, **read the
others for the same claim in different words.**

**The cited sibling was right and the citing original was wrong.** A propagation was urged from
§02 into §10:39–41. Reading §10 showed it already stated the point correctly — and that it cites
§02 as its source. The error ran the other way. **Never propagate on a reviewer's assertion
without reading the sibling; it may already contain the correction.**

**The panel cannot see `essays/`, and a repaired defect survived there.** The §02 repair removed
an account of the *Phenomenology* as a stripping-away leaving a residue. A bidirectional grep for
the deleted phrases — run across the whole repository, not merely `synopsis/` and `README.md` —
found the same error twice in a tracked essay that cites §02 as its authority. No reviewer could
have caught it: the essays are never in the panel's context. **The grep for deleted phrases is not
a formality after a fidelity repair; it is the only instrument that reaches the unreviewed parts
of the corpus. Run it repository-wide.** The essays are mirrored in Russian too, so such a repair
incurs a translation obligation as well as an English one.

**A style facet attacked a fidelity repair for the third consecutive round.** The proposal would
have restored the universal quantifier that round 10 had deliberately removed, in the name of a
firmer cadence. Declined, as in the two preceding rounds. The pattern is now regular enough to
state as procedure: **check every style proposal against the last two rounds' rulings on the same
claim before weighing its prose merits.** A style facet optimizes the sentence it is shown and
cannot know what the sentence cost.

**"Accept the fact, reject the remedy" was applied three times in one round** — including once
where the proposed rewrite was *more* editorial than the text it replaced, judged by the
reviewer's own stated criterion. The observation and the repair are separate objects and are
separately right or wrong.

**Describe the corpus; do not narrate its repair.** Two vendors independently objected to a clause
that located a qualification by where the exposition would later make it precise. The replacement
states the qualification's **content** instead. This had been settled once before, at §26, on the
same reasoning; two independent confirmations make it standing doctrine. A forward pointer is
legitimate when it is anchored in content and illegitimate when it narrates the document.

**Prefer the editing tool to a generated script for edits inside a line.** Every edit this round
was made directly, which sidestepped the double-encoding trap entirely and — because each
replacement lay wholly within one line — left every line ending untouched, so the Russian mirror's
1:1 parity survived the round without repair work.

### Round 12 — §10, and the twin a phrase-grep could not find

A regression panel on §10: two vendors across fidelity, generalist and style. Two Blockers, four
Highs and a scatter of smaller findings were accepted; five were declined. One vendor returned
"publishable" on two of the three facets and missed both Blockers.

**"Publishable" is not evidence of absence.** Both vendors read the same file against the same
rubric in the same round. One found two Blockers; the other found none, and said so twice. A clean
report is something a model produced, not a property of the text. **Never let a favourable verdict
retire a facet**, and never count verdicts across vendors.

**A "verified ✓" list can be false, and the vendor's own sibling facet may disprove it.** One
report certified the attribution of "the truth is the whole" as checked and sound; the same
vendor's generalist facet flagged that very sentence. The quotation is at §09:13, and the text
credited it to another installment in another section. **A claim marked verified is still a claim.
Check it like any other** — the more so when a sibling facet disagrees with it.

**A stored primary-text warrant turns a Question into a ruling.** The panel could only *ask*
whether the threefold gloss of *Aufhebung* was Hegel's own; it said as much, and deferred. The
stored quotation — "to sublate has a **twofold** meaning: it means to preserve, to maintain, and
equally it means to cause to cease" — settled it at once: the third face is the word's ordinary
sense of raising up, not Hegel's gloss. **Keep the primary-text warrants in the working set. They
convert the findings a panel cannot close into findings the author can.**

**A file can contradict itself twenty lines apart.** §10 argued conservation at :118 and :130
while calling *Dasein* a "residue" at :110, and set out three distinct modes of transition at :9
while universalizing a single collapse-model at :140. Eleven earlier rounds had read the file
without seeing either, because each read it a passage at a time. **Reading a file against itself,
end to end, is a distinct check** — not a by-product of reading it closely.

**A repaired defect has unpropagated twins. Grep for the claim, not the string.** §10:140 was the
twin, in different words, of the §02:52 over-generalization repaired in round 11. The section
mislabel repaired at six sites in §10 had a seventh in §11:11, reachable only by sweeping the
corpus for the *form* of the error. Conversely, a sweep for the bare word "residue" returned
twenty-three hits across fourteen files, of which twenty were correctly scoped and owed nothing.
**The same phrase is a defect in one place and doctrine in another; judge every hit by its claim.**

**A sweep that propagates nothing is still a result worth logging.** Recording that the
twenty-three hits were examined and that the defect was local spares the next panel from raising
it again and the next author from running the sweep again.

**One edit can discharge two findings.** The §10:130 attribution was reported once as the wrong
installment and once as the wrong section. It was a single error with a single repair.

**Accept the fact, reject the scope.** A High gathered three sentences under one charge of
over-generalization. One was the defect; the other two stated correct doctrine about sublation and
were held. **A finding's evidence and its extent are separately right or wrong** — the companion
to the older rule that an observation and its proposed remedy are separate objects.

**Verify the premise of a systematic-error hypothesis before acting on it.** Six wrong section
labels looked like the residue of an earlier restructuring, which would have made them a migration
to finish rather than slips to correct. One line elsewhere in the same file used the sections
correctly, and disproved it. The repair was the same either way; the entry in this log is not.

**A no-op edit is silent.** An edit whose search text and replacement text are identical reports
success and changes nothing. In a batch of ten it is invisible, and here it dropped a Blocker.
**Re-read the file after a batch; never count the tool's successes.**

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
