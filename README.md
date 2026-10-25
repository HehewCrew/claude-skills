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
| [replacement-part](#replacement-part) | A broken real part copied into a printable model from photos and a tape measure, fit-tested before the real material | "make a 3D model of this" · "copy this part" |
| [print-ready](#print-ready) | Bambu Studio projects that open and print with nothing to configure (a heavier base baked in), and a cost per piece and set that says what a price earns per printer hour | "the 3mf ready to use" · "how much does a set cost to print?" |

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
/plugin install replacement-part@claude-skills
/plugin install print-ready@claude-skills
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

## replacement-part

For a lid, cover, lens, bracket or shell that broke, from the user's photos and a tape measure, printed on a Bambu Lab printer.

- **Fit first, shape second:** it asks only for the dimensions that decide the fit (outer size, hole-to-hole, holes, wall) and what the part does, which picks the material (light through it, heat, children, outdoors).
- **Measurements from people who aren't CAD users:** side-section sketches to confirm the profile isn't read upside down, the model rendered with arrows and labels when a word doesn't land, and shape options rendered side by side.
- **Parametric and rounded:** a revolved profile with cuts, every dimension marked measured or estimated; edges rounded in 2D and then with a Blender bevel, with the traps that make a bevel silently do nothing.
- **Printable near the plate's size:** 45° ledges instead of steps, normal supports instead of tree supports and no brim (the slicer refuses them at the plate's edge), and an estimate sliced with the real supports and walls.
- **A fit test before the real material:** a thin ring with the exact outline and holes, pinned onto the original or the mounting.

Ships `bevel.py` (Blender, headless), `slice_with.py` (Bambu Studio slicing with process overrides) and a worked example (`revolved_lid.py`). Needs the bambu-studio-ai skill's Python environment (`manifold3d`, `trimesh`) and Blender 4.2+.

## print-ready

For a set of models sold in sizes or variants (a chess set, a product line) and printed on a Bambu Lab printer.

- **Sizes from one reference dimension**, measured from the files, and one-colour plates written as **3MF**: detailed STL plates pass GitHub's 100 MB limit.
- **Heavier pieces, measured before recommended:** base heights and infills sliced side by side (weight and time), with the overhead a split estimate adds removed.
- **Files that need no setup:** a height-range modifier (e.g. the bottom 15 mm at 40 % infill) written into the project and re-sliced with the project's own settings, including the trap that makes Bambu ignore it silently (`<object id="1">`).
- **Costs that hold up:** filament, electricity (draw, not the power-supply rating), a machine-hour floor, a savings reserve, and what a selling price earns per printer hour; a set / half set / single-piece price ladder.

Ships `plate.py`, `make_ready.py` and `cost.py`. Needs the bambu-studio-ai skill's Python environment and Bambu Studio installed.

## Works with (optional)

Nothing here needs another skill to run. These add to them if you have them:

| Plugin | Optional piece | What it adds | Where to get it |
|---|---|---|---|
| pots | A calendar connector | The session-start check that flags critical todos with no calendar slot | Google Calendar through claude.ai's connector settings, or any calendar MCP server |
| stack-it-right | A mobile-web skill | A checklist for the website / PWA / app decision when phones are involved | e.g. [mobile-web-correctness](https://github.com/daniel-lopez-puig/claude-skills) |
| stack-it-right | An `ask-question` skill | Nothing extra: its question rules are already built into stack-it-right | – |
| session-open | A calendar connector | Critical-todo check and slot accountability (without it, those two checks say so and are skipped) | Google Calendar through claude.ai's connector settings, or any calendar MCP server |
| session-open | The pots plugin | The critical-todos check and the todos in the session task list | This repo: `pots@claude-skills` |
| replacement-part | [bambu-studio-ai](https://github.com/heyixuan2/bambu-studio-ai) | Its Python environment, analyze/preview scripts and Bambu Studio slicing, which `slice_with.py` builds on (required for slicing; modelling needs only `manifold3d` + `trimesh`) | GitHub, MIT |
| print-ready | [bambu-studio-ai](https://github.com/heyixuan2/bambu-studio-ai) | Its Python environment and `slice.py`, which give the projects `make_ready.py` finishes (required) | GitHub, MIT |
| print-ready | The replacement-part plugin | `slice_with.py`, for slicing with supports or other process overrides | This repo: `replacement-part@claude-skills` |
| session-open | A shared weekly plan file | The week check: this project's hours left and notes left by other projects | `~/.claude/weekly-plan.md`, kept by hand or by a planner skill (format in the skill) |

## License

[MIT](LICENSE)
