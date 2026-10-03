#!/usr/bin/env python3
"""Render preview HTML files to PNG screenshots (one per tab) with Playwright/Chromium.

usage: screenshot.py preview.html [more.html] --out shots/ [--tabs overview,energy] [--scale 1]
Requires: pip install playwright && playwright install chromium   (or a system Chromium)
Optional: --fonts-dir DIR containing Inter / Source Serif 4 / JetBrains Mono woff2 files
          (e.g. from npm @fontsource packages, SIL OFL 1.1) when the machine is offline.
(c) 2026 DXBMARK LLC - Apache-2.0
"""
import argparse
import base64
import os
import sys
from pathlib import Path

TABS = ["overview", "voice", "energy", "infra", "backups"]
RAIL_LABEL = {"overview": "Overview", "voice": "Voice", "energy": "Energy", "infra": "Infrastructure", "backups": "Backups"}


def font_css(fonts_dir):
    if not fonts_dir:
        return None
    d = Path(fonts_dir)
    faces = []
    spec = [("Inter", "inter-latin-%d-normal.woff2", (400, 500, 600)),
            ("Source Serif 4", "source-serif-4-latin-%d-normal.woff2", (600,)),
            ("JetBrains Mono", "jetbrains-mono-latin-%d-normal.woff2", (400,))]
    for fam, pat, weights in spec:
        for w in weights:
            f = d / (pat % w)
            if f.exists():
                b64 = base64.b64encode(f.read_bytes()).decode()
                faces.append("@font-face{font-family:'%s';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam, w, b64))
    return "\n".join(faces) or None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--tabs", default=",".join(TABS))
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--fonts-dir")
    ap.add_argument("--width", type=int, default=1194)
    ap.add_argument("--height", type=int, default=834)
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright missing: pip install playwright && playwright install chromium")
    css = font_css(a.fonts_dir)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH")
        launch = {"executable_path": exe} if exe else {}
        browser = p.chromium.launch(**launch)
        for f in a.files:
            page = browser.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.scale)
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            if css:
                page.route("**/fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=css))
                page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
            else:
                page.route("**/fonts.g*apis.com/**", lambda r: r.abort())
            page.goto(Path(f).resolve().as_uri())
            page.wait_for_selector("#dc-root nav")
            stem = Path(f).stem.replace(".dc", "")
            for tab in [t for t in a.tabs.split(",") if t]:
                page.click('nav[aria-label="Sections"] button[aria-label="%s"]' % RAIL_LABEL[tab])
                page.wait_for_timeout(150)
                # the preview is a fixed iPad-size canvas whose main column scrolls; grow the canvas so tall tabs are never clipped
                grow = page.evaluate("""() => { const root = document.querySelector('#dc-root nav').parentElement;
                    const m = root.querySelector('main'); const extra = m.scrollHeight - m.clientHeight;
                    if (extra > 2) { root.style.height = (root.getBoundingClientRect().height + extra) + 'px'; } return Math.max(0, extra); }""")
                if grow > 2:
                    page.set_viewport_size({"width": a.width, "height": a.height + int(grow)})
                page.wait_for_timeout(100)
                target = out / ("%s-%s.png" % (stem, tab))
                page.screenshot(path=str(target))
                page.set_viewport_size({"width": a.width, "height": a.height})
                made.append(str(target))
            if errors:
                print("JS errors in %s: %s" % (f, errors), file=sys.stderr)
                sys.exit(2)
            page.close()
        browser.close()
    print("\n".join(made))


if __name__ == "__main__":
    main()
