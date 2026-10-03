# Cameras and security views

## Pipeline
Camera (RTSP/ONVIF) → Home Assistant camera entity (go2rtc provides low-latency WebRTC) → optional Frigate for local detection
→ dashboard. Core integrations: go2rtc and ONVIF (see `references/sources.md`).

## Dashboard rules
- Tablet / wall panel: snapshots or sub-streams in a grid, tap to open the live view. Do not autoplay many main streams.
- Camera tiles stay fully opaque (no glass blur over video). Label every tile; show the offline state clearly.
- Group security events (doors, motion, tamper) beside the cameras; confirm-to-act for unlock/disarm.
- Restrict camera and security views to the right Home Assistant users (`visible:` on views, non-admin tablet accounts).

## Privacy defaults built into the design
The generated Security view and the design sheets show these defaults so the client sees them up front:
audio off unless needed, no cameras in private areas, visible "camera in use" labelling, restricted viewers, and a clear
retention setting chosen by the client. The client decides retention and signage for their own site.

## Computer-vision add-ons
Detection (person/vehicle/package), line-crossing and counting belong in Frigate or an edge service, producing sensors in Home
Assistant; the dashboard only displays counts and events. Measure false positives on the client's own footage before promising KPIs.
