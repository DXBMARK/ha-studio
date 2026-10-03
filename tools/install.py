#!/usr/bin/env python3
"""Install the skill folder for a given platform. Dry-run by default; nothing is written without --yes.

  python3 tools/install.py --target codex-user        [--yes] [--symlink]
  python3 tools/install.py --target codex-repo --dest /path/to/project
  targets: claude-code-user (~/.claude/skills), claude-code-project (<dest>/.claude/skills),
           codex-user (~/.agents/skills), codex-repo (<dest>/.agents/skills),
           antigravity-user (~/.gemini/config/skills; 2.0/IDE), antigravity-cli-user (~/.gemini/antigravity-cli/skills), antigravity-project (<dest>/.agents/skills),
           gemini-cli-project (<dest>/.gemini/skills)

Existing installs are never overwritten: the installer stops and tells you to remove or rename the old folder yourself.
Antigravity/Gemini global paths differ between versions — confirm against the current docs for your release.
"""
import argparse, pathlib, shutil, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / 'skills' / 'ha-studio'
H = pathlib.Path.home()
TARGETS = {
    'claude-code-user': lambda d: H / '.claude/skills',
    'claude-code-project': lambda d: d / '.claude/skills',
    'codex-user': lambda d: H / '.agents/skills',
    'codex-repo': lambda d: d / '.agents/skills',
    'antigravity-user': lambda d: H / '.gemini/config/skills',
    'antigravity-cli-user': lambda d: H / '.gemini/antigravity-cli/skills',
    'antigravity-project': lambda d: d / '.agents/skills',
    'gemini-cli-project': lambda d: d / '.gemini/skills',
}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--target', required=True, choices=sorted(TARGETS)); ap.add_argument('--dest', default='.')
    ap.add_argument('--yes', action='store_true', help='actually write'); ap.add_argument('--symlink', action='store_true')
    a = ap.parse_args()
    base = TARGETS[a.target](pathlib.Path(a.dest).resolve())
    target = base / SRC.name
    print(f'{"symlink" if a.symlink else "copy"}: {SRC}\n   → {target}')
    if target.exists() or target.is_symlink():
        print('refusing: target already exists. Remove or rename it yourself, then re-run.'); return 1
    if not a.yes:
        print('dry run (add --yes to write).'); return 0
    base.mkdir(parents=True, exist_ok=True)
    if a.symlink: target.symlink_to(SRC, target_is_directory=True)
    else: shutil.copytree(SRC, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print('installed.'); return 0

if __name__ == '__main__':
    sys.exit(main())
