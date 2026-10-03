#!/usr/bin/env python3
"""WCAG contrast checker for glass themes (tokens/*.json).

Glass cards are translucent, so the real surface colour depends on what is behind
them. We composite the card colour over the *worst-case* backdrop (the lightest
backdrop sample for dark themes, the darkest for light themes) and check every
text/accent pair at that surface.  Exit code 1 if any required pair fails.

Usage: contrast_check.py [tokens_dir_or_file ...] [--json]
"""
import json, math, re, sys, pathlib

def _oklch(m):
    L, C, h = float(m[0].rstrip('%')) / (100 if m[0].endswith('%') else 1), float(m[1]), math.radians(float(m[2]))
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, mm, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s
    enc = lambda x: 12.92 * x if x <= 0.0031308 else 1.055 * (max(x, 0) ** (1 / 2.4)) - 0.055
    return tuple(min(1, max(0, enc(v))) * 255 for v in (r, g, bb)) + (1.0,)

def parse(c):
    """-> (r,g,b,a) with rgb 0-255."""
    c = c.strip()
    m = re.fullmatch(r'#([0-9a-fA-F]{3,8})', c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = ''.join(x * 2 for x in h)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a
    m = re.fullmatch(r'rgba?\(([^)]+)\)', c)
    if m:
        p = [x.strip() for x in m.group(1).split(',')]
        return float(p[0]), float(p[1]), float(p[2]), float(p[3]) if len(p) > 3 else 1.0
    m = re.fullmatch(r'oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)\s*\)', c)
    if m:
        return _oklch(m.groups())
    raise ValueError(f'unsupported colour: {c}')

def over(fg, bg):
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)

def lum(c):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])

def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def backdrop_samples(tok, strength=1.0):
    """Base colour plus each gradient glow composited on the base.

    strength scales the glow alpha: 1.0 = the very peak of a radial glow (a few px under
    one card corner), 0.5 = what a card typically sits on."""
    base = parse(tok['base'])
    samples = [base]
    for col in re.findall(r'#[0-9a-fA-F]{6,8}', tok['background']):
        r, g, b, a = parse(col)
        samples.append(over((r, g, b, a * strength), base))
    return samples

# (foreground token, minimum ratio, description)
PAIRS = [
    ('t', 4.5, 'primary text'), ('ink2', 4.5, 'secondary ink'), ('m', 4.5, 'muted text'),
    ('acct', 4.5, 'accent text'), ('ok', 4.5, 'status ok'), ('warn', 4.5, 'status warn'),
    ('bad', 4.5, 'status bad'),
]

def check(tok):
    c = tok['colors']
    base = parse(tok['base'])
    dark = lum(base) < 0.4
    def surface(strength):
        smp = backdrop_samples(tok, strength)
        w = max(smp, key=lum) if dark else min(smp, key=lum)
        return over(parse(c['card']), w)
    surf = surface(0.5)      # required: AA at a typical worst-case position
    peak = surface(1.0)      # advisory: AA-large (3:1) even at the glow peak
    rows = []
    for key, need, label in PAIRS:
        r = ratio(over(parse(c[key]), surf), surf)
        rp = ratio(over(parse(c[key]), peak), peak)
        rows.append({'pair': f'{key} on glass', 'what': label, 'ratio': round(r, 2), 'need': need, 'ok': r >= need,
                     'peak': round(rp, 2), 'peak_ok': rp >= 3.0})
    # accent button: text-on-accent
    r = ratio(parse(c['ona']), parse(c['acc']))
    rows.append({'pair': 'ona on acc', 'what': 'text on accent button', 'ratio': round(r, 2), 'need': 4.5, 'ok': r >= 4.5})
    # UI component boundary (non-text 3:1) – the border is decorative, the chip/line must be perceivable together with bar
    r = ratio(over(parse(c['bar']), surf), surf)
    rows.append({'pair': 'bar on glass', 'what': 'chart bars (non-text)', 'ratio': round(r, 2), 'need': 3.0, 'ok': r >= 3.0})
    return {'theme': tok['slug'], 'dark': dark, 'surface': [round(x) for x in surf[:3]], 'rows': rows,
            'ok': all(x['ok'] for x in rows)}

def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', help='token JSON files or directories (default: assets/tokens)')
    ap.add_argument('--json', action='store_true')
    ns = ap.parse_args(argv)
    as_json = ns.json
    paths = [pathlib.Path(a) for a in ns.paths] or [pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'tokens']
    files = []
    for p in paths:
        files += sorted(p.glob('*.json')) if p.is_dir() else [p]
    results = [check(json.loads(f.read_text())) for f in files]
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"\n{r['theme']}  (surface rgb{tuple(r['surface'])})  {'PASS' if r['ok'] else 'FAIL'}")
            for x in r['rows']:
                print(f"  {'ok ' if x['ok'] else 'BAD'} {x['pair']:<14} {x['ratio']:>5}  need {x['need']}  {x['what']}" + (f"   [peak-glow {x['peak']}{'' if x['peak_ok'] else ' <3 !'}]" if 'peak' in x else ''))
    return 0 if all(r['ok'] for r in results) else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
