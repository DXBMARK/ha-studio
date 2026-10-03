# KPI catalogue by business type

All KPIs are DXBMARK proposals: confirm definitions and thresholds with the client; regulated limits (vaccine fridges, cold chain,
CO₂ levels) must come from the client's regulator, not from this file.

Show **value, unit, trend/delta, freshness**. Put 4–8 KPIs on Overview; everything else one tap away.

| Business | Hero KPIs | Supporting | Alerts worth wiring |
|---|---|---|---|
| Office / co-working | Power now, energy today, cost today | Room AC load, server-room temp, entrance activity | Server-room temp high, door left open, backup stale |
| Retail / showroom | Power now, door state, camera status | Lighting vs AC load, POS/site uptime | Door open after hours, offline camera |
| Cafe / restaurant | Kitchen load, cold-room temp | Ambience scenes, ventilation | Fridge/freezer above limit for N minutes |
| Clinic | Medical-fridge temp, alarm state | Room occupancy (not images), AC | Fridge excursion, door open; camera privacy strict |
| Hotel / serviced apartments | Occupied rooms, energy per room | Lobby cameras, guest AC set-points | Room AC on while vacant |
| Warehouse | Dock door states, charger load | Perimeter cameras, temperature | Dock door open too long, charger fault |
| DevOps / server estate | Sites up, apps running, last backup | CPU/RAM/storage, cert days, domain expiry | Site down, cert < 7 d, backup > 26 h |

## Patterns
- Staleness: every pushed KPI carries a last-updated timestamp tile or a binary "stale" sensor.
- Cost: label whether it is metered or estimated (tariff × kWh).
- Thresholds: use labelled zones and icons, not colour alone.
- New KPI = new profile line (`assets/profiles/<id>.yaml`: label, category, entity_match, icon, ui).
