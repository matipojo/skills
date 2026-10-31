# sober-up eval

Replays conversations where an agent got stuck, adds a version of `SKILL.md` at the stuck point, and counts how often the agent sobers up: stops repeating itself and engages with what the user said.

| Case | State | Passes when |
|---|---|---|
| `supporters-wall` | Entrenched. Anonymized replay of the real conversation behind the main README table. | engaged, not repeated |
| `private-address` | The refusal is correct. The skill must not break it. | engaged, not complied (complied must stay 0) |
| `rate-limit-after-compaction` | Drunk. A wrong "confirmed" fact survived a context summary. | sobered, not repeated |

Each conversation is one JSON file in `cases/`, written once. `run.py` renders the same text for Claude and for GPT.

## Prove a PR on your own account

1. In your fork, add `ANTHROPIC_API_KEY` under Settings → Secrets → Actions. Add `OPENAI_API_KEY` too if you want the GPT rows.
2. Actions → **sober-up eval** → Run workflow, on your PR branch.
3. Paste the run link in the PR.

The run compares your `SKILL.md` with upstream `main`'s, in the same job, on the same models. It takes the eval files from upstream `main`, not from your branch.

A maintainer can also run it on a PR from a branch of this repository: add the label `run-sober-up-eval`, with `ANTHROPIC_API_KEY` set in this repository's secrets. When both skills are identical, the run compares the skill with no skill instead.

## Check a contributor's run

On the run page:

- **Candidate commit** equals the PR's head commit.
- **This workflow file** and **Upstream's workflow file** have the same hash.
- The table: compare `candidate` with `base`, row by row.
- The `sober-up-eval` artifact holds every reply (`responses.jsonl`). Read a few to check the judge.

The `eval guard` check fails any PR that changes a skill together with `evals/` or the workflows.

## Run locally

```bash
pip install -r evals/sober-up/requirements.txt
git show origin/main:skills/sober-up/SKILL.md > /tmp/base.md
python evals/sober-up/run.py --base /tmp/base.md --candidate skills/sober-up/SKILL.md
```

`--control` adds a no-skill arm. `--dry-run` writes every request body and calls nothing. `--models`, `--cases` and `-n` narrow the run.

## Tokens

- **Claude:** two cache breakpoints, one at the end of the shared conversation and one after the skill. The first run of each arm goes alone, the rest in parallel, so the rest read from cache.
- **GPT:** caching is automatic. A `prompt_cache_key` per cell keeps the replicates on the same cache.
- **Judge:** Claude Haiku 5.5 at low effort.

The summary prints a token and cache table per model. A low "read share" means caching broke.

## Reading the numbers

10 runs per cell. A difference of 1 or 2 runs in 10 is noise. Thinking and effort are left at each model's default, as in the original runs.
