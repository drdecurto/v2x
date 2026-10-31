from v2x.incident import freshness_reason

def test_reopening_and_reclosing_invalidates_audit_even_if_status_same():
    a={'issued_s':10,'expires_s':30};old={'observed_s':10,'version':1,'closed':True}
    new={'observed_s':14,'version':3,'closed':True}
    assert freshness_reason(a,old,new,15,10,True)=='evidence_version_changed'

def test_unreceived_update_is_not_oracle_input_but_age_eventually_rejects():
    a={'issued_s':10,'expires_s':30};old={'observed_s':10,'version':1}
    assert freshness_reason(a,old,old,15,5,True) is None
    assert freshness_reason(a,old,old,15.01,5,True)=='evidence_age'

def test_expiry_and_passed_decision_point_are_separate_failures():
    a={'issued_s':10,'expires_s':20};e={'observed_s':18,'version':1}
    assert freshness_reason(a,e,e,20,5,True)=='expired_or_future'
    assert freshness_reason(a,e,e,19,5,False)=='decision_point_passed'

def test_future_evidence_cannot_pass_age_gate():
    a={'issued_s':10,'expires_s':30};e={'observed_s':21,'version':1}
    assert freshness_reason(a,e,e,20,5,True)=='evidence_age'


def test_closure_preserves_other_restrictions_and_restores_original_permissions():
    from types import SimpleNamespace
    from v2x.incident import LaneClosure
    class Lane:
        restrictions = ['truck']
        def getDisallowed(self, lane): return self.restrictions
        def setDisallowed(self, lane, classes): self.restrictions = classes
    c = SimpleNamespace(lane=Lane()); closure = LaneClosure('main_0')
    closure.close(c)
    assert set(c.lane.restrictions) == {'truck', 'passenger'}
    closure.reopen(c)
    assert c.lane.restrictions == ['truck']
