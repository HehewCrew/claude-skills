# claude-skills

Workflow skills for [Claude Code](https://claude.com/claude-code): keep what a session
learned, never lose a to-do, start every session with the same checks, and choose a stack
from real requirements and today's versions, not last year's.

| Plugin | What it gives you | Try it |
|---|---|---|
| [skill-harvest](#skill-harvest) | Turns what a session learned into new skills, on your pick | `/skill-harvest` |
| [pots](#pots) | A per-project to-do list that scans your files, plus an improvement backlog that gates it; private or shared with your team | "what are the todos?" |
| [stack-it-right](#stack-it-right) | A requirements-driven stack choice, checked live against current versions and pricing | "what stack should I use?" |
| [session-open](#session-open) | A start-of-session routine with slot accountability: an ended calendar session not marked ✅ gets asked about | runs at session start · "what for today?" |
| [voice-over-chain](#voice-over-chain) | An Audacity voice-over chain derived from measurements of your own take, simulated, then verified on the exported file | "check my recording" · "is this ready for Resolve?" |
| [print-svg](#print-svg) | SVG lettering and shapes a slicer imports and a 0.4 mm nozzle prints, matched to a customer's reference | "find a close font to this" · "build the SVG with this text" |

## Install

Inside Claude Code:

```
/plugin marketplace add HehewCrew/claude-skills
/plugin install skill-harvest@claude-skills
/plugin install pots@claude-skills
/plugin install stack-it-right@claude-skills
/plugin install session-open@claude-skills
/plugin install voice-over-chain@claude-skills
/plugin install print-svg@claude-skills
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

**Two modes, one line in the project's `CLAUDE.md`:**

| | Lone wolf (default) | Team: `Pots mode: team` |
|---|---|---|
| Where the pots live | Claude Code's per-project memory directory, never in your repo | `.claude/pots/` in the repo |
| Who sees them | only you | everyone who clones the repo |
| How they sync | they don't | through your normal git commits and pulls |

In team mode Claude writes one line at a time (never whole-file rewrites), signs each
entry with your `git user.name`, checks `git fetch` before writing, and never commits or
pulls for you. A `.gitattributes` line (`.claude/pots/*.md merge=union`) lets two
teammates add todos to the same section without a merge conflict. If it leaves a stale
copy of a line someone edited, the next todos call spots the same bold text twice and
keeps the newer one. Say "switch the pots to
team mode" (or "go lone wolf") and Claude moves the files and sets it up, ready for you
to commit. `skill-harvest`'s log and `session-open`'s todo check follow the same mode.
Ideas inboxes and calendars stay personal.

## stack-it-right

Chooses a project's stack in short question rounds, turns the answers into numbered
requirements (R1, R2, …), then **checks every candidate live**: latest stable version,
maintenance status, pricing and free tiers, what's new in the category, open security
advisories. It recommends one stack where every layer traces back to a requirement,
with versions and dated sources, and records it in `CLAUDE.md`, re-checked when revisited
after ~3 months. Without web access it says so and labels the result "unchecked".

## session-open

One fixed routine before the first request of every session, so no check is skipped
because the first question looked small. It reports four things in one line: parked
work, critical todos with no calendar slot, ideas waiting in an inbox, and today's
calendar sessions for this project. Then **slot accountability**:

- a session that **ended without a ✅** gets "is it done?", and a yes marks it `✅` in the calendar;
- a session **on now** (or started early) opens with its task list: the event's own tasks
  merged with the project's todos, most critical first;
- a session **later today** gets an offer to start now.

`what-for-today` runs the slots part mid-day ("start session", "what for today?").
Events are matched to the project by a `Calendar keyword:` line in its `CLAUDE.md`, or by
the folder name. **Setup:** add *"Before answering the first request of every session, run
the `session-open` skill."* to your `CLAUDE.md`, so it runs even when the first request
doesn't look like it needs it.

## voice-over-chain

A voice-over chain is only right for one voice, one mic and one room, so this skill
measures all three instead of copying tutorial presets. You record an ~80 s test take
(real script lines + 30 s of room tone); a bundled script (`vo_measure.py`, ffmpeg only)
reports the speech levels, the room noise and its spectrum (hiss, murmur or mains hum),
the peak-to-loudness ratio and what the loudest peaks are made of. Every Audacity step
(noise reduction, high-pass, loudness, compressor, limiter) gets a value **with the number
it came from**, the chain is **simulated on your take**, you run it in Audacity, and the
exported file is **measured again**: loudness on two speakers, true peak, clipping, and
whether every pause got cut.

- **Traps it knows:** Audacity's limiter output adds make-up gain unless it equals the
  threshold; "treat mono as dual-mono" moves a mono file 3 dB; the Amplify slider caps at
  50 dB; Audacity 4.0 has no macros (it uses effect presets instead).
- **Needs:** ffmpeg on PATH and Python 3. It can't hear: tone is your call, levels are measured.

## print-svg

For custom 3D-printed pieces (a name tag, a keychain phrase, a heart, a monogram) in Bambu Studio, PrusaSlicer or Orca.

- **The font comes from drafts, not memory:** it renders the customer's real text in 10–15 open-licence fonts next to their reference photo, and names the closest by the letterforms that match.
- **Print-ready by construction:** text is outlined (no font needed in the slicer), fitted to the plate around the ring hole, and every shape is a filled ring, since slicers ignore SVG strokes.
- **Printability you can trust:** the real stroke width (2 × area / perimeter, not a bounding box that counts the slant) is checked against two nozzle lines; letter spacing is shown as a trade against size; thickening reports when a letter's opening closes.
- Says first when the slicer's own text tool is the simpler answer.

Ships two scripts (`build_plate.py`, `font_sheet.py`); needs `uharfbuzz fonttools shapely pillow numpy`, installed into a scratch folder.

## Works with (optional)

Nothing here needs another skill to run. These add to them if you have them:

| Plugin | Optional piece | What it adds | Where to get it |
|---|---|---|---|
| pots | A calendar connector | The session-start check that flags critical todos with no calendar slot | Google Calendar through claude.ai's connector settings, or any calendar MCP server |
| stack-it-right | A mobile-web skill | A checklist for the website / PWA / app decision when phones are involved | e.g. [mobile-web-correctness](https://github.com/daniel-lopez-puig/claude-skills) |
| stack-it-right | An `ask-question` skill | Nothing extra: its question rules are already built into stack-it-right | – |
| session-open | A calendar connector | Critical-todo check and slot accountability (without it, those two checks say so and are skipped) | Google Calendar through claude.ai's connector settings, or any calendar MCP server |
| session-open | The pots plugin | The critical-todos check and the todos in the session task list | This repo: `pots@claude-skills` |
| session-open | A shared weekly plan file | The week check: this project's hours left and notes left by other projects | `~/.claude/weekly-plan.md`, kept by hand or by a planner skill (format in the skill) |

## License

[MIT](LICENSE)
