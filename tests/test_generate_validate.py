import json, pathlib, subprocess, sys
import generate_lovelace as gl, validate_dashboard as vd
from _common import load_yaml, ROOT

PROFILES = sorted((ROOT / 'assets/profiles').glob('*.yaml'))

def test_profiles_parse_and_have_kpis():
    assert len(PROFILES) == 7
    for p in PROFILES:
        d = load_yaml(p)
        assert d['id'] == p.stem and d['kpis'] and d['tabs']

def test_every_profile_generates_valid_dashboard(inv):
    for p in PROFILES:
        dash, gaps = gl.build(inv, load_yaml(p), 'dxbmark_aurora', 'T')
        errs, warns = vd.validate(dash, inv, json.dumps(dash))
        assert errs == [], (p.stem, errs)
        assert {v['path'] for v in dash['views']} >= {'overview', 'energy'}

def test_generator_never_invents_entities(inv):
    dash, gaps = gl.build(inv, load_yaml(ROOT / 'assets/profiles/clinic.yaml'), None, 'T')
    known = {e['entity_id'] for e in inv['entities']}
    errs, _ = vd.validate(dash, inv, '')
    assert not [e for e in errs if 'not in inventory' in e]
    assert any('Medical fridge' in g for g in gaps)       # missing KPI is reported, not faked

def test_empty_tabs_are_skipped_and_reported(inv):
    import copy
    i = copy.deepcopy(inv); i['entities'] = [e for e in i['entities'] if e['category'] != 'camera']
    dash, gaps = gl.build(i, load_yaml(ROOT / 'assets/profiles/office.yaml'), None, 'T')
    # security view still exists thanks to locks/alarm, but camera heading section is dropped
    cams = [c for v in dash['views'] if v['path'] == 'security' for s in v['sections'] for c in s['cards'] if c['type'] == 'picture-entity']
    assert cams == []

def test_validator_catches_problems(inv):
    bad = {'views': [{'title': 'A', 'path': 'a', 'type': 'sections', 'sections': [{'type': 'grid', 'cards': [
        {'type': 'tile', 'entity': 'sensor.nope'}, {'type': 'bogus'}, {'type': 'tile', 'entity': 'Bad Id'},
        {'type': 'tile', 'entity': 'light.reception', 'icon': 'flash'}]}]},
        {'title': 'A', 'path': 'a', 'type': 'sections', 'sections': [{'type': 'grid', 'cards': []}]}]}
    errs, _ = vd.validate(bad, inv, 'token: ' + 'eyJhbGciOiJIUzI1NiJ9' + '.eyJpc3MiOiJhYmNkZWZnaGlqa2xtbm9wIn0' + '.abcdefghijklmnopqrstuv')
    joined = '\n'.join(errs)
    for needle in ('not in inventory', 'unknown card type', 'bad entity id', 'must look like mdi', 'duplicate path', 'secret-like'):
        assert needle in joined, needle

def test_demo_dashboard_example_is_current(inv):
    cur = load_yaml(ROOT / 'assets/examples/demo_dashboard.yaml')
    dash, _ = gl.build(inv, load_yaml(ROOT / 'assets/profiles/office.yaml'), 'dxbmark_aurora', 'DXBMARK HQ')
    assert cur == dash

def test_cli_roundtrip(tmp_path):
    S = ROOT / 'scripts'
    out = tmp_path / 'd.yaml'
    subprocess.run([sys.executable, S / 'generate_lovelace.py', ROOT / 'assets/examples/demo_inventory.json', '--out', out], check=True, capture_output=True)
    r = subprocess.run([sys.executable, S / 'validate_dashboard.py', out, '--inventory', ROOT / 'assets/examples/demo_inventory.json'], capture_output=True, text=True)
    assert r.returncode == 0 and 'OK' in r.stdout


def test_rooms_view_and_admin_visibility(tmp_path):
    import subprocess, sys, yaml, pathlib
    sk = pathlib.Path(__file__).resolve().parents[1] / 'skills' / 'ha-studio'
    areas = tmp_path / 'areas.yaml'
    areas.write_text('Lobby:\n  - light.reception\n  - light.does_not_exist\n')
    out = tmp_path / 'd.yaml'
    r = subprocess.run([sys.executable, str(sk / 'scripts/generate_lovelace.py'), str(sk / 'assets/examples/demo_inventory.json'),
                        '--profile', 'office', '--areas', str(areas), '--admin-user', 'u1', '--out', str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    d = yaml.safe_load(out.read_text())
    paths = {v['path']: v for v in d['views']}
    assert 'rooms' in paths and 'light.does_not_exist' in r.stderr   # unknown entity reported, not invented
    assert paths['infra']['visible'] == [{'user': 'u1'}] and 'visible' not in paths['overview']
