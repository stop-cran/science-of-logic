# Extracting the Concept, Not the Common Part

*A note from the road for friends and colleagues, with a worked software example — and an invitation to argue back.*

---

If you write code with other people, you will eventually find yourself in the conversation that goes like this. Two (or three, or seven) places in the codebase look suspiciously alike. Someone proposes pulling the shared bit out into a helper. Someone else worries that the resulting helper has no clear meaning, that its name is awkward (`utils2.processCommon`, `BaseStuffHandler`), that the parameters keep growing as new callers want slightly different behaviour. The discussion ends one of two ways: either with a helper that nobody loves and that future maintainers will fight to delete, or with the realization that what *is* common to those places is in fact a thing — a concept with its own meaning in the domain — and that the right move is to extract *that*, after which the original places fall back into their proper shape as particular cases of it.

The two outcomes are not stylistic preferences. They are categorially different operations, and the difference is exactly the one that runs through the *Logic* between **the abstract universal of empiricism** and **the concrete universal of the Concept**. This note is a short attempt to say why, with the hope that you'll either nod or push back — and either way, that you'll talk to Copilot about your own examples and see what shakes out.

---

## The scene: two ways of "extracting the common part"

Here is the kind of case I mean. Suppose you have, in some order-management codebase:

- `Order.computeTax()` — walks the line items, applies category-specific rates, exempts certain customer classes, returns a `Money` value.
- `Invoice.computeTax()` — walks the line items, applies category-specific rates, exempts certain customer classes, returns a `Money` value.

The two methods look almost identical. You go to extract.

**Path A — the empirical extraction.** You pull out the syntactically common bits. You produce something like:

```text
TaxUtility.computeFromLines(lines, customerClass, exemptionRules) -> Money
```

It works. The duplication is gone. But the helper has no domain meaning. It's a *thing that happens to be reused*, not a *thing in the world your code is about*. It tends to grow parameters as Order and Invoice diverge ("oh, but Invoice also needs a `dateOfSupply` for VAT timing"). Eventually it accretes flags (`isInvoice: bool`) and the abstraction begins to leak: callers pass in dummy values to satisfy parameters that don't apply to their case. The helper has become a coupling without a concept.

**Path B — the conceptual extraction.** You ask: *what is the thing whose tax is being computed?* Both `Order` and `Invoice` are kinds of *taxable transaction*. The taxable transaction has line items, a customer (with a tax-class), a date that determines the applicable rate schedule, and a computed tax — which is **its** tax, not somebody else's. You introduce `TaxableTransaction` (or whatever your domain language calls it). It has its own behaviour, its own invariants, its own tests. `Order` and `Invoice` become two particular kinds of taxable transaction, each with the additional content proper to it (an order is not yet a financial document; an invoice is). The duplication is gone, but more importantly: a thing with its own meaning has been recognized, and the original two now stand to it as singular instances stand to their universal.

The first extraction is over within minutes and creates a debt. The second extraction is sometimes harder to see and harder to land — but it pays interest indefinitely, because every future change to "how taxable transactions work" now has one place to live, and the meaning of that place is clear.

A second, more instructive case. Two services in your system both retry network calls with exponential backoff. The empirical extraction gives you `RetryUtil.tryWithBackoff(fn, opts)`. The conceptual one notices that what you actually have is *resilience policy*: retry is one of several strategies (also: circuit breaker, bulkhead, timeout, fallback), each carrying its own meaning, each composable, each with a name that any backend engineer recognizes. The right artifact is not a helper but a small **policy** abstraction, of which `Retry` is one instance and `CircuitBreaker` is another. The two services then *configure* their resilience rather than *implement* it.

A third, cautionary case. Two classes both have an `updatedAt` field and an `updatedBy` field. The empirical extractor reaches for `extends TimestampedEntity`. But on inspection, one `updatedAt` records "the last time an admin manually edited this record"; the other records "the last time this event was successfully propagated to subscribers." These are not the same thing. They share four fields and they share *no* concept. Extracting their commonality produces a fake universal that drags two unrelated change cycles into a single base class. The right move here is the *opposite* of extraction: leave them alone, perhaps even rename them so that nobody is tempted to merge them again.

