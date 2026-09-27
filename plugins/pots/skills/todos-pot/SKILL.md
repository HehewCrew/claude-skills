---
name: todos-pot
description: The current project's to-do list. It keeps a stored list of todos and, each time it is called, merges in the open items found in the project's own files, so nothing recorded anywhere is missed. Opens with the improvement-pot gate. Use when the user asks for their todos ("what are the todos", "what's left", "what do we have to do", /todos-pot), when they ask to add a todo ("add to todos", "todo: ..."), and when a piece of work closes with something still left for the user to do (see "Adding todos").
---

# Todos pot

A per-project to-do list. It combines two things: a **stored list** (todos said in chat, or left over when work closes) and a **fresh scan** of the project's own files, which is where most open work is actually recorded.

## Where it lives

One file per project: **`todos-pot.md` in the current project's memory directory**, the directory named in the system prompt's Memory section (for example `~/.claude/projects/<project-slug>/memory/todos-pot.md`). It is private and never goes into the repository.

- If the file does not exist, create it with the header below and add one pointer line to that directory's `MEMORY.md`: `- [Todos pot](todos-pot.md) — the project's stored todos, merged with a scan of its files when todos-pot is called`.
- If there is no memory directory, ask the user where to keep it.

```markdown
---
name: todos-pot
description: Stored todos for this project; todos-pot merges them with a scan of the project's files
metadata:
  type: project
---

# Todos pot
```

Entry format, under `## <topic>`:

```markdown
- [ ] **<the todo in one line>** *(<YYYY-MM-DD added>, when: <timeline>)* — <one line of context: why, and where it came from>
```

## When todos-pot is called: the order is fixed

### Step 1: the improvement-pot gate

Read the project's `improve-pot.md` (the `improve-pot` skill's file, in the same memory directory) and count the open (`[ ]`) items across every topic.

- **None, or no file:** say nothing about it and go to step 2.
- **One or more:** reply with `n potential improvement(s)` (for example `2 potential improvements`), then one bullet per item with a short description (a few words from the item's bold line). Nothing else: no explanation, no todos yet. Stop and wait.
  - "skip improvement", or a plain "skip" → go to step 2 and don't mention the pot again this session.
  - Anything else about the pot ("show them", "let's do those") → work on the pot items as asked.
- If the user's message calling todos already says "skip improvement" or "skip", pass the gate silently.

### Step 2: gather the todos

1. **The stored list:** every open item in `todos-pot.md`.
2. **Scan the project's files.** Read before listing; never answer from memory of an earlier call.
   - **Unchecked checkboxes** in the project's Markdown (`- [ ]`, and `[ ]` in table cells), found with Grep. Skip generated or vendored folders (`dist/`, `node_modules/`, `.venv/`, build output) and archived or published content.
   - **Planner and schedule files.** Rows not marked done that have a date, from today onwards, plus overdue ones.
   - **"Open", "To Be Defined", "Still open" or "Later" sections** in the project's docs and READMEs.
   - **The project's `CLAUDE.md`**, for anything it lists as still open or blocking.
   - **Parked work,** if you keep it as `undone-*.md` memories in the memory directory. They are only listed here, not moved.
3. **Merge and de-duplicate.** When a stored todo and a file item are the same thing, show it once, and prefer the file's wording, since the file is the record.

### Step 3: present

Group the list by when, then by source:

- **Dated:** today, this week, next, overdue first. One line each, with the date.
- **Undated, by area:** grouped by topic or source file, one short line each, with the file as a link.
- **Parked (undone)**, last.

Keep each line short. If the scan finds a very long tail of low-level open items (for example, dozens in one doc's checklist), show that file's count and its few most consequential items, and offer to expand it. Never silently drop a whole file.

## Adding todos

🔒 **Every new todo needs a timeline.** A timeline is anything that places it in time:
- a date: `2026-10-02`
- a deadline: `before the launch`, `before 2026-09-30`
- a start condition: `after launch`, `after the site goes dynamic`
- a window: `this week`, `in October`

**If the user gives no timeline, ask for one before saving.** One short question, such as *"When for this one: a date, before something, or after something?"*. Then save it with their answer. If they say it has none, record `when: no timeline (user)`, so it is clear this was asked and not forgotten. Never invent a timeline. For a leftover, a deadline from the conversation counts. If the conversation gave none, ask.

- **On request:** "add to todos …", "todo: …", or "put that on the todo list". Save it to the stored list and confirm in one line.
- **Leftovers:** when a piece of work closes and the final message tells the user something is still theirs to do (a decision, a physical task, a deadline), add it to the stored list. Say so in one line: *"Added to todos: …"*. Don't add it if the project's files already record it as open; the scan will find it.
- De-duplicate before adding. If it's already there, update the entry instead.

## Closing todos

- When a todo is done in this session, or the user says it's done, mark it `[x]` with *(done YYYY-MM-DD)*.
- Items found by the scan are closed in their own file, following that project's conventions, not here.
- Don't delete entries.

## Optional: session-start check for critical todos with no calendar slot

Only with a calendar connector (e.g. Google Calendar). To run it at the start of every session, add a line to your `CLAUDE.md`: *"At session start, run the todos-pot skill's session-start check."* It is **not** a todos-pot call, so the improvement-pot gate does not apply, and it lists only what needs planning.

1. **Pick the critical ones** from the stored list's open items (`- [ ]`), plus anything the project's `CLAUDE.md` names as blocking a launch or a hard deadline:
   - due within **7 days**, or overdue: read the date from `when:`;
   - or **blocks a launch, a milestone or a hard deadline**, as the todo or `CLAUDE.md` says.
   Skip anything whose `when:` starts after a condition that hasn't happened yet, e.g. "after the launch".
2. **Check the calendar directly**, not through an agent (a read and a comparison is quicker inline). If nothing was picked, say nothing and stop. Otherwise:
   - **Skip** todos already marked `(planned: …)` in the pot; whatever creates their event writes that mark.
   - **For the rest,** list events once, from today to 21 days ahead, in the user's timezone. If the result is saved to a file, pull just the date, time and title of each event with a short script instead of reading it whole.
   - **Match on meaning:** an event covers a todo when its title names the same piece of work, on or before the due date. A title starting with `✅` counts as covered.
3. **Show it**, short:
   ```
   2 critical todos not planned yet:
   - Renew the domain · due Fri 25 Sep
   - Record the demo video · (undated) · blocks the 3 Oct launch   (maybe: "🎥 Demo shoot", Thu 1 Oct)
   Want me to put them in the calendar?
   ```
4. **On a yes,** draft each event (title, numbered tasks, "done when"), offer two or three free slots before its deadline, and create only the one the user picks. Then mark the todo `(planned: <Day DD Mon HH:MM>)`.
5. No calendar connector? Say so in one line and show the critical list, unchecked, anyway.
