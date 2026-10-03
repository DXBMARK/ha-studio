#!/usr/bin/env python3
"""Regenerate every README screenshot from source (previews, dashboards, component + icon sheets).

  python3 tools/make_screenshots.py [--fonts-dir DIR] [--out docs/screenshots]

Needs Playwright + Chromium. --fonts-dir lets you embed OFL fonts (Inter, Source Serif 4, JetBrains Mono)
when the machine is offline. Output PNGs use sample data only — no real company or customer data.
"""
import argparse, base64, pathlib, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SK = REPO / 'skills' / 'ha-studio'

def font_css(d):
    if not d: return ''
    spec = [('Inter', 'inter-latin-%d-normal.woff2', (400, 500, 600)),
            ('Source Serif 4', 'source-serif-4-latin-%d-normal.woff2', (600,)),
            ('JetBrains Mono', 'jetbrains-mono-latin-%d-normal.woff2', (400,))]
    out = ''
    for fam, pat, ws in spec:
        for w in ws:
            f = pathlib.Path(d) / (pat % w)
            if f.exists():
                out += "@font-face{font-family:'%s';font-weight:%d;src:url(data:font/woff2;base64,%s)}" % (fam, w, base64.b64encode(f.read_bytes()).decode())
    return out

def run(*a):
    subprocess.run([sys.executable, *map(str, a)], check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--fonts-dir'); ap.add_argument('--out', default=str(REPO / 'docs' / 'screenshots'))
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    run(SK / 'scripts/build_design.py', '--out', tmp / 'prev', '--format', 'html', '--google-fonts')
    for t in ('aurora', 'midnight', 'frost'):
        args = [SK / 'scripts/screenshot.py', tmp / 'prev' / f'{t}.html', '--out', out]
        if a.fonts_dir: args += ['--fonts-dir', a.fonts_dir]
        run(*args)
    run(SK / 'scripts/build_sheets.py', '--out', tmp / 'sheets')
    from playwright.sync_api import sync_playwright
    css = font_css(a.fonts_dir)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1194, 'height': 800})
        for f in sorted((tmp / 'sheets').glob('*.html')):
            pg.goto(f.as_uri())
            if css: pg.add_style_tag(content=css)
            pg.wait_for_timeout(300)
            h = pg.evaluate('document.body.firstElementChild.getBoundingClientRect().height')
            pg.screenshot(path=str(out / (f.stem + '.png')), clip={'x': 0, 'y': 0, 'width': 1194, 'height': int(h)})
        b.close()
    from PIL import Image   # WebP keeps gradients/colours at a fraction of PNG size (README loads fast)
    for f in sorted(out.glob('*.png')):
        Image.open(f).convert('RGB').save(f.with_suffix('.webp'), quality=90, method=6)
        f.unlink()
    print('screenshots →', out)

if __name__ == '__main__':
    main()
