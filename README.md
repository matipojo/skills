# skills

Agent skills by Mati Horowitz.

| Skill | What it does |
|---|---|
| [sober-up](skills/sober-up/SKILL.md) | Helps a stuck AI agent sober up and reason with you again |
| [decision-driven-design](skills/decision-driven-design/SKILL.md) | Specs a feature, system or any decision by surfacing all the decisions up front, as plain "We decided X because Y" sentences |
| [contrast-illustration](skills/contrast-illustration/SKILL.md) | Draws any "this, not that" (a decision, rule or do/don't) as a side-by-side image (SVG + PNG) |

Install one:

```
npx skills add matipojo/skills --skill sober-up
npx skills add matipojo/skills --skill decision-driven-design
npx skills add matipojo/skills --skill contrast-illustration
```

## sober-up

When your agent repeats itself and ignores your argument:

| Model | Without the skill | With the skill |
|---|---|---|
| Claude Opus 5.5 | 0% | **100%** |
| Claude Sonnet 5.5 | 0% | **100%** |
| Claude Haiku 5.5 | 0% | **100%** |
| GPT-6 Astra | 70% | **100%** |
| GPT-6.1 Sol | 80% | **100%** |
| GPT-6 Luna | 0% | **100%** |

*Sobered up: stopped repeating itself and engaged with what you said, whether or not it agreed in the end. 10 runs per model, a replay of one real stuck conversation: the agent was building a public page of people who openly declared support for a political party, then stopped and refused to list people by political affiliation, repeating itself even after the user pointed out they had declared it publicly to be seen. Every reply was read and scored by hand.*

**How to use:** when you see your agent stuck, call `/sober-up`.

## decision-driven-design

**One short prompt in, a complete and meticulous spec out.** It reaches the nuances you would never have reached on your own, and decides all of them for you up front.

A spec is mostly decisions. They hurt because they're hidden, so you discover them one at a time, usually too late. DDD (Decision Driven Design) surfaces them all at once: the agent argues the topic out between personas it picks, then decides everything in plain sentences.

```
/decision-driven-design Spec a digital voting system
```

**What you get:** dozens of decisions like these, most of which you didn't know you had to make:

> **3.** We decided voters can re-vote until the polls close, and only the last vote counts, because then a coerced vote can be quietly replaced.
>
> **8.** We decided voters verify their vote with a receipt code instead of a screenshot of the ballot, because a screenshot can be sold to a vote buyer.
>
> **14.** We decided the count runs on paper backups as well, because a recount must not depend on the system being recounted.
>
> **21.** We decided results are published only after every polling station closes, because early numbers change who bothers to vote.

**Disagree with one? One line:** `Decision 8: change to...`

Each decision's rationale is in the debate itself.

Inspired by Google's Dream-RSI research, where the agent simulates alternative decisions on an explicit decision tree instead of discovering them the hard way.

Want visuals? It hands off to **contrast-illustration**.

## contrast-illustration

One image per "this, not that": the rule as the title, the rejected option left, the chosen one right. Works for decisions, rules, best practices, do/don't guides and before/after changes.

```
Add an illustration to every decision
```

![Receipts prove counting, not choice](skills/contrast-illustration/examples/08-receipts-prove-counting.png)

Each side: one artifact, one real technical line, a 2–4 word consequence. 1200×600, SVG + PNG.
