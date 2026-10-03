# HA Studio — agent instructions

This repository ships one Agent Skill: `skills/ha-studio/` (open Agent Skills format).

- When a task involves Home Assistant dashboards, Lovelace YAML, the Energy dashboard, tablet/wall-panel layouts, KPIs,
  cameras or infrastructure monitoring (Proxmox, Dokploy, domains, backups), load `skills/ha-studio/SKILL.md`
  and follow its workflow.
- Read-only by default: never change a Home Assistant instance, config directory or user files without explicit permission.
- Never put tokens or secrets into generated files, URLs, screenshots or commits.
- Before claiming completion run `pytest -q` and
  `python3 skills/ha-studio/scripts/lint_skill.py`.
- Codex/Antigravity: place or symlink the skill folder in `.agents/skills/`.
