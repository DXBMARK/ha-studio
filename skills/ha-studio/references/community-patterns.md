# Patterns from well-loved community dashboards

Studied (ideas only, nothing copied): the Home Assistant dashboards docs, the default onboarding dashboard, a published
room-based community dashboard (https://github.com/jlnbln/My-HA-Dashboard, no licence stated, so no code or assets were used)
and a 2026 roundup (https://www.seeedstudio.com/blog/2026/01/09/best-home-assistant-dashboards/). Checked 2026-10-03.

| Pattern seen | How HA Studio does it | Needs add-ons? |
| :- | :- | :- |
| Room-based views with lights, climate, media per room | `generate_lovelace.py --areas areas.yaml` builds a Rooms view from an area map you supply (areas are never guessed) | No |
| Layout adapts to the user | `--admin-user ID` (repeatable) sets view `visible: [{user: ID}]` on Energy, Security, Infra, Backups; everyone else sees Overview, Rooms, Voice | No (core `visible` option) |
| Responsive: phone, tablet, desktop | Sections view grid reflows; design previews are checked at iPad size | No |
| Glanceable hierarchy: critical state first, one action per tile | KPI row, then rooms, then systems; status uses icon + text, never colour alone | No |
| Polished, rounded, glassy look | Aurora / Midnight / Frost themes with measured contrast, opaque dialogs, fallbacks for reduced transparency | No (theme only) |
| Heavier styling with custom cards (card-mod, bubble-card, mushroom, button-card) | Optional "enhanced" step: only if the client installs them from HACS; the default output uses core cards so it survives HA updates | Yes (HACS) |
| Music and media control | media_player tiles on Voice; Music Assistant optional | Optional |
| Wall panel / e-ink / kiosk | 48 px targets, large type, low-motion; kiosk-mode is a client choice | Optional |

## Rules we keep
- Core cards first; custom cards are an explicit opt-in per client, listed with their licences.
- Never copy another dashboard's YAML or CSS unless its licence allows it; describe the idea, build it fresh.
- Every Rooms entry must exist in the inventory; gaps are reported.
- Say clearly in the hand-over that undocumented theme variables may change between HA releases.

## Getting an area map
Developer tools > Template:
`{% for a in areas() %}{{ area_name(a) }}: {{ area_entities(a) }}{{ "\n" }}{% endfor %}`
Convert to `{"Area": ["light.x", ...]}` and pass it with `--areas`.
