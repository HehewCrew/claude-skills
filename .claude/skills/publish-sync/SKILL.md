---
name: publish-sync
description: Use in the claude-skills repo before any commit that touches plugins/ or .claude-plugin/ (a skill, agent or plugin added, edited, renamed or removed), when a plugin's version or description may be stale, when the README, marketplace.json or the GitHub About text may no longer match what the plugins do, or when the user says "publish-sync", "sync the descriptions" or "update the repo description".
---

# publish-sync

Each plugin is described in six places. Change the skill, and all six must follow. The script finds what's out of line; you write the wording.

| # | Place | What it holds |
|---|---|---|
| 1 | `plugins/<p>/skills/*/SKILL.md` frontmatter | the source of truth: edited first, by the change itself |
| 2 | `plugins/<p>/.claude-plugin/plugin.json` | `version`, full `description` (1–3 sentences) |
| 3 | `.claude-plugin/marketplace.json` | the plugin's one-line `description`; `metadata.description` (names every plugin); `metadata.version` |
| 4 | `README.md` | intro paragraph, the plugin table row, `## <plugin>` section, "Works with" table, install lines |
| 5 | GitHub About | `gh repo view --json description` (names every plugin, ≤ 350 chars) |
| 6 | GitHub topics | only when a new kind of plugin arrives |

## Steps

1. **Run the check** from the repo root: `python .claude/skills/publish-sync/check.py --github` (set `PYTHONIOENCODING=utf-8`). It compares the working tree with the branch's merge-base with `main`.
2. **Read what changed:** `git diff <base> -- plugins/<p>/` for each plugin the check names. Know what the change does before writing a word about it.
3. **Fix every ERROR**, then decide every REVIEW line: update the text when the change is something a reader would choose the plugin for (a new mode, a new skill, a new trigger); leave it when it isn't (wording, a fix), and say so.
   - **Versions:** plugin `version` — patch for fixes and wording, minor for a new feature or skill, major when existing users must change something. `metadata.version` takes the highest bump of any plugin in the change.
   - **Wording:** match each place's voice and length. Read the neighbouring entries first. The marketplace line is one short sentence; the table row is ≤ 15 words; the plugin.json description may run to three sentences; the README section explains and shows.
   - **A new or removed plugin** touches every place that names the plugin set: the README intro, table and install lines, the "Works with" table, `metadata.description` and the About text.
4. **Re-run the check** until it prints 0 errors and every REVIEW line is answered.
5. **GitHub About and topics, only after the change is on `main` on GitHub.** The About text describes what visitors can install, so it follows the merge, never the branch. Draft the new text, show old and new, and ask before `gh repo edit HehewCrew/claude-skills --description "…"` (or `--add-topic`). It is public the moment it runs. If the change isn't merged yet, end by saying the About update is waiting on the merge.
6. **Report** in a few lines: what changed where, the version bumps, the REVIEW lines left as they were and why, and whether the About text is done or waiting.

## Common mistakes

- Bumping `plugin.json` and forgetting `marketplace.json` (both its entry and `metadata.version`).
- Editing the GitHub About from a branch: it then advertises what isn't installable yet.
- Copying the plugin.json description into the marketplace line: the marketplace needs the short version.
- Rewriting descriptions for a typo fix. A REVIEW line can be answered with "still fits".
