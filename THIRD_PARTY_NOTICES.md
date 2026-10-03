# Third-party notices

DXBMARK LLC owns the original content of this repository (code, templates, tokens, text, screenshots of its own
mock-ups) and publishes it under Apache-2.0. The items below belong to their respective owners and remain under
their own licences. Nothing here transfers or claims their rights.

| Item | Used for | Licence | How it is used |
|---|---|---|---|
| Font Awesome Free (icons as SVG paths) | `assets/icons/fa-subset.json` (55 icons), HTML previews, `docs/screenshots/icons.webp` | CC BY 4.0 (icons); OFL 1.1 (fonts); MIT (code) — https://fontawesome.com/license/free | 55 icons copied as SVG path data. Attribution: "Font Awesome Free by Fonticons, Inc., CC BY 4.0" (also embedded as a comment in every generated preview). Only solid-style icons are included; no brand glyphs; Pro assets are never included. |
| Material Design Icons | `mdi:` names in generated YAML | Apache-2.0 (some icons keep original licences) | Names only; no icon files bundled. |
| Inter | Preview typography | SIL OFL 1.1 | Loaded from Google Fonts at runtime; embedded only inside rendered screenshots. |
| Source Serif 4 | Preview headings | SIL OFL 1.1 (Reserved Font Name "Source") | Same; the font is not modified or renamed. |
| JetBrains Mono | Preview monospace | SIL OFL 1.1 | Same. |
| Home Assistant (core, frontend) | Target platform; card/theme names | Apache-2.0 (code) | Referenced only. No code copied. |
| Home Assistant documentation | Source of facts | CC BY-NC-SA 4.0 | Not copied. Facts are restated in original wording and linked; no doc text or doc examples are reproduced. |
| ui-ux-pro-max (nextlevelbuilder/ui-ux-pro-max-skill, v2.13.0, commit 09170ee) | Design knowledge base (search scripts + CSV data) | MIT, Copyright (c) 2024 Next Level Builder | Bundled unmodified in `skills/ha-studio/vendor/ui-ux-pro-max/` with its LICENSE (large Google-Fonts and Phosphor catalogues omitted). We rely on upstream's MIT statement for its data. |
| Playwright, PyYAML, pytest | Development and tests | Apache-2.0 / MIT | Installed from PyPI by the user; not redistributed. |
| n8n | Optional integration discussed in docs | Sustainable Use License | No n8n code or workflows are distributed. Users install n8n themselves under its licence. |
| shields.io | README badges (images loaded from img.shields.io at view time) | Service terms | Not redistributed. |
| GitHub Actions, CodeQL, Dependabot | CI, security scan, updates | GitHub terms | Workflows only. |
| Docker base image `python:3.12-slim` and Docker actions | Container image (ghcr.io) | Their respective licences | Pulled at build time; not committed. |
| jlnbln/My-HA-Dashboard and community dashboards | Inspiration for room-based and per-user layouts | n/a | Studied for ideas only; no code, text or images copied. |

The Home Assistant name, logo and trademarks belong to their owners (Open Home Foundation). This repository does not
use the logo and uses the name only descriptively ("compatible with Home Assistant").
