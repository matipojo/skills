# decision-driven-design

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

```
npx skills add matipojo/skills --skill decision-driven-design
```
