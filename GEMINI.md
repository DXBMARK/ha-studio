# HA Studio (Gemini context)

Skill folder: `skills/ha-studio/` (open Agent Skills format). For Home Assistant dashboard, Lovelace, Energy,
camera, KPI or infrastructure-monitoring tasks, read `skills/ha-studio/SKILL.md` first and follow its workflow.
Rules: read-only by default, never invent entities, never write secrets into output, state what is unverified.
Generator options: `--areas FILE` (Rooms view from a user-supplied area map), `--admin-user USER_ID` (view `visible` for
admin-only tabs), optional HACS custom cards (bubble-card, Mushroom, card-mod) never required by the baseline.
