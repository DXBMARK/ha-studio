#!/usr/bin/env python3
"""Run the whole HA Studio pipeline locally on the bundled demo data and serve the results in your browser.

  python3 tools/serve_demo.py [--port 8099] [--out DIR] [--no-serve]
  python3 tools/serve_demo.py --states-file my_states.json     # your own Home Assistant export

Builds: inventory -> energy audit -> theme -> Lovelace dashboard (+ Rooms view, admin-only tabs) -> validation ->
contrast report -> three iPad glass previews -> component and icon sheets, then serves an index page on 127.0.0.1.
Nothing is sent anywhere; no Home Assistant connection is made. (c) 2026 DXBMARK LLC - Apache-2.0
"""
import argparse, functools, html, http.server, pathlib, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SK = REPO / 'skills' / 'ha-studio'
S = SK / 'scripts'
EX = SK / 'assets' / 'examples'


def run(label, out, *args, ok=(0,)):
    r = subprocess.run([sys.executable, str(S / args[0]), *map(str, args[1:])], capture_output=True, text=True)
    (out / 'reports').mkdir(exist_ok=True)
    name = label.lower().replace(' ', '_') + '.txt'
    (out / 'reports' / name).write_text(f'$ {args[0]} {" ".join(map(str, args[1:]))}\n\n{r.stdout}{r.stderr}', encoding='utf-8')
    status = 'ok' if r.returncode in ok else f'exit {r.returncode}'
    print(f'  {label:<24} {status}')
    return label, (r.returncode in ok, f'reports/{name}', status)


def build(out, states_file, inventory):
    out.mkdir(parents=True, exist_ok=True)
    steps = []
    inv = out / 'inventory.json'
    if inventory:
        inv.write_text(pathlib.Path(inventory).read_text(encoding='utf-8'), encoding='utf-8')
    else:
        steps.append(run('Inventory', out, 'ha_inventory.py', '--states-file', states_file or EX / 'demo_states.json', '--out', inv, '--force'))
    steps.append(run('Energy audit', out, 'energy_audit.py', inv, '--tariff', '0.15', '--json', out / 'energy_audit.json', '--force'))
    steps.append(run('Theme', out, 'gen_theme.py', 'aurora', '--out', out / 'dxbmark_aurora.yaml', '--force'))
    steps.append(run('Dashboard', out, 'generate_lovelace.py', inv, '--profile', 'office', '--theme', 'dxbmark_aurora',
                     '--title', 'Demo Office', '--areas', EX / 'demo_areas.yaml', '--admin-user', 'REPLACE_WITH_HA_USER_ID',
                     '--out', out / 'dashboard.yaml', '--force'))
    steps.append(run('Validation', out, 'validate_dashboard.py', out / 'dashboard.yaml', '--inventory', inv))
    steps.append(run('Contrast', out, 'contrast_check.py'))
    steps.append(run('Previews', out, 'build_design.py', '--out', out / 'preview', '--format', 'html', '--google-fonts', '--force'))
    steps.append(run('Sheets', out, 'build_sheets.py', '--out', out / 'sheets', '--force'))
    return steps


def index(out, steps):
    rows = ''.join(f'<li><a href="{p}">{html.escape(l)}</a> <span class="{"ok" if ok else "bad"}">{s}</span></li>' for l, (ok, p, s) in steps.items())
    files = [('Generated dashboard (paste into the raw configuration editor)', 'dashboard.yaml'),
             ('Generated theme', 'dxbmark_aurora.yaml'), ('Inventory (demo)', 'inventory.json')]
    fl = ''.join(f'<li><a href="{p}">{html.escape(t)}</a></li>' for t, p in files)
    pv = ''.join(f'<li><a href="preview/{t}.html" target="_blank">{t.title()} preview (iPad, interactive)</a></li>' for t in ('aurora', 'midnight', 'frost'))
    sh = ''.join(f'<li><a href="sheets/{t}-components.html" target="_blank">{t.title()} components and contrast</a></li>' for t in ('aurora', 'midnight', 'frost'))
    page = f'''<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>HA Studio local demo</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;background:#0b0b0d;color:#f4f4f5}}
a{{color:#f97e1a}}h1{{font-family:Georgia,serif}}h2{{margin-top:28px;font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#b0b0ba}}
.ok{{color:#00d68f}}.bad{{color:#ff8a8a}}small{{color:#b0b0ba}}</style>
<h1>HA Studio — local demo</h1><p><small>Runs only on this computer with bundled sample data. DXBMARK LLC · Apache-2.0</small></p>
<h2>Designs</h2><ul>{pv}</ul><h2>Components, palette, contrast</h2><ul>{sh}<li><a href="sheets/icons.html" target="_blank">Icon set</a></li></ul>
<h2>Generated files</h2><ul>{fl}</ul><h2>Pipeline reports</h2><ul>{rows}</ul>'''
    (out / 'index.html').write_text(page, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--port', type=int, default=8099)
    ap.add_argument('--out', help='output folder (default: a temp folder)')
    ap.add_argument('--states-file', help='Home Assistant /api/states JSON export instead of the demo data')
    ap.add_argument('--inventory', help='an existing inventory.json')
    ap.add_argument('--no-serve', action='store_true', help='build only')
    a = ap.parse_args()
    out = pathlib.Path(a.out) if a.out else pathlib.Path(tempfile.mkdtemp(prefix='ha-studio-demo-'))
    print('Building into', out)
    steps = build(out, a.states_file, a.inventory)
    index(out, dict(steps))
    if a.no_serve:
        return 0 if all(v[0] for _, v in steps) else 1
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=str(out))
    with http.server.ThreadingHTTPServer(('127.0.0.1', a.port), handler) as srv:
        print(f'\nOpen http://127.0.0.1:{a.port}/   (Ctrl+C to stop)')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\nstopped')
    return 0


if __name__ == '__main__':
    sys.exit(main())
