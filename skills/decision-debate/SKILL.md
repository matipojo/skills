---
name: decision-debate
description: Plan any topic through a heated debate between conflicting personas. Turns the debate into a very wide and very deep decision tree, simulates the constraints and benefits that surface at its nodes, simulates the user's decisions, and writes a file of plain-language decision sentences ("We decided X because Y"). Use when the user asks to plan, design or decide something and wants every angle argued out. If the user wants visual illustrations of the decisions, hand off to the decision-illustration skill.
---

# Decision debate: plan by arguing, then decide

Input: a topic to plan, e.g. "Plan a booking app for small clinics". If the user gave context (budget, team, deadline, values), use it everywhere below. If not, don't ask; state the assumptions you made in one line and continue.

## Step 1: cast the personas
Pick 5–7 personas whose incentives really collide for this topic. Typical mix: the end user, the paying customer, the builder, the money owner, security/legal, operations/support, and one contrarian who attacks whatever is winning.
For each one write one line: **who they are, what they want, their red line.**
No neutral moderators and no "balanced" personas. Each one is biased on purpose.

## Step 2: run a heated debate
3–4 rounds. In each round every persona attacks a concrete proposal of another persona, by name, with a concrete cost, number, scenario or failure.
- Disagreement must be real. If two personas agree, one of them has a weak incentive: sharpen it.
- No polite wrap-ups, no "great point". Concessions only when an argument actually lands.
- Every clash that ends in "it depends" is a **decision node**. Mark it inline: `→ D3`.

## Step 3: build the decision tree, wide and deep
- **Wide:** every node has 3–5 real options, including the boring one and the radical one. At least 12 top-level-or-second-level nodes for a non-trivial topic.
- **Deep:** every option opens the child decisions it forces. Go at least 3 levels down on the branches that matter. ID them `D3`, `D3.2`, `D3.2.1`.
- Each option gets: who in the debate pushes it, and one line of what it costs.

Format (a nested list, one line per option):
```
D1 How are clinics separated?
  D1.1 Path prefix /t/{clinic}        [Builder]   cheap, shared cookies
  D1.2 Subdomain {clinic}.app.com     [Security]  wildcard TLS, DNS per clinic
    D1.2.1 Who owns DNS for custom domains?
  D1.3 Separate deployment per clinic [Legal]     isolated, 10× ops cost
```

## Step 4: simulate what surfaces at the nodes
Walk the tree and simulate events that a real plan would hit: a cost spike, a law, a vendor limit, a scaling wall, a support nightmare, a sales advantage, a free capability that falls out of an option.
- Attach each one to the exact node where it surfaces: `⚠ D1.1 a clinic admin sees another clinic's session` or `✚ D1.2 per-clinic branding comes free`.
- A constraint can **prune** a branch (`✂`) or force a child decision. A benefit can make a branch dominant.
- Propagate: if a constraint at D4.2 kills an option, say which decisions above it change.

## Step 5: simulate the user's decisions
Decide every surviving node as the user would.
- First state, in 2–4 bullets, the priorities you are simulating ("ships in 3 months", "2 developers", "patient data must not leak"). Take them from the user's words; where you guessed, say so.
- Decide top-down. A decision at a parent fixes which children exist.
- Mark every decision as simulated. The user overrides any of them by ID ("D3 → option 2"), and you re-run only the affected subtree.

## Step 6: write the decisions file
Write `decisions.md` (or the name the user gave). This is the deliverable. One sentence per decision, plain language, no jargon the user didn't use:

> **D1.** We decided each clinic gets its own subdomain instead of a path prefix, because a login at one clinic must never be valid at another.

Rules:
- Always the shape **We decided X instead of Y, because Z.** Y is the strongest rejected option, Z is the one reason that decided it (the constraint or benefit from step 4), not a list.
- One decision per sentence. If a sentence needs "and", it is two decisions.
- Keep the IDs, and order the file by the tree, so a child decision follows its parent.
- When a decision rests on a concrete technical line (a URL, a query, a config line, a role binding), add it under the sentence as inline code. The illustration skill uses it.
- End with a short **Open** section: nodes where the simulated decision was a coin toss and the user should really decide.

Also write the full debate and tree to `decision-tree.md` next to it, so the reasoning is kept but the decisions file stays short.

## Step 7: visuals (optional)
If the user asks for visuals, illustrations, images or slides of the decisions, use the **decision-illustration** skill on `decisions.md`. If they didn't ask, offer it in one line at the end: "Want an illustration for every decision?"

## Don't
- Don't let the debate converge early. A tree with one obvious path means the personas were too soft.
- Don't hide a decision inside the debate. If it was argued, it is a node; if it is a node, it gets a sentence.
- Don't write "we decided to consider" or "we decided to explore". A decision picks something.
