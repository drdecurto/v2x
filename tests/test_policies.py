from v2x.policy import decide,rules_valid,common_valid

def fixture():
    return {'issued_s':10,'expires_s':20,'road':'A','claimed_closed':True,'action':'detour'}, {'road_A_closed':True,'road_B_available':True}

def test_expiry_is_exclusive_for_every_policy():
    a,e=fixture()
    for p in ('none','rules','content','deadline'):
        assert not decide(p,a,e,20,3,1,'accept')['admit']

def test_fabricated_closure_rejected_by_rules_even_if_llm_accepts():
    a,e=fixture();e['road_A_closed']=False
    for p in ('rules','content','deadline'):
        assert not decide(p,a,e,11,3,1,'accept')['admit']

def test_deadline_fallback_uses_template_and_no_model_delay():
    a,e=fixture()
    d=decide('deadline',a,e,11,1,2,'reject')
    assert d['admit'] and not d['text'] and d['delay_s']==0

def test_unknown_model_output_not_silently_accepted():
    a,e=fixture()
    assert not decide('content',a,e,11,3,1,None)['admit']
