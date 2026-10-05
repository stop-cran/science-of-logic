# Hard Core, Soft Shell: Automation That Stays Alive

*A note from the road for friends and colleagues, on consolidating repeatable work without losing the judgment that keeps it useful. With an invitation to argue back.*

---

Consider a practice with repeatable operations and changing conditions: deploying software, building an artifact, migrating data. There are two responsibilities worth distinguishing. One is **hard**: an executable procedure with defined inputs, state, preconditions and checks. It can branch, remember previous work and refuse an input; determinism does not mean doing the same thing regardless of what arrives. The other is **soft**: the judgment about whether the procedure and its contract remain adequate, and what should change when they do not. People exercise that judgment, sometimes with agents; a written skill records how the work is to be governed. These are roles, not two kinds of file: code can enforce policy, and prose can prescribe a fixed routine.

The craft is not just to split them. It is to split them **and keep them connected** — so that repeatable work is genuinely consolidated and those answerable for it can still judge and revise it. Get the connection wrong in one direction and the same procedure keeps being improvised; get it wrong in the other and a running tool is mistaken for a finished understanding of the work. Hegel's account of Objectivity sharpens this distinction between a mechanism and an adequate account of its place in a whole. The software application is ours: the categories do not prescribe an architecture or establish its reliability.

The occasion was concrete: a real skill — a written body of instructions an agent follows — that pulled its deploy steps into an owned script while reframing its list of invariants as "the contract any change to that script must preserve." What follows is the account a colleague and I landed on, offered in the hope you'll either nod or push back.

---

## Two ways to get it wrong

The thesis is easiest to see against two errors. Each preserves something valuable while neglecting what that achievement still depends on.

### Perpetual improvisation: vibe-coding as a way of life

The first error is to keep improvising work whose repeatable requirements are already understood. Each time a deploy is needed, you prompt an agent, it reads a prose description, it reconstructs the steps, it mostly works. Prose-guided exploration can help discover an unsettled procedure; it is not a necessary first stage of every automation. A known procedure can be implemented directly, and a one-off task may not warrant a reusable tool at all. The mistake is treating repeated reconstruction as an adequate substitute for a stable operation when the work calls for one.

The problem is not that prose preserves nothing: it can retain a specification, reasons and experience. The problem is that a procedure reconstructed on each run can vary where the contract requires consistency. A step gets omitted; a refusal becomes a guess; the handling of a partial failure changes. What has been learned remains available, but its execution has not been reliably consolidated. The achievement is *agility* and keeping judgment available. The limit appears when that very practice needs a **repeatable operation** it has not yet secured.

### Abandoned automation: treating execution as sufficient

The other error is to freeze the practice into a script and treat successful execution as sufficient evidence of continuing adequacy. A fully automated job can be entirely appropriate within a stable domain. The mistake is not that nobody intervenes on every run, but that nobody remains answerable when the domain, the requirements or the evidence changes.

Here Hegel's account of [**Mechanism**](../synopsis/09-doctrine-of-the-concept.md#mechanism) is useful without making every script identical with his category. Formal mechanism presents objects as independently subsisting while their connection and determination are external; its further development investigates how their independence is mediated. Hegel also expressly recognizes mechanical memory (*Encyclopaedia* §195, Addition). The objection is not to retaining state or acquiring a dependable operation, but to making mechanism the sufficient account of the whole. Our engineering checklist asks where a running procedure is being credited with more than it establishes:

1. **Autonomy within conditions.** The script can really run without a person reconstructing its steps. That achievement depends on inputs, interfaces, permissions and other conditions. Record the relevant dependencies rather than infer unconditional independence from unattended execution.
2. **Execution is not justification of the End.** A procedure can check whether a result meets a supplied contract. Performing that check does not by itself establish that the contract captures what the work requires. An exit code is useful when its meaning rests on adequate checks; it is not a substitute for identifying them.
3. **Memory is not automatically learning.** Logs, migration ledgers and adaptive mechanisms can retain experience and affect later runs. Their presence does not guarantee that a mistaken assumption will be recognized and corrected. Specify how relevant failures reach someone or something charged with investigating them.
4. **Appropriateness needs criteria.** Known preconditions and refusal rules belong in executable checks where they can be enforced. Cases outside those rules need a defined route for judgment, not improvisation disguised as success. The skill records the route and the limits of delegated decisions.
5. **Side effects need their own guarantees.** A half-applied deploy changes the world. Atomicity, rollback and idempotence are distinct requirements: all-or-nothing effects within a stated boundary, restoration where possible, and the same specified effect under repeated execution. They must be implemented in the execution path, directly or through suitable services, not merely promised in prose. Ordinary successful runs may leave recovery untested; repeated successful requests can also expose an idempotence defect. For high-impact changes, **check failure and repetition explicitly**, prioritizing by exposure, coverage and consequence. An irreversible effect cannot be made reversible by calling a later action a rollback; compensation has its own limits. If recovery fails, report the remaining state rather than imply success. This is a risk-based argument, not a deduction that these invariants always decay first.

