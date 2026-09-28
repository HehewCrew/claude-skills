---
name: skill-harvest
description: Look back over the current session, plus the project's memory and context, for work worth turning into a new skill or agent (or an extension of an existing one), project-specific or global, and propose the best candidates for the user to pick. Use when the user invokes /skill-harvest or asks "any skills we could make from this?"; at the end of a session (the user wraps up, says they are closing the chat, asks to clean up or deploy before closing); or, on Claude's own judgement, at a natural pause once the session holds a clear candidate: a multi-step procedure done twice, or one that needed hard-won fixes that will be needed again. Proposes only; builds nothing without the user's pick.
---

# Skill harvest

Sessions keep solving the same kinds of problems. This skill catches the ones worth keeping, **while the context that makes them good is still in the conversation**, and turns them into skills or agents the user approves.

## When to run it

- **Asked:** `/skill-harvest`, or "anything here worth a skill?".
- **At the end of a session:** the user wraps up, says they are closing the chat, or asks for a final deploy or cleanup. Run it after that work is done, as the last step.
- **On your own judgement, mid-session:** only at a natural pause (a task just finished, never in the middle of one), and only when there is at least one **strong** candidate (see the bar below). Offer it in one line ("This session has a skill candidate: <name>. Harvest now?") rather than running the whole review unasked.
- **At most once per session**, unless the user asks again.

## Step 1: gather

Read, in this order, and only what is relevant:

1. **The session itself:** what was done, repeated, fixed, or explained more than once, and every correction the user made ("not like that", "always …", "why did you …").
2. **The project's memory directory:** `MEMORY.md` and the files it points to, especially `feedback` memories and any to-do, ideas or improvement lists the project keeps there, plus **`skill-harvest.md`**, the log of past proposals (see Step 4). No memory directory? Skip this step.
3. **The project's `CLAUDE.md`** and the user's global `~/.claude/CLAUDE.md`.
4. **What already exists, so nothing is duplicated:**
   - global skills in `~/.claude/skills/`;
   - project skills in `<project>/.claude/skills/`, including nested ones such as `website/.claude/skills/`;
   - agents in `~/.claude/agents/` and `<project>/.claude/agents/`;
   - the skills and plugins listed in the session's system reminders.
   Read the `description:` line of each; open the body only for a possible overlap.

## Step 2: find candidates

A candidate must clear **all four** points of the bar:

1. **It will happen again.** The session did it twice, or it is plainly recurring: every post, every deploy, every client job, every session.
2. **It is more than one step,** or one step with a trap in it.
3. **It carries knowledge that is not obvious:** a gotcha that cost a retry, a rule the user set, a working order that matters, a tool invocation that took several tries. A procedure Claude would get right cold anyway is not worth a skill.
4. **Nothing existing covers it.** If a skill covers it partly, the candidate is **"extend `<skill>`"**, not a new one. If two existing skills overlap, **"merge"** is a candidate too. An existing skill the session proved wrong is a candidate for a **fix**.

**Skill or agent?** Default to a **skill**: it runs in the main thread, costs no start-up, and keeps the user's gates. Propose an **agent** only when all of these hold:
- the work is self-contained;
- it reads a lot, so keeping that reading out of the main context is worth something;
- it needs no decision from the user mid-way.

Agents cost time and start cold; an agent that proves slower than doing the work inline should be retired.

**Project or global?**
- **Project:** the skill depends on the project's files, rules, brand or layout. It lives in `<project>/.claude/skills/<name>/`, is committed with the repo, and follows the project's branch rules.
- **Global:** it is about how the user works, or about a tool or platform used across projects. It lives in `~/.claude/skills/<name>/`.
- **Split:** when half is general and half is project-specific, propose a global skill plus a short project section or reference file, rather than two copies.

## Step 3: propose

Show **at most five** candidates, ranked by value (how often it recurs × what it saves or prevents), in one table:

```
Skill candidates from this session

| # | Name | Kind | Scope | What it would do | Evidence from this session |
|---|------|------|-------|------------------|----------------------------|
| 1 | icon-kit | new skill | project | Rebuild the logo-derived icons (favicon, covers, profile picture) from the source logo | Built 3 icon sets today; the \n escaping and 16 px size traps |
```

Rules for the table:
- **Evidence is concrete:** what happened in this session or in memory, not a general claim.
- **Names** are short and kebab-case, and none clashes with an existing skill.
- **If nothing clears the bar, say so in one line and stop.** No candidate is a fine result; a weak one is not.

Then **recommend** the one or two to build first, with one line on why. Ask with **AskUserQuestion** (`multiSelect: true`), one option per candidate, the recommended ones first and marked `(Recommended)`.

## Step 4: log, then build what was picked

**The log.** Keep `skill-harvest.md` in the project's memory directory, so a declined idea is not proposed again. If the file does not exist, create it with frontmatter (`name: skill-harvest`, a one-line `description`, `metadata: type: project`), and add a pointer line to `MEMORY.md`. **Team mode:** if the project's root `CLAUDE.md` has `Pots mode: team` (the `pots` plugin's shared mode), keep the log at `.claude/pots/skill-harvest.md` instead, with no pointer. Append lines only, add `· <git user.name>` at the end of each, and never commit on your own. Append one line per candidate shown:

```
- 2026-09-25 · icon-kit (project skill) · built → .claude/skills/icon-kit/
- 2026-09-25 · deploy-verify (global skill) · declined: "deploys are rare"
```

A declined candidate comes back only when the session gives **new** evidence, and says what changed.

**Building.** For each picked candidate:

1. **Match the house style.** Read one or two existing skills in the same scope first and follow their shape:
   - frontmatter `name` and a `description` that names its triggers explicitly: the slash command, the phrases, the situations;
   - a short purpose line;
   - numbered steps;
   - a Rules section.
   Write it for Claude, not for a reader: imperative, specific, no filler.
2. **Put the hard-won knowledge in:** the exact commands that worked, the traps and their fixes, the user's corrections with their reasons, dates on owner rules.
3. **Scripts go inside the skill folder** when the procedure needs one; a long reference goes in a sibling `reference.md`, linked from `SKILL.md`.
4. **Wire it up:**
   - add a line to the project's or the global `CLAUDE.md` only when the skill must run at a fixed moment (session start, before a commit, and so on); otherwise the description alone triggers it;
   - for an agent, write `.claude/agents/<name>.md` in the format of the existing agents.
5. **Check it once:**
   - reread the description as if choosing among all the listed skills: would it trigger on the right requests, and not on others?
   - if it ships a script, run the script.
6. **Commit** project skills per the project's commit and branch rules. Global skills live outside any repo.
7. **Confirm** with one line per skill: name, path, and the trigger that invokes it.

## Rules

- **Never build without a pick.** A "yes" to harvesting is not a yes to a specific skill.
- **Never duplicate.** Extending an existing skill beats a near-copy.
- **Stay short.** The review is one table and one question, not a report.
- **Don't harvest one-offs.** A fix to one bug, one post or one client's file is not a skill. The *procedure* that produced it might be.
- **Respect the project's precedence rules:** a project's own skills and `CLAUDE.md` outrank generic workflow plugins. A new skill must not contradict them.
