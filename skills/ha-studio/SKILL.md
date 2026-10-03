---
name: ha-studio
description: "Plan, design and generate business-grade dashboards compatible with Home Assistant (Lovelace Sections YAML, themes, glass iPad and wall-panel previews) with KPIs, per-device energy, cameras, smart devices, Proxmox/Dokploy/domain/backup monitoring and voice. Use whenever the user mentions Home Assistant, Lovelace, HA dashboard, Energy dashboard, tablet or wall panel, smart-office/retail/clinic/hotel monitoring, camera walls, or adding devices to a dashboard."
license: Apache-2.0
compatibility: Works offline from an exported states file; live read-only inventory needs a Home Assistant URL and a long-lived token in the environment. Python 3.10+ with PyYAML; Playwright only for screenshots. Independent project, compatible with Home Assistant, not affiliated with or endorsed by it.
metadata:
  owner: DXBMARK LLC
  version: 1.0.0
  upstream-licences: see THIRD_PARTY_NOTICES.md
---

# HA Studio

Turns a Home Assistant (HA) installation into a dashboard a business owner can read in two seconds:
KPIs first, then rooms and devices, energy per device, cameras, infrastructure, backups and voice.
Every output is **generated config for review** — nothing is pushed to HA unless the person explicitly asks.

## Operating rules (read first)

1. **Read-only by default.** Inventory, audit and generate; never call HA services, edit files in the HA config
   directory, restart HA or change entities without the person's clear, direct permission for that specific change.
   Treat the person's files as confidential: do not move, rename, overwrite or delete them; write results to new files
   (the scripts refuse to overwrite an existing `--out` unless `--force` is given).
2. **Never invent entities.** Use only ids found in the inventory. A KPI with no matching entity is reported as a gap
   with a suggestion (which integration or helper would create it).
3. **Secrets stay out of output.** Tokens come from environment variables, HA `!secret`, or a password manager —
   never into dashboard YAML, URLs, screenshots, chat or commits. `validate_dashboard.py` rejects secret-like strings.
4. **Cameras are privacy-sensitive.** Default to snapshots/sub-streams, audio off, restricted views, no cameras in
   private areas, and show the privacy defaults to the client in the dashboard design (see `references/cameras-security.md`).
5. **Stay inside documented behaviour.** Entity ids differ per integration and version, so take them from the inventory
   only; the sources behind every pattern are in `references/sources.md`. Do not add keys or endpoints that are not listed there.
6. **No branding of others.** No Home Assistant logo and no certification-style claims (it is not a certified or endorsed product); say "compatible with Home Assistant" and add the non-affiliation notice.

## Workflow

Copy this checklist and tick as you go:

```
- [ ] 1 Intake        business type, devices, screens (iPad/wall panel/desktop), languages, who sees what
- [ ] 2 Inventory     ha_inventory.py (live, read-only) or --states-file export
- [ ] 3 Classify+plan categories, KPI list (profile), gaps, per-user visibility
- [ ] 4 Energy audit  energy_audit.py → every device has power + energy; fix list
- [ ] 5 Design        pick variant (Aurora / Midnight / Frost), tokens, density; contrast_check.py
- [ ] 6 Generate      generate_lovelace.py + gen_theme.py (+ package YAML for infra/backup KPIs)
- [ ] 7 Preview       build_design.py → HTML preview → screenshot.py (optional, needs Playwright)
- [ ] 8 Validate      validate_dashboard.py --inventory …; fix until OK
- [ ] 9 Deliver       files + short change list + gaps + what was NOT verified; apply only on request
```

### 1 Intake
Ask only what changes the build: business type (→ `assets/profiles/*.yaml`: office, retail, cafe, clinic,
hotel, warehouse, devops), screen types, tariff/currency, who may see cameras, languages (RTL for Arabic),
which infra to show (Proxmox, Dokploy, domains, backup targets), **rooms** (the person supplies an area → entity
map; areas are never guessed), **who is an admin** (HA user ids that may see Energy/Security/Infra/Backups) and whether
optional custom cards are wanted. If the person is away, take the most
reasonable reading, state it at the top, and continue.

### 2 Inventory
```
HA_URL=http://homeassistant.local:8123 HA_TOKEN=… python3 scripts/ha_inventory.py --out inventory.json
python3 scripts/ha_inventory.py --states-file states.json --out inventory.json   # offline
```
Entities are classified (power, energy, camera, light, climate, lock, security, backup, infra, voice…). Review
`counts` and `unavailable`; flag duplicates and orphans instead of silently dropping them.

