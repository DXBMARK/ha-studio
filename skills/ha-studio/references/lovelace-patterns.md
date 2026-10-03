# Lovelace patterns used by the generator

Sections is the default view type in current HA: a view holds `sections`, each a grid of cards. The generator
emits this shape (keys listed in `references/sources.md`):

```yaml
views:
  - title: Overview
    path: overview
    icon: mdi:view-dashboard
    type: sections
    theme: dxbmark_aurora
    sections:
      - type: grid
        cards:
          - {type: heading, heading: Key indicators, icon: "mdi:chart-box"}
          - {type: gauge, entity: sensor.grid_power, min: 0, max: 10000, needle: true}
          - {type: tile, entity: light.reception, features: [{type: light-brightness}]}
```

## Card choice
- **KPI value** → `tile`. A `gauge` only for one hero metric with a defined range and labelled severity zones.
- **Trend** → `statistics-graph` (uses long-term statistics) for days; `history-graph` for hours.
- **Control** → `tile` with a feature (brightness, target temperature, cover position). Min 48 px hit area on touch.
- **Camera** → `picture-entity` with `camera_view: auto` (snapshot cards, live on tap). Never autoplay many streams.
- **Energy** → `energy-distribution`, `energy-usage-graph`, `energy-devices-graph`, `energy-sources-table`; these read the
  Energy dashboard configuration, so configure that first (`references/energy.md`).
- **Notes/links** → `markdown` (no secrets, no tokens in URLs).

## Layout
- 12–16 tiles per view; split by room or function instead of scrolling. No auto-scroll or carousels on wall panels.
- Put the KPI section first; controls second; diagnostics last.
- Use one `theme:` per view (or per dashboard) so tablets can differ from desktop.
- Custom cards (card-mod, Mushroom, button-card, apexcharts-card, Bubble Card, Advanced Camera Card) are optional polish,
  installed separately via HACS. Declare each as an explicit dependency; the generated baseline must work without them.

## Delivery modes
1. Paste into a dashboard's **raw configuration editor** (UI-managed dashboard) — simplest.
2. YAML-mode dashboard declared under `lovelace: dashboards:` in `configuration.yaml`, file kept in git.
3. Per-user visibility with `visible:` on views (cameras and security views for admins/managers only).
