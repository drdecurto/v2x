import pytest
from v2x.replay import replay_observations

def obs():return [{'source_id':'a','sequence':1,'observed_at_s':0},{'source_id':'a','sequence':2,'observed_at_s':1}]
def p(t,seq,received=True,delay=0):return dict(tx_offset_s=t,seq=seq,received=received,delay_s=delay)
def test_reordered_arrivals_never_roll_back_receiver():
 _,r=replay_observations([p(0,0,delay=2),p(1,1,delay=.1)],obs(),epoch_s=0,max_age_s=3)
 assert [(x['observation_sequence'],x['decision']) for x in r]==[(2,'updated'),(1,'superseded_rejected')]
def test_loss_does_not_reveal_new_source_state():
 e,r=replay_observations([p(.5,0),p(1,1,False),p(1.1,2,False)],obs(),epoch_s=0,max_age_s=5)
 assert [x['received'] for x in e]==[True,False,False] and len(r)==1 and r[0]['observation_sequence']==1
 assert e[0]['observation_sequence']==1
@pytest.mark.parametrize('delay,decision',[(5,'updated'),(5.001,'age_rejected')])
def test_age_boundary(delay,decision):
 _,r=replay_observations([p(0,0,delay=delay)],obs(),epoch_s=0,max_age_s=5)
 assert r[0]['decision']==decision
@pytest.mark.parametrize('packets',[[p(1,0),p(.5,1)],[p(0,0,delay=-.1)],[p(0,0,delay=float('nan'))]])
def test_invalid_timing_rejected(packets):
 with pytest.raises(ValueError):replay_observations(packets,obs(),epoch_s=0,max_age_s=5)
def test_no_trace_loop_or_future_observation():
 with pytest.raises(ValueError,match='causally'):replay_observations([p(0,0)],obs()[1:],epoch_s=0,max_age_s=5)
