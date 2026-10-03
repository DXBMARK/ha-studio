import pytest, subprocess, sys
from conftest import SK

def test_build_all_variants_html(tmp_path):
    r = subprocess.run([sys.executable, SK / 'scripts/build_design.py', '--out', tmp_path, '--format', 'html', '--brand', 'ACME', '--user', 'Sam'],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for t in ('aurora', 'midnight', 'frost'):
        h = (tmp_path / f'{t}.html').read_text()
        assert 'ACME' in h and '@@' not in h                     # all placeholders replaced
        assert 'prefers-reduced-transparency' in h and 'forced-colors' in h and '--solid' in h
        assert 'Lobby cam' in h

def test_dc_format(tmp_path):
    r = subprocess.run([sys.executable, SK / 'scripts/build_design.py', '--out', tmp_path, '--format', 'dc', '--themes', 'aurora'], capture_output=True, text=True)
    assert r.returncode == 0 and (tmp_path / 'aurora.dc.html').exists()

def test_render_without_js_errors(tmp_path):
    pw = pytest.importorskip('playwright.sync_api')
    subprocess.run([sys.executable, SK / 'scripts/build_design.py', '--out', tmp_path, '--format', 'html', '--themes', 'aurora'], check=True, capture_output=True)
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            pytest.skip('chromium not available')
        pg = b.new_page(viewport={'width': 1194, 'height': 834}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto((tmp_path / 'aurora.html').as_uri()); pg.wait_for_timeout(500)
        assert 'Power now' in pg.inner_text('body')
        for tab in ('Voice', 'Energy', 'Infrastructure', 'Backups'):
            pg.get_by_label(tab).first.click(); pg.wait_for_timeout(150)
        assert errs == []
        b.close()
