import json, pathlib, subprocess, sys, urllib.request, urllib.error
import pytest
from conftest import REPO, SK
import ha_inventory, _common, gen_theme

def run(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)

def test_scripts_refuse_to_overwrite(tmp_path):
    inv = SK / 'assets/examples/demo_inventory.json'
    out = tmp_path / 'd.yaml'; out.write_text('keep me')
    r = run(SK / 'scripts/generate_lovelace.py', inv, '--out', out)
    assert r.returncode != 0 and 'already exists' in r.stderr and out.read_text() == 'keep me'
    assert run(SK / 'scripts/generate_lovelace.py', inv, '--out', out, '--force').returncode == 0
    t = tmp_path / 't.yaml'; t.write_text('keep')
    assert run(SK / 'scripts/gen_theme.py', 'aurora', '--out', t).returncode != 0 and t.read_text() == 'keep'

def test_inventory_never_follows_redirects(monkeypatch):
    h = ha_inventory._NoRedirect()
    assert h.redirect_request(None, None, 302, 'Found', {}, 'http://evil.example') is None

def test_inventory_rejects_non_http_schemes():
    with pytest.raises(SystemExit):
        ha_inventory.fetch('file:///etc/passwd', 'x', '/api/states')

def test_secret_scan_redacts_values():
    hits = _common.find_secrets('password = "supersecretvalue12345"')
    assert hits == ['[redacted]']

def test_theme_dialogs_are_opaque():
    for f in (SK / 'assets/tokens').glob('*.json'):
        tok = json.loads(f.read_text())
        v = list(gen_theme.build(tok).values())[0]['modes']
        vars_ = list(v.values())[0]
        assert vars_['card-background-color'].startswith('#') and 'rgba' in vars_['ha-card-background']

def test_samples_contain_no_owner_private_data():
    bad = ('waqtor', 'Tariq', 'dxbmark.com', 'pay.dxbmark')
    for f in list((SK / 'assets').rglob('*')) + list((SK / 'scripts').glob('*.py')):
        if f.is_file() and f.suffix in ('.json', '.yaml', '.html', '.py', '.js'):
            t = f.read_text(errors='ignore')
            assert not any(b in t for b in bad), (f, [b for b in bad if b in t])

def test_no_brand_glyphs_shipped():
    icons = json.loads((SK / 'assets/icons/fa-subset.json').read_text())['icons']
    assert not {'wa', 'stripe', 'gdrive', 'docker', 'wp'} & set(icons)

def test_generated_preview_carries_icon_attribution(tmp_path):
    assert run(SK / 'scripts/build_design.py', '--out', tmp_path, '--themes', 'aurora').returncode == 0
    h = (tmp_path / 'aurora.html').read_text()
    assert 'Font Awesome Free' in h and 'CC BY 4.0' in h and 'Tariq' not in h

def test_cli_help_works_everywhere():
    for s in sorted((SK / 'scripts').glob('*.py')):
        if s.name.startswith('_'): continue
        r = run(s, '--help')
        assert r.returncode == 0 and 'usage' in r.stdout.lower(), s.name
