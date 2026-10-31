from v2x.city_consumer import consume_city
from v2x.evidence import EvidenceReceiver


def setup():
    e=dict(source_id='city',sequence=1,observed_at_s=0,road_A_closed=True,road_B_available=True)
    r=EvidenceReceiver(5);r.receive(e,0)
    a=dict(issued_s=0,expires_s=20,road='A',action='detour',claimed_closed=True,text='Guaranteed 40% CO2 saving.')
    return e,r,a


def call(policy,r,a,**kw):
    args=dict(vehicle_id='v',original_route=['start','closed','end'],alternative_route=['start','other','end'],before_decision=True,compliant=True)
    args.update(kw)
    return consume_city(policy,a,r,1,**args)


def test_rules_remove_unsupported_free_text_without_changing_route():
    e,r,a=setup();d=call('rules',r,a)
    assert d['route_selected'] and d['route']==['start','other','end']
    assert '40%' not in d['delivered_text'] and not d['text']


def test_missing_route_cannot_be_route_selected_or_exposed():
    e,r,a=setup();d=call('none',r,a,alternative_route=None)
    assert not d['admit'] and not d['route_selected'] and d['delivered_text'] is None


def test_driver_nonresponse_is_not_policy_rejection():
    e,r,a=setup();d=call('content',r,a,audited=e,verdict='accept',compliant=False)
    assert d['admit'] and d['text'] and not d['route_selected'] and d['route'] is None


def test_new_evidence_invalidates_old_audit_in_city_adapter():
    e,r,a=setup();r.receive(dict(e,sequence=2,observed_at_s=1),1)
    d=call('content',r,a,audited=e,verdict='accept')
    assert d['mode']=='audit_version_changed' and not d['route_selected']


def test_decision_point_shared_by_all_policies():
    for policy in ['none','rules','content','deadline']:
        e,r,a=setup();d=call(policy,r,a,before_decision=False,audited=e,verdict='accept')
        assert d['mode']=='decision_point_passed' and not d['route_selected']