These three cases — successful conceptual extraction, conceptual extraction that produces a *richer* abstraction than the call sites suggested, and a case where the right answer is no extraction at all — exhaust the typology I want to point at. The single thread running through all three is: **the question is never "what code is shared?"; it is always "is there a thing here?"**

---

## The Logic behind it

Hegel calls the first kind of universal — the one Path A reaches for — the **abstract universal**: "what is common to a class of things." This is the empiricist's notion of a universal, and the [synopsis treats it explicitly in the discussion of empiricism](../synopsis/01-from-school-logic-to-dialectic.md#3-empiricism) as one of the major historical-logical positions whose contradictions had to be worked through. The abstract universal is got by stripping away differences until what is left is shared. It is "red and round and yields juice" as the universal *fruit*, or "has lines and customer and exemption rules" as the universal *thing whose tax is computed*. The procedure works — but what it produces is **a content from which the differences have been removed**, not a content that **contains the differences within it as its own articulation**. That is why the abstract universal always feels thin, why its name is always awkward, and why it fights with new requirements: when a new difference shows up, the abstract universal has nowhere to put it except as a parameter or a flag.

Hegel calls the second kind of universal — the one Path B finds — the **concrete universal** or simply *the* universal of the Concept. The [discussion of universal-particular-singular in synopsis 09](../synopsis/09-doctrine-of-the-concept.md#the-concept-proper-universal-particular-singular) is the relevant passage. The concrete universal is **not behind or above** its instances; it is the *active inner unity that pervades and sustains a domain of differences*. The biological species is the standard example: not a list of features common to all dogs, but the inner principle that makes a dog a dog and that is fully present in every dog. *Taxable Transaction*, as a domain concept that genuinely lives in your codebase, is an example in the small: not the residue of subtracting Order from Invoice, but the active unity that makes both of them what they are, present in each of them as *this* taxable transaction.

The same point can be put in terms of the syllogism, which the [synopsis presents as the very form of explanation](../synopsis/09-doctrine-of-the-concept.md#the-syllogism-the-concept-rejoined-to-itself). A successful explanation finds a particular that genuinely mediates between a singular and a universal — a real middle term, not an arbitrary connector. *Taxable Transaction* mediates between this particular invoice (singular) and the universal of taxation (universal); it is a real middle term because it is what taxation *is being applied to* in the case at hand. *TaxUtility.computeFromLines* mediates nothing — it is a verb hanging in the air, a function whose only middle is that two callers happen to use it. The first is a syllogism with explanatory power; the second is a coincidence in code.

There is also a deeper reason why the empirical extraction tends to fail, and the [synopsis on Understanding and Reason](../synopsis/03-understanding-and-reason.md) gives the diagnosis. The empirical extraction is the work of *Understanding* (*Verstand*) alone — the fixing of common features, the formation of an aggregate. *Reason* (*Vernunft*) is what is needed to recognize that an aggregate has an inner unity which is a *thing*, not just a tendency. The "wait, is there a concept here?" pause that distinguishes a senior engineer's refactor from a junior's is exactly the moment when Understanding's work hands itself off to Reason. Done right, the result preserves everything Understanding had collected (this is the [moment Hegel calls *Aufhebung*](../synopsis/02-with-what-must-science-begin.md#vi-what-this-teaches-the-structure-of-the-dialectical-step) — preserved, negated, lifted), and gives it back articulated as the inner moments of a thing with its own name.

One final connection. The [synopsis on the Idea](../synopsis/09-doctrine-of-the-concept.md#cognition) emphasizes that theoretical and practical cognition are two moments of one process: the world that is to be understood is the same world that is to be transformed, and the activity of transforming it is itself a deepening of the understanding of it. Refactoring is the form this takes for a working programmer. A refactoring is a real act on the codebase (practical), but a *good* refactoring requires conceptual insight (theoretical) — and the practical act of attempting the refactor is itself how the conceptual insight is most often discovered. The reason the empirical extraction so often disappoints is that it tries to be practical without being theoretical: it does the work of merging without the work of recognizing what is being merged. The reason the conceptual extraction sometimes feels miraculous when it lands is that the act of finding the right concept is the act of changing the code in such a way that the code itself begins to *say* something it was previously only doing.

---

## A working test: do you have a concept?

Three quick questions you can ask before extracting anything. They are not hard rules; they are the test that distinguishes Path A from Path B in practice.

1. **Can you name the thing without referring to its callers?** *TaxableTransaction* passes; *OrderInvoiceCommonTaxBase* does not. If the only way to name your candidate abstraction is by listing the things that use it, you have an aggregate, not a concept.

2. **Does the thing have its own behaviour and its own invariants — and would you write its tests in isolation?** A real concept has a domain shape: things that are true of every instance of it, things you would test even if no caller existed. *ResiliencePolicy* has invariants (a policy must terminate, must be composable, must report observability data); *RetryUtil* has none beyond what its callers happen to need.

3. **When a new difference shows up between callers, do you reach for a flag or for a new particular kind?** A concrete universal articulates into particulars: *Retry*, *CircuitBreaker*, *Bulkhead* are kinds of *ResiliencePolicy*. An abstract universal accretes flags and parameters. If your candidate abstraction's first response to divergence is `if (isInvoice) ...`, you have built a coupling, not a concept. (This is Hegel's point that the concrete universal differentiates *itself* into its particulars; the abstract universal can only be partitioned from outside.)

If all three questions answer cleanly in the conceptual direction, extract. If even one wobbles, sit with the code longer — or take the case to a colleague, or to Copilot, and have the argument out before committing.

---

## An invitation to argue with this — and with Copilot

Two requests for the friends and colleagues this is addressed to.

**First, push back.** I and the AI co-author who has been helping me build this synopsis (Copilot, GPT-class large language model, currently Claude Opus 4.7) have been working through Hegel's *Logic* and its bearing on scientific and technical practice over the past several weeks. Many things in the synopsis will look strange on first reading, and some things may simply be wrong — either because Hegel is wrong, or because we are wrong about Hegel, or because the application to a present-day case (cosmology, software, biology, anything) is forced. *We would rather hear about it.* The synopsis is meant as a working document, not a tablet. If a passage seems either obscure or smuggled, please say so.

**Second, take a case to Copilot.** The most useful thing you can probably do with the synopsis is bring a real problem from your own work and ask whether the categorial moves it makes have anything to say about it. The "extract the concept, not the common part" example in this note came out of exactly such a conversation — a lunchtime argument with colleagues, brought back to the drafting table the next morning. Copilot is good at this kind of dialogue: you describe the case, you describe what feels wrong about the obvious solution, and the two of you work the problem through with the categorial vocabulary as a resource (not a weapon). You do not need to have read the synopsis cover to cover — Copilot can pull the relevant passages in as needed. What is needed is a case you actually care about and a willingness to be talked out of your first answer.

The whole synopsis is, in a sense, an extended demonstration that **the agent of clarification is identical with what is clarified** — that thinking comes to its own through its own work, not by being given to it from outside. (This is the Hegelian formulation [the synopsis closes with](../synopsis/09-doctrine-of-the-concept.md#self-emancipation-by-the-same-agent), and its materialist counterpart that Marx drew from it.) The same form holds in the small. Your codebase will not be conceptually clarified by anyone who is not already inside it. But the work of clarifying it can be helped along, sometimes decisively, by a partner who can see the form of what you are doing while you are doing it.

If you have a refactoring you are undecided about, a design choice you keep arguing about with your team, a place where the empirical extraction keeps biting you, or a place where you suspect the concept is right there but you cannot quite name it — that is exactly the kind of conversation we would like to be having.

---

*See also: the [main README](../README.md) for the full sequence of installments; in particular [synopsis 06 (Orientation to the Logic)](../synopsis/06-logic-orientation.md) for the framework the present note draws on, and [synopsis 09 (Doctrine of the Concept)](../synopsis/09-doctrine-of-the-concept.md) for the discussion of universal-particular-singular and the syllogism that this note applies to refactoring.*
