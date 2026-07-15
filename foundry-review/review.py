#!/usr/bin/env python3
"""Cross-model review of a Hegel-synopsis installment via Azure AI Foundry.

Runs an agentic tool-loop against a Foundry-served chat model (e.g. grok-4.3,
DeepSeek-V4-Pro) so models *not* available in the GitHub Copilot CLI can act as
`synopsis-reviewer-*` critics. The model is given the project's governing review
docs and a small, repo-sandboxed toolset (read_file / grep / list_dir /
run_gate) — the same moves a human reviewer makes — and produces a review in the
REVIEW.md output format.

Review-only: this script never edits the synopsis. It prints (and optionally
saves) each model's findings; the author applies fixes in a separate session.

Endpoint/resource is user-specific (a fork uses a different Foundry resource), so
nothing is hardcoded. Resolve it from (in order): --endpoint, --resource,
$SOL_FOUNDRY_ENDPOINT (full URL), $SOL_FOUNDRY_RESOURCE (custom-domain name).
Auth is Microsoft Entra (AAD) only, via your `az login` — no API keys.

Usage (from repo root):
    pip install -r foundry-review/requirements.txt
    az login   # need "Cognitive Services User" on the resource
    $env:SOL_FOUNDRY_RESOURCE = "romanko-exp"
    python foundry-review/review.py \
        --target synopsis/24-appearance-*.md \
        --context synopsis/20-*.md synopsis/21-*.md synopsis/22-*.md synopsis/23-*.md \
        --model grok-4.3 --model DeepSeek-V4-Pro
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from azure.identity import AzureCliCredential

AAD_SCOPE = "https://cognitiveservices.azure.com/.default"
DEFAULT_API_VERSION = "2024-05-01-preview"
MAX_TURNS = 60
# Governing docs handed to the reviewer as the rubric it must apply.
GOVERNING_DOCS = [
    "REVIEW.md",
    ".github/copilot-instructions.md",
]

REVIEWER_ROLE = """\
You are a rigorous, high-signal external critic of the English Hegel synopsis in
this repository, standing in for the project's `synopsis-reviewer-*` two-vendor
review pair. You are a *fresh vendor* the author cannot get inside the GitHub
Copilot CLI, so your value is catching what the in-house Claude/GPT reviewers
rationalize away.

Do a full, independent review. Read the installment COLD and on-disk (via the
tools) — never from memory. Assume the author is attached to the current wording;
surface only objections that would survive a skeptical second reviewer:
dialectical-fidelity traps, cross-installment inconsistency, a missing
categorial-not-empirical guardrail where physics appears, broken cross-references,
and house-style breaks.

Operating rules:
- You are REVIEW-ONLY. You cannot and must not edit files. Report; the author
  applies.
- Governing docs are provided below (REVIEW.md and the Copilot instructions).
  REVIEW.md governs your severity rubric and output format — follow it exactly.
- Use the tools to READ THE ACTUAL FILES before judging: read the target
  installment in full, read every cross-referenced sibling you rely on, and run
  the mechanical gate (run_gate) — treat any gate failure as a Blocker.
- Verify every cross-reference (§NN), ordinal count, and "first/secured/located"
  claim by actually reading the cited installment. Do not trust memory.
- Flag retrofit ripple: if a claim here contradicts an earlier committed
  installment or a README, name the file and line.
- Tier each finding by severity (Blocker / High / Medium / Low / Optional) and
  mark it a *fix* or a *hold (rationale)*. Principled holds that defend fidelity
  to Hegel or house style are welcome.
- End in REVIEW.md's output format: 1) Verdict, 2) Verified checks, 3) Findings
  by severity, 4) Questions for the author, 5) Handoff. Be concise and specific;
  cite file paths and line numbers. Do not nitpick what the gate already covers.

