#!/usr/bin/env python3
"""Query the bundled ui-ux-pro-max design knowledge base (MIT) with Home Assistant corrections.

Read-only: never writes files. Wraps vendor/ui-ux-pro-max/scripts/search.py and appends the adaptations that
matter for HA dashboards (the upstream data targets web and landing pages).

  design_search.py "glassmorphism energy dashboard dark"            # design-system recommendation
  design_search.py "touch target contrast" --domain ux              # one domain
  design_search.py "kpi tiles" --domain chart --max-results 5
"""
import argparse, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
UPSTREAM = HERE.parent / 'vendor' / 'ui-ux-pro-max' / 'scripts' / 'search.py'
BLOCKED = {'--persist', '--output-dir', '--page', '--force'}   # keep this tool read-only

HA_NOTES = """
## HA Studio adaptations (apply on top of the result above)
- Ignore landing-page advice (hero, CTA, conversion). A dashboard is an operations screen: status first, one action per tile.
- Colours/fonts become theme variables (`primary-color`, `ha-card-background`, `card-background-color`), not hard-coded hex or web fonts.
- Contrast is measured on the composited card (text 4.5:1, UI 3:1) with scripts/contrast_check.py; keep dialogs opaque.
- Touch targets 48 px on wall panels and tablets; never rely on colour alone for state (add icon or text).
- Provide fallbacks for prefers-reduced-transparency, prefers-contrast, forced-colors.
- Only use entities that exist in the user's inventory; report gaps instead of inventing them.
""".strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('query')
    ap.add_argument('--domain', help='style|color|chart|landing|product|ux|typography|icons|motion|react|web')
    ap.add_argument('--stack', help='e.g. html-tailwind (rarely useful for HA)')
    ap.add_argument('--max-results', type=int, default=3)
    ap.add_argument('--no-notes', action='store_true', help='omit the HA adaptation footer')
    a, extra = ap.parse_known_args()
    bad = BLOCKED.intersection(extra)
    if bad:
        sys.exit(f'design_search.py is read-only; refused option(s): {", ".join(sorted(bad))}')
    if not UPSTREAM.exists():
        sys.exit('vendored ui-ux-pro-max not found (skills/ha-studio/vendor/ui-ux-pro-max)')
    cmd = [sys.executable, str(UPSTREAM), a.query, '--max-results', str(a.max_results)]
    if a.domain:
        cmd += ['--domain', a.domain]
    elif a.stack:
        cmd += ['--stack', a.stack]
    else:
        cmd += ['--design-system', '-p', 'HA dashboard']
    cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode:
        sys.stderr.write(r.stderr)
        return r.returncode
    if not a.no_notes:
        print('\n' + HA_NOTES)
    return 0


if __name__ == '__main__':
    sys.exit(main())
