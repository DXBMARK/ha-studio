#!/usr/bin/env python3
"""Generate a Home Assistant Lovelace dashboard (Sections view) from an inventory + business profile.

  generate_lovelace.py inventory.json --profile office --theme dxbmark_aurora --out dxbmark.yaml [--title "DXBMARK HQ"]

* Uses only entities that exist in the inventory; KPIs with no matching entity are listed as gaps
  (printed, and added as a comment block) instead of being invented.
* Output is a dashboard in YAML mode: paste it in the dashboard's raw configuration editor, or save it
  as a file referenced from `lovelace: dashboards:` in configuration.yaml.
* Nothing is sent to Home Assistant.
"""
import argparse, json, pathlib, re, sys
from _common import ROOT, load_yaml, dump_yaml, die, write_text

ROOM_RE = re.compile(r'^(?:sensor|light|climate|switch)\.(.+?)_(?:lights?|ac|power|energy|heater|plug)')

def pick(ents, category, pattern, used=()):
    rx = re.compile(pattern)
    for e in ents:
        if e['category'] == category and rx.search(e['entity_id']) and e['entity_id'] not in used and not e['unavailable']:
            return e
    return None

def tile(entity, name=None, icon=None, features=None, **kw):
    c = {'type': 'tile', 'entity': entity}
    if name: c['name'] = name
    if icon: c['icon'] = icon
    if features: c['features'] = features
    c.update(kw)
    return c

def heading(text, icon=None):
    c = {'type': 'heading', 'heading': text}
    if icon: c['icon'] = icon
    return c

def section(cards):
    return {'type': 'grid', 'cards': cards}

def view(title, path, icon, sections, theme):
    v = {'title': title, 'path': path, 'icon': icon, 'type': 'sections'}
    if theme: v['theme'] = theme
    v['sections'] = [s for s in sections if len(s['cards']) > 1]
    return v

def rooms_view(inv, areas, theme, gaps):
    """One section per area from a user-supplied {area: [entity_id, ...]} map (no area data is guessed)."""
    have = {e['entity_id']: e for e in inv['entities']}
    sections = []
    for area, ids in areas.items():
        cards = [heading(area, 'mdi:floor-plan')]
        for eid in ids:
            e = have.get(eid)
            if not e:
                gaps.append(f'Room "{area}": entity {eid} not in inventory'); continue
            if e['unavailable']:
                gaps.append(f'Room "{area}": entity {eid} is unavailable'); continue
            if e['domain'] == 'light':
                cards.append(tile(eid, features=[{'type': 'light-brightness'}]))
            elif e['domain'] == 'climate':
                cards.append(tile(eid, features=[{'type': 'target-temperature'}]))
            else:
                cards.append(tile(eid))
        sections.append(section(cards))
    return view('Rooms', 'rooms', 'mdi:floor-plan', sections, theme)


