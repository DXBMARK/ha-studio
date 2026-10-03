# Versioning and releases

HA Studio follows [Semantic Versioning 2.0.0](https://semver.org): `MAJOR.MINOR.PATCH`.

- **MAJOR**: breaking change to the skill's workflow, script CLI flags or output format.
- **MINOR**: new backwards-compatible feature (new script, option, profile, reference).
- **PATCH**: fixes, wording, screenshots, dependency updates.

Single source of truth: `CHANGELOG.md` (newest `## X.Y.Z` heading). `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
`gemini-extension.json` and the `metadata.version` in `skills/ha-studio/SKILL.md` must carry the same number;
`tests/test_versions.py` fails CI otherwise.

## Releasing

1. Update the version in the four files above and add a `## X.Y.Z — date` section to `CHANGELOG.md`.
2. `python3 -m pytest -q` and `python3 skills/ha-studio/scripts/lint_skill.py` pass.
3. Commit, then tag: `git tag -a vX.Y.Z -m "HA Studio X.Y.Z" && git push origin main vX.Y.Z`.
4. The `release` workflow builds the ZIPs, ChatGPT pack, Gem text and `SHA256SUMS`, creates the GitHub Release with notes
   taken from the changelog, and publishes the container image `ghcr.io/dxbmark/ha-studio:X.Y.Z` (also `X.Y` and `latest`).

Released tags are never moved or deleted; fixes ship as a new PATCH.
