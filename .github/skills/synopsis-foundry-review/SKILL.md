---
name: synopsis-foundry-review
description: >-
    Get a cross-model review of an English synopsis installment from a chat model served
    through Azure AI Foundry (e.g. grok-4.3, DeepSeek-V4-Pro) — vendors not available inside
    the GitHub Copilot CLI. Use when the user wants a fresh-vendor `synopsis-reviewer-*`
    critique, an extra cross-model round on a §NN installment, or to run/fix
    foundry-review/review.py. Review-only: it prints findings; it never edits the synopsis.
user-invocable: true
---

# Synopsis cross-model review — Azure AI Foundry

Reusable orchestrator in the **science-of-logic** repo (`foundry-review/`) that runs a
Foundry-served chat model as a **`synopsis-reviewer-*` critic** over one installment. It
exists to add review vendors the **GitHub Copilot CLI can't route to** — `grok-4.3` (xAI),
`DeepSeek-V4-Pro`, etc. — so the two-vendor loop in `REVIEW.md` can be widened to three or
four genuinely different models. The model is handed the project's governing docs
(`REVIEW.md` + `.github/copilot-instructions.md`) and a small,
**review-corpus-sandboxed** toolset — `read_file`, `grep`, `list_dir`, `run_gate` — the same
moves a human reviewer makes, then returns a review in `REVIEW.md`'s output format.

## Review-only, by design

- It **prints** each model's review (and optionally writes
  `out/<target-stem>--<model>.md`); it **never** edits, creates, or stages the synopsis.
  Apply fixes in a separate authoring session, per the project workflow (the same review →
  apply-with-judgment → commit loop as the in-CLI reviewers).
- The tools are **read-only and review-corpus-confined**. The model may read only
  `synopsis/**/*.md`, `README.md`, `REVIEW.md`, and
  `.github/copilot-instructions.md`; `.git/`, unrelated worktree files, parent paths,
  absolute paths, and symlink escapes are rejected. The only execution tool is `run_gate`,
  which runs the existing mechanical checker.
- **Data boundary:** anything matching the allowlist is sent to the selected model even if
  it is uncommitted or git-ignored. Treat `synopsis/**/*.md` as publishable text and keep
  anything sensitive out of it.

## Endpoint / resource is user-specific — never hardcode it

Like the audiobook skill, the Azure AI Foundry resource is **user-specific** (a fork uses a
different resource). Nothing is baked in. Resolve it from (in order): `--endpoint`,
`--resource`, `$SOL_FOUNDRY_ENDPOINT` (full URL), `$SOL_FOUNDRY_RESOURCE` (custom-domain
name, from which `https://{resource}.services.ai.azure.com` is built). The current user's
resource is in **Copilot user memory** (subject *Azure TTS / MAI-Voice-2* — the same Foundry
account); recall it rather than assuming, or ask the user.

Auth is **Microsoft Entra (AAD)** only, via your `az login` — no API keys, no secrets.
Token scope `https://cognitiveservices.azure.com/.default`; you need at least **Cognitive
Services User** on the resource (the same role family the TTS pipeline uses).

If neither environment variables nor user memory identify the resource, discover it in the
user-selected subscription rather than scanning every accessible subscription:

```powershell
$subscription = "<subscription name or id>"
$sub = az account show --subscription $subscription --query id -o tsv
az cognitiveservices account list --subscription $sub `
    --query "[].{name:name, resourceGroup:resourceGroup, location:location, kind:kind}" -o table
```

Before describing a deployment as the "latest" model, compare the available regional model
version with the deployed version and provisioning state:

```powershell
az cognitiveservices model list --subscription $sub --location swedencentral `
    --query "[?contains(to_string(model.name),'DeepSeek')].{name:model.name, version:model.version}" -o table
az cognitiveservices account deployment list --subscription $sub `
    --name "<resource>" --resource-group "<resource-group>" `
    --query "[].{deployment:name, model:properties.model.name, version:properties.model.version, state:properties.provisioningState, capacity:sku.capacity}" -o table
```

