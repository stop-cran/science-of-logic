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
(`REVIEW.md` + `.github/copilot-instructions.md`) and a small, **repo-sandboxed** toolset —
`read_file`, `grep`, `list_dir`, `run_gate` — the same moves a human reviewer makes, then
returns a review in `REVIEW.md`'s output format.

## Review-only, by design

- It **prints** each model's review (and optionally writes `out/<model>.md`); it **never**
  edits, creates, or stages the synopsis. Apply fixes in a separate authoring session, per
  the project workflow (the same review → apply-with-judgment → commit loop as the in-CLI
  reviewers).
- The tools are **read-only and repo-confined**: every path is resolved under the repo root
  and rejected if it escapes; the only "write" is `run_gate`, which just runs the existing
  mechanical checker.

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

## The models must be deployed first

Unlike TTS (a served capability), chat models need an explicit **deployment** on the
resource. `grok-4.3` and `DeepSeek-V4-Pro` are `GlobalStandard` (pay-per-token, no idle
cost). Deploy once (Azure CLI), review as many times as you like, delete when done:

```powershell
$rg = "rg-temp-infrastructure-dashboard"   # user-specific: romanko-exp's resource group (adjust for your resource; find it via `az cognitiveservices account list`)
az cognitiveservices account deployment create --name romanko-exp --resource-group $rg `
    --deployment-name grok-4.3 --model-name grok-4.3 --model-version 1 --model-format xAI `
    --sku-name GlobalStandard --sku-capacity 200
az cognitiveservices account deployment create --name romanko-exp --resource-group $rg `
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
`az cognitiveservices account deployment delete --name romanko-exp --resource-group $rg --deployment-name grok-4.3`.

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
print to stdout; `--out-dir` also writes `out/<model>.md` (git-ignored). `--quiet` drops the
per-turn tool trace on stderr.

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
- Retries transient `429/5xx` with exponential backoff (no jitter); trims any leaked reasoning preamble down
  to the `Verdict` heading (`clean_final`).

## What it does NOT do

- Does **not** edit, create, move, or stage any synopsis file — report-only.
- Does **not** hardcode the endpoint/resource (user-specific) or use API keys (AAD only).
- Does **not** deploy models for you — deploy once via Azure CLI (above).
- Does **not** replace the in-CLI `synopsis-reviewer-claude` / `-gpt` pair or `REVIEW.md`'s
  rotation discipline; it **widens** the vendor set for a given round.
- Does **not** commit review outputs — `out/` is git-ignored (only the scripts are
  versioned).
- Does **not** review the Russian corpus yet (would need the nauka-logiki repo root via
  `--repo` and its own governing docs); English only for now.

## Verifying a change

- **Cheap smoke test** — one model, one context file:
  `python foundry-review/review.py --target 'synopsis/24-*.md' --context 'synopsis/23-*.md' --model grok-4.3`.
  A healthy run reads the target, reads the sibling, greps the README, runs the gate, and
  returns a `REVIEW.md`-format verdict in a handful of turns (~30–60 s).
- **Sandbox check** — the path guard is load-bearing: `read_file('../secret')` must return an
  "escapes repo" error, not the file.
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
- **401 / 403** — your identity lacks **Cognitive Services User** on the resource, or `az
  login` is stale.
- **`AzureCliCredential … timeout`** — warm the CLI once with
  `az account get-access-token --resource https://cognitiveservices.azure.com`; the script
  already uses `process_timeout=30`.
- **A reasoning model dumps its chain-of-thought before the review** (seen with
  `DeepSeek-V4-Pro`) — expected; `clean_final` trims everything before the `Verdict` heading.
  If a model uses a different first-heading than "1. Verdict", widen `_VERDICT_RE`.
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
