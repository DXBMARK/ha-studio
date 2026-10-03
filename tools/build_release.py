#!/usr/bin/env python3
"""Build release artefacts into dist/.

  ha-studio-<ver>.zip      claude.ai upload (skill folder at the ZIP root)
  chatgpt-pack-<ver>.zip           instructions (+lite) and flat knowledge files for a ChatGPT Project / GPT
  gem-instructions.md              paste-in text for a Gemini Gem
  SHA256SUMS                       checksums

  python3 tools/build_release.py [--out dist]
Runs the skill lint first and refuses to build on errors.
"""
import argparse, hashlib, json, pathlib, re, sys, zipfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SK = REPO / 'skills' / 'ha-studio'
SKIP_DIRS = {'__pycache__', '.pytest_cache'}
sys.path.insert(0, str(SK / 'scripts'))
from lint_skill import lint

def files_of(root):
    for f in sorted(root.rglob('*')):
        if f.is_file() and not (set(f.parts) & SKIP_DIRS) and f.suffix != '.pyc':
            yield f

def build_skill_zip(out, ver):
    z = out / f'ha-studio-{ver}.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files_of(SK):
            zf.write(f, f'ha-studio/{f.relative_to(SK).as_posix()}')
        for extra in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md', 'TRADEMARKS.md'):
            if (REPO / extra).exists():
                zf.write(REPO / extra, f'ha-studio/{extra}')
    return z

def flat_knowledge():
    """ChatGPT knowledge files must be flat: references + profiles as markdown, no sub-folders."""
    items = {}
    for f in sorted((SK / 'references').glob('*.md')):
        items[f'ref-{f.name}'] = f.read_text(encoding='utf-8')
    prof = ['# Business profiles (KPI definitions)\n']
    for f in sorted((SK / 'assets/profiles').glob('*.yaml')):
        prof.append(f'\n## {f.stem}\n```yaml\n{f.read_text(encoding="utf-8")}```\n')
    items['profiles.md'] = ''.join(prof)
    items['example-dashboard.yaml.md'] = '# Example generated dashboard\n```yaml\n' + (SK / 'assets/examples/demo_dashboard.yaml').read_text(encoding='utf-8') + '```\n'
    items['example-package.yaml.md'] = '# Example infra package\n```yaml\n' + (SK / 'assets/examples/packages/dxbmark_infra.yaml').read_text(encoding='utf-8') + '```\n'
    return items

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=str(REPO / 'dist')); a = ap.parse_args()
    errs, _ = lint(SK)
    if errs:
        print('lint failed:', *errs, sep='\n  '); return 1
    ver = json.loads((REPO / '.claude-plugin/plugin.json').read_text())['version']
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    made = [build_skill_zip(out, ver)]
    cz = out / f'chatgpt-pack-{ver}.zip'
    with zipfile.ZipFile(cz, 'w', zipfile.ZIP_DEFLATED) as zf:
        for n in ('instructions.md', 'instructions-lite.md'):
            zf.write(REPO / 'chatgpt' / n, n)
        for n, t in flat_knowledge().items():
            zf.writestr(f'knowledge/{n}', t)
    made.append(cz)
    gem = out / 'gem-instructions.md'
    gem.write_text((REPO / 'chatgpt/instructions.md').read_text(encoding='utf-8'), encoding='utf-8')
    made.append(gem)
    (out / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in made))
    for p in made: print(f'{p.stat().st_size:>9}  {p.name}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