The achievement is *consolidation*: a dependable means can free attention for work that needs judgment. The error is to treat that means as a sufficient account of the practice, even after the conditions of its adequacy have changed. A script with explicit safeguards is better automation, not less mechanical execution.

### The common diagnosis

Both errors isolate a part of the work from what makes it adequate. Their remedy is not a midpoint on a slider between prompting and code: it is a **maintained relation between judgment and execution**. The repeatable operation should not require continual reinvention; the authority to execute it should not exempt its contract from examination. These failures can occur at different points in one project's history, but that history is not a necessary route for every project.

---

## The take: retain the mechanism and its accountable connection

The resolution in our case is to **retain the executable mechanism while keeping its purpose, contract and revision accountable.** The skill names the owned tool, its requirements, the evidence of success and the response to failure; the tool implements the operations and enforceable safeguards. Its modifiability is a real engineering property, not a contradiction in terms. Neither artifact learns merely by existing: people and agents perform the investigation and make the changes. The **connection** must be available to the next person doing the work, rather than depend on an unwritten understanding held by the first author.

One instructive trajectory makes the connection concrete. It also shows where a comparison with the *Logic* helps, and where assigning another category would outrun the case:

1. **Explore the procedure.** The agent works from a prose description while the requirements are still being clarified. Preserve what is learned, including unsuccessful attempts and the reasons for refusing an action.

2. **Find the limit of repeated reconstruction.** Suppose the practice requires the same approved operation, but reconstructing it on each run keeps changing a required step. The discrepancy is between the practice's own requirement and its execution, not between prose and an external preference for code. That supplies a reason to consolidate the operation, while retaining the judgment needed to specify it.

3. **Extract an owned artifact.** Put the repeatable operation and its enforceable checks into a tool, with an explicit interface and contract. This secures an executable procedure, not immunity from bugs or changing conditions. Hegel's [realization of the Concept as Objectivity](../synopsis/09-doctrine-of-the-concept.md#iii-objectivity) concerns a logical development, not the manufacture of a program from a description. The relevant comparison with mechanism is the achieved operation and the limits of treating it as independently sufficient.

