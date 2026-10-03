# Platform compatibility (summary — full steps in the repo README)

The skill is one folder (`skills/ha-studio/`) in the open Agent Skills format. Adapters only package it.

| Platform | Install | Notes |
|---|---|---|
| Claude Code | `/plugin marketplace add <owner>/ha-studio` → `/plugin install ha-studio@dxbmark` | Updates arrive when `version` changes |
| Claude (claude.ai) | Upload `ha-studio-<version>.zip` in Settings → Capabilities → Skills | Needs a plan with code execution; ZIP root = skill folder |
| Claude API | Upload via the Skills API, attach with `container.skills` | Container has no network: use offline `--states-file` |
| Codex | Copy/symlink to `.agents/skills/` (repo) or `~/.agents/skills/` (user); invoke `$ha-studio` | `AGENTS.md` is a short pointer |
| ChatGPT | Business/Enterprise/Edu: Skills (if enabled). Otherwise a Project or custom instructions with `chatgpt/` files | Instructions ≤ 5,000 chars; knowledge as flat files |
| Gemini | Gemini CLI (where still available): `gemini skills install <git URL>`; Gemini app: paste `gem-instructions.md` into a Gem | Consumer Gemini CLI access ended in 2026; enterprise remains |
| Antigravity | Copy into `.agents/skills/` or the global skills folder; or `agy` plugin install from a clone | Check the current docs for your version |

Portability rules kept in this skill: only the six spec frontmatter keys, name = folder name, no reserved words in the name,
SKILL.md < 500 lines, references one level deep, scripts use the Python standard library plus PyYAML.
