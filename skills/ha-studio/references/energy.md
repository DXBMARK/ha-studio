# Energy: every device visible, every kWh accounted for

## What the Energy dashboard needs
- A grid consumption sensor (`device_class: energy`, `state_class: total_increasing`, kWh/Wh/MWh) and optionally
  production, battery, gas, water.
- **Individual devices**: one cumulative energy sensor per device. Power-only plugs need an energy counterpart.
- Upstream device: when a device sits behind another tracked device (a sub-meter inside a circuit), set the upstream device so it
  is not counted twice.

## Power-only device → energy
Create an **Integral** helper (Riemann sum) with the power sensor as source, method `left` (or `trapezoidal`, the default), metric prefix `k`,
time unit `h`. The result is a kWh counter with the right classes. `energy_audit.py`
prints these as review items — creating helpers is a deliberate user action.

## Cycles and tariffs
`utility_meter` helpers give daily/monthly cycles and peak/off-peak tariffs. Use the Energy dashboard's own price
setting for official cost; template "what-if" cost sensors are for cards only and must say so.

## Reading the audit
- *Paired*: power + energy exist. Good.
- *Missing energy*: add the Riemann helper.
- *Bad state_class*: a cumulative counter exposed as `measurement` breaks statistics. Fix at the source integration or
  via a template sensor; changing classes on an existing entity can leave inconsistent statistics — back up first.
- *Untracked load*: grid W minus sum of device W. A big positive gap = missing devices; negative = overlapping sensors.

## Dashboard pieces
Overview shows power now (gauge), energy today, cost today; the Energy view shows distribution, usage and devices graphs plus
live power tiles for the top consumers and a statistics graph of the top five. Per-room cross-tab models in the HTML preview
are sample data only.