4. **Find what an error means.** A failure can expose a bug, a changed interface, an inadequate contract, or a correct refusal of an inadmissible request. The script should perform the specified runtime handling; the skill should route the evidence for diagnosis and any authorized repair. Dependence on an environment does not by itself establish [**Chemism**](../synopsis/09-doctrine-of-the-concept.md#chemism). Hegel's chemical objects have a specific affinity, and their process subsides in a neutral product that does not itself sustain renewed differentiation (*Encyclopaedia* §§200–203). An error report has not demonstrated that structure. We need the diagnosis, not a chemical rung to complete a ladder.

5. **Make the means answer to the purpose.** [**Teleology**](../synopsis/09-doctrine-of-the-concept.md#teleology) supplies the stronger comparison: Hegel retains mechanical and chemical processes as means through which the End realizes itself (*Encyclopaedia* §§206–209). Their regularity is used, not abolished. Suppose a local catalog publication must expose either the old complete catalog or the new complete catalog, never a half-written one. Under a storage interface supporting atomic replacement, a tool can prepare and check the candidate before replacing the active file. Injecting a failure before replacement and checking that the old catalog remains active tests a relevant part of that contract. This is a publication guarantee against process interruption, not power-loss durability or atomicity for every side effect of a deployment. The purpose directs the implementation and its checks; the result supplies evidence for retaining or revising the design.

What is retained is not an unchanging script opposed to a permanently fluid skill, but reliable operations within a practice capable of examining their adequacy. A sound tool may remain unchanged for a long time. Keeping a route for correction is not an obligation to keep changing it.

---

## The bonus: the practice that improves itself

There is a further turn that is easy to miss. An investigation can improve the *script*, but it can also reveal a mistaken requirement or a missing decision in the **skill**. When the lesson applies more widely, it may improve the **methodology** under which several skills are maintained. These are different claims with different scopes: a bug fix is not automatically a new deployment policy, and a local policy is not automatically a general principle. The practice learns about its own practice when those responsible examine the reasons for its rules, not merely repair deviations from them.

The [**Idea**](../synopsis/09-doctrine-of-the-concept.md#iv-the-idea) raises a further question; it is not a status this loop has thereby earned. An externally assigned purpose can be to maintain a workflow indefinitely. Adding feedback does not by itself make the purpose **immanent**, and persistence does not establish adequacy. In Hegel's [**Life**](../synopsis/09-doctrine-of-the-concept.md#life), differentiated members sustain the living whole through which they are what they are; its development includes assimilation and the genus process, not simply one organism continuing to exist. [**Cognition**](../synopsis/09-doctrine-of-the-concept.md#cognition) is a further determination, not another name for maintenance. Our narrower comparison is reciprocal correction: understanding directs an intervention, and its results can expose a mistaken understanding. A practice can also preserve an inadequate purpose very efficiently. Its revision may require changing that purpose, or ending the practice, rather than making its own survival an end in itself.

A word of restraint belongs here. A successful case can suggest a **candidate** principle; a second, substantially different case can test whether it works for the reason we think. Neither count establishes necessity. Hegel's [critique of induction and analogy](../synopsis/29-the-syllogism-mediation-and-the-threshold-of-objectivity.md) asks what connects the instance and its property, rather than treating a list as the explanation (*Encyclopaedia* §§190–192). Our practical rule is to state the proposed connection, its conditions and possible counterexamples, and let the strength of the evidence govern adoption. A single decisive failure may already justify correcting a rule; there is no requirement to wait for a second disaster. Continued empirical testing is not by itself the [spurious infinite](../synopsis/13-finitude-and-the-true-infinite.md). The mistake is expecting accumulation alone to supply the ground it leaves unexplained. Provisional methodological adoption is a real achievement without being proof of Hegel's concrete universal.

---

## A short test before you split

Three questions to ask before pulling a repeatable operation out of a skill (or a step out of your own hands):

1. **Can you state what the artifact must preserve, and under which conditions, without merely reciting its implementation?** That gives changes a criterion beyond reproducing the current steps. Distinguish requirements from implementation choices, while retaining any genuinely required constraint on how the work is done. Revisit the distinction when the contract changes; do not let a description of existing behaviour quietly replace the reason for requiring it.

2. **Can the result be checked against criteria not inferred from whatever the script happened to do?** Reading a write back can establish a genuine postcondition: the required value is present at the approved target. But reading back the same value at the wrong target does not establish that the deployment was correct. What matters is the source of the expected target and state, the evidence collected, and the scope of the claim — not whether the checker occupies a separate process. The skill should require the check and identify its criterion and implementation. It can invoke a shared checker rather than duplicate that code in prose. An exit code may summarize those checks; find out which ones before treating it as sufficient evidence.

3. **Can a justified lesson change the skill or methodology, not only the script?** Name who may revise the contract and how the evidence reaches them. A defect in the means can require a code fix; a defect in the requirement can require changing the rule. Preserve that distinction rather than making every failure trigger both. The possibility of correction matters more than the frequency of edits.

---

## Coda: what can outlive a project

There is a reason to care about this beyond any one deploy. **Projects come and go.** An articulated lesson can travel beyond the occasion that taught it, provided its grounds and limits remain applicable. So can code: a well-defined tool can serve another project, while a once-useful methodology can become obsolete. Hegel's own example complicates any simple ranking of purposes above instruments: the plough remains useful after the immediate enjoyments it procures have passed (*Science of Logic*, §1615). This does not make tools immortal; it makes their durability a question about what they preserve and under which conditions.

The [companion note](2026-04-28-extracting-the-concept.md) supplies the same discipline: a proposed abstraction must explain what belongs together and what must stay different; a modest shared function may be the right result. Writing experience into a methodology does not turn it into a self-grounding universal, and [true infinity](../synopsis/13-finitude-and-the-true-infinite.md) is not longevity. Hegel's account of method in the Absolute Idea contains the developed content of the *Logic*, not a transferable checklist (*Encyclopaedia* §237). What we can preserve here is more modest and still worth having: the operation, the reasons for its contract, the evidence of its limits, and a way to reconsider them together in new work.

---

## An invitation to argue with this — and with Copilot

Two requests for the colleagues this is addressed to.

**First, push back.** Copilot, the AI co-author of this synopsis, and I have been working through Hegel's *Logic* and its bearing on technical practice. The proposal here is to consolidate suitable operations while preserving accountable judgment of their purpose, contract and results. The practical advice must stand on the requirements and evidence of the case. Hegel's distinctions help us ask why a successful means is not a sufficient account of the whole, and why revising the means differs from examining the end. They have not supplied a universal history of automation, a ranking of regressions, or proof that a feedback loop is the Idea. If the comparison obscures more than it clarifies, we would rather hear it.

**Second, bring a real case.** If you have a skill, a pipeline, a build, or a manual step you are deciding whether to extract into a tool — or one you already extracted that keeps drifting — describe the procedure, its requirements and what actually happens. The investigation may call for a better tool, a clearer contract, different ownership, or no extraction at all. Do not decide the diagnosis from the vocabulary in advance. You do not need to have read the synopsis; Copilot can bring relevant passages into the conversation, with their grounds and limits open to inspection.

The thread, here as in the companion note, is that **understanding must be made answerable to the work**. A team can learn a well-founded rule from outside; an outside colleague can see what its authors have missed. The point is not to rediscover everything for oneself, but to make the reasons and evidence available to those using the rule. That is how a useful inheritance can remain open to correction rather than harden into an unexplained maxim.

---

*See also: the [main README](../README.md) for the full sequence of installments; [synopsis 09 (Doctrine of the Concept)](../synopsis/09-doctrine-of-the-concept.md) for the distinctions compared with this case; [synopsis 13 (Finitude and the True Infinite)](../synopsis/13-finitude-and-the-true-infinite.md) for infinity as more than indefinite continuation; [synopsis 29 (The Syllogism)](../synopsis/29-the-syllogism-mediation-and-the-threshold-of-objectivity.md) for induction, analogy and their explanatory demands; and the companion note [Extracting the Concept, Not the Common Part](2026-04-28-extracting-the-concept.md).*