### 3–4 Plan and audit
`python3 scripts/energy_audit.py inventory.json --tariff 0.15` lists devices lacking an energy counterpart
(→ Riemann-sum helper), wrong `state_class`, unavailable sensors and untracked load vs the grid.
KPI choices per business type: `references/business-kpis.md`. Entity/card mapping: `references/entity-model.md`,
`references/lovelace-patterns.md`, energy details: `references/energy.md`.

### 5 Design
Three approved glass variants ship as tokens in `assets/tokens/`: **aurora** (dark, orange), **midnight** (navy, sky),
**frost** (light). Keep their look; change only content. Run `python3 scripts/contrast_check.py` after any token
edit — all pairs must pass. Rules for glass, wall panels, touch sizes, states and icons:
`references/design-system.md`, `references/icons.md`.

### 6 Generate
```
python3 scripts/generate_lovelace.py inventory.json --profile office --theme dxbmark_aurora --title "…" --out dashboard.yaml \
    [--areas areas.yaml] [--admin-user <HA_USER_ID> ...] [--force]
python3 scripts/gen_theme.py aurora --out themes/dxbmark_aurora.yaml
```
- `--areas FILE` (`{"Reception": ["light.reception", "lock.main_door"]}`, example `assets/examples/demo_areas.yaml`) adds a
  **Rooms** view, one section per area. Entities missing or unavailable are reported as gaps, not invented. How to get the
  map: `references/community-patterns.md`.
- `--admin-user USER_ID` (repeatable) sets the core view option `visible: [{user: <id>}]` on the Energy, Security, Infra
  and Backups views, so other users do not see those tabs. Visibility hides tabs; it is not an access-control boundary.
- **Optional custom cards** (bubble-card, Mushroom, card-mod, button-card, apexcharts-card via HACS) are polish only.
  The generated baseline uses core cards and works without them; if the client wants them, list each as an explicit
  dependency to install first and never output a card type that is not installed.

Infra/backup KPIs (Proxmox, Dokploy, certificates, Google Drive, stale-backup alert) come from
`assets/examples/packages/dxbmark_infra.yaml` plus `references/infrastructure.md`. Prefer HA-native mechanisms
(official integrations, REST sensors, template sensors, webhooks). n8n is optional and licence-restricted
(see `references/infrastructure.md`).

### 7 Preview (optional)
`python3 scripts/build_design.py --out preview/ --brand "…"` builds standalone HTML iPad previews;
`python3 scripts/screenshot.py preview/aurora.html --out shots/` renders PNGs. These are design mockups with sample
data, not live HA.

### 8–9 Validate and deliver
`python3 scripts/validate_dashboard.py dashboard.yaml --inventory inventory.json` must print OK. Deliver the files,
a 5-line summary (views, KPIs, gaps, helpers to create, items not verified), and exact apply steps (raw
configuration editor or YAML-mode dashboard). Applying to a live HA is a separate step that needs a yes.

## Adding devices later
Re-run inventory, diff against the previous `inventory.json`, map new entities by domain + `device_class`
(`references/entity-model.md`), run the energy audit, regenerate. Keep a changelog line per added device.

## Working with other skills
This skill bundles a read-only copy of the ui-ux-pro-max design knowledge base (MIT, see `vendor/ui-ux-pro-max/LICENSE`).
Query it with `scripts/design_search.py "<query>" [--domain style|color|chart|ux|typography|motion]`; the wrapper adds the Home
Assistant corrections (landing-page advice does not apply, use theme variables, contrast on the composited card).
It also combines well with frontend/artifact skills for HTML previews, DevOps/data skills for the infra side,
and a computer-vision skill for camera analytics.

## Files
- `scripts/` — ha_inventory, energy_audit, generate_lovelace, gen_theme, contrast_check, validate_dashboard,
  build_design, build_sheets, screenshot, design_search, lint_skill
- `references/` — entity-model, lovelace-patterns, energy, infrastructure, business-kpis, cameras-security,
  design-system, community-patterns, icons, platforms, sources
- `assets/` — tokens, themes, profiles, templates (iPad glass HTML), icons (FA Free subset), examples, runtime
