# Security policy

## Reporting
Email **info@dxbmark.com** (or the contact listed on dxbmark.com) with details and steps to reproduce.
Please do not open public issues for vulnerabilities. We aim to acknowledge within 5 business days.

## Scope and design
- The tools are **read-only** towards Home Assistant (`GET /api/states`, `GET /api/config`) and never call services.
- Tokens are read from environment variables only; never accepted as CLI arguments, never written to output.
  `validate_dashboard.py` and `lint_skill.py` reject secret-like strings.
- Generated dashboards can expose entity names and states. Restrict camera/security views to specific users and keep
  tablet accounts non-admin.
- Use least-privilege, revocable tokens (e.g. a dedicated HA user, read-only Proxmox API token).
- Do not paste real tokens into chats with any AI assistant.

## Supported versions
The latest release receives fixes.