## The models must be deployed first

Unlike TTS (a served capability), chat models need an explicit **deployment** on the
resource. `grok-4.3` and `DeepSeek-V4-Pro` are `GlobalStandard` (pay-per-token, no idle
cost). Deploy once (Azure CLI), review as many times as you like, delete when done:

```powershell
$resource = "<your-foundry-resource>"
$rg = "<its-resource-group>"
az cognitiveservices account deployment create --name $resource --resource-group $rg `
    --deployment-name grok-4.3 --model-name grok-4.3 --model-version 1 --model-format xAI `
    --sku-name GlobalStandard --sku-capacity 200
az cognitiveservices account deployment create --name $resource --resource-group $rg `
    --deployment-name DeepSeek-V4-Pro --model-name DeepSeek-V4-Pro --model-version 2026-04-23 `
    --model-format DeepSeek --sku-name GlobalStandard --sku-capacity 200
```

`--sku-capacity` is in **kTPM** (200 ⇒ 200 000 tokens/min); capacity 1 (1 000 TPM) is far
too small for a 27 KB installment plus siblings — the loop will 429 for minutes. One
deployment operation at a time (a second concurrent create returns `RequestConflict`).
Confirm the model is in-region first:

```powershell
az cognitiveservices model list --location swedencentral `
    --query "[?contains(to_string(model.name),'rok') || contains(to_string(model.name),'eepSeek')].{name:model.name, ver:model.version}" -o table
```

Delete a deployment when finished:
`az cognitiveservices account deployment delete --name $resource --resource-group $rg --deployment-name grok-4.3`.

## Prerequisites

- Python + `pip`; install `foundry-review/requirements.txt`.
- Azure CLI (`az`) with an active login and **Cognitive Services User** on the resource.
- Node.js + `npx` for the mandatory mechanical gate.
- A succeeded chat-model deployment with enough capacity for the installment and context.

## How to use

From the repo root (Windows PowerShell):

```powershell
pip install -r foundry-review/requirements.txt      # azure-identity, requests
az login                                             # Cognitive Services User on the resource
$env:SOL_FOUNDRY_RESOURCE = "<your-foundry-resource>"   # e.g. from user memory

# Review §24 with §20–§23 as cross-ref context, both models, save clean copies:
python foundry-review/review.py `
    --target 'synopsis/24-*.md' `
    --context 'synopsis/20-*.md' 'synopsis/21-*.md' 'synopsis/22-*.md' 'synopsis/23-*.md' `
    --model grok-4.3 --model DeepSeek-V4-Pro `
    --out-dir foundry-review/out
```

`--target` must glob to exactly one file. `--context` files are the siblings the reviewer is
told to verify cross-references against (it still reads the target in full and greps the
README itself). With no `--model`, it defaults to `grok-4.3` + `DeepSeek-V4-Pro`. Reviews
print to UTF-8 stdout; `--out-dir` also writes
`out/<target-stem>--<model>.md` (git-ignored), so successive installments do not overwrite
one another. The report is persisted before console printing. `--quiet` drops the per-turn
tool trace on stderr. `--read-timeout` controls the per-request timeout in seconds (default:
600). Every target and explicitly supplied context pattern must match an existing allowed
file; otherwise the command exits before authentication or paid model use.

### Configuration

| Flag / variable | Meaning |
| --- | --- |
| `--target` | Exactly one existing `synopsis/**/*.md` file; glob allowed |
| `--context` | Existing `synopsis/**/*.md` siblings; every supplied glob must match |
| `--model` | Foundry deployment name; repeatable |
| `--resource` / `SOL_FOUNDRY_RESOURCE` | Foundry custom-domain resource name |
| `--endpoint` / `SOL_FOUNDRY_ENDPOINT` | Full endpoint; overrides the resource name |
| `--repo` | Alternate repository root containing the same English corpus layout |
| `--api-version` | Model Inference API version (default `2024-05-01-preview`) |
| `--temperature` | Sampling temperature (default `0.2`) |
| `--read-timeout` | Per-request timeout in seconds (default `600`) |
| `--max-turns` | Agent/tool-loop ceiling per model (default `60`) |
| `--contract-retries` | Final-format correction attempts (default `2`) |
| `--out-dir` | Persist success or diagnostic output |
| `--quiet` | Suppress per-turn tool traces |

### Worked example — one supplemental DeepSeek pass

```powershell
# 1. Resolve the resource in the user-selected subscription.
$sub = az account show --subscription "<subscription>" --query id -o tsv
az cognitiveservices account deployment list --subscription $sub `
    --name "<resource>" --resource-group "<resource-group>" -o table

# 2. Run one report-only review with the preceding four installments as context.
python foundry-review/review.py `
    --target 'synopsis/25-*.md' `
    --context 'synopsis/21-*.md' 'synopsis/22-*.md' 'synopsis/23-*.md' 'synopsis/24-*.md' `
    --model DeepSeek-V4-Pro --resource "<resource>" `
    --out-dir foundry-review/out --quiet
```

