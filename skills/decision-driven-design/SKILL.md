---
name: decision-driven-design
description: Decision Driven Design (DDD). Spec a feature, a system, or any set of decisions that must be made, by making all the decisions visible up front. Simulates a debate between personas chosen for the topic, builds an explicit decision tree, simulates every decision in advance, and writes them as numbered plain sentences ("We decided X because Y") that the user fixes one by one ("Decision 8: change to..."). Use when the user asks to spec, design, plan or decide something. If the user wants visual illustrations of the decisions, hand off to the contrast-illustration skill.
---

# Decision Driven Design (DDD)

A spec is mostly decisions. They are painful because they are hidden: you chase them and discover them one at a time. DDD flips this. Surface every decision up front, decide all of them in advance, and let the user correct only the few that are wrong.

Input: a topic, e.g. "Spec a team invite flow" or "Should we move to a monorepo?". Features, systems, and plain decisions all work. If the user gave context (goals, budget, team, deadline, values), use it everywhere below. If not, don't ask; state your assumptions in one line and continue.

## Step 1: choose the personas
Choose 4–7 personas that are **specific to this topic**, the people whose interests really collide here. Not a generic set. For a team invite flow that might be the workspace admin, the invited user, the security lead, the growth lead who wants viral signups, the support agent, the billing owner.
For each one write one line: **who they are, what they want, their red line.** No neutral moderator, every persona is biased on purpose.

## Step 2: simulate the debate
3–4 heated rounds. Each persona attacks a concrete proposal of another, by name, with a concrete cost, number, scenario or failure.
- Disagreement must be real. If two personas agree, sharpen one of them.
- No polite wrap-ups. A persona concedes only when an argument actually lands.
- Every clash that ends in "it depends" is a decision node. Mark it inline: `→ N3`.

The debate is the rationale. Every decision later points back to the round where it was argued.

## Step 3: build an explicit decision tree
- **Wide:** every node has 3–5 real options, including the boring one and the radical one.
- **Deep:** an option opens the child decisions it forces. Go at least 3 levels down where it matters. IDs: `N3`, `N3.2`, `N3.2.1`.
- Per option: which persona pushes it, and one line of what it costs.

```
N1 How does someone get invited?
  N1.1 Shareable invite link       [Growth]     fastest, link leaks to strangers
  N1.2 Invite by email address     [Security]   only that person can join
    N1.2.1 Do invites expire?
  N1.3 Admin approves every join   [Admin]      safe, slow, admin bottleneck
```

## Step 4: simulate alternatives on the tree
Walk the tree and simulate what each branch would hit in reality: a law, a cost spike, an attack, a vendor limit, a support burden, an advantage that comes free.
- Attach it to the exact node: `⚠ N1.1 a link posted in a public chat lets anyone join` or `✚ N1.2 the email doubles as a verified login`.
- A constraint can **prune** a branch (`✂`) or force a child decision. A benefit can make a branch dominant.
- Propagate: if a constraint deep in the tree kills an option, update the decisions above it.

## Step 5: simulate every decision in advance
Decide every surviving node as the user would. Don't stop to ask.
- First state the priorities you are simulating, in 2–4 bullets, taken from the user's words. Mark the ones you guessed.
- Decide top-down: a parent's decision fixes which children exist.

## Step 6: write the decisions
Write `decisions.md` (or the name the user gave). This is the deliverable: numbered decisions, one plain sentence each.

```markdown
**8.** We decided invites go to a specific email address instead of a shareable link, because a link forwarded once lets a stranger into the workspace.
<sub>N1.2 · debate round 2: Security lead vs. Growth lead</sub>
```

- Shape: **We decided X instead of Y, because Z.** Y is the strongest rejected option. Z is the one reason that decided it, not a list.
- Plain language, no jargon the user didn't use. One decision per sentence: if it needs "and", it is two decisions.
- Number them **1, 2, 3…** in tree order, so a child follows its parent. The small line under each one points to its node and the debate round that holds the rationale.
- When a decision rests on a concrete technical line (a URL, a query, a config line, a role binding), add it as inline code. The illustration skill uses it.
- End with an **Open** list: the decisions that were a coin toss, which the user should really make.

Write the personas, the full debate and the tree to `decision-tree.md` next to it, so the rationale is kept and the decisions file stays short.

## Step 7: fix by number
The user corrects with one line: **"Decision 8: change to…"**.
- Change that decision, then re-simulate only its subtree: children that no longer make sense are replaced, new children are added.
- Keep every other number stable. New decisions get the next free number.
- Report in one line which decisions changed as a result.

## Step 8: visuals (optional)
If the user asks for visuals, illustrations, images or slides of the decisions, use the **contrast-illustration** skill on `decisions.md`. If they didn't ask, offer it in one line at the end: "Want an illustration for every decision?"

## Don't
- Don't let the debate converge early. A tree with one obvious path means the personas were too soft.
- Don't leave a decision hidden in the debate. If it was argued, it is a node. If it is a node, it gets a numbered sentence.
- Don't write "we decided to consider" or "we decided to explore". A decision picks something.
