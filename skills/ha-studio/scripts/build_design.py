#!/usr/bin/env python3
"""Build the glass iPad dashboard design (Overview / Voice / Energy / Infra / Backups).

Outputs, per theme variant:
  --format html : standalone, dependency-free HTML preview (uses assets/runtime/dc-shim.js)
  --format dc   : Claude Design component (.dc.html) that references ./support.js

All icons are inlined Font Awesome Free SVG paths from assets/icons/fa-subset.json
(CC BY 4.0, see THIRD_PARTY_NOTICES.md).  Sample data only: the design is a visual
blueprint, entity wiring is done by generate_lovelace.py.

(c) 2026 DXBMARK LLC - Apache-2.0
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ["aurora", "midnight", "frost"]

CARD = ("background: var(--card); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur); "
        "border: 1px solid var(--border); box-shadow: var(--shadow); border-radius: var(--r);")
BTN = "font-family: inherit; color: var(--t); text-align: left; cursor: pointer;"
H1 = ("margin: 0; font-family: 'Source Serif 4', Georgia, serif; font-weight: 600; font-size: 28px; "
      "line-height: 36px; letter-spacing: -0.01em;")
H2 = "margin: 0; font-size: 15px; line-height: 24px; font-weight: 600;"
MUTED = "font-size: 12px; line-height: 16px; color: var(--m);"
MONO = ("font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px; line-height: 14px; "
        "color: var(--m);")
NOWRAP = "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
CIRCLE = ("width: 40px; height: 40px; border-radius: 9999px; display: flex; align-items: center; "
          "justify-content: center; flex-shrink: 0;")
ROUND = ("border: 0; border-radius: 9999px; background: var(--chip); color: var(--t); cursor: pointer; "
         "display: flex; align-items: center; justify-content: center; padding: 0; flex-shrink: 0;")
CHIP_BTN = ("height: 44px; padding: 0 18px; border: 0; border-radius: 9999px; font-family: inherit; "
            "font-size: 14px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; "
            "justify-content: center; gap: 8px; flex-shrink: 0;")

KEYS = {
    "RAIL": ["house", "mic", "bolt", "server", "shield"],
    "KPI": ["bolt", "server", "shield", "cloud"],
    "SYS": ["house", "cubes", "rocket", "hub", "wp", "globe"],
    "DEV": ["snow", "server", "pc", "net", "fridge", "mug", "print", "bulb", "vol"],
    "VM": ["server", "cube"],
    "DOM": ["wp", "invoice", "globe"],
    "APP": ["wp", "invoice", "globe", "rocket", "db"],
    "API": ["wa", "stripe", "invoice", "gdrive"],
    "JOB": ["server", "shield", "db", "house", "wp", "hub"],
    "STO": ["hdd", "shield", "rocket", "gdrive", "house"],
    "SCENE": ["sun", "focus", "hand", "moon"],
    "MODE": ["snow", "fan", "power"],
}


def load_icons():
    data = json.loads((ROOT / "assets/icons/fa-subset.json").read_text())
    return data["icons"]


ICONS = load_icons()


# Template data may name brand glyphs; they are not shipped, so map them to generic icons.
BRAND_FALLBACK = {"wa": "bell", "stripe": "invoice", "gdrive": "cloudup", "docker": "cubes", "wp": "globe"}


def ic(name, size=20, extra=""):
    i = ICONS[BRAND_FALLBACK.get(name, name)] if name not in ICONS else ICONS[name]
    vb = i["viewBox"].split()
    return ('<svg viewBox="%s" width="%d" height="%d" fill="currentColor" aria-hidden="true" '
            'style="flex-shrink:0;%s"><path d="%s"></path></svg>') % (i["viewBox"], size, size, extra, i["path"])


def chain(var, keys, size=20):
    return "".join(
        '<sc-if value="{{ %s.ic_%s }}" hint-placeholder-val="{{ false }}">%s</sc-if>' % (var, k, ic(k, size))
        for k in keys)


def chip_row(listname, var, minw=88):
    return ('<sc-for list="{{%s}}" as="%s" hint-placeholder-count="3"><button onClick="{{ %s.pick }}" '
            'aria-pressed="{{ %s.active }}" style="%s min-width: %dpx; {{ %s.style }}">{{ %s.label }}</button>'
            '</sc-for>') % (listname, var, var, var, CHIP_BTN, minw, var, var)


def status_chip(var):
    return ('<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; '
            'border-radius: 9999px; background: var(--chip); font-size: 12px; font-weight: 600; '
            'white-space: nowrap; flex-shrink: 0;"><span style="width: 8px; height: 8px; border-radius: 9999px; '
            '{{ %s.dot }}"></span>{{ %s.statusText }}</span>') % (var, var)


def keys_js(keys):
    return json.dumps(keys).replace('"', "'")


def solid_surface(tokens):
    """Opaque stand-in for the glass card: card colour composited over the base colour."""
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from contrast_check import parse, over
    r, g, b, _ = over(parse(tokens["colors"]["card"]), parse(tokens["base"]))
    return "#%02x%02x%02x" % (round(r), round(g), round(b))


FONTS_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600'
              '&family=JetBrains+Mono:wght@400&family=Source+Serif+4:wght@600&display=swap">')


def build(tpl, tokens, brand, user, subtitle, site, initials, fmt, google_fonts=False):
    rep = {
        "@@FONTS_LINK@@": FONTS_LINK if google_fonts else "<!-- fonts: system fallbacks (use --google-fonts to load Inter, Source Serif 4, JetBrains Mono from Google Fonts) -->",
        "@@NAME@@": tokens["name"], "@@BASE@@": tokens["base"], "@@BG@@": tokens["background"],
        "@@VARS@@": " ".join("%s: %s;" % kv for kv in {**tokens["cssVars"], "--solid": solid_surface(tokens)}.items()),
        "@@BRAND@@": brand, "@@USER@@": user, "@@SUBTITLE@@": subtitle, "@@SITE@@": site, "@@INITIALS@@": initials,
        "@@H1@@": H1, "@@H2@@": H2, "@@MUTED@@": MUTED, "@@MONO@@": MONO, "@@NOWRAP@@": NOWRAP,
        "@@CARD@@": CARD, "@@BTN@@": BTN, "@@CIRCLE@@": CIRCLE, "@@ROUND@@": ROUND,
        "@@RAIL_ICONS@@": chain("r", KEYS["RAIL"], 22), "@@KPI_ICONS@@": chain("k", KEYS["KPI"], 18),
        "@@SYS_ICONS@@": chain("s", KEYS["SYS"], 18), "@@DEV_ICONS@@": chain("d", KEYS["DEV"], 16),
        "@@VM_ICONS@@": chain("v", KEYS["VM"], 16), "@@DOM_ICONS@@": chain("d", KEYS["DOM"], 16),
        "@@APP_ICONS@@": chain("a", KEYS["APP"], 16), "@@API_ICONS@@": chain("a", KEYS["API"], 20),
        "@@JOB_ICONS@@": chain("j", KEYS["JOB"], 18), "@@STO_ICONS@@": chain("s", KEYS["STO"], 20),
        "@@SCENE_ICONS@@": chain("s", KEYS["SCENE"], 18), "@@MODE_ICONS@@": chain("m", KEYS["MODE"], 16),
        "@@SYS_STATUS@@": status_chip("s"), "@@VM_STATUS@@": status_chip("v"), "@@DOM_STATUS@@": status_chip("d"),
        "@@APP_STATUS@@": status_chip("a"), "@@API_STATUS@@": status_chip("a"), "@@JOB_STATUS@@": status_chip("j"),
        "@@RANGE_CHIPS@@": chip_row("ranges", "r"), "@@JOB_CHIPS@@": chip_row("jobFilters", "f", 120),
        "@@GEAR@@": ic("gear", 20), "@@BULB@@": ic("bulb", 20), "@@LOCK@@": ic("lock", 20),
        "@@UNLOCK@@": ic("unlock", 20), "@@DOOR@@": ic("door", 20), "@@CAM@@": ic("cam", 20),
        "@@THERM@@": ic("therm", 20), "@@SNOW16@@": ic("snow", 16), "@@MINUS@@": ic("minus", 18),
        "@@PLUS@@": ic("plus", 18), "@@MINUS16@@": ic("minus", 16), "@@PLUS16@@": ic("plus", 16),
        "@@VOL26@@": ic("vol", 26), "@@PAUSE@@": ic("pause", 20), "@@PLAY@@": ic("play", 20),
        "@@PAUSE16@@": ic("pause", 16), "@@PLAY16@@": ic("play", 16), "@@STOP16@@": ic("stop", 16),
        "@@ROTATE16@@": ic("rotate", 16), "@@HORN@@": ic("horn", 18), "@@CHEV@@": ic("chev", 12),
        "@@CUBES@@": ic("cubes", 20),
    }
    for name, keys in KEYS.items():
        rep["@@%s_KEYS_JS@@" % name] = keys_js(keys)
    out = tpl
    for _ in range(3):
        for k in sorted(rep, key=len, reverse=True):
            out = out.replace(k, rep[k])
    if "@@" in out:
        raise SystemExit("unreplaced token in template: " + out.split("@@")[1][:40])
    out = out.replace("<helmet>", "<!-- Icons: Font Awesome Free by Fonticons, Inc., CC BY 4.0 (https://fontawesome.com/license/free). Design by DXBMARK LLC, Apache-2.0. Sample data only. -->\n<helmet>", 1)
    if fmt == "html":
        shim = (ROOT / "assets/runtime/dc-shim.js").read_text()
        out = out.replace('<script src="./support.js"></script>', "<script>\n" + shim + "\n</script>")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="out", help="output directory")
    ap.add_argument("--themes", default=",".join(THEMES), help="comma list: " + ",".join(THEMES))
    ap.add_argument("--format", choices=["html", "dc"], default="html")
    ap.add_argument("--brand", default="DXBMARK")
    ap.add_argument("--user", default="Alex")
    ap.add_argument("--subtitle", default="Operations")
    ap.add_argument("--site", default="Saturday · Main office")
    ap.add_argument("--initials", default="AM")
    ap.add_argument("--google-fonts", action="store_true", help="load fonts from Google Fonts (off by default: no third-party requests)")
    ap.add_argument("--force", action="store_true", help="overwrite existing output files")
    a = ap.parse_args(argv)
    tpl = (ROOT / "assets/templates/ipad-glass.tpl.html").read_text()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for slug in [t.strip() for t in a.themes.split(",") if t.strip()]:
        tokp = ROOT / "assets/tokens" / (slug + ".json")
        if not tokp.exists():
            sys.exit("unknown theme: %s (have: %s)" % (slug, ", ".join(THEMES)))
        tokens = json.loads(tokp.read_text())
        html = build(tpl, tokens, a.brand, a.user, a.subtitle, a.site, a.initials, a.format, a.google_fonts)
        name = "%s.%s" % (slug, "html" if a.format == "html" else "dc.html")
        from _common import write_text
        write_text(out / name, html, a.force)
        written.append(str(out / name))
    print("\n".join(written))


if __name__ == "__main__":
    main()
