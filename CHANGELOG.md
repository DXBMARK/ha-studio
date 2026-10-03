# Changelog

## 1.1.0 — 2026-10-03
- Added `tools/serve_demo.py`: runs the whole pipeline locally on demo data (or your export) and serves an index page.
- Dependencies pinned to exact tested versions (`requirements-test.txt`, `requirements-dev.txt`; PyYAML 6.0.2 → 6.0.3 patch).
- GitHub Actions pinned to commit SHAs within their current major versions; Dependabot limited to minor/patch.
- README: single "Get in touch" footer (duplicate contact table removed), "Try it locally" and "Why a Docker image" sections.

## 1.0.0 — 2026-10-03
- First release: skill `ha-studio` (workflow, 10 references, 7 business profiles).
- Scripts: inventory, energy audit, Lovelace generator, theme generator, contrast checker, dashboard validator,
  HTML preview builder, screenshot tools, skill linter.
- Three approved glass variants (Aurora, Midnight, Frost) with WCAG-checked tokens and HA themes.
- Packaging for Claude Code (plugin + marketplace), claude.ai ZIP, Codex, ChatGPT pack, Gemini, Antigravity.
- Rooms view from a user-supplied area map (`--areas`) and admin-only tabs through the core view option `visible` (`--admin-user`).
- Optional HACS custom cards documented as dependencies; the baseline uses core cards only.
- Bundled ui-ux-pro-max (MIT) with a read-only `design_search.py` wrapper.
- Full Arabic README, shield badges, CI, CodeQL, Dependabot, container image on ghcr.io, release workflow, version-consistency test.
- Fixed clipped Icon set and Infra screenshots.
