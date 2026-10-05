# Extracting the Concept, Not the Common Part

*A note from the road for friends and colleagues, with a worked software example — and an invitation to argue back.*

---

If you write code with other people, you will eventually find yourself in the conversation that goes like this. Two (or three, or seven) places in the codebase look suspiciously alike. Someone proposes pulling the shared bit out into a helper. Someone else worries that the resulting helper has no clear meaning, that its name is awkward (`utils2.processCommon`, `BaseStuffHandler`), that the parameters keep growing as new callers want slightly different behaviour. Sometimes the result is a helper that nobody loves and that future maintainers struggle to remove. Sometimes the discussion finds a responsibility with its own meaning in the domain, and the shared code acquires a reason to belong together. And sometimes a small, well-defined helper was all that was needed.

The difference is not just a stylistic preference. There is a useful question here that Hegel's *Logic* sharpens through its distinction between **the abstract universal** and **the concrete universal of the Concept**: have we merely selected a shared feature, or understood a principle connecting the differences? The software application is ours. A good design does not become Hegel's Concept merely by getting a domain name, and his Logic does not choose our architecture for us. This note tries to make the comparison earn its keep in a case — with the hope that you'll either nod or push back.

---

## The scene: two ways of "extracting the common part"

Here is the kind of case I mean. Suppose you have, in some order-management codebase:

- `Order.computeTax()` — walks the line items, applies category-specific rates, exempts certain customer classes, returns a `Money` value.
- `Invoice.computeTax()` — walks the line items, applies category-specific rates, exempts certain customer classes, returns a `Money` value.

The two methods look almost identical. You go to extract.

**Path A — extraction by resemblance.** You pull out the syntactically common bits. You produce something like:

```text
TaxUtility.computeFromLines(lines, customerClass, exemptionRules) -> Money
```

It works. The duplication is gone, and that is a real achievement. The function might already express a sound, limited calculation. But resemblance alone has not established that its callers need the same calculation. Trouble appears when differences are admitted without understanding them: an invoice needs a date of supply, an order has only an expected date, and the helper acquires an `isInvoice` branch plus dummy values for whichever parameters do not apply. A parameter is not itself the problem. The problem is that the shared operation no longer has one account of what its inputs mean.

**Path B — extraction by responsibility.** You ask: *what must remain the same, and why do these cases differ?* Suppose our simplified system uses the same rate schedule and exemption rules for order estimates and invoice calculations. An order supplies an expected date; an invoice supplies the recorded date of supply. The shared responsibility is **the calculation under a stated tax basis**, not the whole order or invoice. A `TaxCalculation` component takes line amounts and categories, customer tax status, and the applicable date; the callers remain responsible for establishing those inputs and distinguishing an estimate from an invoiced amount. Its contract can require that the same basis produces the same result and that exempt lines contribute zero tax. Those are rules we can explain and test, rather than consequences of the callers' names. If the two workflows actually require different rules, the proposed boundary must change.

Notice what this does *not* require: making `Order` and `Invoice` subclasses of `TaxableTransaction`. They are different documents, not automatically two species of one entity. Nor does it require a class rather than a function: the helper from Path A can become the right implementation once its contract is understood. The gain is a reasoned boundary — shared tax rules can change together without dragging the documents' unrelated lifecycles with them. That boundary earns its keep under these requirements; it does not promise dividends forever.

A second case. Two services retry network calls with exponential backoff. A shared `RetryUtil.tryWithBackoff(fn, opts)` can be exactly right: it can specify which failures permit another attempt, how delays grow, and when to stop. If the services must also limit the duration of a call or stop sending requests to a failing dependency, the responsibility becomes broader: *resilience policy*. Retry, timeout and circuit breaking answer different aspects of that problem, and a small **policy** abstraction may let the services configure their composition rather than reimplement it. The ordering and interaction of the strategies then need an explicit contract. This is a reason to investigate a richer abstraction, not to build a framework merely because several familiar strategy names can be listed.

A third, cautionary case. Two classes both have an `updatedAt` field and an `updatedBy` field. Someone reaches for `extends TimestampedEntity`. But on inspection, one `updatedAt` records "the last time an admin manually edited this record"; the other records "the last time this event was successfully propagated to subscribers." These are not the same event. The two shared field names do not establish a shared lifecycle. A base class that makes the events obey one update rule would tie unrelated change cycles together. The right move at that level is the *opposite* of extraction: leave the lifecycles separate, perhaps rename the fields. A lower-level timestamp or actor value type could still be useful; that is a different responsibility.

