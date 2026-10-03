import json, pathlib, sys
REPO = pathlib.Path(__file__).resolve().parent.parent
SK = REPO / 'skills' / 'ha-studio'
sys.path.insert(0, str(SK / 'scripts'))
import pytest

@pytest.fixture(scope='session')
def inv():
    return json.loads((SK / 'assets/examples/demo_inventory.json').read_text())

@pytest.fixture(scope='session')
def states():
    return json.loads((SK / 'assets/examples/demo_states.json').read_text())
