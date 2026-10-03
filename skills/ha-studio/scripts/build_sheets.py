#!/usr/bin/env python3
"""Build static HTML "design sheets" for docs: palette + contrast, components, icon grid.

  build_sheets.py --out sheets/            → sheets/<theme>-components.html and sheets/icons.html
Then render with screenshot.py-style Playwright (see tools/make_screenshots.py).
(c) 2026 DXBMARK LLC - Apache-2.0
"""
import argparse, html, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _common import ROOT, write_text
from contrast_check import check, parse, over

def icon(name, icons, size=22):
    i = icons[name]
    return f'<svg viewBox="{i["viewBox"]}" width="{size}" height="{size}" fill="currentColor" aria-hidden="true"><path d="{i["path"]}"/></svg>'

def components(tok, icons):
    v = ';'.join(f'{k}:{x}' for k, x in tok['cssVars'].items())
    res = check(tok)
    sw = ''.join(f'<div class="sw" style="background:{tok["colors"][k]}"><b>{k}</b><span>{tok["colors"][k][:22]}</span></div>'
                 for k in ('acc', 'acct', 'ok', 'warn', 'bad', 't', 'm'))
    rows = ''.join(f'<tr><td>{r["pair"]}</td><td>{r["ratio"]}</td><td>≥ {r["need"]}</td><td class="{"ok" if r["ok"] else "bad"}">{"PASS" if r["ok"] else "FAIL"}</td></tr>' for r in res['rows'])
    tile = lambda ic, t, s, on: (f'<div class="tile {"on" if on else ""}"><span class="ico">{icon(ic, icons)}</span><div><b>{t}</b><small>{s}</small></div></div>')
    return f'''<!doctype html><meta charset=utf-8><title>{html.escape(tok["name"])} components</title>
<style>*{{box-sizing:border-box}}body{{margin:0;font:14px Inter,system-ui,sans-serif;background:{tok["base"]}}}
.root{{{v};width:1194px;padding:28px;background:{tok["background"]};color:var(--t);min-height:760px}}
h1{{font:600 26px "Source Serif 4",Georgia,serif;margin:0 0 4px}}p{{color:var(--m);margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.card{{background:var(--card);border:1px solid var(--border);border-radius:var(--r);box-shadow:var(--shadow);backdrop-filter:var(--blur);padding:18px}}
.card h2{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--m);margin:0 0 12px}}
.sws{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}.sw{{border-radius:12px;padding:10px;height:64px;display:flex;flex-direction:column;justify-content:flex-end;font-size:11px;border:1px solid var(--line);color:#000;mix-blend-mode:normal;text-shadow:0 0 2px #fff8}}
.tile{{display:flex;gap:12px;align-items:center;padding:12px;border-radius:16px;background:var(--chip);border:1px solid var(--line);min-height:64px;margin-bottom:8px}}
.tile.on{{background:var(--accsoft);border-color:var(--acc)}}.tile small{{display:block;color:var(--m)}}.ico{{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:var(--chip);color:var(--acct)}}
.btn{{border:0;border-radius:999px;padding:12px 20px;min-height:48px;font:600 14px Inter;background:var(--acc);color:var(--ona);margin-right:8px}}.btn.g{{background:var(--chip);color:var(--t);border:1px solid var(--line)}}
.chip{{display:inline-flex;gap:6px;align-items:center;padding:5px 11px;border-radius:999px;font-size:12px;margin:0 6px 6px 0}}
.ok{{color:var(--ok)}}.bad{{color:var(--bad)}}.chip.o{{background:var(--chip);color:var(--ok)}}.chip.w{{background:var(--warnbg);color:var(--warn)}}.chip.b{{background:var(--badbg);color:var(--bad)}}
table{{width:100%;border-collapse:collapse;font-size:12px}}td{{padding:4px 6px;border-bottom:1px solid var(--line)}}
.bar{{height:10px;border-radius:6px;background:var(--chip);overflow:hidden}}.bar i{{display:block;height:100%;width:62%;background:var(--bar)}}</style>
<div class=root><h1>{html.escape(tok["name"])}</h1><p>Tokens, components and measured contrast (WCAG) — HA Studio</p>
<div class=grid>
<div class=card><h2>Palette</h2><div class=sws>{sw}</div></div>
<div class=card><h2>Contrast on glass ({"PASS" if res["ok"] else "FAIL"})</h2><table>{rows}</table></div>
<div class=card><h2>Tiles</h2>{tile("bulb","Reception","On · 18 W",True)}{tile("door","Server room","Door closed",False)}{tile("cam","Lobby cam","No person",False)}</div>
<div class=card><h2>Buttons, status, bars</h2><button class=btn>Announce</button><button class="btn g">Pause</button><br><br>
<span class="chip o">{icon("check",icons,14)} Online</span><span class="chip w">{icon("warn",icons,14)} SSL 12 d</span><span class="chip b">{icon("warn",icons,14)} Backup stale</span>
<div style="margin-top:10px" class=bar><i></i></div></div></div></div>'''

def icon_sheet(tok, icons):
    cells = ''.join(f'<div class=c>{icon(n, icons, 28)}<small>{n}</small></div>' for n in icons)
    lic = '<br>'.join(json.loads((ROOT / 'assets/icons/fa-subset.json').read_text())['_license'].values())
    return f'''<!doctype html><meta charset=utf-8><title>Icons</title><style>body{{margin:0;font:12px Inter,system-ui;background:{tok["base"]};color:{tok["colors"]["t"]}}}
.w{{width:1194px;padding:28px;background:{tok["background"]}}}h1{{font:600 24px "Source Serif 4",Georgia,serif;margin:0 0 14px}}
.g{{display:grid;grid-template-columns:repeat(10,1fr);gap:10px}}.c{{display:flex;flex-direction:column;align-items:center;gap:6px;padding:12px 4px;border-radius:14px;background:{tok["colors"]["card"]};border:1px solid {tok["colors"]["border"]};color:{tok["colors"]["acct"]}}}
small{{color:{tok["colors"]["m"]};font-size:11px}}p{{color:{tok["colors"]["m"]};font-size:11px;margin-top:14px}}</style>
<div class=w><h1>Icon set ({len(icons)} glyphs, preview only; dashboards use mdi: names)</h1><div class=g>{cells}</div><p>{lic}</p></div>'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--force', action='store_true'); a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    icons = json.loads((ROOT / 'assets/icons/fa-subset.json').read_text())['icons']
    toks = {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / 'assets/tokens').glob('*.json'))}
    for slug, t in toks.items():
        write_text(out / f'{slug}-components.html', components(t, icons), a.force)
    write_text(out / 'icons.html', icon_sheet(toks['aurora'], icons), a.force)
    print('sheets →', out)

if __name__ == '__main__':
    main()
