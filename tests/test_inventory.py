import ha_inventory as hi

def test_classification_by_device_class():
    assert hi.classify('sensor.x_power', {'device_class': 'power'}) == 'power'
    assert hi.classify('sensor.x_energy', {'device_class': 'energy'}) == 'energy'
    assert hi.classify('camera.door', {}) == 'camera'
    assert hi.classify('binary_sensor.d', {'device_class': 'door'}) == 'security'
    assert hi.classify('sensor.pve_node_cpu_usage', {}) == 'infra'
    assert hi.classify('sensor.backup_state', {}) == 'backup'
    assert hi.classify('foo.bar', {}) == 'other'

def test_normalise_flags_unavailable(states):
    ents = hi.normalise(states)
    bad = [e for e in ents if e['unavailable']]
    assert [e['entity_id'] for e in bad] == ['sensor.old_zigbee_plug_power']

def test_demo_inventory_counts(inv):
    assert inv['counts']['camera'] == 4 and inv['counts']['power'] == 10

def test_no_write_methods_in_source():
    src = (hi.__file__ and open(hi.__file__).read())
    assert "method='POST'" not in src and 'method="POST"' not in src and "'PUT'" not in src
    assert '/api/services' not in src
