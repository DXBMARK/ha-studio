# Icons

- **HA dashboards** use Material Design Icons by name (`mdi:flash`). Referencing names has no licence cost.
- **HTML previews** inline Font Awesome Free SVGs (`assets/icons/fa-subset.json`, CC BY 4.0, attribution in
  THIRD_PARTY_NOTICES.md). Never include Font Awesome Pro assets. Brand icons are the owners' trademarks.
- Keep one concept per icon: flash = power, lightning-bolt = energy, shield-home = alarm, cctv = camera, server = Proxmox,
  docker = containers, backup-restore = backup, web-check = uptime.

| Concept | mdi | FA Free (preview) |
|---|---|---|
| Power | `mdi:flash` | bolt |
| Energy | `mdi:lightning-bolt` | bolt |
| Cost | `mdi:cash` | coins / money-bill |
| Temperature | `mdi:thermometer` | temperature-half |
| Alarm | `mdi:shield-home` | shield-halved |
| Camera | `mdi:cctv` | video (no CCTV glyph in Free) |
| Door / lock | `mdi:door`, `mdi:lock` | door-closed, lock |
| Server | `mdi:server` | server |
| Containers | `mdi:docker` | cubes |
| Backup | `mdi:backup-restore` | clock-rotate-left |
| Uptime | `mdi:web-check` | globe |
| Voice | `mdi:microphone` | microphone |

Gaps in FA Free (window, router, siren, UPS): use MDI in HA; in previews compose from available glyphs or a custom SVG.
HA may bundle an older MDI than the newest npm release; a brand-new icon name can render blank — fall back to a stable one.
