---
name: improve-pot
description: Save an idea as a potential improvement for a topic in the current project - one the user mentions, or one taken from Claude's own output - into that project's improvement pot, which the todos-pot skill opens with. Use ONLY when the user asks for it - they invoke /improve-pot, or say "save that as a potential improvement", "add it to the pot", "improve-pot this", "note that for later". Never save on your own initiative. The gate that opens todos-pot is defined in the todos-pot skill.
---

# Improve pot

A per-project list of **potential improvements**: ideas worth coming back to that are not being worked on now. It fills only when the user asks. It is read only as the gate at the start of the `todos-pot` skill, and never by brainstorming.

## Where the pot lives

One file per project: **`improve-pot.md` in the current project's memory directory**, the directory named in the system prompt's Memory section (for example `~/.claude/projects/<project-slug>/memory/improve-pot.md`). It is private to the user and never goes into the repository.

- If the file does not exist, create it with the header below. Then add one pointer line to that directory's `MEMORY.md`: `- [Improvement pot](improve-pot.md) — potential improvements, read as the gate when todos-pot is called`.
- If there is no memory directory (for example, a session with memory off), ask the user where to keep the pot rather than guessing.

```markdown
---
name: improve-pot
description: Potential improvements for this project, grouped by topic; read as the gate when todos-pot is called
metadata:
  type: project
---

# Improvement pot
```

## Saving an idea

1. **Find the idea.**
   - If the user states it, use their words.
   - If they point at Claude's output ("save that", "the second one"), take that idea from the conversation.
   - If "that" could mean more than one idea, ask which one. Never save a guess.
2. **Pick the topic.**
   - A topic is a short noun phrase naming the area, such as `website: search page` or `onboarding emails`.
   - Reuse an existing heading when the idea fits one; don't create a near-duplicate.
   - If the user names a topic, use it.
3. **Check for duplicates.** If the pot already holds the same idea, say so, and add the new angle to that entry instead of adding a second one.
4. **Write the entry** under `## <topic>`, creating the heading if needed:
   ```markdown
   - [ ] **<the idea in one line>** *(<YYYY-MM-DD>, from <user|Claude>)* — <why it would help, and the context it came from, in one or two sentences>
   ```
   - Use absolute dates.
   - Keep enough context that the entry makes sense weeks later without this conversation.
5. **Confirm** in one line: what was saved, and under which topic.

Saving is quick and does not interrupt the current task. Do not start working on the idea unless the user asks.

## Where it is read

**Only by the `todos-pot` skill**, as its opening gate (step 1 there): `n potential improvement(s)`, one short bullet per open item, then wait for "skip". **Brainstorming skills do not read the pot**: it stays a deliberate backlog, not a source of ideas to re-pitch. The pot is not read at any other time.

## Closing items

- When a pot item is acted on (built, decided, or taken into a plan the user approved), mark it `[x]` and add *(done YYYY-MM-DD: <where it went>)*.
- When the user rejects an item, mark it `[-]` with *(dropped YYYY-MM-DD: <reason>)*.
- Don't delete entries, so the history stays visible.
- Only change an item's state when the user said so, or when it was clearly done in this session.