When you have finished reading and are ready to deliver, STOP calling tools and
write the review as your final message.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file in the repository. Returns the file "
            "content with 1-based line numbers. Optionally restrict to a line range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repo-relative path, e.g. synopsis/24-....md"},
                    "start_line": {"type": "integer", "description": "1-based first line (optional)"},
                    "end_line": {"type": "integer", "description": "1-based last line, inclusive (optional)"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search file contents with a regular expression (Python re, "
            "case-insensitive). Returns matching lines as 'path:lineno: text'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Python regular expression"},
                    "glob": {"type": "string", "description": "Glob to limit files, e.g. 'synopsis/*.md' (default: synopsis/*.md and README.md)"},
                    "max_results": {"type": "integer", "description": "Cap on returned lines (default 80)"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and subdirectories under a repo-relative directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Repo-relative dir (default '.')"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_gate",
            "description": "Run the mechanical checker (tools/check-synopsis.js) and return "
            "its output. A failure is a Blocker.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class Repo:
    """Repo-sandboxed filesystem tools. All paths are confined under root."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def _resolve(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"path escapes repo: {rel}")
        return p

    def read_file(self, path: str, start_line: int | None = None, end_line: int | None = None) -> str:
        p = self._resolve(path)
        if not p.is_file():
            return f"ERROR: not a file: {path}"
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        lo = (start_line or 1) - 1
        hi = end_line if end_line is not None else len(lines)
        lo = max(lo, 0)
        hi = min(hi, len(lines))
        width = len(str(hi))
        out = [f"{i + 1:>{width}}  {lines[i]}" for i in range(lo, hi)]
        header = f"# {path} (lines {lo + 1}-{hi} of {len(lines)})\n"
        return header + "\n".join(out)

    def grep(self, pattern: str, glob: str | None = None, max_results: int = 80) -> str:
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"ERROR: bad regex: {e}"
        globs = [glob] if glob else ["synopsis/*.md", "README.md"]
        hits: list[str] = []
        for g in globs:
            for fp in sorted(self.root.glob(g)):
                if not fp.is_file():
                    continue
                rel = fp.relative_to(self.root).as_posix()
                for n, line in enumerate(fp.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{rel}:{n}: {line.strip()}")
                        if len(hits) >= max_results:
                            hits.append(f"... (truncated at {max_results})")
                            return "\n".join(hits)
        return "\n".join(hits) if hits else "(no matches)"

    def list_dir(self, path: str = ".") -> str:
        p = self._resolve(path)
        if not p.is_dir():
            return f"ERROR: not a directory: {path}"
        entries = []
        for c in sorted(p.iterdir()):
            entries.append(("d " if c.is_dir() else "f ") + c.relative_to(self.root).as_posix())
        return "\n".join(entries) if entries else "(empty)"

    def run_gate(self) -> str:
        try:
            r = subprocess.run(
                ["npx", "-y", "-p", "markdown-it@14", "node", "tools/check-synopsis.js"],
                cwd=self.root, capture_output=True, text=True, timeout=300, shell=(os.name == "nt"),
            )
            return (r.stdout + r.stderr).strip() or f"(no output; exit {r.returncode})"
        except Exception as e:  # noqa: BLE001
            return f"ERROR running gate: {e}"


# Some reasoning models (e.g. DeepSeek) stream their chain-of-thought into the
# final message `content` ahead of the formatted review. Trim to the Verdict head.
_VERDICT_RE = re.compile(r"^\s*(?:#{1,6}\s*)?\*{0,2}\s*1[.)]?\s*\*{0,2}\s*Verdict\b",
                         re.IGNORECASE | re.MULTILINE)


def clean_final(text: str) -> str:
    m = _VERDICT_RE.search(text)
    return text[m.start():].lstrip() if m else text


def dispatch(repo: Repo, name: str, args: dict) -> str:
    try:
        if name == "read_file":
            return repo.read_file(args["path"], args.get("start_line"), args.get("end_line"))
        if name == "grep":
            return repo.grep(args["pattern"], args.get("glob"), int(args.get("max_results", 80)))
        if name == "list_dir":
            return repo.list_dir(args.get("path", "."))
        if name == "run_gate":
            return repo.run_gate()
        return f"ERROR: unknown tool {name}"
    except Exception as e:  # noqa: BLE001
        return f"ERROR in {name}: {e}"


def resolve_endpoint(args) -> str:
    if args.endpoint:
        base = args.endpoint
    elif os.environ.get("SOL_FOUNDRY_ENDPOINT"):
        base = os.environ["SOL_FOUNDRY_ENDPOINT"]
    elif args.resource:
        base = f"https://{args.resource}.services.ai.azure.com"
    elif os.environ.get("SOL_FOUNDRY_RESOURCE"):
        base = f"https://{os.environ['SOL_FOUNDRY_RESOURCE']}.services.ai.azure.com"
    else:
        sys.exit(
            "No Foundry endpoint configured. Pass --resource <name> or --endpoint <url>, "
            "or set $SOL_FOUNDRY_RESOURCE / $SOL_FOUNDRY_ENDPOINT."
        )
    return base.rstrip("/")


def build_system_prompt(repo: Repo) -> str:
    parts = [REVIEWER_ROLE, "\n\n===== GOVERNING DOCS =====\n"]
    for rel in GOVERNING_DOCS:
        p = repo.root / rel
        if p.is_file():
            parts.append(f"\n----- {rel} -----\n")
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "".join(parts)


def build_first_user_msg(target: str, context: list[str]) -> str:
    lines = [
        f"Review the installment `{target}`. Read it in full first (read_file).",
        "",
        "Cross-referenced siblings you should consult as needed (read the spans you "
        "rely on; verify every §NN claim against them):",
    ]
    lines += [f"  - {c}" for c in context] or ["  (none supplied — discover via grep/list_dir)"]
    lines += [
        "",
        "Also read the target's README entry (grep the filename in README.md) and run "
        "the mechanical gate (run_gate) before delivering.",
        "",
        "Deliver a single review in REVIEW.md's output format. Do not edit anything.",
    ]
    return "\n".join(lines)


def review_one(model: str, base: str, api_version: str, token: str,
               system_prompt: str, first_user: str, repo: Repo,
               temperature: float, verbose: bool) -> str:
    url = f"{base}/models/chat/completions?api-version={api_version}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": first_user},
    ]
    for turn in range(1, MAX_TURNS + 1):
        payload = {
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": temperature,
        }
        resp = _post_with_retry(url, headers, payload)
        choice = resp["choices"][0]
        msg = choice["message"]
        finish = choice.get("finish_reason")
        tool_calls = msg.get("tool_calls") or []
        # Persist the assistant turn (strip reasoning to keep context lean).
        messages.append({
            "role": "assistant",
            "content": msg.get("content") or "",
            **({"tool_calls": tool_calls} if tool_calls else {}),
        })
        if tool_calls:
            for tc in tool_calls:
                fn = tc["function"]["name"]
                raw = tc["function"].get("arguments") or "{}"
                try:
                    a = json.loads(raw)
                except json.JSONDecodeError:
                    a = {}
                result = dispatch(repo, fn, a)
                if verbose:
                    preview = a if fn != "read_file" else {k: a[k] for k in a}
                    print(f"    [{model}] turn {turn}: {fn}({json.dumps(preview, ensure_ascii=False)}) "
                          f"-> {len(result)} chars", file=sys.stderr)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result[:60000],
                })
            continue
        # No tool calls -> final answer.
        if verbose:
            print(f"    [{model}] finished in {turn} turn(s), finish_reason={finish}", file=sys.stderr)
        return clean_final(msg.get("content") or "(empty response)")
    return f"(stopped after {MAX_TURNS} turns without a final review)"


def _post_with_retry(url, headers, payload, attempts=6):
    delay = 3.0
    last = None
    for i in range(attempts):
        r = requests.post(url, headers=headers, json=payload, timeout=300)
        if r.status_code == 200:
            return r.json()
        last = f"{r.status_code}: {r.text[:500]}"
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(delay)
            delay = min(delay * 1.8, 45)
            continue
        raise SystemExit(f"Foundry call failed ({last})")
    raise SystemExit(f"Foundry call failed after {attempts} attempts ({last})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-model Foundry review of a synopsis installment.")
    ap.add_argument("--target", required=True, help="Repo-relative installment to review (glob ok).")
    ap.add_argument("--context", nargs="*", default=[], help="Cross-ref sibling files (glob ok).")
    ap.add_argument("--model", action="append", default=[], help="Foundry deployment name (repeatable).")
    ap.add_argument("--repo", default=None, help="Repo root (default: parent of this script's dir).")
    ap.add_argument("--resource", default=None, help="Foundry custom-domain name (e.g. romanko-exp).")
    ap.add_argument("--endpoint", default=None, help="Full Foundry endpoint URL (overrides --resource).")
    ap.add_argument("--api-version", default=DEFAULT_API_VERSION)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--out-dir", default=None, help="If set, also write each review to <out-dir>/<model>.md.")
    ap.add_argument("--quiet", action="store_true", help="Suppress per-turn tool trace on stderr.")
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo_root = Path(args.repo).resolve() if args.repo else script_dir.parent
    repo = Repo(repo_root)

    def expand(patterns: list[str]) -> list[str]:
        out: list[str] = []
        for pat in patterns:
            matches = sorted(globmod.glob(str(repo_root / pat)))
            out += [Path(m).resolve().relative_to(repo_root).as_posix() for m in matches] or [pat]
        return out

    targets = expand([args.target])
    if len(targets) != 1:
        sys.exit(f"--target must resolve to exactly one file; got {targets}")
    target = targets[0]
    context = expand(args.context)
    models = args.model or ["grok-4.3", "DeepSeek-V4-Pro"]

    base = resolve_endpoint(args)
    token = AzureCliCredential(process_timeout=30).get_token(AAD_SCOPE).token
    system_prompt = build_system_prompt(repo)
    first_user = build_first_user_msg(target, context)
    verbose = not args.quiet

    if args.out_dir:
        Path(repo_root / args.out_dir).mkdir(parents=True, exist_ok=True)

    for model in models:
        print(f"\n{'=' * 78}\n== REVIEW — {model} — target {target}\n{'=' * 78}", flush=True)
        t0 = time.time()
        try:
            review = review_one(model, base, args.api_version, token, system_prompt,
                                 first_user, repo, args.temperature, verbose)
        except SystemExit as e:
            review = f"(FAILED: {e})"
        print(review, flush=True)
        print(f"\n-- {model}: {time.time() - t0:.0f}s --", flush=True)
        if args.out_dir:
            (repo_root / args.out_dir / f"{model}.md").write_text(review, encoding="utf-8")


if __name__ == "__main__":
    main()
