# skills

Agent skills by Mati Horowitz.

| Skill | What it does |
|---|---|
| [sober-up](skills/sober-up/SKILL.md) | Helps a stuck AI agent sober up and reason with you again |

Install one:

```
npx skills add matipojo/skills --skill sober-up
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
