import json, re, subprocess, sys, zipfile, pytest
from conftest import REPO, SK
import lint_skill

def test_lint_clean():
    errs, _ = lint_skill.lint(SK)
    assert errs == []

def test_lint_detects_bad_skill(tmp_path):
    d = tmp_path / 'my-claude-skill'; d.mkdir()
    (d / 'SKILL.md').write_text('---\nname: my-claude-skill\ndescription: x\nargument-hint: y\n---\nbody\n')
    errs, _ = lint_skill.lint(d)
    joined = ' '.join(errs)
    assert 'unknown frontmatter keys' in joined and 'claude' in joined

def test_description_budget_and_trigger_words():
    t = (SK / 'SKILL.md').read_text()
    desc = re.search(r'^description: (.*)$', t, re.M).group(1)
    assert len(desc) <= 1024
    for w in ('Home Assistant', 'Lovelace', 'dashboard', 'energy', 'camera'):
        assert w.lower() in desc.lower()

def test_skill_md_under_500_lines():
    assert len((SK / 'SKILL.md').read_text().splitlines()) < 500

def test_manifests_consistent():
    plug = json.loads((REPO / '.claude-plugin/plugin.json').read_text())
    mk = json.loads((REPO / '.claude-plugin/marketplace.json').read_text())
    gem = json.loads((REPO / 'gemini-extension.json').read_text())
    fm_ver = re.search(r'version: ([\d.]+)', (SK / 'SKILL.md').read_text()).group(1)
    assert plug['version'] == mk['plugins'][0]['version'] == gem['version'] == fm_ver
    assert plug['name'] == mk['plugins'][0]['name'] == SK.name
    assert 'skills' not in plug and 'skills' not in mk['plugins'][0]      # avoid duplicate-manifest conflict
    assert plug['license'] == 'Apache-2.0'

def test_chatgpt_limits():
    assert len((REPO / 'chatgpt/instructions.md').read_text()) <= 5000
    assert len((REPO / 'chatgpt/instructions-lite.md').read_text()) <= 1500

def test_legal_files_present_and_owner_is_dxbmark():
    for f in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md', 'TRADEMARKS.md', 'SECURITY.md', 'CONTRIBUTING.md', 'README.md'):
        assert (REPO / f).exists(), f
    assert 'Apache License' in (REPO / 'LICENSE').read_text()[:200]
    assert 'DXBMARK LLC' in (REPO / 'NOTICE').read_text()
    assert 'CC BY 4.0' in (REPO / 'THIRD_PARTY_NOTICES.md').read_text()

def test_no_home_assistant_logo_or_forbidden_wording():
    bad = re.compile(r'works with home assistant', re.I)
    for f in REPO.rglob('*'):
        if f.is_file() and f.suffix in ('.md', '.yaml', '.json', '.py', '.html') and '.git' not in f.parts and 'tests' not in f.parts:
            t = f.read_text(errors='ignore')
            if f.name in ('TRADEMARKS.md', 'README.md', 'THIRD_PARTY_NOTICES.md', 'verification-checklist.md'):  # these state the rule itself
                continue
            assert not bad.search(t), f
    assert not list(REPO.rglob('*logo*'))

def test_release_build(tmp_path):
    r = subprocess.run([sys.executable, REPO / 'tools/build_release.py', '--out', tmp_path], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    z = tmp_path / 'ha-studio-1.0.0.zip'
    names = zipfile.ZipFile(z).namelist()
    assert 'ha-studio/SKILL.md' in names                      # skill folder at ZIP root
    assert not any(n.startswith('ha-studio/ha-studio') for n in names)
    assert not any('__pycache__' in n for n in names)
    pack = zipfile.ZipFile(tmp_path / 'chatgpt-pack-1.0.0.zip').namelist()
    assert 'instructions.md' in pack and all('/' not in n.split('knowledge/', 1)[-1] for n in pack if n.startswith('knowledge/'))
    assert len([n for n in pack if n.startswith('knowledge/')]) <= 20  # ChatGPT project file caps
    assert (tmp_path / 'SHA256SUMS').read_text().count('\n') == 3

def test_installer_is_dry_run_and_non_destructive(tmp_path):
    cmd = [sys.executable, REPO / 'tools/install.py', '--target', 'codex-repo', '--dest', tmp_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert 'dry run' in r.stdout and not (tmp_path / '.agents').exists()
    assert subprocess.run(cmd + ['--yes'], capture_output=True).returncode == 0
    assert (tmp_path / '.agents/skills/ha-studio/SKILL.md').exists()
    r2 = subprocess.run(cmd + ['--yes'], capture_output=True, text=True)
    assert r2.returncode == 1 and 'refusing' in r2.stdout           # never overwrites

def test_no_secrets_in_repo():
    from _common import find_secrets
    for f in REPO.rglob('*'):
        if f.is_file() and f.suffix in ('.md', '.yaml', '.json', '.py', '.html', '.yml', '.js') and '.git' not in f.parts and f.name not in ('test_generate_validate.py', 'test_hardening.py'):
            assert find_secrets(f.read_text(errors='ignore')) == [], f
