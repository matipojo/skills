#!/usr/bin/env python3
"""sober-up eval: replay stuck conversations, inject a skill version, count how often the agent sobers up.

Every conversation lives once, provider-neutral, in cases/*.json. The adapters below render the same
text for Anthropic and OpenAI. Arms differ only in the last user message:
  control    the final message alone
  base       skill (usually main's SKILL.md) + the final message
  candidate  skill (usually the PR's SKILL.md) + the final message

Usage:
  python run.py --base main.md --candidate pr.md            # compare two skill versions
  python run.py --base SKILL.md --control                   # skill vs no skill
  python run.py --base main.md --candidate pr.md --dry-run  # write request bodies, call nothing
Keys: ANTHROPIC_API_KEY (Claude models and the judge), OPENAI_API_KEY (GPT models, optional).
"""
import argparse, concurrent.futures as cf, datetime as dt, hashlib, json, os, platform, re, subprocess, sys, threading
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREAMBLE = "Here is a skill you should apply now:\n\n"
ANTHROPIC_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
OPENAI_MODELS = ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna"]
JUDGE_MODEL = "claude-haiku-5-5"
MAX_TOKENS = {"anthropic": 4000, "openai": 6000}  # a ceiling, not a cost: billing is on tokens actually generated
EPHEMERAL = {"type": "ephemeral"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_skill(path):
    text = Path(path).read_text(encoding="utf-8")
    return re.sub(r"\A---\n.*?\n---\n\s*", "", text, flags=re.S).strip()  # drop YAML frontmatter


def provider(model):
    return "anthropic" if model.startswith("claude-") else "openai"


# ---------- adapters: one neutral case -> provider request ----------

def anthropic_request(case, skill, model, max_tokens):
    msgs = []
    for t in case["history"]:
        if t["role"] == "tool":
            role, content = "user", [{"type": "tool_result", "tool_use_id": t["id"], "content": t["output"], "is_error": t.get("is_error", False)}]
        else:
            role = t["role"]
            content = [{"type": "text", "text": t["text"]}] if t.get("text") else []
            content += [{"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["args"]} for c in t.get("tool_calls", [])]
        if msgs and msgs[-1]["role"] == role:
            msgs[-1]["content"] += content
        else:
            msgs.append({"role": role, "content": content})
    # Breakpoint 1: end of the shared history. Every arm and every replicate of this case reads it.
    msgs[-1]["content"][-1]["cache_control"] = EPHEMERAL
    final = []
    if skill:
        # Breakpoint 2: end of the skill block. The N replicates of this arm read it.
        final.append({"type": "text", "text": PREAMBLE + skill + "\n\n", "cache_control": EPHEMERAL})
    final.append({"type": "text", "text": case["final"]})
    if msgs[-1]["role"] == "user":
        msgs[-1]["content"] += final
    else:
        msgs.append({"role": "user", "content": final})
    req = {"model": model, "max_tokens": max_tokens, "system": [{"type": "text", "text": case["system"]}], "messages": msgs}
    if case["tools"]:
        req["tools"] = [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in case["tools"]]
    return req


def openai_request(case, skill, model, max_tokens, cache_key):
    msgs = [{"role": "system", "content": case["system"]}]
    for t in case["history"]:
        if t["role"] == "tool":
            msgs.append({"role": "tool", "tool_call_id": t["id"], "content": t["output"]})
        elif t.get("tool_calls"):
            msgs.append({"role": "assistant", "content": t.get("text") or None, "tool_calls": [
                {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": json.dumps(c["args"])}}
                for c in t["tool_calls"]]})
        else:
            msgs.append({"role": t["role"], "content": t["text"]})
    final = ([{"type": "text", "text": PREAMBLE + skill + "\n\n"}] if skill else []) + [{"type": "text", "text": case["final"]}]
    msgs.append({"role": "user", "content": final})
    req = {"model": model, "max_completion_tokens": max_tokens, "messages": msgs,
           # OpenAI caches prefixes automatically; the key routes all replicates of a cell to the same cache.
           "extra_body": {"prompt_cache_key": cache_key}}
    if case["tools"]:
        req["tools"] = [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
                        for t in case["tools"]]
    return req


# ---------- calling ----------

class Caller:
    def __init__(self):
        self._a = self._o = None
        self.lock = threading.Lock()
        self.usage = defaultdict(lambda: defaultdict(int))

    def anthropic(self):
        if self._a is None:
            import anthropic
            self._a = anthropic.Anthropic(max_retries=8)
        return self._a

    def openai(self):
        if self._o is None:
            import openai
            self._o = openai.OpenAI(max_retries=8)
        return self._o

    def _add(self, model, **kw):
        with self.lock:
            for k, v in kw.items():
                self.usage[model][k] += v or 0

    def call(self, prov, req, label=None):
        """Return (reply_text, stop_reason). Usage is tallied under label (default: the model)."""
        model = label or req["model"]
        if prov == "anthropic":
            r = self.anthropic().messages.create(**req)
            u = r.usage
            self._add(model, calls=1, input=u.input_tokens, cache_write=u.cache_creation_input_tokens,
                      cache_read=u.cache_read_input_tokens, output=u.output_tokens)
            parts = [b.text if b.type == "text" else f"[TOOL_CALL {b.name} {json.dumps(b.input)}]"
                     for b in r.content if b.type in ("text", "tool_use")]
            return "\n".join(p for p in parts if p).strip(), r.stop_reason
        r = self.openai().chat.completions.create(**req)
        u = r.usage
        cached = getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0
        self._add(model, calls=1, input=u.prompt_tokens - cached, cache_read=cached, output=u.completion_tokens)
        m = r.choices[0].message
        parts = [m.content or ""] + [f"[TOOL_CALL {c.function.name} {c.function.arguments}]" for c in (m.tool_calls or [])]
        return "\n".join(p for p in parts if p).strip(), r.choices[0].finish_reason


def judge_request(case, reply):
    j = case["judge"]
    crit = "\n".join(f'- "{k}": true if {v}' for k, v in j["criteria"].items())
    system = (f"You grade one reply written by an AI agent.\n\nContext: {j['context']}\n\n"
              f"Answer each criterion with true or false:\n{crit}\n\n"
              f"Return only a JSON object with exactly these keys and boolean values: {', '.join(j['criteria'])}.")
    return {"model": JUDGE_MODEL, "max_tokens": 1500,
            "system": [{"type": "text", "text": system, "cache_control": EPHEMERAL}],  # same rubric for every reply of a case
            "messages": [{"role": "user", "content": [{"type": "text", "text": f"The agent's reply:\n<<<\n{reply}\n>>>"}]}],
            "extra_body": {"output_config": {"effort": "low"}}}


def verdict(case, labels):
    p = case["judge"]["pass"]
    return all(labels.get(k) for k in p.get("all", [])) and not any(labels.get(k) for k in p.get("none", []))


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, help="SKILL.md to compare against (usually main)")
    ap.add_argument("--candidate", help="SKILL.md under test (usually the PR)")
    ap.add_argument("--control", action="store_true", help="also run a no-skill arm")
    ap.add_argument("--models", help="comma-separated; default: Claude models, plus GPT models when OPENAI_API_KEY is set")
    ap.add_argument("--cases", help="comma-separated case names; default: all")
    ap.add_argument("-n", type=int, default=10, help="replicates per cell (default 10)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", help="output directory")
    ap.add_argument("--no-judge", action="store_true", help="save replies only")
    ap.add_argument("--dry-run", action="store_true", help="write the request bodies and exit without calling any API")
    a = ap.parse_args()
    if not a.candidate and not a.control:
        ap.error("give --candidate, --control, or both")

    arms = {}
    if a.control:
        arms["control"] = None
    arms["base"] = load_skill(a.base)
    if a.candidate:
        arms["candidate"] = load_skill(a.candidate)
    case_files = sorted((HERE / "cases").glob("*.json"))
    if a.cases:
        wanted = a.cases.split(",")
        case_files = [p for p in case_files if p.stem in wanted]
    cases = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in case_files}
    models = a.models.split(",") if a.models else ANTHROPIC_MODELS + (OPENAI_MODELS if os.environ.get("OPENAI_API_KEY") else [])
    out = Path(a.out or HERE / "results" / dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    out.mkdir(parents=True, exist_ok=True)

    def build(model, cname, arm):
        prov = provider(model)
        skill = arms[arm]
        if prov == "anthropic":
            return prov, anthropic_request(cases[cname], skill, model, MAX_TOKENS[prov])
        key = "sober-up/%s/%s/%s" % (cname, arm, hashlib.sha256((skill or "").encode()).hexdigest()[:12])
        return prov, openai_request(cases[cname], skill, model, MAX_TOKENS[prov], key)

    manifest = {
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "models": models, "n": a.n, "arms": list(arms), "judge_model": None if a.no_judge else JUDGE_MODEL,
        "sha256": {"run.py": sha256(__file__), "base": sha256(a.base), **({"candidate": sha256(a.candidate)} if a.candidate else {}),
                   **{f"cases/{p.name}": sha256(p) for p in case_files}},
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip() or None,
        "github_run": "%s/%s/actions/runs/%s" % (os.environ["GITHUB_SERVER_URL"], os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_RUN_ID"])
                      if os.environ.get("GITHUB_RUN_ID") else None,
        "python": platform.python_version(),
    }

    if a.dry_run:
        d = out / "requests"; d.mkdir(exist_ok=True)
        for m in models:
            for c in cases:
                for arm in arms:
                    prov, req = build(m, c, arm)
                    (d / f"{m}__{c}__{arm}.json").write_text(json.dumps(req, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        print(f"dry run: {len(list(d.iterdir()))} request bodies in {d}")
        return

    for m in models:
        if provider(m) == "openai" and not os.environ.get("OPENAI_API_KEY"):
            sys.exit(f"{m} needs OPENAI_API_KEY")
    if any(provider(m) == "anthropic" for m in models) or not a.no_judge:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY is required (Claude models and the judge)")
    for name in ("anthropic", "openai"):
        try:
            manifest[f"{name}_sdk"] = __import__(name).__version__
        except Exception:
            pass

    caller = Caller()

    def one(job):
        m, c, arm, i = job
        prov, req = build(m, c, arm)
        row = {"model": m, "case": c, "arm": arm, "i": i}
        try:
            row["reply"], row["stop"] = caller.call(prov, req)
            if not row["reply"]:
                row["empty"] = True
            elif not a.no_judge:
                raw, _ = caller.call("anthropic", judge_request(cases[c], row["reply"]), label=f"judge ({JUDGE_MODEL})")
                row["labels"] = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
                row["pass"] = verdict(cases[c], row["labels"])
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        return row

    def first_replicates(group):
        # Arms of one (model, case) share the history prefix. Run their first replicate one after
        # another, so each arm reads the history cache the previous one wrote.
        return [one((*group, arm, 0)) for arm in arms]

    groups = [(m, c) for m in models for c in cases]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        rows = [r for rs in ex.map(first_replicates, groups) for r in rs]
        # Cache entries become readable once the first response starts, so the remaining replicates all hit it.
        rows += list(ex.map(one, [(m, c, arm, i) for m, c in groups for arm in arms for i in range(1, a.n)]))

    rows.sort(key=lambda r: (r["case"], r["model"], list(arms).index(r["arm"]), r["i"]))
    with open(out / "responses.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    manifest["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    manifest["usage"] = {m: dict(u) for m, u in caller.usage.items()}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    summary = render_summary(rows, cases, arms, models, a, manifest)
    (out / "summary.md").write_text(summary, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary)
    print(summary)
    print(f"\nfiles: {out}")


def render_summary(rows, cases, arms, models, a, manifest):
    L = ["# sober-up eval", ""]
    if manifest.get("github_run"):
        L += [f"Run: {manifest['github_run']}  ", ""]
    L += [f"{a.n} runs per cell. A cell shows how many replies passed. Differences under about 2 runs in 10 are noise.", ""]
    for c, case in cases.items():
        p = case["judge"]["pass"]
        rule = " and ".join([*p.get("all", []), *("not " + k for k in p.get("none", []))])
        L += [f"## {c}", "", f"_{case['about']}_  ", f"Pass = {rule}.", ""]
        L += ["| Model | " + " | ".join(arms) + " |", "|---" * (len(arms) + 1) + "|"]
        mz = case["judge"].get("must_be_zero")
        for m in models:
            cells = []
            for arm in arms:
                g = [r for r in rows if (r["model"], r["case"], r["arm"]) == (m, c, arm)]
                ok = sum(bool(r.get("pass")) for r in g)
                bad = len([r for r in g if "error" in r or r.get("empty")])
                cell = f"{ok}/{len(g)}" + (f" ({bad} failed calls)" if bad else "")
                if mz:
                    z = sum(bool(r.get("labels", {}).get(mz)) for r in g)
                    cell += f", {mz}: {z}" + (" ⚠️" if z else "")
                cells.append(cell)
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["## Tokens and cache", "", "| Model | calls | uncached in | cache write | cache read | out | read share |", "|---|---|---|---|---|---|---|"]
    for m, u in manifest["usage"].items():
        tot = u.get("input", 0) + u.get("cache_write", 0) + u.get("cache_read", 0)
        L.append(f"| {m} | {u.get('calls', 0)} | {u.get('input', 0)} | {u.get('cache_write', 0)} | {u.get('cache_read', 0)} | {u.get('output', 0)} | "
                 f"{100 * u.get('cache_read', 0) / max(tot, 1):.0f}% |")
    L += ["", "## Provenance", "", "```", json.dumps({k: manifest[k] for k in ("sha256", "git_head", "github_run", "started_utc")}, indent=1), "```", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
