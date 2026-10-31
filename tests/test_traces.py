import pandas as pd
import pytest
from v2x.traces import align_packets

def fixture():
    tx=pd.DataFrame({'tx_equipment_id':[1]*5,'seq_num':range(5),'timestamp':[0,1000,2000,3000,4000]})
    rx=pd.DataFrame({'tx_equipment_id':[1,1,1],'tx_seq_num':[1,3,99],'tx_timestamp (us)':[1000,3000,99000],'rx_timestamp (us)':[1100,3100,99100],'latency (ms)':[.1,.1,.1],'extra':[0,0,1]})
    return tx,rx

def test_missing_tx_is_loss_only_inside_observed_support():
    t,r=fixture();out,stats=align_packets(t,r)
    assert stats['boundary_tx_excluded']==2
    assert stats['observed_tx']==3 and stats['received']==2
    assert out['received'].tolist()==[True,False,True]

def test_negative_delay_stops_ingestion():
    t,r=fixture();r.loc[0,'rx_timestamp (us)']=900
    with pytest.raises(ValueError,match='Negative delay'):align_packets(t,r)

def test_duplicate_identity_stops_ingestion():
    t,r=fixture();t=pd.concat([t,t.iloc[[0]]])
    with pytest.raises(ValueError,match='Duplicate'):align_packets(t,r)
