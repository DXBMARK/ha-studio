# Entity model → dashboard mapping

Home Assistant exposes everything as an entity: `domain.object_id`, a `state` string and `attributes`.
Map by **domain first, then `device_class`**, never by guessing from the friendly name.

| Category (inventory) | Rule | Default card |
|---|---|---|
| power | `sensor` + `device_class: power` (W/kW) | tile (live value), `statistics-graph` for top consumers |
| energy | `sensor` + `device_class: energy` (kWh/Wh/MWh) | Energy dashboard cards; tile for "today" |
| cost | `sensor` + `device_class: monetary` | tile |
| light | `light` | tile + `light-brightness` feature |
| climate | `climate` | tile + `target-temperature` feature |
| cover / lock / alarm | `cover`, `lock`, `alarm_control_panel` | tile (confirm before unlock/disarm on wall panels) |
| security | `binary_sensor` with motion, door, window, smoke, moisture, occupancy, opening, tamper | tile, grouped under Security |
| camera | `camera` | `picture-entity` (snapshot/sub-stream), live view on tap |
| voice | `assist_satellite`, `conversation`, `tts`, `stt`, `wake_word`, `media_player` | tiles under Voice |
| backup / infra | id contains backup, proxmox/pve, uptime/kuma, dokploy, docker, cert_expiry, whois | tiles under Backups / Infra |
| weather | `weather` | weather-forecast card (optional) |

## Rules
- **Statistics need `state_class`.** `measurement` for instantaneous values, `total_increasing` for cumulative
  counters that reset to zero, `total` for cumulative values that can go down. Long-term charts and the Energy
  dashboard depend on this.
- **Units matter.** A sensor reporting `W` and one reporting `kW` must be normalised before summing.
- **States `unavailable` / `unknown` are data.** Show them (muted, with an icon) rather than hiding the tile;
  exclude them from sums.
- **Stable ids.** Dashboards break when entity ids change. Prefer renaming through the entity registry once, then
  regenerate, over patching YAML by hand.
- **Areas and devices.** Group tiles by area when the inventory carries areas; otherwise group by category.
- **New device types.** Unknown domain → show a plain tile, list it as "unclassified" in the summary, and propose a
  category rule for `ha_inventory.py` (`CATEGORY_RULES`).
