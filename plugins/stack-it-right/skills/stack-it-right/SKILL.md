---
name: stack-it-right
description: Use when starting a new project, or a new part of one, whose programming language, framework, database, hosting or platform is not yet decided; when the user asks "what stack should I use", "what should I build this with", "Python or JS?", "do I need a backend?", "app or website?"; before scaffolding anything in an empty or near-empty folder; or when a recorded stack is being revisited. Derives the stack from the project's requirements and checks every candidate live (latest versions, maintenance, pricing) before recommending. Also when invoked as /stack-it-right.
---

# Stack it right

The stack is the most expensive decision to undo. Settle it with the user, in their terms, before any scaffolding: ask only what changes the answer, **check what is current today**, recommend one stack that traces back to the requirements, and record it.

**Question rounds.** If an `ask-question` skill is installed, follow its rules. Otherwise: check the folder and conversation before asking; state an assumption in one line instead of asking when it wouldn't change the answer; use AskUserQuestion with at most 4 questions per round; phrase options in the user's terms, not jargon; put the recommendation first, marked "(Recommended)"; flag anything paid or any new dependency.

## Step 1: collect what's already known

Read the folder, `CLAUDE.md`, memory and the conversation. Existing code, data files (a spreadsheet, a database dump) and the user's other projects all answer questions. Tick off every row below that they already settle.

## Step 2: ask, in rounds

Go through the rounds in order. Before each one, drop every question the earlier answers already settle (a static catalogue site doesn't need the real-time question). Stop early once one stack clearly wins. **Write each answer down as a numbered requirement** (R1, R2, …): Step 4 must trace every choice back to them.

**Round 1: what it is**

| Question | Decides |
|---|---|
| What does it do, in one sentence, and for whom? | Everything below |
| Where will people use it: phone browser, installed app, desktop, a terminal, or other software (an API, a bot)? | Web / mobile / desktop / CLI / backend-only |
| How do users arrive: a link (social media, messaging apps, search), a store, colleagues, just the user? | Website vs app; SEO; in-app browsers |
| How many users and how much data, now and in a year? | Static vs server; database; hosting tier |

**Round 2: what it needs**

| Question | Decides |
|---|---|
| Do users sign in? Do different people see different things? | Auth; backend or not |
| What does it store, and does it change often? Files, photos, video? | Database or flat files; object storage |
| Must it work offline, update live, or run in the background? | Local-first; websockets; app vs web |
| What must it connect to: payments, messaging apps, email, maps, an AI model, existing software? | SDK availability per language |

**Round 3: who and how much**

| Question | Decides |
|---|---|
| Who will maintain it after it's built, and which languages do they know? | Language; boring vs new |
| Monthly budget for hosting and services, including zero? | Free tiers, static hosting, self-hosting |
| Where should it run: this PC, a free host, a paid cloud, the client's server? | Hosting and deployment |
| Quick prototype, or something to maintain for years? | Framework weight; tests; typing |

**Round 4: the risks (ask only the ones that apply)**

| Question | Decides |
|---|---|
| Sensitive data: payments, health, children, personal data of EU users? | Managed services; compliance |
| Which languages and scripts: right-to-left (Arabic, Hebrew), several languages? | i18n library; RTL support; fonts |
| Hard performance needs: heavy graphics, big computations, instant response? | Language and runtime |
| Anything imposed: a client's tech, a required platform, an existing team? | Overrides the rest |

## Step 3: check what's current, live

Training knowledge goes stale: versions move, projects get deprecated or relicensed, free tiers shrink, better options appear. **Never recommend from memory alone.** Shortlist two or three candidates per layer from the requirements, then check each one with web search and web fetch, today:

- **Latest stable version and its release date:** the official release notes or changelog, the package registry (npm, PyPI, crates.io, Maven…), or GitHub releases.
- **Health:** actively maintained (recent releases and commits), or deprecated, end-of-life, archived, acquired or relicensed. An LTS or support end date that falls within the project's life counts against it.
- **Pricing and limits** of any hosting or service: the current free tier, what triggers paid usage, and any recent change. Read the official pricing page, not a blog.
- **What's new in the category:** anything released or matured in the last 12 months that fits the requirements better. Newness alone is not a reason: it must serve a requirement better than the mature option, with docs and a community to match.
- **Security advisories** open against the version you'd pick.

Prefer primary sources, and date every fact ("checked 2026-09-27"). If web access isn't available, say so in one line and mark the whole recommendation **"unchecked: from training data"**, so the user knows to verify it.

## Step 4: recommend one stack

Weigh the checked candidates with these defaults, in order:
1. **Meets every requirement,** each choice traced to the R-numbers it answers. A choice that answers none is dropped.
2. **Cheapest and simplest that does it:** static before server, free tier or local before paid, one language before two, fewest moving parts.
3. **What the maintainer already knows,** and what the project's existing code uses.
4. **Current and healthy:** the latest stable (or LTS) version, actively maintained; mainstream and well documented over niche, which Claude also codes most reliably.
5. **An exit path:** no lock-in the project can't afford.

Present it as one table: layer (language, framework, UI, data, auth, hosting, tests, CI) → choice **with version** → requirements it answers → one-line why → the runner-up → checked (date + source link). Below it: the expected monthly cost, what would make you switch to the runner-up, anything new the check turned up that didn't make the cut (and why), and one alternative whole stack if two were close. If phones are involved and a mobile skill is installed (e.g. `mobile-at-best` or `mobile-web-correctness`), check the website/PWA/app decision against it.

Then confirm with one AskUserQuestion: accept, swap a layer, or take the alternative.

## Step 5: record it

Once accepted, write a **Stack** section into the project's `CLAUDE.md` (create it if missing): each layer with its version, the requirements it answers, the date it was checked, and the reason in one line, so later sessions don't re-open the decision. **When a later session revisits the stack more than ~3 months after that date, re-run Step 3 for the recorded layers first.** Don't scaffold until the user says to.

## Rules

- **Requirements first, technology second.** Every layer must answer a stated requirement; "it's popular" or "it's new" is not a requirement.
- **No unchecked version numbers.** A version or price in the table comes from today's check, with its source.
- **One recommendation,** not a menu; the runner-up and the alternative stack are the escape hatches.
