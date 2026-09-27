# claude-skills

Skills for [Claude Code](https://claude.com/claude-code).

## skill-harvest

Sessions keep solving the same kinds of problems. `skill-harvest` looks back over the
current session (and the project's memory, if it has one) for procedures worth keeping:
things done twice, fixes that cost a retry, rules you set along the way. It proposes at
most five candidates in one table, logs what you declined so it isn't proposed again,
and builds only the skills you pick.

Run it with `/skill-harvest`, by asking "anything here worth a skill?", or at the end
of a session.

## Install

As a plugin, inside Claude Code:

```
/plugin marketplace add HehewCrew/claude-skills
/plugin install skill-harvest@claude-skills
```

Or copy `plugins/skill-harvest/skills/skill-harvest/` into `~/.claude/skills/`.

## License

MIT
