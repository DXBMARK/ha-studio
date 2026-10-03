"""Shared helpers for ha-studio scripts (stdlib + PyYAML only)."""
import json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECRET_PATTERNS = [
    re.compile(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}'),      # JWT / HA long-lived token
    re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),                                          # GitHub tokens
    re.compile(r'(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{30,}'),                                               # API keys
    re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\']?[A-Za-z0-9/_+=-]{16,}'),
]

def _loader():
    import yaml
    class HALoader(yaml.SafeLoader):
        """SafeLoader that tolerates Home Assistant's custom tags (!secret, !include, ...)."""
    def _any(loader, suffix, node):
        if isinstance(node, yaml.ScalarNode):
            return f'!{suffix} {loader.construct_scalar(node)}'
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_mapping(node)
    HALoader.add_multi_constructor('!', _any)
    return HALoader

def load_yaml(path):
    import yaml
    with open(path, encoding='utf-8') as f:
        return yaml.load(f, Loader=_loader())

def dump_yaml(data, header=''):
    import yaml
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    return (header.rstrip() + '\n' if header else '') + body

def find_secrets(text):
    return ['[redacted]' for p in SECRET_PATTERNS for m in p.finditer(text)]

def die(msg, code=2):
    print(f'error: {msg}', file=sys.stderr)
    sys.exit(code)


def write_text(path, text, force=False):
    """Write an output file; refuse to overwrite an existing one unless force=True."""
    p = pathlib.Path(path)
    if p.exists() and not force:
        die(f'{p} already exists; choose another --out or pass --force')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
