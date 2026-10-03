#!/usr/bin/env python3
"""Lint the skill folder against the open Agent Skills format and this repo's own rules.

  lint_skill.py [skills/ha-studio]

Errors (exit 1): frontmatter keys/limits, name == folder name, forbidden words in name, SKILL.md length,
broken relative links in SKILL.md/references, secrets, YAML/JSON that does not parse, missing license notice.
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _common import load_yaml, find_secrets

ALLOWED_KEYS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}

def lint(root):
    root = pathlib.Path(root)
    errs, warns = [], []
    sk = root / 'SKILL.md'
    if not sk.exists():
        return ['SKILL.md missing'], warns
    text = sk.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return ['SKILL.md has no YAML frontmatter'], warns
    fm = load_yaml_str(m.group(1))
    extra = set(fm) - ALLOWED_KEYS
    if extra: errs.append(f'unknown frontmatter keys: {sorted(extra)}')
    name, desc = fm.get('name', ''), fm.get('description', '')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name or ''): errs.append('name must be lowercase-hyphen')
    if len(name) > 64: errs.append('name > 64 chars')
    if re.search(r'claude|anthropic', name): errs.append('name must not contain "claude"/"anthropic"')
    if name != root.name: errs.append(f'name "{name}" != folder "{root.name}"')
    if not desc: errs.append('description missing')
    elif len(desc) > 1024: errs.append(f'description {len(desc)} > 1024 chars')
    if re.search(r'[<>]', desc): errs.append('description must not contain angle brackets')
    body = text[m.end():]
    n = len(text.splitlines())
    if n > 500: errs.append(f'SKILL.md has {n} lines (>500); move detail to references/')
    for md in [sk] + sorted((root / 'references').glob('*.md')):
        t = md.read_text(encoding='utf-8')
        for link in re.findall(r'\]\((?!https?:|#|mailto:)([^)\s]+)\)', t) + re.findall(r'`((?:references|scripts|assets)/[^`\s]+)`', t):
            tgt = (md.parent / link).resolve() if not link.startswith(('references/', 'scripts/', 'assets/')) else (root / link).resolve()
            if '*' in link or '<' in link: continue
            if not tgt.exists(): errs.append(f'{md.relative_to(root)}: broken path {link}')
    for f in root.rglob('*'):
        if not f.is_file() or f.suffix in ('.png', '.jpg', '.woff2', '.ttf', '.pyc'): continue
        try: t = f.read_text(encoding='utf-8')
        except Exception: continue
        for s in find_secrets(t): errs.append(f'{f.relative_to(root)}: secret-like string {s}')
        if f.suffix in ('.yaml', '.yml'):
            try: load_yaml(f)
            except Exception as e: errs.append(f'{f.relative_to(root)}: YAML error {e}')
        if f.suffix == '.json':
            try: json.loads(t)
            except Exception as e: errs.append(f'{f.relative_to(root)}: JSON error {e}')
    return errs, warns

def load_yaml_str(s):
    import yaml
    return yaml.safe_load(s) or {}

def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('skill_dir', nargs='?', default=str(pathlib.Path(__file__).resolve().parent.parent))
    root = ap.parse_args().skill_dir
    errs, warns = lint(root)
    for w in warns: print('warn :', w)
    for e in errs: print('ERROR:', e)
    print(f'{"FAIL" if errs else "OK"}: {len(errs)} error(s), {len(warns)} warning(s)')
    return 1 if errs else 0

if __name__ == '__main__':
    sys.exit(main())
