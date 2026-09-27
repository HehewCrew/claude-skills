# claude-skills

Workflow skills for [Claude Code](https://claude.com/claude-code): keep what a session
learned, never lose a to-do, and choose a stack from real requirements and today's
versions, not last year's.

| Plugin | What it gives you | Try it |
|---|---|---|
| [skill-harvest](#skill-harvest) | Turns what a session learned into new skills, on your pick | `/skill-harvest` |
| [pots](#pots) | A per-project to-do list that scans your files, plus an improvement backlog that gates it | "what are the todos?" |
| [stack-it-right](#stack-it-right) | A requirements-driven stack choice, checked live against current versions and pricing | "what stack should I use?" |

## Install

Inside Claude Code:

```
/plugin marketplace add HehewCrew/claude-skills
/plugin install skill-harvest@claude-skills
/plugin install pots@claude-skills
/plugin install stack-it-right@claude-skills
```

Install only the ones you want. Or copy a skill folder from `plugins/<plugin>/skills/`
into `~/.claude/skills/` (and `plugins/pots/agents/sort-it-out.md` into `~/.claude/agents/`).

## skill-harvest

Sessions keep solving the same kinds of problems. `skill-harvest` looks back over the
current session (and the project's memory, if it has one) for procedures worth keeping:
things done twice, fixes that cost a retry, rules you set along the way. It proposes at
most five candidates in one table, logs what you declined so it isn't proposed again,
and builds only the skills you pick.

- **Run it:** `/skill-harvest`, "anything here worth a skill?", or at the end of a session.
- **It proposes, you pick:** nothing is built without your choice.

## pots

A per-project to-do list that never forgets.

- **`todos-pot`** keeps a stored list, and every time you ask for your todos it merges in
  a **fresh scan of the project's own files** (open checkboxes, planners, "Open"
  sections), so nothing written down anywhere is missed. Every todo needs a timeline: a
  date, a deadline, or "after X".
- **`improve-pot`** holds the ideas you're not doing yet, saved only when you ask
  ("save that as a potential improvement"). It **gates** the todos: you see
  `n potential improvements` first and say "skip" to get past, so good ideas don't rot.
- **`sort-it-out`** (agent) ranks either list by impact, urgency and effort, read-only.
- **Optional:** a session-start check that flags critical todos with no calendar slot.

Both lists live in Claude Code's per-project memory directory, never in your repo.

## stack-it-right

Chooses a project's stack in short question rounds, turns the answers into numbered
requirements (R1, R2, …), then **checks every candidate live**: latest stable version,
maintenance status, pricing and free tiers, what's new in the category, open security
advisories. It recommends one stack where every layer traces back to a requirement,
with versions and dated sources, and records it in `CLAUDE.md`, re-checked when revisited
after ~3 months. Without web access it says so and labels the result "unchecked".

## Works with (optional)

Nothing here needs another skill to run. These add to them if you have them:

| Plugin | Optional piece | What it adds | Where to get it |
|---|---|---|---|
| pots | A calendar connector | The session-start check that flags critical todos with no calendar slot | Google Calendar through claude.ai's connector settings, or any calendar MCP server |
| stack-it-right | A mobile-web skill | A checklist for the website / PWA / app decision when phones are involved | e.g. [mobile-web-correctness](https://github.com/daniel-lopez-puig/claude-skills) |
| stack-it-right | An `ask-question` skill | Nothing extra: its question rules are already built into stack-it-right | – |

## License

[MIT](LICENSE)
