import energy_audit as ea

def test_stem_strips_repeated_suffix():
    assert ea.stem('sensor.grid_energy_import') == 'grid'
    assert ea.stem('sensor.reception_lights_power') == 'reception_lights'

def test_audit_demo(inv):
    r = ea.audit(inv)
    assert len(r['paired']) == 8
    assert r['missing_energy'] == ['sensor.coffee_machine_power', 'sensor.old_zigbee_plug_power']
    assert [b['entity_id'] for b in r['bad_state_class']] == ['sensor.printer_energy']
    assert r['untracked']['grid_entity'] == 'sensor.grid_power'
    assert round(r['untracked']['untracked_w']) == 567

def test_report_mentions_riemann(inv):
    txt = ea.report(ea.audit(inv))
    assert 'Riemann' in txt and 'sensor.coffee_machine_power' in txt

def test_negative_untracked_explained(inv):
    import copy
    i = copy.deepcopy(inv)
    for e in i['entities']:
        if e['entity_id'] == 'sensor.grid_power': e['state'] = '100'
    assert 'overlap' in ea.report(ea.audit(i))
