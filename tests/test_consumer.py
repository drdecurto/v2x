from v2x.consumer import consume
from v2x.evidence import EvidenceReceiver
import pytest
A={'issued_s':0,'expires_s':20,'road':'A','action':'main','claimed_closed':False}
def evidence(seq=1,stamp=0,closed=False):return dict(source_id='rsu',sequence=seq,observed_at_s=stamp,road_A_closed=closed,road_B_available=True)
@pytest.mark.parametrize('policy',['none','rules','content','deadline'])
def test_common_unavailable_fallback(policy):
 r=EvidenceReceiver(5)
 assert consume(policy,A,r,1,before_junction=True)['mode']=='evidence_unavailable'
 r.receive(evidence(),1)
 assert consume(policy,A,r,6,before_junction=True)['mode']=='evidence_unavailable'
def test_new_observation_invalidates_old_audit_even_same_state():
 r=EvidenceReceiver(5);old=evidence();r.receive(old,0);r.receive(evidence(2,2),2)
 assert consume('content',A,r,3,before_junction=True,audited=old,verdict='accept')['mode']=='audit_version_changed'
 assert consume('deadline',A,r,3,before_junction=True,deadline_fallback=True)['mode']=='verified_template'
def test_observed_closed_route_blocks_all():
 for policy in ['none','rules','content','deadline']:
  r=EvidenceReceiver(5);r.receive(evidence(closed=True),0)
  assert consume(policy,A,r,1,before_junction=True)['mode']=='observed_route_unavailable'
def test_unseen_change_cannot_be_inferred():
 r=EvidenceReceiver(5);old=evidence();r.receive(old,0)
 assert consume('content',A,r,2,before_junction=True,audited=old,verdict='accept')['admit']
