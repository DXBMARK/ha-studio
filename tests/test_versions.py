import json, pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent

def versions():
    out = {'plugin.json': json.loads((R / '.claude-plugin/plugin.json').read_text())['version'],
           'gemini-extension.json': json.loads((R / 'gemini-extension.json').read_text())['version']}
    mk = json.loads((R / '.claude-plugin/marketplace.json').read_text())
    for p in mk['plugins']:
        out['marketplace:' + p['name']] = p['version']
    sk = (R / 'skills/ha-studio/SKILL.md').read_text()
    out['SKILL.md'] = re.search(r'^\s+version:\s*"?([\d.]+)"?', sk, re.M).group(1)
    out['CHANGELOG'] = re.search(r'^## (\d+\.\d+\.\d+)', (R / 'CHANGELOG.md').read_text(), re.M).group(1)
    return out

def test_all_versions_agree_and_are_semver():
    v = versions()
    assert len(set(v.values())) == 1, v
    assert re.fullmatch(r'\d+\.\d+\.\d+', next(iter(v.values())))

def test_release_notes_extract():
    import subprocess, sys
    ver = versions()['CHANGELOG']
    r = subprocess.run([sys.executable, str(R / 'tools/release_notes.py'), ver], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip()
