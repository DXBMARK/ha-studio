import pathlib, subprocess, sys
S = pathlib.Path(__file__).resolve().parents[1] / 'skills' / 'ha-studio'
RUN = [sys.executable, str(S / 'scripts' / 'design_search.py')]


def test_vendored_license_and_notice():
    lic = (S / 'vendor' / 'ui-ux-pro-max' / 'LICENSE').read_text()
    assert 'MIT License' in lic and 'Next Level Builder' in lic
    notices = (S.parents[1] / 'THIRD_PARTY_NOTICES.md').read_text()
    assert 'ui-ux-pro-max' in notices and 'MIT' in notices


def test_domain_search_and_ha_notes():
    r = subprocess.run(RUN + ['touch target', '--domain', 'ux'], capture_output=True, text=True)
    assert r.returncode == 0 and 'Touch' in r.stdout and 'HA Studio adaptations' in r.stdout


def test_read_only_flags_refused(tmp_path):
    r = subprocess.run(RUN + ['x', '--persist', '--output-dir', str(tmp_path)], capture_output=True, text=True)
    assert r.returncode != 0 and 'read-only' in r.stderr
    assert not any(tmp_path.iterdir())
