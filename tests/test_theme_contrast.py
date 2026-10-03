import json, pytest
import gen_theme, contrast_check as cc
from _common import ROOT, load_yaml

TOKENS = sorted((ROOT / 'assets/tokens').glob('*.json'))

@pytest.mark.parametrize('f', TOKENS, ids=lambda p: p.stem)
def test_tokens_pass_wcag(f):
    r = cc.check(json.loads(f.read_text()))
    assert r['ok'], [x for x in r['rows'] if not x['ok']]

def test_contrast_math():
    assert round(cc.ratio((0, 0, 0, 1), (255, 255, 255, 1)), 1) == 21.0
    assert cc.ratio(cc.parse('#777777'), cc.parse('#ffffff')) < 4.5          # known fail
    assert abs(cc.parse('oklch(100% 0 0)')[0] - 255) < 1

def test_low_contrast_is_detected():
    tok = json.loads((TOKENS[0]).read_text()); tok['colors']['m'] = '#4a4a4a'
    assert not cc.check(tok)['ok']

@pytest.mark.parametrize('f', TOKENS, ids=lambda p: p.stem)
def test_themes_are_current_and_valid(f):
    tok = json.loads(f.read_text())
    built = gen_theme.build(tok)
    name = f'dxbmark_{tok["slug"]}'
    mode = 'light' if tok['slug'] == 'frost' else 'dark'
    assert list(built[name]['modes']) == [mode]
    on_disk = load_yaml(ROOT / f'assets/themes/{name}.yaml')
    assert on_disk == built
    for k in ('primary-color', 'ha-card-background', 'primary-text-color'):
        assert k in built[name]['modes'][mode]
