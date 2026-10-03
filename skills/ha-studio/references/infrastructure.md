# Infrastructure and backups in HA

Prefer official integrations and HA-native building blocks; run each against a non-production instance first.

| Need | Mechanism | Notes |
|---|---|---|
| Proxmox VE node/VM/storage | Core Proxmox VE integration, API token | Use a dedicated least-privilege token; never a root password |
| Backup job results | Webhook or REST sensor fed by your backup tool | Land the result in a helper so it survives restarts |
| Websites / services up | Uptime Kuma integration | Status, response time, certificate expiry, uptime per monitor |
| Certificates | `cert_expiry` integration | Gives a timestamp sensor (e.g. `sensor.cert_expiry_timestamp_example_com`); template a "days left" sensor (see example package) |
| Domains | `whois` integration | Expiry timestamp; alert at 60/30/7 days (our proposal) |
| Dokploy projects | REST sensor to the instance API | `x-api-key` header, `GET /api/project.all`; other endpoints: read your instance's Swagger UI |
| HA backups | Core backup integration | Manager state, next scheduled, last attempted, last successful backup sensors |
| Offsite copy | Google Drive backup integration | Stores backups in its own folder and adds storage sensors; freshness of non-HA archives needs an external check |
| Vendor APIs (billing, messaging, CRM) | Webhook-triggered automation or REST sensor | Keep keys in `!secret`; one limited token per integration |

## Durable KPIs
For KPIs pushed from outside Home Assistant, land them in helpers (`input_number`, `input_text`) or pull them with REST sensors, so a value
exists after a restart.

## Thresholds (DXBMARK proposals, tune per client)
SSL days left: warn < 21, critical < 7. Backup age: warn > 26 h, critical > 50 h (daily job). Disk usage: warn 80 %, critical 90 %.
These are starting values, not standards.

## Bridge options
1. **HA-native (default)**: REST/template sensors, webhooks (`local_only: true` where possible), automations.
2. **n8n (optional)**: its Sustainable Use License limits use to internal business or non-commercial purposes. This repo ships no n8n
   code; a client who wants n8n installs it under n8n's own licence.

## Security defaults
Least-privilege tokens, `!secret` for credentials, no tokens in dashboards or kiosk URLs, HTTPS, separate Home Assistant users for tablets.
