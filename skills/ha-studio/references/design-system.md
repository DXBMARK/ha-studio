# Design system: glass that stays readable

## Approved variants (tokens in `assets/tokens/*.json`, themes in `assets/themes/`)
| Variant | Mood | Accent | Surface |
|---|---|---|---|
| Aurora | warm dark | orange `#f97e1a` | `rgba(255,255,255,.07)` card, 20 px radius, 24 px blur |
| Midnight | cool navy | sky `#62c4e1` | `rgba(255,255,255,.06)` card, 24 px radius, 32 px blur |
| Frost | light | orange, accent text `#a84700` | `rgba(255,255,255,.55)` card, 20 px radius, 28 px blur |

Change content, not the look. After editing any token, run `python3 scripts/contrast_check.py` (exit 0 required).

## Accessibility rules
- Text ≥ 4.5:1, UI marks and chart bars ≥ 3:1 against the **composited** glass surface. `contrast_check.py` composites the card over a
  worst-case backdrop sample (glow at half strength) and reports the glow-peak ratio as advisory.
- Plain white-tint glass with light text fails on mid-tone backdrops; keep backdrops dark (or light) and known.
- Structure CSS as *opaque unless proven capable*: solid fallback, `@supports (backdrop-filter: blur(1px))` enhancement,
  overrides for `prefers-reduced-transparency`, `prefers-contrast` and `forced-colors`. Offer a no-blur "soft surface" mode;
  blur is expensive on tablets — benchmark on the real device.
- Camera and chart areas opaque. Borders are decorative; never the only cue for a control.
- Status = icon + text + colour. Critical red text needs a lighter red on dark cards (checked by the script).

## Touch and wall panels
- Hit areas ≥ 48 px, primary tiles ≥ 64 px, gaps ≥ 12 px; hold-to-confirm for unlock/disarm.
- Key values ≥ 24 px, 12–16 tiles per view, no auto-scroll, one idea per view.
- Dark theme, dim at rest, brighten on presence, shift content periodically to limit burn-in.
- RTL (Arabic): mirror layout with logical properties; keep numerals and units legible (tabular figures).

## State matrix (every widget)
loading · empty · error · stale · `unavailable` · `unknown` · normal. Define each; test with the demo inventory.

## Previews
`assets/templates/ipad-glass.tpl.html` + `scripts/build_design.py` build standalone iPad previews (sample data, inline Font Awesome
Free SVG icons, bundled shim). HA itself uses `mdi:` names — see `references/icons.md`.

## Theme variable stability
Home Assistant's theme docs list only a few variables (`primary-color`, `accent-color`, text colours) and state that other variables can change between releases. `ha-card-background`, `ha-card-backdrop-filter`, `ha-card-border-*`, `card-background-color` work today but are undocumented: say so to the client and re-test after HA updates.

## Using ui-ux-pro-max
A read-only copy ships in `vendor/ui-ux-pro-max/` (MIT, Copyright (c) 2024 Next Level Builder, upstream
https://github.com/nextlevelbuilder/ui-ux-pro-max-skill, commit 09170ee, v2.13.0). Query it with
`python3 scripts/design_search.py "<query>" --domain <style|color|chart|ux|typography|motion>`.
Correct its defaults: its design-system output is landing-page oriented, its glass recipe must be re-checked for contrast with
`contrast_check.py`, and its icon set is not MDI. The vendored folder is unmodified upstream code and data (large font/icon
catalogues were left out); keep its LICENSE with any copy.
