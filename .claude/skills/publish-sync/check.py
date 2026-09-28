"""Check that every place describing a plugin agrees with the plugins themselves.

Run from the repository root:  python .claude/skills/publish-sync/check.py [--base REF] [--github]

Compares the working tree (staged, unstaged and untracked files) with REF (default: the
merge-base with main, or origin/main when on main). Prints ERROR lines (must fix) and
REVIEW lines (a changed plugin whose descriptions elsewhere did not change: read and decide).
Exit code 1 if any ERROR, else 0.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MARKET = ".claude-plugin/marketplace.json"


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def at_base(base, path):
    r = subprocess.run(["git", "show", f"{base}:{path}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def base_ref(explicit):
    if explicit:
        return explicit
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch == "main":
        return "origin/main"
    return git("merge-base", "HEAD", "main").strip()


def readme_section(text, name):
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text or "", re.M | re.S)
    return m.group(1).strip() if m else None


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "0"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--github", action="store_true", help="also check the GitHub About text names every plugin")
    a = ap.parse_args()
    base = base_ref(a.base)

    changed = set(git("diff", "--name-only", base).split()) | set(
        git("ls-files", "--others", "--exclude-standard").split())
    errors, review = [], []

    market = json.loads((ROOT / MARKET).read_text(encoding="utf-8"))
    market_base = json.loads(at_base(base, MARKET) or '{"plugins": [], "metadata": {}}')
    entries = {p["name"]: p for p in market.get("plugins", [])}
    entries_base = {p["name"]: p for p in market_base.get("plugins", [])}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_base = at_base(base, "README.md")

    plugins = sorted(p.name for p in (ROOT / "plugins").iterdir() if (p / ".claude-plugin/plugin.json").exists())
    any_plugin_changed = False

    for name in plugins:
        pj_path = f"plugins/{name}/.claude-plugin/plugin.json"
        pj = json.loads((ROOT / pj_path).read_text(encoding="utf-8"))
        pj_base_text = at_base(base, pj_path)
        pj_base = json.loads(pj_base_text) if pj_base_text else None
        touched = sorted(f for f in changed if f.startswith(f"plugins/{name}/"))

        # Always true, changed or not
        for field in ("name", "version", "description"):
            if not pj.get(field):
                errors.append(f"{pj_path}: missing \"{field}\"")
        if pj.get("name") != name:
            errors.append(f"{pj_path}: name \"{pj.get('name')}\" differs from its folder \"{name}\"")
        if name not in entries:
            errors.append(f"{MARKET}: no entry for plugin \"{name}\"")
        elif entries[name].get("source") != f"./plugins/{name}":
            errors.append(f"{MARKET}: \"{name}\" source should be ./plugins/{name}")
        if not re.search(rf"^\|\s*\[{re.escape(name)}\]\(#{re.escape(name)}\)", readme, re.M):
            errors.append(f"README.md: no row for \"{name}\" in the plugin table")
        if readme_section(readme, name) is None:
            errors.append(f"README.md: no \"## {name}\" section")
        if f"/plugin install {name}@{market.get('name')}" not in readme:
            errors.append(f"README.md: no \"/plugin install {name}@{market.get('name')}\" line")
        for skill in sorted((ROOT / f"plugins/{name}/skills").glob("*/SKILL.md")):
            rel = skill.relative_to(ROOT).as_posix()
            if f"`{skill.parent.name}`" not in readme and skill.parent.name != name:
                errors.append(f"README.md: skill `{skill.parent.name}` ({name}) is never mentioned")
            fm = re.match(r"---\n(.*?)\n---", skill.read_text(encoding="utf-8").replace("\r\n", "\n"), re.S)
            meta = dict(re.findall(r"^(\w+):\s*(.*)$", fm.group(1), re.M)) if fm else {}
            if meta.get("name") != skill.parent.name:
                errors.append(f"{rel}: frontmatter name \"{meta.get('name')}\" differs from its folder")
            if not meta.get("description"):
                errors.append(f"{rel}: no description in frontmatter")
            elif len(meta["description"]) > 1024:
                errors.append(f"{rel}: description is {len(meta['description'])} chars (limit 1024)")
        if name not in market.get("metadata", {}).get("description", ""):
            errors.append(f"{MARKET}: metadata.description doesn't name \"{name}\"")

        if not touched:
            continue
        any_plugin_changed = True

        # Changed since base
        if pj_base and version_tuple(pj.get("version")) <= version_tuple(pj_base.get("version")):
            errors.append(f"{pj_path}: plugin changed ({len(touched)} files) but version is still {pj.get('version')}")
        if name in entries and name in entries_base and entries[name] == entries_base[name]:
            review.append(f"{MARKET}: \"{name}\" changed but its marketplace description didn't — does it still fit?")
        if pj_base and pj.get("description") == pj_base.get("description"):
            review.append(f"{pj_path}: \"{name}\" changed but its description didn't — does it still fit?")
        if readme_base is not None and readme_section(readme, name) == readme_section(readme_base, name):
            review.append(f"README.md: \"{name}\" changed but its README section didn't — does it still fit?")

    for name in entries:
        if name not in plugins:
            errors.append(f"{MARKET}: entry \"{name}\" has no plugins/{name}/ folder")

    if any_plugin_changed and version_tuple(market.get("metadata", {}).get("version")) <= version_tuple(
            market_base.get("metadata", {}).get("version")):
        errors.append(f"{MARKET}: plugins changed but metadata.version is still {market['metadata'].get('version')}")

    if a.github:
        r = subprocess.run(["gh", "repo", "view", "--json", "description", "-q", ".description"],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            review.append(f"GitHub: couldn't read the About text ({r.stderr.strip()[:80]})")
        else:
            for name in plugins:
                if name not in r.stdout:
                    errors.append(f"GitHub About: doesn't name \"{name}\"")
            if any_plugin_changed:
                review.append(f"GitHub About: plugins changed — does it still fit? Now: \"{r.stdout.strip()}\"")

    print(f"publish-sync check against {base[:12]} · {len(plugins)} plugins · "
          f"{len(errors)} error(s) · {len(review)} to review")
    for e in errors:
        print("ERROR  ", e)
    for r_ in review:
        print("REVIEW ", r_)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