A successful result contains the five ordered `REVIEW.md` sections (numbered or unnumbered)
and is saved as
`foundry-review/out/25-…--DeepSeek-V4-Pro.md`. The author then triages findings and applies
accepted fixes in a separate authoring session. Foundry reviews are supplemental external
passes governed by `REVIEW.md`'s rotation and stop rules; they do not replace the default
Claude + GPT first-review breadth pair.

## What it does

- Builds the reviewer **system prompt** from the vendor-neutral critic role plus the live
  text of `REVIEW.md` and `.github/copilot-instructions.md` (so the rubric never drifts from
  the repo).
- Seeds the first user turn with the target path and the cross-ref list, and instructs the
  model to read on-disk, verify every `§NN`, run the gate, and answer in `REVIEW.md` format.
- Runs an **agentic tool loop** (up to `MAX_TURNS`) against
  `POST {endpoint}/models/chat/completions` (Azure AI Model Inference API); executes each
  `read_file` / `grep` / `list_dir` / `run_gate` locally and feeds results back until the
  model stops calling tools and emits the review.
- Enforces the handoff contract before accepting a result: `run_gate` must have completed
  successfully, or its failure must be reported as a Blocker; the final response must
  contain the five ordered `REVIEW.md` sections, numbered or unnumbered. A noncompliant
  draft gets at most two correction attempts by default (`--contract-retries`).
- Retries transient `429/5xx`, request timeouts, and connection failures with exponential
  backoff (no jitter); trims any leaked reasoning preamble down to the `Verdict` heading
  (`clean_final`).

## What it does NOT do

- Does **not** edit, create, move, or stage any synopsis file — report-only.
- Does **not** hardcode the endpoint/resource (user-specific) or use API keys (AAD only).
- Does **not** deploy models for you — deploy once via Azure CLI (above).
- Does **not** replace the in-CLI `synopsis-reviewer-claude` / `-gpt` pair or `REVIEW.md`'s
  rotation discipline; it **widens** the vendor set for a given round.
- Does **not** commit review outputs — `out/` is git-ignored (only the scripts are
  versioned).

## Current limits

These are current capability boundaries, not permanent review-only invariants:

- Does **not** review the Russian corpus yet (would need the nauka-logiki repo root via
  `--repo` and its own governing docs); English only for now.
- The reviewer contract verifies the gate outcome and output structure, but philosophical
  judgment remains model-produced and author-checked rather than mechanically provable.

## Verifying a change

- **Regression suite** — run
  `python -m unittest discover -s foundry-review -p 'test_*.py'` from the repo root. It
  covers the corpus sandbox, fail-closed inputs, gate-result enforcement, output contract,
  timeout retry, and diagnostic naming.
- **Cheap smoke test** — one model, one context file:
  `python foundry-review/review.py --target 'synopsis/24-*.md' --context 'synopsis/23-*.md' --model grok-4.3`.
  A healthy run reads the target, reads the sibling, greps the README, runs the gate, and
  returns a `REVIEW.md`-format verdict in a handful of turns. Grok may finish in roughly
  30–60 seconds; a full DeepSeek reasoning review can take 5–12 minutes even at 200 kTPM.
