#!/usr/bin/env python3
"""Read-only Home Assistant inventory.

Reads entity states (GET /api/states) and writes a normalised inventory JSON that the other
scripts consume.  It never calls a service and never writes to Home Assistant.

  HA_URL=http://homeassistant.local:8123 HA_TOKEN=<long-lived token> ha_inventory.py --out inventory.json
  ha_inventory.py --states-file states.json --out inventory.json        # offline / exported states

The token is read from the environment only (never a CLI flag, so it stays out of shell history).
"""
import argparse, collections, json, os, re, sys, urllib.request, urllib.error
from _common import die, write_text

CATEGORY_RULES = [
    # (category, predicate(domain, object_id, attrs))
    ('camera',   lambda d, o, a: d == 'camera'),
    ('voice',    lambda d, o, a: d in ('assist_satellite', 'conversation', 'tts', 'stt', 'wake_word')),
    ('power',    lambda d, o, a: d == 'sensor' and a.get('device_class') == 'power'),
    ('energy',   lambda d, o, a: d == 'sensor' and a.get('device_class') == 'energy'),
    ('cost',     lambda d, o, a: d == 'sensor' and a.get('device_class') == 'monetary'),
    ('climate',  lambda d, o, a: d == 'climate'),
    ('light',    lambda d, o, a: d == 'light'),
    ('switch',   lambda d, o, a: d in ('switch', 'input_boolean')),
    ('cover',    lambda d, o, a: d == 'cover'),
    ('lock',     lambda d, o, a: d == 'lock'),
    ('alarm',    lambda d, o, a: d == 'alarm_control_panel'),
    ('media',    lambda d, o, a: d == 'media_player'),
    ('security', lambda d, o, a: d == 'binary_sensor' and a.get('device_class') in ('motion', 'door', 'window', 'smoke', 'moisture', 'occupancy', 'opening', 'tamper', 'garage_door')),
    ('backup',   lambda d, o, a: re.search(r'backup', o) is not None and d in ('sensor', 'binary_sensor', 'event')),
    ('infra',    lambda d, o, a: re.search(r'proxmox|pve|uptime|kuma|dokploy|docker|cert_expiry|whois|domain|cpu|memory|disk|node_', o) is not None and d in ('sensor', 'binary_sensor', 'switch', 'update')),
    ('weather',  lambda d, o, a: d == 'weather'),
    ('sensor',   lambda d, o, a: d == 'sensor'),
    ('binary',   lambda d, o, a: d == 'binary_sensor'),
]

def classify(entity_id, attrs):
    d, o = entity_id.split('.', 1)
    for cat, pred in CATEGORY_RULES:
        try:
            if pred(d, o, attrs):
                return cat
        except Exception:
            continue
    return 'other'

def normalise(states):
    ents = []
    for s in states:
        eid = s.get('entity_id')
        if not eid or '.' not in eid:
            continue
        a = s.get('attributes') or {}
        ents.append({
            'entity_id': eid,
            'domain': eid.split('.', 1)[0],
            'name': a.get('friendly_name') or eid,
            'state': s.get('state'),
            'unit': a.get('unit_of_measurement'),
            'device_class': a.get('device_class'),
            'state_class': a.get('state_class'),
            'category': classify(eid, a),
            'unavailable': s.get('state') == 'unavailable',      # 'unknown' is legitimate for many entities (e.g. conversation)
        })
    return ents

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow redirects: the bearer token must only ever go to the host the user configured."""
    def redirect_request(self, *a, **k):
        return None

_OPENER = urllib.request.build_opener(_NoRedirect)

def fetch(url, token, path):
    if not re.match(r'^https?://', url or ''):
        die('HA_URL must start with http:// or https://')
    req = urllib.request.Request(url.rstrip('/') + path, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    try:
        with _OPENER.open(req, timeout=20) as r:     # GET only: read-only by construction
            return json.load(r)
    except urllib.error.HTTPError as e:
        die(f'HTTP {e.code} from {path} — check HA_TOKEN / HA_URL' + (' (redirects are refused; use the final URL)' if 300 <= e.code < 400 else ''))
    except Exception as e:
        die(f'cannot reach Home Assistant: {e}')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--states-file', help='JSON file with the output of GET /api/states (offline mode)')
    ap.add_argument('--out', default='-', help='output inventory JSON (default stdout)')
    ap.add_argument('--force', action='store_true', help='overwrite --out if it exists')
    a = ap.parse_args()
    cfg = {}
    if a.states_file:
        states = json.load(open(a.states_file, encoding='utf-8'))
    else:
        url, tok = os.environ.get('HA_URL'), os.environ.get('HA_TOKEN')
        if not url or not tok:
            die('set HA_URL and HA_TOKEN in the environment, or use --states-file')
        states = fetch(url, tok, '/api/states')
        cfg = fetch(url, tok, '/api/config') or {}
    ents = normalise(states)
    by_cat = collections.Counter(e['category'] for e in ents)
    inv = {
        'schema': 1,
        'ha_version': cfg.get('version'),
        'location': cfg.get('location_name'),
        'currency': cfg.get('currency'),
        'unit_system': (cfg.get('unit_system') or {}),
        'counts': dict(sorted(by_cat.items())),
        'unavailable': [e['entity_id'] for e in ents if e['unavailable']],
        'entities': sorted(ents, key=lambda e: (e['category'], e['entity_id'])),
    }
    out = json.dumps(inv, indent=2, ensure_ascii=False)
    if a.out == '-':
        print(out)
    else:
        write_text(a.out, out + '\n', a.force)
        print(f'{len(ents)} entities → {a.out}  {inv["counts"]}', file=sys.stderr)

if __name__ == '__main__':
    main()