def build(inv, prof, theme, title, areas=None, admins=()):
    ents = inv['entities']
    by = lambda c: [e for e in ents if e['category'] == c and not e['unavailable']]
    gaps = []

    # ---- Overview -------------------------------------------------------------------------
    kpi_cards = [heading('Key indicators', 'mdi:chart-box')]
    for k in prof.get('kpis', []):
        e = pick(ents, k['category'], k['entity_match'])
        if not e:
            gaps.append(f'KPI "{k["label"]}": no {k["category"]} entity matching /{k["entity_match"]}/')
            continue
        if k.get('ui') == 'gauge':
            kpi_cards.append({'type': 'gauge', 'entity': e['entity_id'], 'name': k['label'], 'min': 0, 'max': k.get('max', 10000),
                              'needle': True, 'severity': {'green': 0, 'yellow': int(k.get('max', 10000) * .6), 'red': int(k.get('max', 10000) * .85)}})
        else:
            kpi_cards.append(tile(e['entity_id'], k['label'], k.get('icon')))
    rooms = [heading('Rooms & devices', 'mdi:floor-plan')]
    for e in by('light')[:6]:
        rooms.append(tile(e['entity_id'], features=[{'type': 'light-brightness'}]))
    for e in by('climate')[:4]:
        rooms.append(tile(e['entity_id'], features=[{'type': 'target-temperature'}]))
    for e in by('lock')[:2] + by('cover')[:2]:
        rooms.append(tile(e['entity_id']))
    overview = view('Overview', 'overview', 'mdi:view-dashboard', [section(kpi_cards), section(rooms)], theme)

    # ---- Energy ---------------------------------------------------------------------------
    pw = by('power')
    top = sorted(pw, key=lambda e: -(float(e['state']) if re.fullmatch(r'-?\d+(\.\d+)?', str(e['state'])) else 0))[:8]
    energy_cards = [heading('Energy', 'mdi:lightning-bolt'),
                    {'type': 'energy-distribution', 'link_dashboard': True},
                    {'type': 'energy-usage-graph'},
                    {'type': 'energy-devices-graph'},
                    {'type': 'energy-sources-table'}]
    power_cards = [heading('Live power per device', 'mdi:flash')] + [tile(e['entity_id']) for e in top]
    if top:
        power_cards.append({'type': 'statistics-graph', 'title': 'Power (24 h, mean)', 'days_to_show': 1, 'stat_types': ['mean', 'max'],
                            'chart_type': 'line', 'entities': [e['entity_id'] for e in top[:5]]})
    energy = view('Energy', 'energy', 'mdi:flash', [section(energy_cards), section(power_cards)], theme)

    # ---- Security / cameras ---------------------------------------------------------------
    cams = by('camera')
    cam_cards = [heading('Cameras', 'mdi:cctv')]
    for c in cams[:8]:
        cam_cards.append({'type': 'picture-entity', 'entity': c['entity_id'], 'camera_view': 'auto', 'show_state': False, 'show_name': True})
    sec_cards = [heading('Access & alarms', 'mdi:shield-lock')]
    for e in by('alarm')[:1] + by('lock')[:3] + by('security')[:8]:
        sec_cards.append(tile(e['entity_id']))
    security = view('Security', 'security', 'mdi:shield-home', [section(cam_cards), section(sec_cards)], theme)

    # ---- Infra ----------------------------------------------------------------------------
    infra = by('infra')
    inf_cards = [heading('Infrastructure & websites', 'mdi:server-network')]
    for e in infra[:12]:
        inf_cards.append(tile(e['entity_id']))
    infra_v = view('Infra', 'infra', 'mdi:server', [section(inf_cards)], theme)

    # ---- Backups --------------------------------------------------------------------------
    bk = by('backup')
    bk_cards = [heading('Backups', 'mdi:backup-restore')] + [tile(e['entity_id']) for e in bk[:8]]
    backups = view('Backups', 'backups', 'mdi:cloud-upload', [section(bk_cards)], theme)

    # ---- Voice ----------------------------------------------------------------------------
    vo = by('voice') + by('media')
    vo_cards = [heading('Voice & Assist', 'mdi:microphone')] + [tile(e['entity_id']) for e in vo[:8]]
    voice = view('Voice', 'voice', 'mdi:microphone', [section(vo_cards)], theme)

    views = {'overview': overview, 'energy': energy, 'security': security, 'infra': infra_v, 'backups': backups, 'voice': voice}
    if areas:
        views['rooms'] = rooms_view(inv, areas, theme, gaps)
    chosen = [views[t] for t in prof.get('tabs', views) if t in views and views[t]['sections']]
    if areas and 'rooms' not in prof.get('tabs', []):
        chosen.insert(1, views['rooms'])
    if admins:   # staff see the operational tabs; admin-only tabs are hidden from other users (view `visible`)
        for v in chosen:
            if v['path'] in ('infra', 'backups', 'security', 'energy'):
                v['visible'] = [{'user': u} for u in admins]
    for t in prof.get('tabs', []):
        if t in views and not views[t]['sections']:
            gaps.append(f'Tab "{t}" skipped: no matching entities in the inventory')
    return {'title': title, 'views': chosen}, gaps

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inventory'); ap.add_argument('--profile', default='office')
    ap.add_argument('--theme', default='aurora', help='HA theme name to set on each view (see gen_theme.py); "" for none')
    ap.add_argument('--title', default='Dashboard'); ap.add_argument('--out', default='-')
    ap.add_argument('--areas', help='JSON/YAML file {"Area name": ["light.x", "climate.y"]}; adds a Rooms view (areas are never guessed)')
    ap.add_argument('--admin-user', action='append', default=[], metavar='USER_ID',
                    help='HA user id allowed to see Energy/Security/Infra/Backups tabs (repeatable); others do not see them')
    ap.add_argument('--force', action='store_true', help='overwrite --out if it exists')
    a = ap.parse_args()
    inv = json.load(open(a.inventory, encoding='utf-8'))
    pf = pathlib.Path(a.profile)
    if not pf.exists():
        pf = ROOT / 'assets' / 'profiles' / f'{a.profile}.yaml'
    if not pf.exists():
        die(f'profile not found: {a.profile}')
    prof = load_yaml(pf)
    areas = load_yaml(pathlib.Path(a.areas)) if a.areas else None
    dash, gaps = build(inv, prof, a.theme or None, a.title, areas, a.admin_user)
    header = '# Generated by ha-studio (DXBMARK LLC, Apache-2.0). Review before applying.\n'
    if gaps:
        header += '# Gaps (not invented):\n' + ''.join(f'#   - {g}\n' for g in gaps)
    text = dump_yaml(dash, header)
    if a.out == '-':
        print(text)
    else:
        write_text(a.out, text, a.force)
        print(f'{len(dash["views"])} views → {a.out}; gaps: {len(gaps)}', file=sys.stderr)
        for g in gaps:
            print('  gap:', g, file=sys.stderr)

if __name__ == '__main__':
    main()