These cases can lead to a shared calculation, a *richer* policy, or a refusal to merge two lifecycles. They are not an exhaustive taxonomy. The thread running through them is: **"what code is shared?" begins the inquiry; "what makes it belong together, and what must stay different?" carries it forward.**

---

## The Logic behind it

Hegel criticizes the treatment of universality as merely what several things have in common: the **abstract universal** isolated from its relation to particularity (*Encyclopaedia* §§163–164). The synopsis [examines that criticism in detail](../synopsis/27-the-concept-universal-particular-and-singular.md#v-the-universal-free-power-not-the-common-element). It is not a dismissal of [empirical inquiry](../synopsis/01-from-school-logic-to-dialectic.md#3-empiricism), nor a claim that abstraction is useless. In our example, both records have line items: selecting that shared feature is accurate. What it does not establish is why the same tax rule applies, or which differences matter to its application. We have **a content selected by leaving differences aside**, not yet **a principle explaining their connection**. Such an abstraction can be precisely adequate to a limited job; the mistake is to demand that it explain what it has omitted.

Hegel's **concrete universal** makes the stronger demand that particularity belong to the universal's own determination, rather than be supplied as an external collection of cases. The [discussion of universal–particular–singular in synopsis 09](../synopsis/09-doctrine-of-the-concept.md#the-concept-proper-universal-particular-singular) develops this point: the universal is **not behind or above** the particular and singular, but their *inner unity*. Our software comparison borrows the demand to explain the differences. Exemption status and the applicable date determine different results under a tax rule; the names `Order` and `Invoice` alone do not. The record kinds must also be distinguished from a particular order or invoice. But neither this distinction nor a class-to-object relation by itself establishes Hegel's logical singularity. We have argued for a limited calculation boundary, not derived the full Concept or the existence of these business practices.

The syllogism sharpens the question of the connection. As [synopsis 29 explains](../synopsis/29-the-syllogism-mediation-and-the-threshold-of-objectivity.md), naming a middle term does not establish its explanatory force. Suppose the rule in our toy system taxes a non-exempt line of category A at 20% on its date of supply. This invoice records just such a line, with a net amount of 100; the tax on that line is therefore 20. The connection rests on the applicable rule and the facts making this line a case of it, not on naming the document a *Taxable Transaction*. A function can implement that connection perfectly well. This explains the result under the stipulated rule; it does not explain the rule's legal origin or derive its rate from logic. Nor does a sound conditional inference by itself establish Hegel's stronger account of rational mediation.

The [synopsis on Understanding and Reason](../synopsis/03-understanding-and-reason.md) supplies a further distinction. *Understanding* (*Verstand*) fixes determinations with indispensable precision; it is not a junior faculty to be replaced by *Reason* (*Vernunft*). In Hegel's account these are moments of one activity, and the dialectical moment exposes a determination's own limit before the speculative moment grasps the positive result (*Encyclopaedia* §§79–82). Our helper offers a modest comparison: it promises one shared operation, but accommodating incompatible meanings in its inputs undermines that promise. Recognizing this conflict gives a reason to revise the boundary, not merely a cue to invent a better name. A successful repair retains the valid calculation and the callers' distinct obligations while rejecting their misleading grouping. That is the point of comparison with [*Aufhebung*](../synopsis/02-with-what-must-science-begin.md#vi-what-this-teaches-the-structure-of-the-dialectical-step): preservation through a determinate correction, not keeping every earlier design choice.

One final connection. Hegel's unity of theoretical and practical cognition, discussed in the [synopsis on the Idea](../synopsis/09-doctrine-of-the-concept.md#cognition), is a systematic claim, not another name for an edit–test loop. Our narrower comparison is reciprocal correction: understanding directs an intervention, and the difficulties it encounters can expose a mistaken understanding. Attempting a refactoring can reveal that apparently identical calculations carry different obligations. But a change can also entrench a bad abstraction, and passing tests establish only what they cover. Refactoring properly preserves observable behaviour; correcting an erroneous business rule is a further change, not something to hide inside it. When the investigation succeeds, the code can begin to *say* something it was previously only doing. Its clearer structure makes the responsibility available for scrutiny rather than certifying it as finally understood.

---

## A working test: what justifies the extraction?

Three questions can help before extracting. They are prompts for evidence, not a certificate that you have found Hegel's concrete universal.

1. **Do the shared parts mean the same thing, and what gives them a reason to change together?** The tax calculation has a common rule under stated assumptions; the two timestamps record different events. Naming a responsibility helps expose the answer, but *TimestampedEntity* sounds perfectly respectable and can still conceal the wrong grouping.

2. **Can you state the contract and test it separately from the callers?** *TaxCalculation* must preserve the agreed basis of its result. A retry helper can likewise have a specified attempt budget, delay schedule and cancellation behaviour. These are genuine contracts, not privileges of a class called *ResiliencePolicy*. Which guarantees are required depends on the task: termination and telemetry are not universal properties of every policy.

3. **Does the abstraction preserve the differences that matter without acquiring unrelated responsibilities?** In the tax example, the callers establish different dates while sharing the calculation. In the resilience case, retry and circuit breaking need different behaviour and a clear account of their interaction. A parameter, branch, subtype or composed strategy may express a justified distinction. None proves self-particularization merely by its syntactic form.

Clear answers support a candidate extraction; they do not settle its cost, stability or scope. Try it against the actual caller obligations and likely changes, keeping the option of a smaller helper or no shared abstraction. If the answers wobble, sit with the code longer — or take the case to a colleague, or to Copilot, and have the argument out before committing.

---

## An invitation to argue with this — and with Copilot

Two requests for the friends and colleagues this is addressed to.

**First, push back.** I and the AI co-author who has been helping me build this synopsis (Copilot, a large-language-model assistant) have been working through Hegel's *Logic* and its bearing on scientific and technical practice. Many things in the synopsis will look strange on first reading, and some things may simply be wrong — either because Hegel is wrong, or because we are wrong about Hegel, or because the application to a present-day case (cosmology, software, biology, anything) is forced. *We would rather hear about it.* The synopsis is meant as a working document, not a tablet. If a passage seems either obscure or smuggled, please say so.

**Second, take a case to Copilot.** The most useful thing you can probably do with the synopsis is bring a real problem from your own work and ask whether the categorial moves it makes have anything to say about it. The "extract the concept, not the common part" example in this note came out of exactly such a conversation — a lunchtime argument with colleagues, brought back to the drafting table the next morning. Copilot is good at this kind of dialogue: you describe the case, you describe what feels wrong about the obvious solution, and the two of you work the problem through with the categorial vocabulary as a resource (not a weapon). You do not need to have read the synopsis cover to cover — Copilot can pull the relevant passages in as needed. What is needed is a case you actually care about and a willingness to be talked out of your first answer.

A thread the synopsis develops is that **understanding must be actively worked out, not merely handed over as a finished formula**. Its [comparison of Hegelian self-mediation with Marx's self-emancipation principle](../synopsis/09-doctrine-of-the-concept.md#self-emancipation-by-the-same-agent) is our comparison, not an identity of their subjects or a demonstrated historical derivation. The smaller lesson for this essay is participation in the inquiry. The people clarifying a codebase are not identical with the code, and an outside colleague can uncover what its authors have missed. What matters is that the proposed understanding be made answerable to the actual work, so the people using it can examine and revise it rather than inherit an impressive name.

If you have a refactoring you are undecided about, a design choice you keep arguing about with your team, a place where extraction by resemblance keeps biting you, or a place where you suspect a shared responsibility but cannot yet justify its boundary — that is exactly the kind of conversation we would like to be having.

---

*See also: the [main README](../README.md) for the full sequence of installments; [synopsis 06 (Orientation to the Logic)](../synopsis/06-logic-orientation.md) for the distinction between Hegel's grounding and our practical reconstruction; [synopsis 09 (Doctrine of the Concept)](../synopsis/09-doctrine-of-the-concept.md) for the overview; and the closer readings of [the Concept in synopsis 27](../synopsis/27-the-concept-universal-particular-and-singular.md) and [mediation in synopsis 29](../synopsis/29-the-syllogism-mediation-and-the-threshold-of-objectivity.md).*
