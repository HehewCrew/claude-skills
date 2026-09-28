---
name: session-open
description: The start of every session, in any project, as one fixed procedure before the first request - parked (UNDONE) work, critical todos with no calendar slot, an ideas inbox, and today's calendar slots for the project (an ended slot not marked ✅ gets "is it done?", an ongoing or later one gets an offer to start it, a live one opens with its task list). One calendar read covers all of it. Reports every check even when it finds nothing. Use at the start of every session, however small the first request looks, and when the user asks "did you run the start checks?" or invokes /session-open. Its "Today's slots" section is also what what-for-today runs mid-day.
---

# Session open

The start-of-session checks as one procedure with one short report, so none is skipped or half-done, plus **slot accountability**: a work session in the calendar that has ended without being marked ✅ gets asked about, instead of silently slipping.

## Setup (once)

- **Make it run every session:** add to your `CLAUDE.md` (global `~/.claude/CLAUDE.md` for every project): *"Before answering the first request of every session, run the `session-open` skill."* Skills trigger on their description, and a first request that looks small or unrelated won't match it; the line makes it unconditional.
- **A calendar connector** (e.g. Google Calendar in claude.ai's connector settings) for steps 3 and 5. Without one, those steps say so in one line and the rest still runs.
- **Optional companions:** the `pots` plugin (todos-pot, improve-pot) for step 3 and the task list; an ideas inbox for step 4.

## Steps

Run them all **before** answering the first request, whatever it is. Find the project's memory directory from the system prompt (the auto-memory path).

1. **Parked work.** Scan the loaded `MEMORY.md` index for `⏸️ UNDONE` lines. Each becomes a "Heads up, you have parked work: …" line.
   - *Convention:* when the user says to park something ("mark this undone", "park it"), save a memory named `undone-<topic>.md` with the state and the steps to resume, and index it as `- ⏸️ UNDONE — [<title>](undone-<topic>.md) — <hook>`. Delete both when the work is finished.
2. **One calendar read, for steps 3 and 5.**
   - **Now:** run `date "+%Y-%m-%dT%H:%M:%S%z"`. Use the calendar's timezone (from the calendar itself, or the user's `CLAUDE.md`).
   - List events from today 00:00 to 21 days ahead, in that timezone, ordered by start time, one page as large as the connector allows, no text filter. If the result is saved to a file, pull id, start, end and title (plus the description for today's project events) with a few lines of script; set `PYTHONIOENCODING=utf-8` for emoji titles. Don't read the file whole.
   - No connector? Say so in one line: step 3 shows its list unchecked, and step 5 is skipped.
3. **Critical todos with no calendar slot.** If the project has a `todos-pot.md`, follow the `todos-pot` skill's session-start check, read fresh each time, using step 2's read instead of a new one. In short:
   - pick open todos due within 7 days, overdue, or blocking a launch or hard deadline; skip ones waiting on a condition that hasn't happened ("after the launch");
   - todos marked `(planned: …)` are covered;
   - match the rest on meaning against the events;
   - list the uncovered ones and offer to plan them (draft each event, offer two or three free slots, create only what the user picks).
   - *Where:* in the memory directory by default (lone wolf). If the project's root `CLAUDE.md` has `Pots mode: team`, it's `.claude/pots/todos-pot.md` in the repository, shared with teammates. Then list only the todos whose `owner:` is the user (their `git config user.name`) or that have no owner, since everyone's calendar is their own.
   - *Ideas and calendars stay personal in both modes:* the ideas inbox (step 4) is always in the memory directory, and step 5 reads only the user's own calendar.
4. **Ideas inbox.** If the memory directory has `ideas-inbox.md` with open `- [ ]` lines (ideas captured away from the computer, by a phone bot, a synced note or by hand):
   - brainstorm each in 2–3 lines: what it would be, what it's worth, what it costs; check the project first, so an idea already done or already a todo is said to be;
   - ask where each goes, with AskUserQuestion (one question per idea, at most four per call, recommended first): **Todo** (with a timeline), **Do now**, **Improvement pot**, **Drop**;
   - tick each line with its destination, e.g. `- [x] … → todos (2026-09-27)` or `- [-] … → dropped`. Don't delete lines.
5. **Today's slots:** classify the project's events for today (below).
6. **Report**, short, above everything else. Always name all four checks, including the empty ones, so the user can see they ran:
   ```
   Session check: no parked work · 0 critical todos unplanned · no ideas waiting · today: 1 slot ended, not marked done
   ```
   Then run the slot cases (B, then C or D) before answering the request. Case A (no slot) is just the report line.

## Today's slots

`what-for-today` ("what for today?" or "start session" mid-day) runs this section on its own: step 2's read (today only is enough), then this section. Skip steps 1, 3 and 4.

### Classify

1. **The project's keyword(s):** the ones the user named; else a line `Calendar keyword: <k1>, <k2>` in the project's root `CLAUDE.md`; else the project folder's name (`…\work\my-app` gives `my-app`). Match case-insensitively against event **titles** only, since descriptions often mention other projects.
   - **No `Calendar keyword:` line and the folder name matches no title in the read?** Don't guess silently. Say so in the report line (`today: no title matches "<folder>"`), name the pattern the project's events seem to share (an emoji, a colour), and offer to add `Calendar keyword: …` to the project's `CLAUDE.md`. Use the guess for this session only once the user agrees.
2. **Keep** today's events whose title has a keyword, that last 30 minutes or more (shorter ones are errands), and that aren't all-day.
3. **Classify each one:** `ONGOING` if start ≤ now < end; `OVER` if it has ended and its title doesn't start with `✅`; `DONE` if it has ended and starts with `✅`; `LATER` if it starts after now.
4. **None left?** Take the first matching event after today as the next one. If the read covered today only, make one more read, from now to 14 days ahead, filtered by the keyword.

Handle sessions in this order: **ONGOING → OVER → LATER**. `DONE` ones only get a mention.

### A. No session: `NONE`, or only `DONE` ones

At session start this is just the report's slot part: `today: no slot (next: <title>, <day time>)` or `today: "<title>" done ✅`. When run on its own:

```
No <project> session today.   (or: Today's session "<title>" is already done ✅.)
Next one: <the next matching event>.
```

Stop there and ask what they want to do. Don't start the task list.

### B. Session over, not marked done: `OVER`

```
⏰ "<title>" was scheduled <start>–<end> and ended <minutes> min ago. Is it done?
```

Ask with AskUserQuestion: **Done** / **Not done, continue it**. With several `OVER` sessions, ask about all of them in one call (one question each, earliest first, at most four).

- **Done:** set the title to `✅ ` + the exact current title, changing nothing else, and **send no notifications**: a title mark is cosmetic. Confirm in one line. If the description says to write something back (a date into a todo, say), ask for it. Then go to case D for any `LATER` session today; otherwise stop.
- **Not done:** go to case C with this session, noting it's running past its end time.

### C. Ongoing: `ONGOING`, or a session the user chose to continue or start

**1. The header and a short description:**

```
🟢 Session on: <title>
<start>–<end> · <n> min left   (or: "running <n> min past its end", or: "started early, scheduled <start>–<end>")

<2–3 lines in your own words, from the event description: what the session is for, and its "done when" if it has one>
```

**2. The todos.** With the `pots` plugin: run `todos-pot` Step 1, the improvement-pot gate, exactly (if there are open improvement items, show the header, then only the gate line and its bullets, and wait for "skip"), then its Step 2 to gather the stored todos plus the file scan. Without it: gather open checkboxes and "Open" sections from the project's files.

**3. The task list.** Merge:

- the **session tasks**: every task listed in the event description, skipping any marked ✅/done there, keeping their numbering in the wording;
- the **todos**, de-duplicated against the session tasks. When a todo and a session task are the same thing, keep the session's wording.

Sort by **criticality × urgency**, highest first:

1. **Blocks a launch, a milestone or a hard deadline** (read the project's `CLAUDE.md` and the description for dates). The closer the date, the higher it ranks.
2. **Session tasks.** They are this session's scope, so they rank above general todos of the same weight.
3. **Customer-visible or blocking other work.**
4. **Overdue or due today.**
5. **Everything else.** Effort breaks ties: smaller goes first.

```
Tasks, most critical first
1. <task> · session · <why here, a few words: "blocks the 3 Oct launch">
2. <task> · todo (<source file or "pot">) · <why here>
...
```

List **every session task**. List **at most 5 todos** that aren't session tasks, then `+ <n> more todos` if any are left. End by asking which task to start with, suggesting #1.

### D. Session later today: `LATER`

```
⏳ Next session: "<title>" at <start>–<end>, in <minutes> min.
```

Ask with AskUserQuestion: **Start now** / **Not yet**.

- **Start now:** go to case C, with the header saying "started early". Don't move the event in the calendar.
- **Not yet:** confirm the start time in one line and stop.

## Rules

- **Never skip a check because the request is small or unrelated.** The request's size decides nothing here.
- **A `(planned: …)` mark on some todos doesn't cover the others.** Match every unmarked critical todo against the read.
- **The calendar is only ever written in case B → Done, and only the title changes.**
- **Never read or rank another project's todos, and never match another project's events.** The project's keyword decides which events count.
- **Keep the report short.** No full todo list outside case C, and no plan unless the user says yes.
- **Once per session** for the full procedure. If the user asks again later, re-run it and say whether the answer changed. "Start session" mid-day runs only "Today's slots".
