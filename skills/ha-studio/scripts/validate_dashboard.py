#!/usr/bin/env python3
"""Validate a generated/handwritten Lovelace dashboard YAML before it goes anywhere near Home Assistant.

  validate_dashboard.py dashboard.yaml [--inventory inventory.json]

Checks: parses; every view has a unique path; sections views contain grid sections; card types are known;
entity ids look valid (and exist in the inventory when given); icons use mdi:/phu:/hass: prefixes;
no secrets/tokens; camera cards point at camera.* entities.  Exit 1 on any error (warnings don't fail).
"""
import argparse, json, re, sys
from _common import load_yaml, find_secrets

KNOWN_CARDS = {
    'tile', 'heading', 'gauge', 'statistics-graph', 'history-graph', 'entities', 'entity', 'glance', 'button', 'markdown',
    'picture-entity', 'picture-glance', 'picture', 'horizontal-stack', 'vertical-stack', 'grid', 'conditional', 'sensor',
    'light', 'thermostat', 'media-control', 'alarm-panel', 'weather-forecast', 'map', 'logbook', 'iframe', 'area',
    'energy-distribution', 'energy-usage-graph', 'energy-devices-graph', 'energy-sources-table', 'energy-solar-graph',
    'energy-gas-graph', 'energy-water-graph', 'energy-date-selection', 'energy-carbon-graph', 'energy-grid-neutrality-gauge',
    'energy-self-sufficiency-gauge', 'energy-solar-consumed-gauge', 'energy-carbon-consumed-gauge', 'power-sources-graph',
    'energy-sankey', 'todo-list', 'clock', 'webpage', 'calendar', 'shopping-list', 'plant-status',
}
ENT_RE = re.compile(r'^[a-z_]+\.[a-z0-9_]+$')
ICON_RE = re.compile(r'^(mdi|phu|hass|mdi-icon):[a-z0-9-]+$')

def walk(card, path, errs, warns, ents, inv):
    if not isinstance(card, dict) or 'type' not in card:
        errs.append(f'{path}: card without type'); return
    t = card['type']
    if t.startswith('custom:'):
        warns.append(f'{path}: custom card {t} (HACS dependency)')
    elif t not in KNOWN_CARDS:
        errs.append(f'{path}: unknown card type "{t}"')
    for key in ('entity',):
        if key in card and isinstance(card[key], str):
            ents.append((path, card[key], t))
    for e in card.get('entities', []) or []:
        ents.append((path, e if isinstance(e, str) else (e or {}).get('entity'), t))
    if 'icon' in card and not ICON_RE.match(str(card['icon'])):
        errs.append(f'{path}: icon "{card["icon"]}" must look like mdi:name')
    for i, sub in enumerate(card.get('cards', []) or []):
        walk(sub, f'{path}.cards[{i}]', errs, warns, ents, inv)

def validate(doc, inv=None, raw=''):
    errs, warns, ents = [], [], []
    if not isinstance(doc, dict) or not doc.get('views'):
        return ['top level must be a mapping with "views"'], warns
    paths = set()
    for vi, v in enumerate(doc['views']):
        p = f'views[{vi}]'
        pth = v.get('path') or v.get('title')
        if not pth: errs.append(f'{p}: needs path or title')
        elif pth in paths: errs.append(f'{p}: duplicate path "{pth}"')
        paths.add(pth)
        if v.get('type') == 'sections':
            if not v.get('sections'): errs.append(f'{p}: sections view without sections')
            for si, s in enumerate(v.get('sections', [])):
                if s.get('type', 'grid') != 'grid': warns.append(f'{p}.sections[{si}]: non-grid section type')
                for ci, c in enumerate(s.get('cards', [])):
                    walk(c, f'{p}.sections[{si}].cards[{ci}]', errs, warns, ents, inv)
        else:
            for ci, c in enumerate(v.get('cards', []) or []):
                walk(c, f'{p}.cards[{ci}]', errs, warns, ents, inv)
    known = {e['entity_id'] for e in inv['entities']} if inv else None
    for path, eid, ctype in ents:
        if not eid: continue
        if not ENT_RE.match(eid): errs.append(f'{path}: bad entity id "{eid}"'); continue
        if known is not None and eid not in known: errs.append(f'{path}: entity {eid} not in inventory')
        if ctype in ('picture-entity', 'picture-glance') and not eid.startswith('camera.') and 'camera_image' not in str(eid):
            warns.append(f'{path}: {ctype} on non-camera entity {eid}')
    for s in find_secrets(raw):
        errs.append(f'secret-like string in file: {s}')
    return errs, warns

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dashboard'); ap.add_argument('--inventory')
    a = ap.parse_args()
    raw = open(a.dashboard, encoding='utf-8').read()
    try:
        doc = load_yaml(a.dashboard)
    except Exception as e:
        print(f'FAIL: YAML parse error: {e}'); return 1
    inv = json.load(open(a.inventory, encoding='utf-8')) if a.inventory else None
    errs, warns = validate(doc, inv, raw)
    for w in warns: print('warn :', w)
    for e in errs: print('ERROR:', e)
    print(f'{"FAIL" if errs else "OK"}: {len(errs)} error(s), {len(warns)} warning(s)')
    return 1 if errs else 0

if __name__ == '__main__':
    sys.exit(main())
