#!/usr/bin/env python3
"""Energy audit: can every device be shown in the Energy dashboard, and what is missing?

Reads an inventory JSON (ha_inventory.py).  Checks
  * every power sensor (W) has an energy counterpart (kWh, state_class total/total_increasing)
  * energy sensors have a valid state_class (required for long-term statistics / Energy dashboard)
  * unavailable power/energy sensors
  * sum of tracked device power vs. the grid sensor → "untracked" load
and prints a Markdown report plus ready-to-review helper suggestions.  Read-only: it changes nothing.

  energy_audit.py inventory.json [--tariff 0.15 --currency USD] [--grid sensor.grid_power] [--json out.json]
"""
import argparse, json, re, sys

def stem(eid):
    o = eid.split('.', 1)[1]
    prev = None
    while prev != o:                      # strip repeated suffixes: grid_energy_import -> grid
        prev, o = o, re.sub(r'_(power|energy|consumption|usage|total|import|today)$', '', o)
    return o

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def audit(inv, grid=None, tariff=None):
    ents = inv['entities']
    power = [e for e in ents if e['category'] == 'power']
    energy = [e for e in ents if e['category'] == 'energy']
    en_by_stem = {}
    for e in energy:
        en_by_stem.setdefault(stem(e['entity_id']), []).append(e)
    res = {'paired': [], 'missing_energy': [], 'bad_state_class': [], 'unavailable': [], 'untracked': None, 'cost': None}
    for p in power:
        if p['unavailable']:
            res['unavailable'].append(p['entity_id'])
        match = en_by_stem.get(stem(p['entity_id']))
        if match:
            res['paired'].append({'power': p['entity_id'], 'energy': match[0]['entity_id']})
        else:
            res['missing_energy'].append(p['entity_id'])
    for e in energy:
        if e['unavailable']:
            res['unavailable'].append(e['entity_id'])
        if e.get('state_class') not in ('total', 'total_increasing'):
            res['bad_state_class'].append({'entity_id': e['entity_id'], 'state_class': e.get('state_class')})
    grid_id = grid or next((p['entity_id'] for p in power if re.search(r'grid|mains|main_power|total_power', p['entity_id'])), None)
    if grid_id:
        gw = num(next((p['state'] for p in power if p['entity_id'] == grid_id), None))
        dev = sum(num(p['state']) or 0 for p in power if p['entity_id'] != grid_id and not p['unavailable'])
        if gw is not None:
            res['untracked'] = {'grid_entity': grid_id, 'grid_w': gw, 'tracked_w': round(dev, 1),
                                'untracked_w': round(gw - dev, 1), 'untracked_pct': round(100 * (gw - dev) / gw, 1) if gw else None}
    if tariff is not None:
        kwh = sum(num(e['state']) or 0 for e in energy if e.get('state_class') in ('total', 'total_increasing') and not re.search(r'grid', e['entity_id']))
        res['cost'] = {'tariff': tariff, 'tracked_kwh_lifetime': round(kwh, 2)}
    return res

def riemann_hint(entity_id):
    base = stem(entity_id)
    return (f'Helpers → Add helper → "Integral sensor (Riemann sum)": source={entity_id}, '
            f'method=left, metric prefix=k (kilo), time unit=hours → creates sensor.{base}_energy (kWh, total_increasing).')

def report(res, currency='USD', tariff=None):
    L = ['# Energy audit', '']
    L += [f'- Devices with power **and** energy sensors: **{len(res["paired"])}**',
          f'- Power sensors without an energy counterpart: **{len(res["missing_energy"])}**',
          f'- Energy sensors with wrong state_class: **{len(res["bad_state_class"])}**',
          f'- Unavailable: **{len(res["unavailable"])}**', '']
    if res['untracked']:
        u = res['untracked']
        head = (f'Grid `{u["grid_entity"]}` = {u["grid_w"]} W; tracked devices = {u["tracked_w"]} W; '
                f'untracked ≈ **{u["untracked_w"]} W** ({u["untracked_pct"]} %). ')
        if u['untracked_w'] >= 0:
            tail = 'A large untracked share means loads are missing from the Energy dashboard.'
        else:
            tail = ('Tracked devices exceed the grid reading: some sensors overlap '
                    '(a sub-meter and its parent both counted) or the grid sensor is wrong.')
        L += ['## Untracked load', head + tail, '']
    if res['missing_energy']:
        L += ['## Add an energy counterpart (review before creating)', '']
        L += [f'- `{e}` — {riemann_hint(e)}' for e in res['missing_energy']]
        L += ['']
    if res['bad_state_class']:
        L += ['## Fix state_class (needs total_increasing for a cumulative kWh counter)', '']
        L += [f'- `{b["entity_id"]}` has `{b["state_class"]}`. If it is a cumulative counter, set state_class via the integration or a template sensor; '
              'changing it on an existing entity can leave older statistics inconsistent — back up first.' for b in res['bad_state_class']]
        L += ['']
    if res['unavailable']:
        L += ['## Unavailable', ''] + [f'- `{e}`' for e in sorted(set(res['unavailable']))] + ['']
    if res['cost']:
        c = res['cost']
        L += ['## Cost basis', f'Tariff {c["tariff"]} {currency}/kWh. Prefer the Energy dashboard\'s own tariff setting for official numbers; '
              'use this only for what-if cards.', '']
    return '\n'.join(L)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inventory'); ap.add_argument('--grid'); ap.add_argument('--tariff', type=float)
    ap.add_argument('--currency', default='USD'); ap.add_argument('--json'); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    inv = json.load(open(a.inventory, encoding='utf-8'))
    res = audit(inv, a.grid, a.tariff)
    print(report(res, a.currency, a.tariff))
    if a.json:
        from _common import write_text
        write_text(a.json, json.dumps(res, indent=2) + '\n', a.force)

if __name__ == '__main__':
    main()