- **Sandbox invariant** — exercise every path-taking surface. `read_file('../secret')`,
  `grep(..., glob='../*.md')`, and `list_dir('../')` must return errors; `.git/config` must
  also be rejected by `read_file` and `grep`. Allowed `synopsis/*.md` and `README.md`
  operations must still succeed.
- **Fail-closed input check** —
  `python foundry-review/review.py --target 'synopsis/99-nope-*.md' --model grok-4.3`
  must exit before Azure authentication with a "matched no files" error.
- **Contract check** — a mocked final response lacking a successful gate result (or a
  Blocker for a failed gate) or one of the five headings must be rejected or corrected,
  never persisted as a successful review. Numbered and unnumbered headings must both pass.
- **Auth check** — `az account get-access-token --resource https://cognitiveservices.azure.com`
  should return a token; a cold `az` on Windows can exceed the default 10 s credential
  timeout, so the script sets `process_timeout=30`.

## Troubleshooting

- **`No Foundry endpoint configured`** — set `$env:SOL_FOUNDRY_RESOURCE` (or
  `$env:SOL_FOUNDRY_ENDPOINT`), or pass `--resource` / `--endpoint`.
- **`DeploymentNotFound` / 404 on the model** — the deployment name in `--model` must match
  the `--deployment-name` you created (case-sensitive), and the deployment must be
  `Succeeded`.
- **Repeated 429 / very slow** — capacity too low; redeploy at `--sku-capacity 200`. The
  script backs off up to 6 attempts (exponential, no jitter), but 1 000 TPM cannot fit an installment.
- **Long response / `ReadTimeout`** — network timeouts are retried without discarding the
  local tool-loop state. The default per-request timeout is 600 seconds; use
  `--read-timeout 900` for unusually slow reasoning deployments rather than setting a short
  timeout that triggers duplicate requests.
- **`FAILED:` / turn ceiling** — expected operational failures exit nonzero and, with
  `--out-dir`, are written to `<target-stem>--<model>.failed.txt`; they are never written
  under the normal `.md` review filename. The default ceiling is 60 turns and can be changed
  with `--max-turns`. Contract correction is separately capped at two retries by default;
  the diagnostic file preserves the last rejected draft and its contract errors.
- **401 / 403** — your identity lacks **Cognitive Services User** on the resource, or `az
  login` is stale.
- **Windows console encoding error** — the runner configures stdout/stderr as UTF-8 and
  writes `--out-dir` reports before printing, so a console problem cannot discard a
  completed review.
- **`AzureCliCredential … timeout`** — warm the CLI once with
  `az account get-access-token --resource https://cognitiveservices.azure.com`; the script
  already uses `process_timeout=30`.
- **A reasoning model dumps its chain-of-thought before the review** (seen with
  `DeepSeek-V4-Pro`) — expected; `clean_final` trims everything before the `Verdict` heading.
  If a model uses a different label than "Verdict", widen `_VERDICT_RE`.
- **`run_gate` reports missing `node`/`npx`** — the checker needs Node on PATH (same
  prerequisite as the in-repo mechanical gate).
- **Tool arguments arrive malformed** — the loop tolerates non-JSON `arguments` (treats as
  `{}`); if a model persistently mis-forms calls, lower `--temperature` (default 0.2).

## Key facts / constraints

- Endpoint shape: `https://{resource}.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview`
  (Azure AI Model Inference API — provider-agnostic; grok and DeepSeek share it).
- Auth: AAD bearer, scope `https://cognitiveservices.azure.com/.default`.
- Models used here live in **swedencentral** as `GlobalStandard`: `grok-4.3` (format `xAI`,
  v1) and `DeepSeek-V4-Pro` (format `DeepSeek`, v `2026-04-23`).
- The tool surface is deliberately tiny and read-only; the reviewer's authority comes from
  `REVIEW.md`, which is injected live so this skill tracks the checklist automatically.
